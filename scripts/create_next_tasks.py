#!/usr/bin/env python3
"""Create GitHub Issues for next tasks.

Input formats:
- JSON file: list of {"title": "...", "body": "...", "labels": ["..."]}
  or {"tasks": [ ... ]}
- Markdown file: use headings for tasks:

  ## Task title
  Body lines...

Usage:
  python3 scripts/create_next_tasks.py --repo owner/name --input tasks.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Ensure we can import supervisor.py (stdlib GH API helper)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from supervisor import gh_api_post  # noqa: E402


def eprint(*a: object) -> None:
    print(*a, file=sys.stderr)


def parse_repo(repo: str) -> tuple[str, str]:
    s = repo.strip()
    s = s.removeprefix("https://github.com/")
    if s.endswith(".git"):
        s = s[:-4]
    if "/" not in s:
        raise ValueError(f"Invalid repo '{repo}'. Expected owner/name")
    owner, name = s.split("/", 1)
    if not owner or not name:
        raise ValueError(f"Invalid repo '{repo}'. Expected owner/name")
    return owner, name


def parse_markdown_tasks(text: str) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    cur_title: str | None = None
    cur_lines: list[str] = []

    for line in (text or "").splitlines():
        m = re.match(r"^\s*##+\s+(.+?)\s*$", line)
        if m:
            if cur_title:
                tasks.append({"title": cur_title, "body": "\n".join(cur_lines).strip()})
            cur_title = m.group(1).strip()
            cur_lines = []
        else:
            if cur_title is not None:
                cur_lines.append(line)

    if cur_title:
        tasks.append({"title": cur_title, "body": "\n".join(cur_lines).strip()})

    if not tasks:
        raise ValueError("No tasks found in markdown. Use '## Title' headings for each task.")

    for t in tasks:
        if not t.get("title"):
            raise ValueError("Task title cannot be empty in markdown input.")

    return tasks


def load_tasks_from_json(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        tasks = data
    elif isinstance(data, dict) and isinstance(data.get("tasks"), list):
        tasks = data["tasks"]
    else:
        raise ValueError("Invalid JSON format. Expected a list or {\"tasks\": [...]}.")

    if not tasks:
        raise ValueError("No tasks found in JSON input.")

    parsed: list[dict[str, Any]] = []
    for item in tasks:
        if not isinstance(item, dict):
            raise ValueError("Each task must be a JSON object.")
        title = str(item.get("title", "")).strip()
        if not title:
            raise ValueError("Each task requires a non-empty 'title'.")
        body = str(item.get("body", "") or "")
        labels = item.get("labels")
        if labels is not None and not isinstance(labels, list):
            raise ValueError("Task 'labels' must be a list of strings if provided.")
        parsed.append({"title": title, "body": body, "labels": labels or []})
    return parsed


def load_tasks(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".json"}:
        data = json.loads(text)
        return load_tasks_from_json(data)
    if suffix in {".md", ".markdown", ".txt"}:
        return parse_markdown_tasks(text)

    # Fallback: try JSON, then markdown
    try:
        data = json.loads(text)
        return load_tasks_from_json(data)
    except Exception:
        return parse_markdown_tasks(text)


def normalize_labels(default_labels: list[str], task_labels: list[str]) -> list[str]:
    merged: list[str] = []
    for lb in default_labels + task_labels:
        s = str(lb).strip()
        if s and s not in merged:
            merged.append(s)
    return merged


def build_issue_payload(task: dict[str, Any], default_labels: list[str]) -> dict[str, Any]:
    title = str(task.get("title", "")).strip()
    body = str(task.get("body", "") or "")
    labels = normalize_labels(default_labels, [str(x) for x in task.get("labels", [])])
    payload: dict[str, Any] = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    return payload


def create_issue(owner: str, name: str, token: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{owner}/{name}/issues"
    return gh_api_post(url, token, payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create GitHub Issues for next tasks.")
    parser.add_argument("--repo", required=True, help="Repo in owner/name or GitHub URL form.")
    parser.add_argument("--input", required=True, help="Path to tasks file (markdown or JSON).")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without creating issues.")
    parser.add_argument(
        "--label",
        action="append",
        dest="labels",
        help="Label to apply (repeatable). Defaults to 'agent-task'.",
    )
    parser.add_argument("--no-label", action="store_true", help="Disable default labels entirely.")
    parser.add_argument(
        "--token-env",
        default="GITHUB_TOKEN",
        help="Environment variable holding a GitHub token (default: GITHUB_TOKEN).",
    )

    args = parser.parse_args()

    try:
        owner, name = parse_repo(args.repo)
    except ValueError as e:
        eprint(f"❌ {e}")
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        eprint(f"❌ Input file not found: {input_path}")
        sys.exit(1)

    try:
        tasks = load_tasks(input_path)
    except Exception as e:
        eprint(f"❌ Failed to parse input: {e}")
        sys.exit(1)

    if args.no_label:
        default_labels: list[str] = []
    elif args.labels:
        default_labels = [str(x) for x in args.labels]
    else:
        default_labels = ["agent-task"]

    token = os.environ.get(args.token_env)
    if not args.dry_run and not token:
        eprint(f"❌ Token environment variable '{args.token_env}' is not set.")
        sys.exit(1)

    had_error = False
    for task in tasks:
        payload = build_issue_payload(task, default_labels)
        title = payload.get("title", "(untitled)")

        if args.dry_run:
            print(f"DRY-RUN: would create issue: {title}")
            continue

        try:
            created = create_issue(owner, name, str(token), payload)
            url = created.get("html_url", "") if isinstance(created, dict) else ""
            if url:
                print(url)
            else:
                print(f"Created issue: {title}")
        except Exception as e:
            had_error = True
            eprint(f"❌ Failed to create issue '{title}': {e}")

    if had_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
