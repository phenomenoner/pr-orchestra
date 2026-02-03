# Landscape: Existing approaches to “Supervisor / Team Lead” agent workflows

This is a **practical** map of what already exists, grouped by what problem they solve.

## 1) Multi-agent orchestration frameworks (explicit supervisor/manager role)
These can implement a supervisor, but they are often **heavier than we want** for a minimal GitHub workflow.

### LangGraph Supervisor (LangChain ecosystem)
- What it is: state-graph orchestration + a supervisor pattern that delegates to sub-agents.
- Strength: explicit handoffs, checkpointing/persistence; integrates with LangChain tools.
- Gap for us: framework-heavy; we want a minimal GitHub-centric protocol.
- Links:
  - https://docs.langchain.com/oss/python/langchain/supervisor
  - https://github.com/langchain-ai/langgraph-supervisor-py

### Microsoft AutoGen (GroupChatManager)
- What it is: structured multi-agent group chat with a manager mediating turns.
- Strength: clear “manager” abstraction and software-workflow examples.
- Gap: focuses on conversational routing more than repo/PR integration.
- Links:
  - https://microsoft.github.io/autogen/0.2/docs/notebooks/agentchat_groupchat/

### CrewAI
- What it is: product + framework for building and running multi-agent workflows.
- Strength: lifecycle/deployment focus; templates.
- Gap: heavier product surface; less “minimal protocol”.
- Links:
  - https://docs.crewai.com/

### MetaGPT / ChatDev
- What it is: SOP-driven multi-agent “company/team” for software dev.
- Strength: role-based SOP and structured artifacts.
- Gap: opinionated SOP; heavier than a lightweight repo supervisor.
- Links:
  - https://github.com/FoundationAgents/MetaGPT
  - https://github.com/OpenBMB/ChatDev

### OpenHands / SWE-agent ecosystem
- What it is: software engineering agent SDK/platform; execution + evaluation.
- Strength: production agent tooling; benchmark-driven.
- Gap: full SDK; not minimal.
- Links:
  - https://docs.openhands.dev/sdk
  - https://github.com/OpenHands/OpenHands

## 2) PR review bots (LLM-based)
These help with review, but they are not a full supervisor across many contributors.

### CodeRabbit
- What it is: AI PR review + summaries + conversational review.
- Strength: polished PR UX.
- Gap: single-purpose reviewer; still need orchestration + merge policy.
- Links:
  - https://coderabbit.ai/
  - https://docs.coderabbit.ai/platforms/github-com

## 3) Deterministic GitHub automation (merge/deps/queues)
These are reliable and minimal. They complement a supervisor agent.

- **Mergify**: merge rules/queues
  - https://mergify.io/
- **bors-ng**: merge-when-green batching
  - https://github.com/bors-ng/bors-ng
- **Renovate**: dependency update PR automation
  - https://docs.renovatebot.com/

## Key gap (our opportunity)
Most options are either:
- **Framework-heavy** (great for building agent apps, overkill for a repo team), or
- **Single-purpose bots** (review-only / merge-only).

We can build a minimal, GitHub-first pattern:
- **A language-agnostic contribution protocol** (templates + checklists)
- **A risk gate** (auto-merge only low-risk PRs; escalate high-risk)
- **A supervisor playbook** (triage → audit → merge discipline)

The goal is *not* to replace GitHub tooling, but to add a small “brain + policy” layer.
