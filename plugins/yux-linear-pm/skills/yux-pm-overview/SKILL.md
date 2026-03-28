---
name: yux-pm-overview
description: "Display Linear PM initiative dashboard with health score, sprint progress, project breakdown, and attention items. Use when the user wants a high-level view of their initiative or PM status — e.g., 'pm overview', 'pm dashboard', 'pm status', 'initiative status', 'how is the initiative going', 'project status', '项目概览', '/yux-pm-overview'. This is the PM-level status view (initiative health, sprint progress) — do NOT confuse with yux-linear-status which shows individual development task status. For developer-level task tracking, use yux-linear-status instead."
allowed-tools: Read, Glob, Grep, Bash(git:*), Bash(gh:*), mcp__linear__*
---

# PM Overview

Display Initiative dashboard with health score, sprint progress, and attention items.

Prerequisite: `.claude/pm-config.json` must exist (created by yux-pm-init). If missing, instruct user to run pm init.

## Workflow

### Step 1: Load Configuration

Read `.claude/pm-config.json` to get Initiative name, team ID, and project list.

### Step 2: Fetch Data

Run these calls in parallel:

```
# Current cycle
mcp__linear__list_cycles(teamId: "<team_id>", type: "current")

# Issues per project
For each project in config.projects:
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
