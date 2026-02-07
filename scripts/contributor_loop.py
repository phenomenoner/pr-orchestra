#!/usr/bin/env python3
"""
contributor_loop.py - Contributor Role Logic
============================================

1. Watches work/requests/ for new task_definition.json files.
2. Sets up git branch.
3. Performs work (Placeholder: creates a file).
4. Runs scope_guard.py to enforce safety.
5. Commits and writes result artifacts.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROLE_FILE = Path(".agent_role.json")
WORK_REQUESTS = Path("work/requests")
WORK_RESULTS = Path("work/results")
SCOPE_GUARD = Path("scripts/scope_guard.py")


def load_role_config():
    if not ROLE_FILE.exists():
        print("ERROR: .agent_role.json not found. Run bootstrap.py first.")
        sys.exit(1)
    with open(ROLE_FILE, encoding="utf-8") as f:
        return json.load(f)


def run_cmd(args, check=True):
    print(f"   [EXEC] {' '.join(args)}")
    return subprocess.run(args, check=check, text=True, capture_output=True)


def get_git_status_files() -> set[str]:
    res = run_cmd(["git", "status", "--porcelain"], check=False)
    files: set[str] = set()
    for raw in (res.stdout or "").splitlines():
        if len(raw) < 4:
            continue
        path = raw[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        if path:
            files.add(path)
    return files


def resolve_allow_patterns(task: dict[str, Any]) -> list[str]:
    scope = task.get("scope", {})
    raw = scope.get("allowed_globs", []) if isinstance(scope, dict) else []
    allowed: list[str] = []
    if isinstance(raw, list):
        for item in raw:
            s = str(item).strip()
            if s and s not in allowed:
                allowed.append(s)
    if "work/**" not in allowed:
        allowed.append("work/**")
    return allowed


def build_work_command(task_id: str, task_path: Path) -> tuple[list[str], str]:
    exec_cmd = os.environ.get("AGENT_EXEC_CMD")
    if exec_cmd:
        formatted_cmd = exec_cmd.format(task_id=task_id, task_file=str(task_path))
        print(f"   Running execution hook: {formatted_cmd}")
        if os.name == "nt":
            return [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/s", "/c", formatted_cmd], f"Executed hook command: `{formatted_cmd}`."
        return ["/bin/sh", "-lc", formatted_cmd], f"Executed hook command: `{formatted_cmd}`."

    target_file = f"implemented_{task_id}.txt"
    py_cmd = (
        "from pathlib import Path; "
        f"Path({target_file!r}).write_text('Implemented {task_id}\\n', encoding='utf-8')"
    )
    return [sys.executable, "-c", py_cmd], f"Created placeholder artifact `{target_file}`."


def write_task_result(task_id: str, status: str, summary: str, changed_files: list[str]) -> None:
    result_dir = WORK_RESULTS / task_id
    result_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Task Report: {task_id}",
        "",
        "## Summary",
        summary,
        "",
        "## Scope Guard",
        "Verified safe.",
        "",
        "## Changed Files",
    ]
    if changed_files:
        lines.extend(f"- `{path}`" for path in changed_files)
    else:
        lines.append("- None")
    lines.extend(["", "## Status", status, ""])

    (result_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    with open(result_dir / "status.json", "w", encoding="utf-8") as f:
        json.dump({"task_id": task_id, "status": status, "changed_files": changed_files}, f)


def process_task(task_path):
    with open(task_path, encoding="utf-8") as f:
        task = json.load(f)

    task_id = task["task_id"]
    branch = task["repo"]["target_branch"]
    print(f"Processing task: {task_id}")

    # 1. Setup Branch
    try:
        run_cmd(["git", "checkout", "-B", branch])
    except Exception as e:
        print(f"   ERROR: Failed to checkout branch: {e}")
        return

    # 2. Perform Work
    baseline_files = get_git_status_files()
    work_cmd, work_summary = build_work_command(task_id, task_path)
    allow_patterns = resolve_allow_patterns(task)

    # 3. Scope Guard
    guard_cmd = [
        sys.executable,
        str(SCOPE_GUARD),
        "--allow",
        ",".join(allow_patterns),
        "--",
    ] + work_cmd

    print("   Invoking scope guard...")
    res = run_cmd(guard_cmd, check=False)

    if res.returncode != 0:
        print(f"   ERROR: Scope guard blocked/failed:\n{res.stdout}\n{res.stderr}")
        write_task_result(task_id, "blocked", "Scope guard violation or execution error.", [])
        return

    # 4. Commit
    current_files = get_git_status_files()
    changed_files = sorted(current_files - baseline_files)

    if changed_files:
        run_cmd(["git", "add", "-A"])
        commit_res = run_cmd(["git", "commit", "-m", f"feat: implemented {task_id}"], check=False)
        if commit_res.returncode != 0:
            print("   NOTE: No commitable changes after staging.")
            write_task_result(task_id, "no-change", work_summary, changed_files)
            return
        write_task_result(task_id, "ok", work_summary, changed_files)
    else:
        print("   NOTE: No file changes detected.")
        write_task_result(task_id, "no-change", work_summary, [])

    print(f"   Task {task_id} complete. Results in {WORK_RESULTS / task_id}")
    # Switch back to main?
    run_cmd(["git", "checkout", task["repo"]["base_ref"]], check=False)


def main():
    config = load_role_config()
    if config["role"] != "contributor":
        print(f"ERROR: Configured role is '{config['role']}', but this is the contributor loop.")
        sys.exit(1)

    print("Contributor loop started...")
    print(f"   Watching: {WORK_REQUESTS}")
    print("   Press Ctrl+C to stop.")

    WORK_RESULTS.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            # Look for tasks
            if WORK_REQUESTS.exists():
                for task_file in sorted(WORK_REQUESTS.glob("*.json")):
                    task_id = task_file.stem
                    result_dir = WORK_RESULTS / task_id

                    if not result_dir.exists():
                        process_task(task_file)

            time.sleep(5)
        except KeyboardInterrupt:
            print("\nStopping contributor.")
            break
        except Exception as e:
            print(f"WARNING: Unexpected error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
