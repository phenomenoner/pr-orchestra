# Meeting Mode (planned automation)

Goal: let a supervisor generate a “meeting packet” from GitHub PRs so humans can answer questions quickly and decide merge order.

## Meeting Issue convention
Use a dedicated GitHub Issue as the live agenda + minutes.

**Title format:**
- `Meeting: YYYY-MM-DD — <Repo or Project>`

**Labels:**
- `meeting`
- `supervisor`

**Required sections (in this order):**
1. **Agenda**
2. **PR Table**
3. **Decisions**
4. **Blockers**
5. **Next Tasks**

**Live meeting workflow:**
1. **Before meeting:** open the Meeting Issue using `templates/meeting_issue.md`.
2. Paste the latest packet output into **PR Table** (or link to the packet).
3. **During meeting:** update the Issue body inline (checkboxes + notes). Add short comments for PR-specific questions/answers.
4. **After meeting:** add a brief summary comment (decisions + next tasks), then open new Issues for any tasks (label `agent-task`).

## Inputs
- A GitHub repo
- Open PRs (the contributors’ submissions)
- Optional: a “Meeting” Issue that acts as the agenda thread

## Output (MVP)
- A markdown packet that contains:
  - PR list + status (CI, files changed, additions/deletions)
  - risk level (L0–L3)
  - missing template sections / missing test plan
  - questions for the author
  - recommended merge order

## Proposed command
```bash
python3 scripts/meeting_packet.py --repo owner/name --out docs/MEETING_PACKET.md
```

## Create Issues for next tasks (MVP)
```bash
python3 scripts/create_next_tasks.py --repo owner/name --input docs/NEXT_TASKS.md
```

### Input formats
**Markdown** (each task is a heading):
```markdown
## Task title
Details and acceptance criteria...

## Another task
More notes...
```

**JSON**:
```json
{
  "tasks": [
    {"title": "Task title", "body": "Details", "labels": ["agent-task"]}
  ]
}
```

Notes:
- Default label is `agent-task` (override with `--label` or disable with `--no-label`).
- Use `--dry-run` to preview without creating Issues.

## Follow-up automation (later)
- Post the packet to the Meeting Issue as a comment
- Open new Issues for next tasks (label `agent-task`)
- Update `docs/MILESTONES.md`
