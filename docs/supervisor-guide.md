# Supervisor Guide (meeting mode)

A supervisor is a role you assume for integration, planning, and risk gating.

## What you do in a meeting
1) **Collect**: list open PRs; ensure each has the required PR payload.
2) **Triage**: compute risk level (L0–L3) and identify blockers.
3) **Interrogate**: ask clarifying questions; humans answer live.
4) **Integrate**: decide merge order; merge low-risk first; handle conflicts.
5) **Plan**: turn decisions into Issues (milestones + assignments).

## Minimum artifacts you should produce
- A meeting summary (can be a comment on a “Meeting” Issue)
- Updated milestone plan (or at least next 3–10 Issues)
- Clear assignments (who owns which Issue)

## Policy
This repo ships a minimal risk gate in `scripts/supervisor.py`.
- L0/L1 can be auto-merge eligible (if configured)
- L2 requires review
- L3 blocks and asks a human

Config: `.supervisor-agent.yml`

## Prompts
- Supervisor role prompt: `templates/supervisor_role_prompt.md`
- Contributor instruction: `templates/contributor_agent_instructions.md`

## Automation
GitHub Action template: `templates/github-workflows/supervisor.yml`

Issue creation helper (next tasks):
```bash
python3 scripts/create_next_tasks.py --repo owner/name --input docs/NEXT_TASKS.md --dry-run
```

> Note: `SUPERVISOR_DRY_RUN` controls side effects (labels/comments/auto-merge). If unset, the workflow defaults to **active** (`false`). Set it to `true` to run in dry-run mode.
