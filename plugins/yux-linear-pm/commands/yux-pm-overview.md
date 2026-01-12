---
description: Display initiative dashboard and status
---

# PM Overview - Initiative Dashboard

Display a quick overview dashboard for your configured Initiative.

**Usage**: `/yux-pm-overview`

## Prerequisites

1. PM workspace must be initialized via `/yux-pm-init`
2. Config file exists at `.claude/pm-config.json`

## Workflow

### Step 1: Load Configuration

```
Read .claude/pm-config.json
```

If config doesn't exist:
```
Error: PM workspace not initialized.

Run /yux-pm-init first to select an Initiative and configure sub-projects.
```

### Step 2: Fetch Data

Fetch data in parallel for all projects in the Initiative:

```
# Get current cycle
mcp__linear__list_cycles(teamId: "<team_id>", type: "current")

# Get issues across all Initiative projects
For each project in config.projects:
  mcp__linear__list_issues(
    project: "<project_id>",
    limit: 50,
    includeArchived: false
  )

# Get inbox/triage items
mcp__linear__list_issues(
  team: "<team_id>",
  state: "Triage",
  limit: 20
)
```

### Step 3: Calculate Metrics

**Health Score** (0-100):
```
health = 100

# Overdue issues penalty
overdue_count = issues where due_date < today
health -= overdue_count * 10

# Blocked issues penalty
blocked_count = issues where is_blocked == true
health -= blocked_count * 15

# Large inbox penalty
inbox_count = triage_issues.length
if inbox_count > 5: health -= 10
if inbox_count > 10: health -= 10

# Sprint progress bonus
if current_cycle:
  progress = completed_in_cycle / total_in_cycle
  if progress >= 0.8: health += 10
  elif progress < 0.3 and days_remaining < 3: health -= 20

health = clamp(health, 0, 100)
```

**Health Labels**:
- 80-100: Excellent
- 60-79: Good
- 40-59: Needs Attention
- 0-39: Critical

### Step 4: Display Dashboard

> Output language follows `.claude/yux-config.json` setting

```
=== <Initiative Name> Overview ===

Health: <score>/100 (<label>)

┌─ Current Sprint (<cycle_name>) ──────────────┐
│ Progress: ████████░░ <percent>%              │
│ <completed>/<total> completed | <days> days remaining │
└──────────────────────────────────────────────┘

┌─ Issues by Project ──────────────────────────┐
│ <project-1>:  <count> (<in_progress> in progress) │
│ <project-2>:  <count> (<in_progress> in progress) │
│ <project-3>:  <count> (<in_progress> in progress) │
└──────────────────────────────────────────────┘

┌─ Needs Attention ────────────────────────────┐
│ 📥 <inbox_count> inbox items → /yux-pm-triage │
│ ⚠️ <blocked_count> blocked | ⚠️ <overdue_count> overdue │
└──────────────────────────────────────────────┘

Next actions:
  /yux-pm-triage  - Process inbox
  /yux-pm-plan    - Plan next sprint
  /yux-pm-prd     - Create new feature PRD
```

### Step 5: Show Alerts (if any)

If there are critical items, highlight them:

```
⚠️ Alerts:

1. [OVERDUE] WYX-123: Login feature - 2 days overdue
2. [BLOCKED] WYX-456: API refactor - blocked by WYX-789
3. [STALE] WYX-101: Dark mode - no updates in 14 days
```

## Progress Bar Rendering

```
def render_progress(percent):
  filled = round(percent / 10)
  empty = 10 - filled
  return "█" * filled + "░" * empty
```

## No Cycle Mode

If the team doesn't use cycles:

```
=== <Initiative Name> Overview ===

Health: <score>/100 (<label>)

┌─ Active Work ────────────────────────────────┐
│ In Progress: <count> issues                  │
│ Todo: <count> issues                         │
│ Backlog: <count> issues                      │
└──────────────────────────────────────────────┘

┌─ Issues by Project ──────────────────────────┐
│ ...                                          │
└──────────────────────────────────────────────┘

┌─ Needs Attention ────────────────────────────┐
│ ...                                          │
└──────────────────────────────────────────────┘
```

## Examples

### Basic usage
```
User: /yux-pm-overview

Claude: === Subloom Overview ===

Health: 78/100 (Good)

┌─ Current Sprint (Sprint 24) ─────────────────┐
│ Progress: ████████░░ 80%                     │
│ 8/10 completed | 3 days remaining            │
└──────────────────────────────────────────────┘

┌─ Issues by Project ──────────────────────────┐
│ subloom-api:       12 (3 in progress)        │
│ subloom-web:       8  (2 in progress)        │
│ subloom-extension: 5  (1 in progress)        │
│ subloom-ml:        3  (0 in progress)        │
└──────────────────────────────────────────────┘

┌─ Needs Attention ────────────────────────────┐
│ 📥 3 inbox items → /yux-pm-triage            │
│ ⚠️ 1 blocked | ⚠️ 2 overdue                  │
└──────────────────────────────────────────────┘

Next actions:
  /yux-pm-triage  - Process inbox
  /yux-pm-plan    - Plan next sprint
  /yux-pm-prd     - Create new feature PRD
```

### With alerts
```
User: /yux-pm-overview

Claude: === Subloom Overview ===

Health: 45/100 (Needs Attention)

...

⚠️ Alerts:

1. [OVERDUE] WYX-123: User authentication - 3 days overdue
2. [BLOCKED] WYX-456: Payment integration - blocked by WYX-123
```

## Error Handling

### Config Not Found
```
PM workspace not initialized.

Run /yux-pm-init to configure your Initiative and sub-projects.
```

### Linear Connection Failed
```
Failed to connect to Linear.

Please check your Linear MCP configuration and try again.
```

### No Issues Found
```
=== <Initiative Name> Overview ===

Health: 100/100 (Excellent)

No active issues in your Initiative.

Your backlog is empty! Time to plan new work:
  /yux-pm-prd - Create a new feature PRD
```
