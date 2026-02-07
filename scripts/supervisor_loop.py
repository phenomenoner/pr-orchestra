#!/usr/bin/env python3
"""
supervisor_loop.py - Supervisor Role Logic
==========================================

1. Scans GitHub Issues for 'agent-task' label.
2. Converts Issue -> task_definition.json.
3. Places task in work/requests/ (simulating dispatch).
"""

import json
import os
import sys
import time
import re
from pathlib import Path

# Ensure we can import supervisor.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from supervisor import gh_api_json

ROLE_FILE = Path(".agent_role.json")
WORK_REQUESTS = Path("work/requests")


def load_role_config():
    if not ROLE_FILE.exists():
        print("ERROR: .agent_role.json not found. Run bootstrap.py first.")
        sys.exit(1)
    with open(ROLE_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_token(env_var_name):
    token = os.environ.get(env_var_name)
    if not token:
        # Fallback for testing/mocking if not set
        if os.environ.get("MOCK_MODE"):
            return "mock_token"
        print(f"ERROR: Token environment variable '{env_var_name}' is not set.")
        sys.exit(1)
    return token


def parse_owner_repo(repo_ref: str) -> str:
    s = (repo_ref or "").strip()
    if not s:
        raise ValueError("Repository reference is empty.")

    if s.startswith("git@github.com:"):
        s = s.split(":", 1)[1]
    elif s.startswith("https://github.com/"):
        s = s[len("https://github.com/") :]
    elif s.startswith("http://github.com/"):
        s = s[len("http://github.com/") :]

    if s.endswith(".git"):
        s = s[:-4]
    s = s.strip("/")

    if s.count("/") != 1:
        raise ValueError(f"Invalid repository reference '{repo_ref}'. Expected owner/repo.")

    owner, name = s.split("/", 1)
    if not owner or not name:
        raise ValueError(f"Invalid repository reference '{repo_ref}'. Expected owner/repo.")
    return f"{owner}/{name}"


def infer_allowed_globs(issue: dict) -> list[str]:
    body = str(issue.get("body", "") or "")
    title = str(issue.get("title", "") or "")
    text = f"{title}\n{body}"

    explicit_line = None
    for line in text.splitlines():
        if line.lower().startswith("allowed paths:"):
            explicit_line = line.split(":", 1)[1]
            break
    if explicit_line:
        items = [x.strip() for x in explicit_line.split(",") if x.strip()]
        if items:
            return items

    paths = []
    for match in re.finditer(r"`([^`]+)`", text):
        candidate = match.group(1).strip()
        if "/" in candidate or "." in candidate:
            if candidate not in paths:
                paths.append(candidate)

    if paths:
        return paths

    # Safer default than **/*; supervisors should narrow this per task as needed.
    return [
        "src/**",
        "scripts/**",
        "tests/**",
        "docs/**",
        "templates/**",
        ".supervisor-agent.yml",
        "README.md",
    ]


def fetch_tasks(repo_url, token):
    try:
        owner_repo = parse_owner_repo(repo_url)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return []

    print(f"Scanning issues in {owner_repo} with label 'agent-task'...")

    if token == "mock_token":
        # Return dummy issues for verification
        return [
            {
                "number": 101,
                "title": "Update README with new architecture",
                "body": "Please add the dual-mode architecture description to `README.md`.\n\nAcceptance Criteria:\n- Mention Supervisor and Contributor roles\n- Update status",
                "labels": [{"name": "agent-task"}],
            }
        ]

    url = f"https://api.github.com/repos/{owner_repo}/issues?labels=agent-task&state=open"
    try:
        issues = gh_api_json(url, token)
        return issues if isinstance(issues, list) else []
    except Exception as e:
        print(f"WARNING: Error fetching issues: {e}")
        return []


def generate_task_definition(issue, config):
    # Convert Issue to Task Definition Schema
    task_id = f"issue-{issue['number']}"

    # Simple heuristic to parse body
    body = issue.get("body", "") or ""

    definition = {
        "task_id": task_id,
        "role": "worker",
        "canonical_language": "en",
        "repo": {
            "path": config.get("workspace_root", "."),
            "base_ref": "main",
            "target_branch": f"worker/{task_id}"
        },
        "scope": {
            "allowed_globs": infer_allowed_globs(issue),
            "deny_globs": [".github/workflows/**"],
            "max_files_changed": 10,
            "max_additions": 1000,
            "max_deletions": 1000
        },
        "goal": {
            "title": issue["title"],
            "description": body,
            "acceptance_criteria": ["Check PR description"],
            "test_plan": ["echo 'No automatic tests defined yet'"]
        },
        "stop_conditions": ["security-sensitive", "secrets-required"]
    }
    return definition


def main():
    config = load_role_config()
    if config["role"] != "supervisor":
        print(f"ERROR: Configured role is '{config['role']}', but this is the supervisor loop.")
        sys.exit(1)

    token = get_token(config["token_env_var"])
    repo_url = config["repo_url"]

    print("Supervisor loop started...")
    print(f"   Repo: {repo_url}")
    print("   Press Ctrl+C to stop.")

    WORK_REQUESTS.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            issues = fetch_tasks(repo_url, token)

            for issue in issues:
                task_id = f"issue-{issue['number']}"
                task_file = WORK_REQUESTS / f"{task_id}.json"

                if not task_file.exists():
                    print(f"Found new task: #{issue['number']} - {issue['title']}")
                    defn = generate_task_definition(issue, config)
                    with open(task_file, "w", encoding="utf-8") as f:
                        json.dump(defn, f, indent=2)
                    print(f"   -> Generated task definition: {task_file}")

            time.sleep(10)
        except KeyboardInterrupt:
            print("\nStopping supervisor.")
            break
        except Exception as e:
            print(f"WARNING: Unexpected error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
