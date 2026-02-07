# Roadmap

## Phase 0 (template repo)
- [x] PR payload template
- [x] Minimal risk-gate policy (L0–L3) + config
- [x] Supervisor / contributor role prompts
- [x] E2E local demo

## Phase 1 (GitHub-first, meeting mode)
- [x] `meeting_packet` generator (scan open PRs → packet)
- [x] “Meeting Issue” convention + summary format
- [x] Supervisor command to create Issues for next tasks

## Phase 2 (quality-of-life)
- [x] Better PR payload enforcement (fail check if missing sections)
- [x] Auto-assign reviewers / owners by area
- [x] Relaxed multilingual checks (no forced canonical English summary)

## Out of scope for this repo (tracked for future project)
- Full Agent Workers runtime (container/remote execution) is intentionally deferred.
- See `docs/future-project-ideas.md` for follow-up project notes.

## Parked (revisit only if needed)
- Optional `contributor_backend` switch (OpenClaw sub-agents vs Codex CLI).
  - Default: OpenClaw sub-agents.
  - Revisit if: CI portability becomes a near-term goal, we need a more deterministic patch→test worker loop, or we want stricter sandbox separation.
