# PR Orchestra — Application Blueprint (v0)

> Working title: **PR Orchestra**
>
> Metaphor:
> - **Contributors** = musicians (each with their own instrument/IDE agent)
> - **Supervisor** = conductor (integration, risk gate, planning)
>
> Source of truth: **GitHub** (Issues + Pull Requests)
> Submission format: **PR + required PR payload**

---

## 0) Problem / Why this exists
Modern teams increasingly code with AI assistance, but the *coordination layer* is still brittle:
- Everyone uses different IDE agent plugins (VS Code+Codex, Antigravity, Claude Desktop, …)
- PR quality varies wildly (missing intent/test plan, unclear risk)
- Merges become a social bottleneck, not a technical one

**PR Orchestra** is the “team operating system” that makes *multi-human + multi-agent* collaboration:
- auditable (intent before code, tests before merge)
- parallelizable (small PRs, scoped tasks)
- safe (risk gating + protected paths)
- meeting-friendly (a supervisor can run “war-room” integration)

---

## 1) Actors & Roles
### 1.1 Contributor (default mode for most people)
A contributor is a human+agent pair working in an IDE. They:
- pick up tasks from GitHub Issues (labels/assignments)
- implement changes in a branch
- open a PR that follows the required template (Intent/Approach/Risk/Test Plan/Docs)
- respond to supervisor questions

### 1.2 Supervisor (meeting mode / integration mode)
A supervisor is a *session role* (not a person). During a meeting they:
- scan the open PR set and generate an integration view
- ask clarifying questions
- decide merge order and conflict strategy
- enforce a minimal risk gate (L0–L3)
- convert meeting decisions into next tasks (Issues)
- produce/update milestone plan

---

## 2) Core workflows
### 2.1 Async “daily work” loop (Contributor-centric)
1) Supervisor (or human) maintains a backlog in GitHub Issues.
2) Contributors pick an Issue → create branch → implement.
3) Contributors open PR with required payload and link the Issue.
4) CI runs; supervisor policy labels risk and posts verdict.
5) L0/L1 may auto-merge (policy-controlled). L2/L3 requires review/human.

### 2.2 Sync “meeting mode” loop (Supervisor-centric)
1) Everyone arrives with PRs (and context inside PR description).
2) Supervisor generates a meeting packet:
   - list of PRs, status (CI, size), risk level, dependencies
   - open questions for each PR
   - recommended merge order
3) Humans answer questions live; supervisor updates plan.
4) Supervisor merges / requests changes.
5) Supervisor opens Issues for next steps and assigns owners.

---

## 3) Standard artifacts (GitHub-native)
### 3.1 Labels
Minimum suggested labels:
- `agent-task` (Issue is ready to be picked up)
- `blocked`, `needs-info`, `WIP`, `do-not-merge`
- `risk-L0`, `risk-L1`, `risk-L2`, `risk-L3`

### 3.2 Required PR payload (template)
Required sections:
- Intent (1–3 lines)
- Approach
- Risk/Impact
- Test Plan (exact commands)
- Docs

This repo ships a PR template that enforces this.

### 3.3 Meeting packet output (planned)
Generated file(s) (committed or attached to an Issue):
- `docs/MEETING_PACKET.md` (or comment on a “meeting” Issue)
- `docs/MILESTONES.md` (updated)
- new Issues created for next tasks

---

## 4) Policy & Safety (risk gate)
### 4.1 Risk levels
- **L0**: docs/comments/format-only → auto-merge eligible
- **L1**: small safe change with tests → auto-merge eligible
- **L2**: medium risk (core behavior, large diff, new deps) → manual review
- **L3**: high risk (security/auth/deploy, secrets, architecture refactor) → block + human

### 4.2 Protected paths (always escalate)
Examples:
- `.github/workflows/**`
- `**/auth/**`, `**/security/**`
- `Dockerfile`, `docker-compose.*`
- lockfiles

Config lives in `.supervisor-agent.yml`.

---

## 5) Integration points (IDE agents)
This product intentionally avoids coupling to any specific IDE plugin.

Instead, we standardize:
- the PR template
- contributor instructions (copy/paste prompt)
- supervisor role prompt
- GitHub-native labels / workflows

Each IDE agent is “compatible” if it can:
- follow the PR template
- run tests and paste exact commands/results
- answer supervisor questions

---

## 6) Packaging options
### Option A (fastest): Repo template
- You add these files to an existing repo
- Contributors just follow conventions
- Supervisor policy runs via GitHub Actions

### Option B (later): Installable CLI
A small CLI (Python) provides:
- `pr-orchestra init` (install templates into a repo)
- `pr-orchestra meeting` (generate meeting packet from GitHub PRs)
- `pr-orchestra plan` (milestone draft)

---

## 7) Roadmap (recommended)
### Phase 0 — Template + policy gate (this repo)
- PR template
- risk gate action
- docs for contributor/supervisor

### Phase 1 — Meeting mode automation
- script: fetch open PRs → meeting packet
- open Issues for next tasks

### Phase 2 — Worker-runtime variation (optional)
- treat workers as replaceable runtimes (container/remote agent)
- keep the same task contract + artifacts

---

## 8) Non-goals (for v0)
- replacing GitHub permissions
- building a full orchestration framework
- forcing a single LLM/provider

---

## 9) Glossary
- **Contributor**: implements work, submits PR
- **Supervisor**: integration + risk gate + planning
- **Meeting mode**: synchronous supervisor operation with humans present
