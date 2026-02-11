# PR Orchestra


A GitHub-first coordination layer for **Supervisor + Contributor** development workflows.

> If your team already has capable coding agents, PR Orchestra is the thin orchestration layer that keeps parallel PR work predictable, reviewable, and mergeable.

PR Orchestra helps teams run multi-agent engineering with clear role boundaries:
- **Contributors** implement work and submit PRs.
- **Supervisor** triages risk, coordinates merge order, and turns meetings into next tasks.

---

## Why this repo exists

Most teams already have strong coding agents, but weak coordination between parallel PRs.
PR Orchestra focuses on the missing layer:
- consistent PR payload quality,
- predictable risk-gating,
- meeting-mode integration,
- fast conversion from decisions → actionable issues.

---

## What you get (current scope)

- PR risk gate (`scripts/supervisor.py`)
  - L0–L3 risk classification
  - protected path escalation
  - PR template section enforcement
  - optional reviewer auto-assignment by path rules
- Meeting packet generator (`scripts/meeting_packet.py`)
- Meeting Issue convention + template (`docs/meeting-mode.md`, `templates/meeting_issue.md`)
- Next-task issue creator (`scripts/create_next_tasks.py`)
- Contributor + supervisor loop references (`scripts/contributor_loop.py`, `scripts/supervisor_loop.py`)

---

## Agent Protocol Entry Point

Use this when you want any coding agent to adopt PR Orchestra before touching code.

Rules for agent startup:
- The agent must confirm role first: `Supervisor` or `Contributor`.
- If role is not explicitly provided, the agent must ask before implementation.
- After role is confirmed, the agent should load the matching template prompt and restate constraints.

Suggested kickoff prompt (role not decided yet):

```text
Adopt the PR Orchestra protocol for this session.
Target repo: <owner>/<repo>.
Before coding, ask me which role to assume now: Supervisor or Contributor.
After I answer, load the matching instructions from:
- templates/supervisor_role_prompt.md
- templates/contributor_agent_instructions.md
Then restate the operating rules and wait for my next task.
```

Suggested kickoff prompt (force Contributor mode):

```text
Adopt PR Orchestra protocol in Contributor mode for repo <owner>/<repo>.
Load templates/contributor_agent_instructions.md and templates/pr_template.md.
Follow one-PR-one-intent, keep changes small, and use required PR payload sections.
If task scope is unclear, ask me before coding.
```

Suggested kickoff prompt (force Supervisor mode):

```text
Adopt PR Orchestra protocol in Supervisor mode for repo <owner>/<repo>.
Load templates/supervisor_role_prompt.md and .supervisor-agent.yml.
Run risk triage and meeting-assistant behavior only; do not implement contributor code unless I explicitly switch your role.
```

Optional on-demand coordination add-on:
- If agents are invoked ad-hoc (not continuously), consider using a per-branch
  `supervisor_discussion.md` artifact to keep supervisor guidance and contributor
  replies in one place. See `docs/on-demand-coordination.md`.

---

## Quick Start (with `uv`, Python 3.13)

### 1) Clone and enter repo

```bash
git clone https://github.com/phenomenoner/pr-orchestra.git
cd pr-orchestra
```

### 2) Set GitHub token

PowerShell:
```powershell
$env:GITHUB_TOKEN="<your-token>"
```

Bash:
```bash
export GITHUB_TOKEN="<your-token>"
```

### 3) Initialize role config

```bash
uv run --python 3.13 -- python scripts/bootstrap.py
```

Choose:
- `supervisor` if you want to run meeting/risk workflows
- `contributor` if you want to consume tasks and produce PR artifacts

### 4) Generate a meeting packet

```bash
uv run --python 3.13 -- python scripts/meeting_packet.py \
  --repo owner/repo \
  --out docs/MEETING_PACKET.md
```

### 5) Create next-task issues from meeting output

```bash
uv run --python 3.13 -- python scripts/create_next_tasks.py \
  --repo owner/repo \
  --input docs/NEXT_TASKS.md \
  --dry-run
```

Remove `--dry-run` to create issues for real.

---

## Typical workflow

### A) Async day-to-day flow
1. Keep backlog in GitHub Issues (`agent-task`).
2. Contributors pick tasks and open PRs with required payload sections.
3. Supervisor policy evaluates risk and leaves verdict.
4. Merge low-risk PRs first; escalate risky changes.

### B) Meeting mode flow
1. Open a Meeting Issue from `templates/meeting_issue.md`.
2. Generate and paste packet summary.
3. Capture decisions/blockers in one place.
4. Convert outcomes into issues using `create_next_tasks.py`.

---

## Configuration

Main config file: `.supervisor-agent.yml`

Important knobs:
- `merge_mode`: `auto_merge` | `recommend_only`
- `auto_merge_levels`: e.g. `["L0", "L1"]`
- `protected_paths`: path globs that escalate risk
- `reviewer_rules`: optional path-based reviewer assignment

Example reviewer rule:

```yaml
reviewer_rules:
  - "docs/**=octo-docs"
  - "scripts/**=octo-eng"
```

---

## Multilingual behavior (relaxed)

PR section checks are intentionally **language-tolerant** and no longer require a forced canonical English summary.
If the PR content is understandable and structured, it can pass section checks.

---

## Project structure

- `scripts/`
  - `supervisor.py` — risk gate + side effects
  - `meeting_packet.py` — meeting packet generation
  - `create_next_tasks.py` — create issues from markdown/json task lists
  - `supervisor_loop.py` / `contributor_loop.py` — role loops
- `docs/`
  - `blueprint.md`, `meeting-mode.md`, `risk-gating.md`, `roadmap.md`, etc.
- `templates/`
  - PR template, meeting issue template, role prompts
- `tests/`
  - unit tests for supervisor + meeting + task creation

---

## Out of scope (for this repo)

Full Agent Workers runtime (container/remote execution) is deferred to a future separate project.
See `docs/future-project-ideas.md`.

---

## Development / tests

```bash
uv run --python 3.13 --with pytest pytest -q
uv run --python 3.13 -- python -m unittest -v tests/test_meeting_packet.py tests/test_create_next_tasks.py
```

---

## Related reading / philosophy

- Thought links: SDD vs Vibe Engineering (and how this repo positions itself): `docs/thought-links.md`
- SDD critique (zh): https://ihower.tw/blog/13480-sdd-spec-driven-development
- Vibe Engineering (Simon Willison): https://simonwillison.net/2025/Oct/7/vibe-engineering/

---

## License

MIT (see [LICENSE](LICENSE)).

---

## Start reading here

- `docs/blueprint.md`
- `docs/meeting-mode.md`
- `docs/supervisor-guide.md`
- `docs/contributor-guide.md`
