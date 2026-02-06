#!/usr/bin/env python3
"""
bootstrap.py - Agent Role Handshake & Initialization
====================================================

Interactive CLI to set the agent's role and configuration.
Saves state to .agent_role.json for subsequent loops.
"""

import json
import os
import sys
import subprocess
from pathlib import Path

ROLE_FILE = Path(".agent_role.json")

def get_default_repo():
    try:
        url = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
        return url
    except Exception:
        return ""

def prompt(question, default=None):
    if default:
        p = f"{question} [{default}]: "
    else:
        p = f"{question}: "
    
    val = input(p).strip()
    return val if val else default

def main():
    print("🤖 Agent Coordination Blueprint - Bootstrap")
    print("==========================================")
    print("This script configures the agent's role for this session.\n")

    # 1. Role Selection
    print("Choose Role:")
    print("  [1] Supervisor  (Scans issues, creates tasks, audits PRs)")
    print("  [2] Contributor (Fetches tasks, implements changes, submits PRs)")
    
    while True:
        choice = prompt("Selection", "1")
        if choice in ["1", "Supervisor", "supervisor"]:
            role = "supervisor"
            break
        elif choice in ["2", "Contributor", "contributor"]:
            role = "contributor"
            break
        else:
            print("Invalid selection. Please try again.")

    # 2. Configuration
    default_repo = get_default_repo()
    repo_url = prompt("Repository URL", default_repo)
    
    # Check for token in env
    token_env = "GITHUB_TOKEN"
    if "GH_TOKEN" in os.environ and "GITHUB_TOKEN" not in os.environ:
        token_env = "GH_TOKEN"
    
    token_src = prompt("GitHub Token Environment Variable", token_env)

    # 3. Save State
    config = {
        "role": role,
        "repo_url": repo_url,
        "token_env_var": token_src,
        "workspace_root": os.getcwd()
    }

    with open(ROLE_FILE, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Configuration saved to {ROLE_FILE}")
    print("==========================================")
    print(f"Role: {role.upper()}")
    
    if role == "supervisor":
        print("\nNext steps:")
        print("  python3 scripts/supervisor_loop.py")
        print("  (Ensure you have issues labeled 'agent-task' to process)")
    else:
        print("\nNext steps:")
        print("  python3 scripts/contributor_loop.py")
        print("  (This will look for 'task_definition.json' or wait for assignments)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
