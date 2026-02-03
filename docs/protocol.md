# Contribution Protocol (Human + Agent)

This is the minimal “contract” between:
- Human contributors
- Their personal coding agents
- The project’s supervisor agent

## Core rules
1) **One change = one PR** (small, reviewable)
2) **No silent breaking changes** (must state risk + test plan)
3) **Write intent before code** (problem → approach → constraints)
4) **Reproducibility first** (commands, versions, expected outputs)

## Standard PR payload (copy/paste)
**Title:** <concise>

**Intent (1–3 lines):**
- What problem are we solving?

**Approach:**
- What did you change and why?

**Risk/Impact:**
- Possible regressions / edge cases

**Test plan (exact commands):**
- `...`

**Docs/Notes:**
- What to update (README, changelog, ADR, etc.)

## Multilingual guideline
- Any language is OK for discussion.
- **Supervisor canonical output is English** by default.
- If a PR is authored in Chinese (or other language), include an **English 2–3 line summary**.

## Conflict resolution
- The supervisor decides merge order.
- If two PRs conflict:
  - Prefer merging the one with **clearer tests** and **smaller diff**.
  - Ask the other contributor to rebase after merge.

## “Stop conditions” (when to ask the human lead)
- Security-sensitive changes
- Deleting data / irreversible operations
- Architectural decisions affecting multiple subsystems
- Scope creep > 2× the original PR intent
