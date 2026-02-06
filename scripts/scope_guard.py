#!/usr/bin/env python3
"""
scope_guard.py - Optimistic Sandbox for Worker Tasks via Git
============================================================

Wraps a command execution. Uses Git to detect file changes.
Enforces an 'allowlist' of file globs.
- If an unauthorized file is modified/created, it is REVERTED/DELETED.
- Authorized changes are kept.

Usage:
  python3 scope_guard.py --allow "docs/*.md,src/types.ts" -- uv run ...

Exit Code:
  - Returns the exit code of the wrapped command.
  - Returns 128 if git safety checks fail.
"""

import argparse
import subprocess
import sys
import os
import fnmatch
from typing import List, Set

def git_exec(args: List[str]) -> str:
    """Run a git command and return stdout."""
    return subprocess.check_output(["git"] + args, text=True).strip()

def get_repo_root() -> str:
    return git_exec(["rev-parse", "--show-toplevel"])

def get_git_status() -> Set[str]:
    """Return set of changed files (relative to root)."""
    # --porcelain gives "XY path/to/file"
    out = git_exec(["status", "--porcelain"])
    files = set()
    for line in out.splitlines():
        if not line: continue
        # XY path -> path is from index 3
        # Handle quoted paths? Git porcelain v1 quotes if unusual chars.
        # Simple split for now.
        parts = line.strip().split(maxsplit=1)
        if len(parts) < 2: continue
        path = parts[1]
        # remove quotes if present
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        files.add(path)
    return files

def revert_file(path: str):
    """Restore file to HEAD state or delete if untracked."""
    if not os.path.exists(path):
        return # Already gone?

    # Check if tracked
    try:
        git_exec(["ls-files", "--error-unmatch", path])
        is_tracked = True
    except subprocess.CalledProcessError:
        is_tracked = False

    if is_tracked:
        print(f"  [GUARD] 🛡️ Reverting unauthorized modification: {path}")
        subprocess.run(["git", "restore", "--staged", "--worktree", path], check=True)
    else:
        print(f"  [GUARD] 🛡️ Deleting unauthorized new file: {path}")
        os.remove(path)

def matches_any(path: str, patterns: List[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(path, pat):
            return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Git-based Scope Guard")
    parser.add_argument("--allow", type=str, default="", help="Comma-separated globs of allowed files to write")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run")

    args = parser.parse_args()
    
    if not args.command:
        print("Error: No command provided.")
        sys.exit(1)

    # Allow patterns
    allow_patterns = [p.strip() for p in args.allow.split(",") if p.strip()]
    if not allow_patterns:
        # Default: Read-only? Or warn? Let's assume explicit allow needed for writes.
        pass

    # 1. Check Git Environment
    try:
        root = get_repo_root()
        os.chdir(root)
    except subprocess.CalledProcessError:
        print("Error: scope-guard must be run inside a git repository.")
        sys.exit(1)

    # 2. Snapshot state (Optimistic: Assume clean, or just track delta?)
    # Ideally, we want to know what changed *during* execution.
    # Existing dirty files are a problem. 
    # For now, we capture current status as "baseline".
    # Only *new* changes (not in baseline) or *further* changes are subject to guard.
    # Actually, simplest is: Repo must be clean.
    
    baseline_files = get_git_status()
    if baseline_files:
        print("Warning: Repo is dirty. Scope Guard works best on clean state.")
        print(f"Dirty files: {list(baseline_files)}")
        # We will track changes relative to this, but it's tricky.
        # Let's proceed, but valid changes to already-dirty files might be mixed.
    
    # 3. Run Command
    cmd = args.command
    if cmd[0] == "--": cmd = cmd[1:]
    
    print(f"[GUARD] 🚀 Running: {' '.join(cmd)}")
    print(f"[GUARD] 🔒 Allowed patterns: {allow_patterns}")

    try:
        # Run subprocess
        result = subprocess.run(cmd)
        exit_code = result.returncode
    except Exception as e:
        print(f"Error executing command: {e}")
        exit_code = 1

    # 4. Audit Changes
    current_files = get_git_status()
    # Changes = Current - Baseline
    # (Actually we need to check if modified timestamp changed for baseline files too? 
    #  Git status handles that.)
    
    new_changes = current_files - baseline_files
    
    # Also check if baseline files were modified *further*?
    # For now, let's focus on `new_changes` set.
    
    violations = []
    for path in new_changes:
        if not matches_any(path, allow_patterns):
            violations.append(path)

    # 5. Enforce
    if violations:
        print(f"\n[GUARD] 🚨 Detected {len(violations)} unauthorized file writes:")
        for v in violations:
            revert_file(v)
        print("[GUARD] 🧹 Cleanup complete.")
    else:
        print("\n[GUARD] ✅ No unauthorized side-effects detected.")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
