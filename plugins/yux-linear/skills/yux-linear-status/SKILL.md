---
name: yux-linear-status
description: Unified Linear dashboard (task/backlog/tasks/pm modes). Triggers on "linear status", "show my tasks", "show backlog", "pm overview", "项目概览".
allowed-tools: Read, Write, Bash(git:*), Bash(gh:*), Glob, Grep, mcp__linear__*, AskUserQuestion
---

# Linear Status Hub

Unified dashboard for workflow status, task management, backlog, and initiative overview.

**Usage**:
- `/yux-linear-status` - Current task detail + active tasks
- `/yux-linear-status backlog [filter]` - View backlog with recommendations
- `/yux-linear-status tasks` - All active tasks across worktrees
- `/yux-linear-status pm` - Initiative dashboard with health score

## Step 0: Check Configuration

Before any mode, check `.claude/linear-config.json`:
- If missing: show message and stop:
  "Linear not initialized. Please run `/yux-linear-init` first to set up your project."

## Mode Detection

Parse $ARGUMENTS to determine mode:
- No args or "status" -> **Dashboard mode**
- "backlog" [filter] -> **Backlog mode**
- "tasks" -> **Tasks mode**
- "pm" | "overview" | "initiative" | "dashboard" -> **PM mode**

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

1. Load config from `.claude/linear-config.json`, extract `project.id`
2. Fetch issues: `mcp__linear__list_issues(project: "<project.id>", state: "backlog,todo,in_progress")`
3. Apply filter (all/mine/urgent/unassigned)
4. Display table: ID, title, priority, status, assignee, due date
5. AI recommendation using base scoring algorithm from `../../references/issue-scoring.md`
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

## PM Mode

**Usage**: `/yux-linear-status pm`

Display Initiative dashboard with health score, sprint progress, and attention items.

Prerequisite: `.claude/linear-config.json` must exist with `pm.enabled: true`. If `pm.enabled` is false or `pm` field is missing, show:
  "PM features not enabled. Run `/yux-linear-init` to enable Initiative management."

### Step 1: Load Configuration

Read `.claude/linear-config.json`. Extract `pm.initiative` name, `team.id`, and `pm.projects` list.

### Step 2: Fetch Data

Run these calls in parallel:

```
# Current cycle
mcp__linear__list_cycles(teamId: "<team_id>", type: "current")

# Issues per project
For each project in config.pm.projects:
  mcp__linear__list_issues(project: "<project_id>", limit: 50, includeArchived: false)

# Triage inbox
mcp__linear__list_issues(team: "<team_id>", state: "Triage", limit: 20)
```

If no current cycle exists, skip sprint progress and show active work counts (In Progress / Todo / Backlog) instead.

### Step 3: Calculate Health Score

```
health = 100

# Overdue penalty
overdue_count = issues where due_date < today
health -= overdue_count * 10

# Blocked penalty
blocked_count = issues where is_blocked == true
health -= blocked_count * 15

# Inbox penalty
inbox_count = triage_issues.length
if inbox_count > 5: health -= 10
if inbox_count > 10: health -= 10  (cumulative: -20 total)

# Sprint progress adjustment
if current_cycle:
  progress = completed_in_cycle / total_in_cycle
  if progress >= 0.8: health += 10
  elif progress < 0.3 and days_remaining < 3: health -= 20

health = clamp(health, 0, 100)
```

Health labels:
- 80-100: Excellent
- 60-79: Good
- 40-59: Needs Attention
- 0-39: Critical

### Step 4: Display Dashboard

Present these sections:

1. **Health**: Score out of 100 with label.
2. **Sprint Progress** (if cycle exists): Progress bar, completed/total count, days remaining.
3. **Issues by Project**: Per-project issue count with in-progress count.
4. **Needs Attention**: Inbox count, blocked count, overdue count.
5. **Alerts** (if any): List overdue issues (with days overdue), blocked issues (with blocker ID), and stale issues (no updates in 14+ days).

Example output:

```
=== Product Launch v2 — Initiative Dashboard ===

Health:   78/100 (Good)
Sprint:   Sprint 23 — 80% (8/10) — 3 days remaining

Issues by Project:
  subloom-api    12 issues (3 in progress)
  subloom-web     8 issues (2 in progress)
  subloom-ext     4 issues (1 in progress)

Attention:
  Inbox: 3 items    Blocked: 1    Overdue: 2

Alerts:
  - WYX-89 overdue by 2 days (subloom-api)
  - WYX-102 blocked by WYX-98 (subloom-web)
```

---

## Multi-language Support

Output language is auto-detected from user input. Default to English.
