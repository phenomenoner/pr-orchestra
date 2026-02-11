# Spec-lite checklists — when to write specs vs ship with PR Orchestra

PR Orchestra is designed for **vibe engineering**: lean planning + strong engineering discipline.

This doc turns that into quick, repeatable checklists.

## Use spec-lite (write 10–30 lines) when…
Write a short spec (in an issue, a markdown note, or PR body) if any of these are true:

- **Ambiguity risk**: multiple reasonable interpretations of the requirement.
- **Cross-team alignment**: someone else will depend on the behavior later.
- **Breaking-change potential**: API/CLI behavior might change.
- **Data shape changes**: schemas, persistence formats, migrations.
- **Security/privacy impact**: auth, tokens, PII, exports.
- **Non-trivial UX**: user-facing flows where “almost right” is wrong.

### Spec-lite template (copy/paste)
- Goal (1 sentence):
- Non-goals (1 sentence):
- Acceptance checks (3–7 bullets):
- Risks / rollback (1–3 bullets):
- Test plan (what will prove it works?):

## Skip specs and just run PR Orchestra when…
If the change is small and reversible, prefer shipping:

- **Docs-only / metadata** changes.
- **Small localized refactors** with strong tests.
- **Bugfix with a reproducible failing case** already identified.
- **Mechanical updates** (renames, formatting, lint fixes) with CI.

In these cases, focus on:
- a tight PR intent,
- good diffs,
- and validation evidence.

## Risk gate heuristics (L0–L3)
Use PR Orchestra’s L0–L3 to decide how hard we should slow down:

- **L0** docs: merge fast.
- **L1** small/local code: require tests/CI or clear manual validation.
- **L2** cross-cutting: require spec-lite + reviewer attention.
- **L3** security/irreversible: require explicit human approval + rollback plan.

## What agents should do (contributor loop)
- If task is L2/L3 or unclear: **STOP and ask** for spec-lite inputs.
- Otherwise: implement one PR with one intent, add/adjust tests, report validation.

## What supervisors should do
- Confirm risk level.
- Enforce required PR payload sections.
- Merge order + rollout/rollback.
