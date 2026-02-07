# Future Project Ideas

## 1) Full Agent Workers (separate project)

Status: **deferred / out-of-scope for PR Orchestra**.

Why deferred:
- PR Orchestra currently focuses on a GitHub-first coordination layer (Supervisor + Contributors), not runtime orchestration.
- Worker runtime introduces a different operational surface (containers, isolation, infra lifecycle, secrets boundaries).

Suggested follow-up project scope:
- Worker runtime abstraction (`run task` contract)
- Container/remote execution backends
- Artifact handoff (`patch.diff`, `report.md`, logs)
- Security model (sandbox, permissions, provenance)
- Cost and quota controls per worker

Trigger to start this project:
- Stable adoption of PR Orchestra meeting mode + risk gate in real team workflows.

## 2) Optional contributor backend switch (Codex CLI)

Status: **parked**.

Idea:
- Keep PR Orchestra as the policy/orchestration layer.
- Allow a Contributor to run either as an OpenClaw sub-agent (default) or via Codex CLI (optional) for a more "code-worker" style patch→test loop.

Trigger to revisit:
- CI portability becomes a near-term requirement (e.g., running Contributors inside GitHub Actions without OpenClaw).
- We want a more deterministic patch/diff artifact workflow.
- We need stricter sandbox separation for contributor execution.
