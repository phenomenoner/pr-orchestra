#!/usr/bin/env python3
"""Generate a supervisor meeting packet from open GitHub PRs.

MVP goals:
- Scan open PRs
- Compute lightweight risk (reuse supervisor.risk_level)
- Detect missing PR template sections
- Surface CI state and follow-up questions
- Recommend merge order

Usage:
  python3 scripts/meeting_packet.py --repo owner/name --out docs/MEETING_PACKET.md
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from supervisor import load_config, risk_level, gh_api_json


REQUIRED_SECTIONS: dict[str, tuple[str, ...]] = {
    "Intent": ("intent",),
    "Approach": ("approach",),
    "Risk/Impact": ("risk", "impact"),
    "Test Plan": ("test plan", "testplan", "tests"),
    "Docs/Notes": ("docs", "documentation", "notes"),
}


CI_RANK = {
    "success": 0,
    "pending": 1,
    "neutral": 1,
    "none": 1,
    "failure": 2,
    "error": 2,
}

RISK_RANK = {"L0": 0, "L1": 1, "L2": 2, "L3": 3}


@dataclass
class PRPacketItem:
    number: int
    title: str
    url: str
    author: str
    draft: bool
    labels: list[str]
    ci_state: str
    files_changed: int
    additions: int
    deletions: int
    risk_level: str
    risk_reasons: list[str]
    missing_sections: list[str]
    questions: list[str]


# ---------------------------------------------------------------------------
# GitHub fetch
# ---------------------------------------------------------------------------


def parse_repo(repo: str) -> tuple[str, str]:
    s = repo.strip()
    s = s.removeprefix("https://github.com/")
    if s.endswith(".git"):
        s = s[:-4]
    if "/" not in s:
        raise ValueError(f"Invalid repo '{repo}'. Expected owner/name")
    owner, name = s.split("/", 1)
    return owner, name


def fetch_open_prs(owner: str, name: str, token: str) -> list[dict[str, Any]]:
    prs: list[dict[str, Any]] = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{name}/pulls?state=open&per_page=100&page={page}"
        chunk = gh_api_json(url, token)
        if not isinstance(chunk, list) or not chunk:
            break
        prs.extend([x for x in chunk if isinstance(x, dict)])
        if len(chunk) < 100:
            break
        page += 1
    return prs


def fetch_pr_files(owner: str, name: str, pr_number: int, token: str) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{name}/pulls/{pr_number}/files?per_page=100&page={page}"
        chunk = gh_api_json(url, token)
        if not isinstance(chunk, list) or not chunk:
            break
        files.extend([x for x in chunk if isinstance(x, dict)])
        if len(chunk) < 100:
            break
        page += 1
    return files


def fetch_ci_state(owner: str, name: str, sha: str, token: str) -> str:
    if not sha:
        return "none"
    try:
        url = f"https://api.github.com/repos/{owner}/{name}/commits/{sha}/status"
        payload = gh_api_json(url, token)
        state = str(payload.get("state", "none")).lower() if isinstance(payload, dict) else "none"
        return state or "none"
    except Exception:
        return "none"


# ---------------------------------------------------------------------------
# Content analysis
# ---------------------------------------------------------------------------


def _heading_line_key(line: str) -> str:
    s = line.strip().lower()
    s = re.sub(r"^#+\s*", "", s)  # markdown heading
    s = re.sub(r"^[-*]\s*", "", s)  # bullet style heading
    s = s.strip("*` ")
    s = s.rstrip(":： ")
    return s


def detect_missing_sections(body: str) -> list[str]:
    text = body or ""
    lines = text.splitlines()
    keys = {_heading_line_key(line) for line in lines if line.strip()}

    missing: list[str] = []
    for section, aliases in REQUIRED_SECTIONS.items():
        if not any(any(alias in key for alias in aliases) for key in keys):
            missing.append(section)
    return missing


def detect_dependencies(body: str) -> list[int]:
    nums = set(int(m.group(1)) for m in re.finditer(r"(?:depends on|blocked by|after)\s*#(\d+)", body or "", re.I))
    return sorted(nums)


def build_questions(missing_sections: list[str], ci_state: str, risk: str, deps: list[int]) -> list[str]:
    qs: list[str] = []
    for sec in missing_sections:
        qs.append(f"Please add the missing PR section: {sec}.")

    if ci_state in {"failure", "error"}:
        qs.append("CI is failing. What is the fix plan and ETA?")
    elif ci_state in {"pending", "none", "neutral"}:
        qs.append("CI has not passed yet. Can you post expected checks/results?")

    if risk in {"L2", "L3"}:
        qs.append("This change is medium/high risk. Please clarify rollback and verification steps.")

    if deps:
        nums = ", ".join(f"#{n}" for n in deps)
        qs.append(f"Dependency noted ({nums}). Confirm merge ordering constraints.")

    return qs


# ---------------------------------------------------------------------------
# Packet builder / renderer
# ---------------------------------------------------------------------------


def build_item(owner: str, name: str, pr: dict[str, Any], token: str) -> PRPacketItem:
    number = int(pr.get("number", 0))
    title = str(pr.get("title", "(untitled)"))
    url = str(pr.get("html_url", ""))
    author = str((pr.get("user") or {}).get("login", "unknown"))
    draft = bool(pr.get("draft", False))
    labels = [str(lb.get("name")) for lb in (pr.get("labels") or []) if isinstance(lb, dict) and lb.get("name")]

    files = fetch_pr_files(owner, name, number, token)
    additions = sum(int(f.get("additions", 0)) for f in files)
    deletions = sum(int(f.get("deletions", 0)) for f in files)
    cfg = load_config()
    risk, reasons = risk_level(files, labels, cfg, additions, deletions)

    sha = str((pr.get("head") or {}).get("sha", ""))
    ci_state = fetch_ci_state(owner, name, sha, token)

    body = str(pr.get("body", "") or "")
    missing_sections = detect_missing_sections(body)
    deps = detect_dependencies(body)
    questions = build_questions(missing_sections, ci_state, risk, deps)

    return PRPacketItem(
        number=number,
        title=title,
        url=url,
        author=author,
        draft=draft,
        labels=labels,
        ci_state=ci_state,
        files_changed=len(files),
        additions=additions,
        deletions=deletions,
        risk_level=risk,
        risk_reasons=reasons,
        missing_sections=missing_sections,
        questions=questions,
    )


def recommended_order(items: list[PRPacketItem]) -> list[PRPacketItem]:
    return sorted(
        items,
        key=lambda x: (
            1 if x.draft else 0,
            CI_RANK.get(x.ci_state, 3),
            RISK_RANK.get(x.risk_level, 9),
            x.additions + x.deletions,
            x.number,
        ),
    )


def render_packet(repo: str, items: list[PRPacketItem]) -> str:
    now = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")

    ci_counts: dict[str, int] = {}
    risk_counts: dict[str, int] = {}
    for it in items:
        ci_counts[it.ci_state] = ci_counts.get(it.ci_state, 0) + 1
        risk_counts[it.risk_level] = risk_counts.get(it.risk_level, 0) + 1

    lines: list[str] = []
    lines.append("# Meeting Packet")
    lines.append("")
    lines.append(f"- Repo: `{repo}`")
    lines.append(f"- Generated: {now}")
    lines.append(f"- Open PRs: {len(items)}")
    lines.append("")

    if items:
        ci_summary = ", ".join(f"{k}={v}" for k, v in sorted(ci_counts.items(), key=lambda kv: CI_RANK.get(kv[0], 99)))
        risk_summary = ", ".join(f"{k}={v}" for k, v in sorted(risk_counts.items(), key=lambda kv: RISK_RANK.get(kv[0], 99)))
        lines.append(f"- CI Summary: {ci_summary}")
        lines.append(f"- Risk Summary: {risk_summary}")
    else:
        lines.append("- CI Summary: n/a")
        lines.append("- Risk Summary: n/a")

    lines.append("")
    lines.append("## PR Details")
    lines.append("")

    if not items:
        lines.append("No open PRs.")
    else:
        for it in sorted(items, key=lambda x: x.number):
            lines.append(f"### #{it.number} — {it.title}")
            lines.append(f"- URL: {it.url}")
            lines.append(f"- Author: @{it.author}")
            lines.append(f"- Draft: {'yes' if it.draft else 'no'}")
            lines.append(f"- CI: `{it.ci_state}`")
            lines.append(f"- Risk: **{it.risk_level}** ({'; '.join(it.risk_reasons) if it.risk_reasons else 'n/a'})")
            lines.append(f"- Diff: {it.files_changed} files, +{it.additions} / -{it.deletions}")
            lines.append(
                "- Missing sections: "
                + (", ".join(it.missing_sections) if it.missing_sections else "none")
            )
            if it.labels:
                lines.append("- Labels: " + ", ".join(f"`{x}`" for x in it.labels))
            if it.questions:
                lines.append("- Questions:")
                for q in it.questions:
                    lines.append(f"  - {q}")
            lines.append("")

    lines.append("## Recommended Merge Order")
    lines.append("")

    ordered = recommended_order(items)
    if not ordered:
        lines.append("No merge candidates.")
    else:
        for i, it in enumerate(ordered, start=1):
            lines.append(
                f"{i}. #{it.number} ({it.risk_level}, ci={it.ci_state}, diff={it.files_changed} files, +{it.additions}/-{it.deletions})"
            )

    lines.append("")
    lines.append("## Next Actions (suggested)")
    lines.append("")
    lines.append("- Resolve all failing/pending CI checks before merge decisions.")
    lines.append("- Require missing PR template sections to be filled.")
    lines.append("- Merge low-risk, green PRs first unless dependency constraints override.")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate meeting packet from open PRs")
    ap.add_argument("--repo", required=True, help="owner/name or https://github.com/owner/name")
    ap.add_argument("--out", default="docs/MEETING_PACKET.md", help="Output markdown path")
    ap.add_argument("--token-env", default="GITHUB_TOKEN", help="Token environment variable name")
    args = ap.parse_args()

    token = os.environ.get(args.token_env) or os.environ.get("GH_TOKEN")
    if not token:
        print(f"Missing token. Set {args.token_env} (or GH_TOKEN).")
        return 2

    owner, name = parse_repo(args.repo)
    prs = fetch_open_prs(owner, name, token)

    items = [build_item(owner, name, pr, token) for pr in prs]
    packet = render_packet(f"{owner}/{name}", items)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(packet, encoding="utf-8")

    print(f"Wrote {out_path} ({len(items)} PRs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
