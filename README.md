# PR Orchestra (Supervisor + Contributors)

**PR Orchestra** is a GitHub-first, dual-role coordination blueprint for software projects where **many humans** each use their own IDE agent plugins.

Core idea: enforce strict roles:
- **Contributor** (implement + submit PR)
- **Supervisor** (risk gate + integration + meeting-mode planning)

Start here:
- `docs/blueprint.md`
- `docs/contributor-guide.md`
- `docs/supervisor-guide.md`

## 🏗 Architecture

The system operates in two distinct modes, determined at startup via `bootstrap.py`.

### 1. Supervisor Role ("The Boss")
- **Responsibility**: Project Management & Quality Assurance.
- **Workflow**:
  1. Scans GitHub Issues labeled `agent-task`.
  2. Generates a **Task Definition** (`task.json`) specifying scope, goals, and constraints.
  3. Dispatches the task to the `work/requests/` queue.
  4. Audits incoming PRs using `supervisor.py` (CI/CD enforcement).

### 2. Contributor Role ("The Worker")
- **Responsibility**: Implementation & Execution.
- **Workflow**:
  1. Watches `work/requests/` for new tasks.
  2. Claims a task and creates a feature branch (`worker/<task-id>`).
  3. Executes the work (via configured **Execution Hook** or sub-agent).
  4. Validates changes using **Scope Guard** (`scope_guard.py`) to ensure no unauthorized files are touched.
  5. Commits changes and generates a `report.md`.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- `git`
- GitHub Token (`GITHUB_TOKEN`)

### Setup
Run the bootstrap script to initialize your agent's role:

```bash
python3 scripts/bootstrap.py
```
Follow the interactive prompts to select **Supervisor** or **Contributor** mode.

### Usage

**Supervisor Mode:**
```bash
python3 scripts/supervisor_loop.py
```
*Monitors issues and generates tasks.*

**Contributor Mode:**
```bash
python3 scripts/contributor_loop.py
```
*Picks up tasks, performs work (default: `touch file`), and safeguards commits.*

**Meeting Packet (Supervisor meeting mode):**
```bash
python3 scripts/meeting_packet.py --repo owner/name --out docs/MEETING_PACKET.md
```
*Summarizes open PRs, risk levels, missing PR sections, and recommended merge order.*

**Create Issues for next tasks:**
```bash
python3 scripts/create_next_tasks.py --repo owner/name --input docs/NEXT_TASKS.md
```
*Creates GitHub Issues from a markdown or JSON task list (labels default to `agent-task`).*

Meeting Issue template:
- `templates/meeting_issue.md`

## 📂 Project Structure
- `scripts/supervisor.py`: CI Risk Gate & Auto-merge logic.
- `scripts/scope_guard.py`: Worker Sandbox (prevents unauthorized file edits).
- `scripts/bootstrap.py`: Role initialization.
- `docs/worker-contract.md`: The JSON protocol between roles.

## 🧪 Testing
Run the End-to-End demo to simulate the full loop locally:
```bash
bash tests/demo_e2e.sh
```
