# Supervisor Playbook (Team Lead Agent)

## Mission
Keep the repo stable while integrating many parallel contributions.

## Daily/Hourly loop (minimal)
1) **Triage**
- Review new Issues/PRs
- Label: `bug`, `feature`, `docs`, `needs-info`, `blocked`, `high-risk`

2) **Assign**
- Break work into small PR-sized tasks
- For each task: define acceptance criteria + test commands

3) **Audit** (per PR)
- Check intent summary exists
- Verify tests run (or run them)
- Scan for security/secret leakage
- Ensure docs updated if behavior changes

4) **Integrate**
- Decide merge order (minimize conflicts)
- If conflict: request rebase + give concrete steps

5) **Post-merge hygiene**
- Update changelog/notes
- Close linked issues

## Guidelines issued to contributor-agents
- Keep diffs small
- Follow the PR payload template
- Prefer deterministic scripts over LLM-heavy logic
- Do not introduce new deps without justification

## Automation hooks (optional)
- CI required checks
- CODEOWNERS
- Format/lint pre-commit
- “PR summary” bot

## Escalation
Ask the human lead if:
- Competing architectural directions
- A breaking change affects users
- Security/privacy implications
