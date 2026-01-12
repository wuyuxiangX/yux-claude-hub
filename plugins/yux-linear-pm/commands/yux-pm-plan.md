---
description: Sprint planning and capacity management
---

# PM Plan - Sprint/Cycle Planning

Plan your next sprint: calculate capacity, suggest scope, and assign issues to cycle.

**Usage**: `/yux-pm-plan [cycle]`

## Input

Optional cycle specifier from: $ARGUMENTS
- `next` - Plan next cycle (default)
- `current` - Review/adjust current cycle
- `<cycle-name>` - Plan specific cycle by name

## Prerequisites

1. PM workspace initialized via `/yux-pm-init`
2. Config file exists at `.claude/pm-config.json`

## Workflow

### Step 1: Load Configuration

```
Read .claude/pm-config.json
```

### Step 2: Fetch Cycle and Backlog Data

```
# Get target cycle
mcp__linear__list_cycles(teamId: "<team_id>", type: "next")

# Get backlog issues across Initiative projects
For each project in config.projects:
  mcp__linear__list_issues(
    project: "<project_id>",
    state: "Backlog,Todo",
    limit: 50,
    orderBy: "priority"
  )

# Get current cycle for reference
mcp__linear__list_cycles(teamId: "<team_id>", type: "current")
```

### Step 3: Calculate Capacity

**Capacity Calculation**:
```
cycle_days = (cycle_end - cycle_start).business_days
buffer = 0.2  # 20% buffer for meetings, unexpected work
effective_days = cycle_days * (1 - buffer)

# Convert T-shirt sizes to day estimates
effort_map = {
  "XS": 0.25,  # 2 hours
  "S": 0.5,    # 4 hours
  "M": 2,      # 2 days
  "L": 5,      # 5 days
  "XL": 10     # 10 days (likely needs splitting)
}
```

### Step 4: Display Planning View

> Output language follows `.claude/yux-config.json` setting

```
=== Sprint Planning: <Cycle Name> ===

Period: <start_date> ~ <end_date> (<days> working days)
Capacity: <effective_days> effective days (20% buffer applied)

Current Cycle Review (<current_cycle>):
  Completed: <count> | Carried over: <count>

┌─ Backlog (sorted by priority) ───────────────┐
│ # │ ID      │ Title              │ Project   │ Effort │ Pri   │
│───│─────────│────────────────────│───────────│────────│───────│
│ 1 │ WYX-126 │ User auth          │ api+web   │ L      │ High  │
│ 2 │ WYX-124 │ Login crash fix    │ web       │ S      │ High  │
│ 3 │ WYX-125 │ Data export        │ api       │ M      │ Med   │
│ 4 │ WYX-123 │ Dark mode          │ web+ext   │ M      │ Low   │
│ 5 │ WYX-130 │ Perf optimization  │ api       │ M      │ Med   │
└──────────────────────────────────────────────┘

Total backlog: <count> issues (~<total_days> days)
```

### Step 5: AI Scope Suggestion

**Scoring Algorithm**:
```
score = 0

# Priority weight
if priority == 1 (Urgent): score += 100
if priority == 2 (High):   score += 70
if priority == 3 (Medium): score += 40
if priority == 4 (Low):    score += 20

# Carried over from previous sprint
if was_in_previous_cycle: score += 50

# Has due date within cycle
if due_date and due_date <= cycle_end: score += 60

# Blocking other issues
if blocks_other_issues: score += 30

# Dependencies resolved
if all_blockers_done: score += 20

# Part of active Epic
if parent_epic_in_progress: score += 25
```

**Scope Categories**:
- **Must Complete**: High score, fits capacity
- **Should Complete**: Medium score, fits remaining capacity
- **Stretch Goals**: Lower score, overflow

```
AI Suggested Scope (<used_days>/<capacity_days> days):

┌─ Must Complete ──────────────────────────────┐
│ ✓ WYX-126 User auth (5 days)                │
│ ✓ WYX-124 Login crash fix (0.5 days)        │
│ Total: 5.5 days                              │
└──────────────────────────────────────────────┘

┌─ Should Complete ────────────────────────────┐
│ ○ WYX-125 Data export (2 days)              │
│ ○ WYX-130 Perf optimization (2 days)        │
│ Total: 4 days                                │
└──────────────────────────────────────────────┘

┌─ Stretch Goals ──────────────────────────────┐
│ ◇ WYX-123 Dark mode (2 days)                │
└──────────────────────────────────────────────┘

Reasoning:
• WYX-126 is high priority and blocks login-dependent features
• WYX-124 is a critical bug affecting core user flow
• WYX-125 and WYX-130 round out capacity nicely
• WYX-123 is low priority, saved as stretch goal

Total planned: 9.5 days / 10 days capacity (95%)

Apply this plan? (y/n/edit):
```

### Step 6: Edit Mode

When user selects "edit":

```
Edit Sprint Plan:

Current scope: WYX-126, WYX-124, WYX-125, WYX-130

Commands:
  + WYX-123    Add issue to sprint
  - WYX-130    Remove issue from sprint
  m WYX-125    Move to stretch goals
  done         Apply changes

Enter command:
```

### Step 7: Apply Plan to Linear

When confirmed:

```
For each issue in plan:
  mcp__linear__update_issue(
    id: "<issue_id>",
    cycle: "<cycle_id>",
    assignee: "me"
  )
```

Output:
```
✓ Sprint <Cycle Name> planned!

Added to sprint:
  - WYX-126 User auth (L)
  - WYX-124 Login crash fix (S)
  - WYX-125 Data export (M)
  - WYX-130 Perf optimization (M)

Stretch goals (not added):
  - WYX-123 Dark mode

Sprint capacity: 9.5 / 10 days (95%)

Next actions:
  /yux-pm-overview - View updated dashboard
  /yux-linear-start WYX-124 - Start first task
```

## No Cycle Mode

If the team doesn't use cycles:

```
=== Work Planning ===

Your team doesn't use cycles. Would you like to:

1. Create a time-boxed work plan (2 weeks)
2. Prioritize backlog without time constraints
3. Enable cycles in Linear settings

Choose:
```

For option 1:
```
=== 2-Week Work Plan ===

Period: <today> ~ <today + 14 days>
Capacity: 10 working days

[Same planning flow without cycle assignment]

Note: Issues will be prioritized but not assigned to a cycle.
```

## Cross-Project Balancing

Show work distribution across projects:

```
Sprint Distribution:

subloom-api:       ████████░░ 4 days (40%)
subloom-web:       ██████░░░░ 3.5 days (35%)
subloom-extension: ████░░░░░░ 2 days (20%)
subloom-ml:        █░░░░░░░░░ 0.5 days (5%)

⚠️ Note: subloom-ml has no planned work this sprint.
```

## Carry-Over Handling

If previous cycle has incomplete issues:

```
=== Previous Sprint Carry-Over ===

The following issues were not completed in Sprint 24:

| ID      | Title           | Original Est | Remaining |
|---------|-----------------|--------------|-----------|
| WYX-110 | API refactor    | M (2d)       | ~1d       |
| WYX-115 | Bug fix         | S (0.5d)     | ~0.5d     |

Options:
1. Carry all to next sprint (auto-add)
2. Review each and decide
3. Move to backlog

Choose:
```

## Examples

### Basic usage
```
User: /yux-pm-plan

Claude: === Sprint Planning: Sprint 25 ===

Period: 2026-01-13 ~ 2026-01-27 (10 working days)
Capacity: 8 effective days (20% buffer)

[displays backlog and AI suggestion]

Apply this plan? (y/n/edit): y

✓ Sprint 25 planned!
```

### Plan current sprint
```
User: /yux-pm-plan current

Claude: === Sprint 24 Review ===

Period: 2025-12-30 ~ 2026-01-12 (3 days remaining)
Progress: ████████░░ 80%

Current scope:
  ✓ WYX-100 (completed)
  ✓ WYX-101 (completed)
  ○ WYX-102 (in progress)
  ○ WYX-103 (todo)

At risk:
  ⚠️ WYX-103 may not complete in time

Options:
1. Keep current plan
2. Move WYX-103 to next sprint
3. Adjust scope

Choose:
```

### Edit mode
```
User: /yux-pm-plan

...
Apply this plan? (y/n/edit): edit

Edit Sprint Plan:
Current: WYX-126, WYX-124, WYX-125, WYX-130

Enter command: + WYX-123
Added WYX-123 (Dark mode) - New total: 11.5 days

⚠️ Warning: Over capacity by 1.5 days

Enter command: - WYX-130
Removed WYX-130 - New total: 9.5 days

Enter command: done

Applying updated plan...
```

## Error Handling

### No Backlog Issues
```
=== Sprint Planning ===

Your backlog is empty! Nothing to plan.

Consider:
  /yux-pm-triage - Process inbox items
  /yux-pm-prd    - Create new feature PRD
```

### No Upcoming Cycle
```
No upcoming cycle found.

Options:
1. Create a new cycle in Linear
2. Plan without cycle (prioritize only)

Choose:
```

### Config Not Found
```
PM workspace not initialized.

Run /yux-pm-init to configure your Initiative.
```
