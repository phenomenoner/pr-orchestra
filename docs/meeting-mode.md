# Meeting Mode (planned automation)

Goal: let a supervisor generate a “meeting packet” from GitHub PRs so humans can answer questions quickly and decide merge order.

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

## Follow-up automation (later)
- Post the packet to the Meeting Issue as a comment
- Open new Issues for next tasks (label `agent-task`)
- Update `docs/MILESTONES.md`
