---
name: yux-linear-status
description: Linear workflow dashboard showing current task status, active tasks across worktrees, and backlog recommendations. Use when the user asks about their Linear task progress — e.g., "linear status", "check task status", "show my tasks", "what should I work on next", "show backlog", or "/yux-linear-status". Do NOT trigger on generic "status" questions unrelated to Linear workflow (e.g., git status, CI status, server status). For initiative-level or PM-level project status, use yux-pm-overview instead.
allowed-tools: Read, Write, Bash(git:*), Bash(gh:*), Glob, Grep, mcp__linear__*, AskUserQuestion
---

# Linear Status Hub

Unified dashboard for workflow status, task management, and backlog.

**Usage**:
- `/yux-linear-status` - Current task detail + active tasks
- `/yux-linear-status backlog [filter]` - View backlog with recommendations
- `/yux-linear-status tasks` - All active tasks across worktrees

## Mode Detection

Parse $ARGUMENTS to determine mode:
- No args or "status" -> **Dashboard mode**
- "backlog" [filter] -> **Backlog mode**
- "tasks" -> **Tasks mode**

---

## Dashboard Mode (default)

### When on a task branch

Show comprehensive status of current task:

1. **Issue info**: ID, title, status, priority (from `mcp__linear__get_issue()`)
2. **Branch info**: name, commits ahead, uncommitted changes
3. **PR info** (if exists): number, URL, review status, merge readiness
4. **CI status** (if PR exists): check results from `gh pr checks`
5. **Other active tasks** (from `.claude/linear-tasks.json`, shown as info)
6. **Next step suggestion** based on current state

### When not on a task branch

If `.claude/linear-tasks.json` has active tasks:
```
Not on a task branch. Active tasks:

  LIN-456  feat/LIN-456-user-auth     In Progress   3 commits
  LIN-789  fix/LIN-789-login-crash     In Review     PR #82

Each task runs in its own worktree.
/yux-linear-start to start a new task.
```

If no tasks: suggest `/yux-linear-start`

---

## Backlog Mode

**Usage**: `/yux-linear-status backlog [all|mine|urgent|unassigned]`

### Workflow

1. Load team config from `.claude/linear-config.json`
2. Fetch issues: `mcp__linear__list_issues(team: "<team>", state: "backlog,todo,in_progress")`
3. Apply filter (all/mine/urgent/unassigned)
4. Display table: ID, title, priority, status, assignee, due date
5. AI recommendation based on scoring:
   - Priority weight (Urgent=100, High=70, Medium=40, Low=20)
   - Due date urgency (overdue=+80, <=1 day=+60, <=3 days=+40)
   - Current cycle bonus (+30)
   - In-progress continuity bonus (+50)
   - Bug label bonus (+15)
   - Blocked penalty (-100)
6. Show top recommendation with `/yux-linear-start LIN-xxx` action

### Cycle Integration

If team uses cycles, show sprint progress:
```
Current Cycle: Sprint 23 (Jan 1 - Jan 14)
Progress: 80% (8/10 issues)
```

---

## Tasks Mode

**Usage**: `/yux-linear-status tasks`

Show all active tasks across worktrees:
```
=== Active Tasks (3) ===

  LIN-456  feat/LIN-456-user-auth       In Progress   3 commits
  LIN-789  fix/LIN-789-login-crash       In Review     PR #82  CI: passed
  LIN-234  docs/LIN-234-api-docs         In Progress   1 commit

Each task runs in its own worktree under .claude/worktrees/
```

---

## Multi-language Support

Output language is auto-detected from user input. Default to English.
