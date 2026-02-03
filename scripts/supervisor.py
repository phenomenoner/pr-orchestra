"""Minimal GitHub PR Supervisor (risk gate + auto-merge).

Design goals:
- Minimal dependencies (stdlib only)
- Works in GitHub Actions (reads GITHUB_EVENT_PATH)
- Two modes: auto_merge vs recommend_only
- Discretionary risk gate with simple, explainable rules

This repo is a *template/reference implementation*.
"""

from __future__ import annotations

import fnmatch
import json
import os
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def eprint(*a: object) -> None:
    print(*a, file=sys.stderr)


@dataclass
class Config:
    merge_mode: str = "auto_merge"  # auto_merge | recommend_only
    canonical_language: str = "en"
    bilingual_summary_languages: list[str] = None  # type: ignore
    auto_merge_levels: list[str] = None  # ["L0","L1"]

    max_files_changed: int = 20
    max_additions: int = 500
    max_deletions: int = 500

    block_labels: list[str] = None  # type: ignore
    protected_paths: list[str] = None  # type: ignore


DEFAULT_CONFIG_PATH = Path(".supervisor-agent.yml")


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> Config:
    # Minimal YAML parser for our limited structure (key: value + simple lists).
    # If parsing fails, fall back to defaults.
    cfg = Config(
        bilingual_summary_languages=["zh-hant"],
        auto_merge_levels=["L0", "L1"],
        block_labels=["do-not-merge", "WIP", "blocked", "needs-human"],
        protected_paths=[
            ".github/workflows/**",
            "**/auth/**",
            "**/security/**",
            "Dockerfile",
            "docker-compose.*",
            "**/*lock*",
        ],
    )
    if not path.exists():
        return cfg

    try:
        raw = path.read_text(encoding="utf-8").splitlines()
        cur_key = None
        for line in raw:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.startswith("-") and cur_key:
                item = s[1:].strip().strip('"')
                lst = getattr(cfg, cur_key)
                if isinstance(lst, list):
                    lst.append(item)
                continue
            if ":" in s:
                k, v = s.split(":", 1)
                k = k.strip()
                v = v.strip()
                cur_key = None

                if v.startswith("[") and v.endswith("]"):
                    # inline list
                    items = [x.strip().strip('"') for x in v[1:-1].split(",") if x.strip()]
                    setattr(cfg, k, items)
                elif v == "":
                    # start of block list
                    cur_key = k
                    if getattr(cfg, k, None) is None:
                        setattr(cfg, k, [])
                    else:
                        setattr(cfg, k, [])
                else:
                    # scalar
                    v2 = v.strip('"')
                    if hasattr(cfg, k):
                        # ints
                        if k in {"max_files_changed", "max_additions", "max_deletions"}:
                            setattr(cfg, k, int(v2))
                        else:
                            setattr(cfg, k, v2)
    except Exception as e:
        eprint("Config parse failed; using defaults:", str(e)[:200])

    return cfg


def gh_api_json(url: str, token: str) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "eng-supervisor-agent/0.1",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def matches_any(path: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, g) for g in globs)


def risk_level(files: list[dict], labels: list[str], cfg: Config, additions: int, deletions: int) -> tuple[str, list[str]]:
    reasons: list[str] = []

    # Block labels => L3
    for bl in cfg.block_labels or []:
        if bl in labels:
            return "L3", [f"blocked by label: {bl}"]

    # Protected paths => at least L2
    for f in files:
        p = f.get("filename")
        if isinstance(p, str) and matches_any(p, cfg.protected_paths or []):
            reasons.append(f"touches protected path: {p}")

    # Simple size guard
    if len(files) > cfg.max_files_changed:
        reasons.append(f"too many files changed: {len(files)} > {cfg.max_files_changed}")
    if additions > cfg.max_additions:
        reasons.append(f"too many additions: {additions} > {cfg.max_additions}")
    if deletions > cfg.max_deletions:
        reasons.append(f"too many deletions: {deletions} > {cfg.max_deletions}")

    if reasons:
        return "L2", reasons

    # If only docs/markdown changes => L0
    exts = {Path(f.get("filename", "")).suffix.lower() for f in files if isinstance(f.get("filename"), str)}
    if exts.issubset({".md", ".txt", ".rst"}):
        return "L0", ["docs-only change"]

    # Otherwise: L1 by default (small, non-protected)
    return "L1", ["small change; no protected paths"]


def main() -> int:
    cfg = load_config()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        eprint("Missing GITHUB_TOKEN/GH_TOKEN")
        return 2

    repo = os.environ.get("GITHUB_REPOSITORY")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not repo or not event_path:
        eprint("Missing GITHUB_REPOSITORY or GITHUB_EVENT_PATH")
        return 2

    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    pr = event.get("pull_request") or {}
    pr_number = pr.get("number")
    if not pr_number:
        eprint("No pull_request.number in event")
        return 0

    owner, name = repo.split("/", 1)

    # PR details
    labels = [lb.get("name") for lb in (pr.get("labels") or []) if isinstance(lb, dict) and lb.get("name")]
    labels = [str(x) for x in labels]

    # files list
    files_url = f"https://api.github.com/repos/{owner}/{name}/pulls/{pr_number}/files?per_page=100"
    files = gh_api_json(files_url, token)
    if not isinstance(files, list):
        files = []

    additions = int(pr.get("additions") or 0)
    deletions = int(pr.get("deletions") or 0)

    level, reasons = risk_level(files, labels, cfg, additions, deletions)

    verdict_lines = [
        f"Supervisor verdict: risk={level}",
        f"merge_mode={cfg.merge_mode}",
        f"reasons: {', '.join(reasons) if reasons else 'n/a'}",
    ]

    # For v0 we only print the decision; wiring comments/labels/automerge happens next.
    # Keeping minimal: this script is the policy engine.
    print("\n".join(verdict_lines))

    # Exit codes:
    # 0 = ok
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
