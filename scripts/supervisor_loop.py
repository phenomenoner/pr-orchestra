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
from pathlib import Path

# Ensure we can import supervisor.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from supervisor import gh_api_json

ROLE_FILE = Path(".agent_role.json")
WORK_REQUESTS = Path("work/requests")

def load_role_config():
    if not ROLE_FILE.exists():
        print("❌ .agent_role.json not found. Run bootstrap.py first.")
        sys.exit(1)
    with open(ROLE_FILE) as f:
        return json.load(f)

def get_token(env_var_name):
    token = os.environ.get(env_var_name)
    if not token:
        # Fallback for testing/mocking if not set
        if os.environ.get("MOCK_MODE"):
            return "mock_token"
        print(f"❌ Token environment variable '{env_var_name}' is not set.")
        sys.exit(1)
    return token

def fetch_tasks(repo_url, token):
    # Parse owner/repo from URL
    # Expected: https://github.com/owner/repo or git@github.com:owner/repo.git
    # Simplification: assume we can extract from string or use "owner/repo" if configured that way
    # For now, let's try to extract.
    
    clean_url = repo_url.rstrip(".git")
    if "github.com/" in clean_url:
        owner_repo = clean_url.split("github.com/")[-1]
    elif "github.com:" in clean_url:
        owner_repo = clean_url.split("github.com:")[-1]
    else:
        # Fallback or assume just owner/repo was passed
        owner_repo = clean_url

    print(f"🔎 Scanning issues in {owner_repo} with label 'agent-task'...")
    
    if token == "mock_token":
        # Return dummy issues for verification
        return [{
            "number": 101,
            "title": "Update README with new architecture",
            "body": "Please add the dual-mode architecture description to README.md.\n\nAcceptance Criteria:\n- Mention Supervisor and Contributor roles\n- Update status",
            "labels": [{"name": "agent-task"}]
        }]

    url = f"https://api.github.com/repos/{owner_repo}/issues?labels=agent-task&state=open"
    try:
        issues = gh_api_json(url, token)
        return issues if isinstance(issues, list) else []
    except Exception as e:
        print(f"⚠️ Error fetching issues: {e}")
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
            "allowed_globs": ["**/*"], # Broad for now, can be restricted
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
        print(f"❌ Configured role is '{config['role']}', but this is the supervisor loop.")
        sys.exit(1)

    token = get_token(config["token_env_var"])
    repo_url = config["repo_url"]

    print("🤖 Supervisor Loop Started...")
    print(f"   Repo: {repo_url}")
    print("   Press Ctrl+C to stop.")

    while True:
        try:
            issues = fetch_tasks(repo_url, token)
            
            for issue in issues:
                task_id = f"issue-{issue['number']}"
                task_file = WORK_REQUESTS / f"{task_id}.json"
                
                if not task_file.exists():
                    print(f"✨ Found new task: #{issue['number']} - {issue['title']}")
                    defn = generate_task_definition(issue, config)
                    with open(task_file, "w") as f:
                        json.dump(defn, f, indent=2)
                    print(f"   -> Generated task definition: {task_file}")
                else:
                    # Task already dispatched
                    pass
            
            time.sleep(10)
        except KeyboardInterrupt:
            print("\n🛑 Stopping supervisor.")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
