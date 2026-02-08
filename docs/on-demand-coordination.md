# On-Demand Coordination (Prototype-First Extension)

This doc describes an optional coordination pattern for teams running PR Orchestra
with **on-demand** agents (no cron-like supervision) and **prototype-first**
integration.

## When To Use This
- Contributors are independent agents/humans working in parallel.
- Agents are invoked ad-hoc, not continuously.
- You want faster alignment with minimal ceremony.

## Core Idea
Use a lightweight per-branch coordination artifact:

- File name: `supervisor_discussion.md`
- Location: repo root of the target project (not this repo)
- Owner: seeded by Supervisor, updated by Contributors on-demand

The file acts as a shared, append-friendly “thread” where:
- Supervisor posts recommendations, questions, and integration constraints.
- Contributors reply with status, test evidence, and suggestions.

## Working Rhythm (On-Demand)
### For Contributors (when you start work)
1. Fetch/pull latest branch updates.
2. Read `supervisor_discussion.md` first.
3. Post a short plan under `Agent Reply` before coding.
4. Implement; update docs as you go.
5. Before pushing, update `Agent Reply` + append `Decision Log`.

### For Supervisors
1. Seed `supervisor_discussion.md` on the contributor branch.
2. Keep tone recommendation-first (coordination and tradeoffs).
3. Ask for test evidence and merge-surface notes.
4. Use risk-gating (L0–L3) as a shared language, not a hammer.

## Required Report Fields (Minimal Ceremony)
Keep these fields in every meaningful update:
- Status:
- Changes Since Last Update:
- Smoke Test Result:
- Risks/Conflicts:
- Questions/Suggestions:

## Template
Use `templates/supervisor_discussion.md` from this repo as a starting point and
adapt it to your target project.

## Prototype-First Integration Notes
If you’re in **prototype-first** mode, consider:
- Integration target branch like `proto/main` or `proto/integration-lab`.
- File-level composition and `cherry-pick` over “merge everything” when branch
  histories are incompatible.
- Allow DB resets / mock data where explicitly agreed.
- Never allow secrets in code; avoid auth bypasses on shared environments.

