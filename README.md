# Engineering Supervisor Agent (multi-human + multi-agent OSS workflow)

Goal: a minimal, practical “team lead” / supervisor agent pattern for software projects where **many humans** (possibly multilingual) each use their own coding agents.

This repo focuses on:
- **Coordination** (what to work on, how to report progress)
- **Audit / merge discipline** (review, testing, documentation, conflict handling)
- **Guidelines for contributor-agents** and for the **supervisor-agent**

Non-goals (for v0):
- Replacing GitHub/GitLab permission models
- Building a new CI system
- Heavy multi-agent orchestration frameworks

## Deliverables
- `docs/landscape.md` — existing products/frameworks (what already solves this)
- `docs/protocol.md` — contribution protocol (human + agent, multilingual-friendly)
- `docs/supervisor-playbook.md` — what the supervisor does each cycle
- `templates/` — issue/PR templates and checklists

## Minimal design principle
Prefer **conventions + checklists + automation hooks** over complex agent swarms.

## Status
Drafting + competitor scan in progress.
