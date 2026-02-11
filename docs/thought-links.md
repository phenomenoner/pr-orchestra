# Thought links (SDD, Vibe Engineering) — why PR Orchestra exists

This repo is intentionally **not** a rigid spec-driven framework.

PR Orchestra assumes your coding agents are already capable. The missing piece is usually:
- coordination,
- risk gating,
- reviewability,
- and turning decisions into the next tasks.

## Spec-Driven Development (SDD): great aspiration, messy reality
SDD is commonly framed as: generate requirements → design → tasks, then let an agent implement.

In practice (especially on non-trivial repos), SDD often runs into:
- lots of markdown that humans don’t reliably keep in sync,
- a false sense of safety (agent says it followed the spec, but it didn’t really validate),
- doubled review burden (review spec + review code),
- and brittleness as the codebase evolves.

A good critical overview (zh):
- iHower — Spec-Driven Development(SDD) 的美好願景與殘酷現實
  - https://ihower.tw/blog/13480-sdd-spec-driven-development

Also useful as primary sources / tools to examine:
- GitHub Spec Kit — https://github.com/github/spec-kit

## Vibe Engineering: “senior engineering practices, amplified”
Simon Willison proposes **Vibe Engineering** as the opposite of irresponsible vibe coding:
- still accountable for quality,
- lean planning,
- tests + CI + version control,
- and strong review discipline.

- Simon Willison — Vibe engineering
  - https://simonwillison.net/2025/Oct/7/vibe-engineering/

## Where PR Orchestra fits
PR Orchestra is an opinionated layer to support **vibe engineering at scale**:
- L0–L3 risk classification to decide what needs more review
- templates that enforce a predictable PR payload
- meeting packets + next-task automation to keep async teams aligned

In other words:
- **spec-lite** when it helps (small plans, clear acceptance criteria),
- but rely on *engineering discipline* (tests, review, rollback) as the real safety net.
