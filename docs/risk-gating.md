# Risk Gating: when to auto-merge vs ask for human

This document defines the **minimal discretionary gate** you described:
- Low-impact, low-risk PRs can be merged automatically.
- High-impact/high-risk PRs must be flagged for human intervention.

## Risk levels

### L0 — Safe/Trivial (auto-merge eligible)
Examples:
- Spelling/docs-only changes
- Comment-only
- Formatting (no logic change)

Requirements:
- CI green
- No protected paths touched (see below)

### L1 — Low risk (auto-merge eligible if policy allows)
Examples:
- Small refactor with tests unchanged
- Adding a small unit test
- Fixing a bug in a narrow module with clear repro + test

Requirements:
- CI green
- PR template completed (intent + test plan)
- No protected paths touched
- Missing required PR sections should fail supervisor check

### L2 — Medium risk (supervisor review required; auto-merge off)
Examples:
- Touching core modules
- Changing public API behavior
- Adding new dependencies

Action:
- Supervisor agent requests clarification, extra tests, or splits PR.

### L3 — High risk (human review required)
Examples:
- Security/auth changes
- Large architectural refactor
- Changes that conflict with docs or multiple active PRs
- Secrets/credentials handling
- Migration scripts/data deletion

Action:
- Block merge; ask human lead.

## Protected paths (always escalate)
If a PR touches any of these, it is at least L2 (often L3):
- `/.github/workflows/**`
- `/**/auth/**`, `/**/security/**`
- `Dockerfile`, `docker-compose.*`
- Dependency manifests: `package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, etc.
- Anything that changes CI/CD, deployment, or access control

## Minimal implementation options
1) **No code**: just a checklist the supervisor follows.
2) **Light automation**: a script that computes risk based on changed files + diff size.
3) **GitHub integration**: label PRs (`risk:L0..L3`) and auto-merge only when label permits.

We’ll start with (2) locally, and only do (3) after you confirm you want a GitHub Action/App.
