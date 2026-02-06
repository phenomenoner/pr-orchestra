# Contributor Guide (for humans + IDE agents)

A contributor is the default role for day-to-day work.

## What you do
1) Pick up an Issue labeled `agent-task`.
2) Create a branch.
3) Implement a **small, reviewable** change.
4) Open a PR and fill out the PR template **completely**.
5) Run tests and paste **exact commands**.

## Golden rules
- One PR = one intent.
- Write **intent before code**.
- If you cannot run tests, say so and explain why.
- Do not touch protected paths unless explicitly asked.

## Using your IDE agent
Use your favorite agent plugin (VS Code Codex / Antigravity / Claude Desktop / …).

### Recommended “agent instruction” (copy/paste)
See: `templates/contributor_agent_instructions.md`

## PR template is mandatory
Your PR description must include:
- Intent
- Approach
- Risk/Impact
- Test Plan (exact commands)
- Docs

If you skip these, the supervisor will label higher risk and block/ask for changes.
