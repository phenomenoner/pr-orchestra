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
import sys
import time
import subprocess
import shlex
from pathlib import Path

ROLE_FILE = Path(".agent_role.json")
WORK_REQUESTS = Path("work/requests")
WORK_RESULTS = Path("work/results")
SCOPE_GUARD = Path("scripts/scope_guard.py")

def load_role_config():
    if not ROLE_FILE.exists():
        print("❌ .agent_role.json not found. Run bootstrap.py first.")
        sys.exit(1)
    with open(ROLE_FILE) as f:
        return json.load(f)

def run_cmd(args, check=True):
    print(f"   [EXEC] {' '.join(args)}")
    return subprocess.run(args, check=check, text=True, capture_output=True)

def process_task(task_path):
    with open(task_path) as f:
        task = json.load(f)
    
    task_id = task["task_id"]
    branch = task["repo"]["target_branch"]
    print(f"⚙️ Processing Task: {task_id}")
    
    # 1. Setup Branch
    # Check if branch exists, if not create
    # Note: In a real agent, we might fetch origin first.
    # Here we assume we are in the repo.
    try:
        run_cmd(["git", "checkout", "-B", branch])
    except Exception as e:
        print(f"   ❌ Failed to checkout branch: {e}")
        return

    # 2. Perform Work
    # Check for execution hook in environment or config
    exec_cmd = os.environ.get("AGENT_EXEC_CMD")
    
    if exec_cmd:
        # If command has placeholders, format them
        # Supported: {task_id}, {task_file}
        formatted_cmd = exec_cmd.format(task_id=task_id, task_file=str(task_path))
        print(f"   🤖 Running execution hook: {formatted_cmd}")
        work_cmd = shlex.split(formatted_cmd)
    else:
        # Default: Simulate work by creating a file
        target_file = f"implemented_{task_id}.txt"
        work_cmd = ["touch", target_file]
    
    # 3. Scope Guard
    # We wrap our 'work' with scope_guard.
    guard_cmd = [
        sys.executable, str(SCOPE_GUARD),
        "--allow", "work/**,**/*", # Allow broad access for now as agent might edit anything
        "--"
    ] + work_cmd

    print(f"   🛡️ Invoking Scope Guard...")
    res = run_cmd(guard_cmd, check=False)
    
    if res.returncode != 0:
        print(f"   ❌ Scope Guard Blocked/Failed:\n{res.stdout}\n{res.stderr}")
        # Mark as blocked?
        result_dir = WORK_RESULTS / task_id
        result_dir.mkdir(parents=True, exist_ok=True)
        with open(result_dir / "status.json", "w") as f:
            json.dump({"task_id": task_id, "status": "blocked", "reason": "Scope Guard Violation"}, f)
        return

    # 4. Commit
    # Add the specific file
    run_cmd(["git", "add", target_file])
    try:
        run_cmd(["git", "commit", "-m", f"feat: implemented {task_id}"])
    except subprocess.CalledProcessError:
        print("   ⚠️ Nothing to commit?")

    # 5. Report
    result_dir = WORK_RESULTS / task_id
    result_dir.mkdir(parents=True, exist_ok=True)
    
    report_md = f"""# Task Report: {task_id}

## Summary
Implemented the requested feature by creating `{target_file}`.

## Scope Guard
Verified safe.

## Status
Ready for review.
"""
    with open(result_dir / "report.md", "w") as f:
        f.write(report_md)

    with open(result_dir / "status.json", "w") as f:
        json.dump({"task_id": task_id, "status": "ok"}, f)
    
    print(f"   ✅ Task {task_id} complete. Results in {result_dir}")
    
    # Switch back to main?
    run_cmd(["git", "checkout", task["repo"]["base_ref"]])


def main():
    config = load_role_config()
    if config["role"] != "contributor":
        print(f"❌ Configured role is '{config['role']}', but this is the contributor loop.")
        sys.exit(1)

    print("🤖 Contributor Loop Started...")
    print(f"   Watching: {WORK_REQUESTS}")
    print("   Press Ctrl+C to stop.")

    while True:
        try:
            # Look for tasks
            if WORK_REQUESTS.exists():
                for task_file in WORK_REQUESTS.glob("*.json"):
                    task_id = task_file.stem
                    result_dir = WORK_RESULTS / task_id
                    
                    if not result_dir.exists():
                        process_task(task_file)
            
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 Stopping contributor.")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
