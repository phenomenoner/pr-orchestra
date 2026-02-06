# Worker Contract (Employee Agent Interface)

Goal: let OpenClaw (supervisor) delegate implementation work to a “worker runtime” (e.g., NanoClaw container agent) **without coupling** to WhatsApp/Telegram/etc.

This contract is designed to be:
- Minimal
- Language-agnostic (English canonical, but tasks can be any language)
- Safe (bounded scope, auditable outputs)

## Core idea
A worker is a function:

**Input (JSON) → Output artifacts (files)**

No direct merging. No direct access to secrets. The supervisor audits the outputs.

---

## Input schema (v0)
The supervisor writes a single JSON file to an agreed location (e.g. `work/requests/<task_id>.json`).

```json
{
  "task_id": "string",
  "role": "worker",
  "canonical_language": "en",
  "bilingual_summary_languages": ["zh-hant"],

  "repo": {
    "path": "/workspace/repo",
    "base_ref": "main",
    "target_branch": "worker/<task_id>"
  },

  "scope": {
    "allowed_globs": ["src/**", "docs/**"],
    "deny_globs": [".github/workflows/**", "**/auth/**", "**/security/**"],
    "max_files_changed": 20,
    "max_additions": 500,
    "max_deletions": 500
  },

  "goal": {
    "title": "string",
    "description": "string",
    "acceptance_criteria": ["string"],
    "test_plan": ["bash -lc '...'"]
  },

  "stop_conditions": [
    "security-sensitive",
    "architecture-change",
    "secrets-required",
    "cannot-run-tests"
  ]
}
```

Notes:
- `canonical_language` is the worker’s output language for `report.md`.
- `scope` is enforced by the *supervisor gate* and (optionally) by the worker runtime.

---

## Output artifacts (v0)
Worker writes to `work/results/<task_id>/`:

- `report.md` (required)
  - intent summary
  - what changed
  - tests run + results
  - risks/edge cases
  - anything that hit a stop condition

- `patch.diff` (required)
  - `git diff` output or equivalent

- `commands.log` (optional)
- `tests.log` (optional)

Workers should also write a one-line `status.json`:
```json
{ "task_id": "...", "status": "ok|blocked", "reason": "..." }
```

---

## Supervisor responsibilities
- Create task JSON
- Provide an isolated working tree / branch
- Run risk gate (L0–L3) on outputs
- Decide merge mode (auto-merge vs recommend-only)

---

## Minimal safety rules
- Worker must never embed secrets in output.
- If a stop condition triggers, worker returns `status=blocked` and **does not attempt risky edits**.
- Worker never changes CI, auth, or deployment unless explicitly permitted.
