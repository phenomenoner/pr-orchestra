# NanoClaw-as-Workers (Phase 1: code audit + integration design)

Status: Phase 1 only (no installs). Goal is to decide whether NanoClaw is a good “employee runtime” under OpenClaw.

Repo: https://github.com/gavrielc/nanoclaw

## Quick summary
NanoClaw is a **single Node.js process** that:
- uses **WhatsApp (baileys)** as the I/O channel,
- stores events in **SQLite**,
- runs the agent in an **isolated container** (Apple Container or Docker)
- uses filesystem-based IPC (snapshots in mounted dirs)

Key philosophy we can reuse:
- *skills over features* (transformations instead of adding providers)
- strong isolation boundary (containers) vs app-level permissions
- minimal codebase (easy to audit)

## Relevant modules (for “employee” concept)
### `src/container-runner.ts`
- Builds volume mounts per group.
- **Main group** mounts the whole project root; other groups mount only their folder + a read-only global.
- Runs `container run -i ...` and feeds JSON input via stdin.
- Uses sentinel markers for output parsing.

Why it matters: This is essentially a **sandboxed task executor**. For workers, we can repurpose this pattern:
- mount repo read/write into worker
- worker produces patch + report to an output dir

### `src/task-scheduler.ts`
- Due tasks are executed via `runContainerAgent`.
- This maps cleanly to a “queue of worker jobs”.

### `src/index.ts`
- WhatsApp routing is the I/O surface.
- For our use, we would bypass WhatsApp and call the container runner directly.

## What we can adopt without forking NanoClaw
We don’t need to run NanoClaw as-is. We can borrow the **pattern**:

### Worker contract (minimal)
**Input** (JSON):
- task_id
- repo_path (mounted)
- allowed_paths (whitelist)
- goal (natural language)
- required outputs: patch + short report
- stop conditions

**Output** (files written to mounted /out):
- `patch.diff`
- `report.md` (what changed, commands run, risks)
- optional `tests.log`

### Supervisor side (OpenClaw)
- Uses our risk-gate (L0–L3) to decide:
  - auto-merge vs recommend-only vs block
- Applies consistent templates (English canonical + bilingual summary if needed)

## Phase-1 conclusion (so far)
- ✅ The codebase is small and audit-friendly.
- ✅ The container-runner abstraction is a good “worker runtime” shape.
- ⚠️ For us, the hardest parts are **operational**:
  - installing a container runtime in this environment
  - installing/auth’ing Claude Code

## Next step (still Phase 1)
Define a minimal “worker interface spec” for our Engineering Supervisor Agent repo:
- task schema
- output schema
- merge gate mapping

Then (Phase 2 later): pick a container runtime and run a single worker prototype.
