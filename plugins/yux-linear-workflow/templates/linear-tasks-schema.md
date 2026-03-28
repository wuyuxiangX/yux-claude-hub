# Linear Tasks State Schema

The file `.claude/linear-tasks.json` tracks all active Linear tasks in the current project. This file is shared across all worktrees (lives in main repo's `.claude/` directory) and should not be edited manually.

## Schema

```json
{
  "version": 1,
  "active_task": "LIN-456",
  "tasks": {
    "LIN-456": {
      "issue_id": "LIN-456",
      "issue_uuid": "cfef1fd0-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "title": "Implement user authentication",
      "branch": "feat/LIN-456-user-auth",
      "status": "in_progress",
      "linear_status": "In Progress",
      "pr_number": null,
      "started_at": "2026-03-28T10:00:00Z",
      "last_active_at": "2026-03-28T14:00:00Z"
    }
  }
}
```

## Task Fields

| Field | Type | Description |
|-------|------|-------------|
| `issue_id` | string | Linear issue identifier (e.g., `LIN-456`) |
| `issue_uuid` | string | Linear internal UUID for API calls |
| `title` | string | Issue title from Linear |
| `branch` | string | Git branch name |
| `status` | string | Workflow status: `in_progress`, `pr_created`, `in_review` |
| `linear_status` | string | Linear issue status (synced from API) |
| `pr_number` | number \| null | GitHub PR number, if created |
| `started_at` | string | ISO 8601 timestamp of task start |
| `last_active_at` | string | ISO 8601 timestamp of last activity |

## Lifecycle

1. **Created by** `/yux-linear-start` — registers new task
2. **Updated by** `/yux-linear-commit` — updates `last_active_at`
3. **Updated by** `/yux-linear-pr` — sets `pr_number`, updates `status`
4. **Removed by** `/yux-linear-merge` — deletes task entry on successful merge

## Notes

- Each task runs in its own Claude Code worktree (`.claude/worktrees/LIN-<id>/`)
- This file is resolved via `git rev-parse --git-common-dir` to always find the main repo
- If the file doesn't exist, commands treat it as empty (backward-compatible)
