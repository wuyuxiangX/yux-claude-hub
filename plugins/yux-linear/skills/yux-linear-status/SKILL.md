---
name: yux-linear-status
description: Linear project dashboard (task/backlog/tasks modes). Triggers on "linear status", "show my tasks", "show backlog", "project overview", "项目概览".
allowed-tools: Read, Write, Bash(git:*), Bash(gh:*), Glob, Grep, mcp__linear__*, AskUserQuestion
---

# Linear Status Hub

Unified dashboard for workflow status, task management, and project backlog.

**Usage**:
- `/yux-linear-status` - Current task detail + active tasks
- `/yux-linear-status backlog [filter]` - View backlog with recommendations
- `/yux-linear-status tasks` - All active tasks across worktrees

## Step 0: Check Configuration

Before any mode, check `.claude/linear-config.json`:
- If missing: show message and stop:
  "Linear not initialized. Please run `/yux-linear-init` first to set up your project."

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

1. Load config from `.claude/linear-config.json`, extract `project.id` and `team.id`
2. Fetch issues: `mcp__linear__list_issues(project: "<project.id>", state: "backlog,todo,in_progress")`
3. Apply filter (all/mine/urgent/unassigned)
4. Display table: ID, title, priority, status, assignee, due date
5. AI recommendation using base scoring algorithm from `../../references/issue-scoring.md`
6. Show top recommendation with `/yux-linear-start LIN-xxx` action

### Project Summary

Show project health alongside the backlog:

```
=== Subloom — Backlog ===

Summary: 12 issues (3 in progress, 5 todo, 4 backlog)
Blocked: 1    Overdue: 2    Inbox: 3

  ID       Title                    Priority  Status       Effort
  WYX-101  Fix auth token refresh   High      In Progress  M
  WYX-98   Update error messages    Medium    Todo         S
  ...

Recommended next: WYX-105 Search API endpoint (score: 140)
  /yux-linear-start WYX-105
```

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
