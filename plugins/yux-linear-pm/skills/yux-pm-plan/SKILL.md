---
name: yux-pm-plan
description: "Sprint planning with capacity calculation and AI-powered scope suggestion for Linear PM initiatives. Calculates business days, scores backlog by priority/deadline/blocking, and suggests Must/Should/Stretch categories. Use when the user wants to plan a sprint or review cycle capacity — e.g., 'pm plan', 'plan sprint', 'sprint planning', 'capacity planning', 'what fits in next sprint', '排期', '/yux-pm-plan'. Do NOT use for viewing current status (use yux-pm-overview) or triaging issues (use yux-pm-triage)."
allowed-tools: Read, Write, Glob, Grep, Bash(git:*), Bash(gh:*), mcp__linear__*
---

# PM Plan - Sprint/Cycle Planning

Usage: `/yux-pm-plan [next|current|cycle-name]`

Prerequisite: `.claude/pm-config.json` must exist (run `/yux-pm-init` if missing).

## Step 1: Load Configuration

Read `.claude/pm-config.json`. Extract initiative info, project list, and team ID.

## Step 2: Fetch Data

```
mcp__linear__list_cycles(teamId: "<team_id>", type: "next")
mcp__linear__list_cycles(teamId: "<team_id>", type: "current")

For each project in config.projects:
  mcp__linear__list_issues(
    project: "<project_id>",
    state: "Backlog,Todo",
    limit: 50,
    orderBy: "priority"
  )
```

If arg is `current`, focus on the current cycle for review/adjustment.

## Step 3: Calculate Capacity

```
cycle_days = (cycle_end - cycle_start).business_days
buffer = 0.2
effective_days = cycle_days * (1 - buffer)

effort_map = {
  "XS": 0.25,   # 2 hours
  "S":  0.5,    # 4 hours
  "M":  2,      # 2 days
  "L":  5,      # 5 days
  "XL": 10      # 10 days
}
```

## Step 4: Score and Rank Backlog

```
score = 0

# Priority weight
Urgent:  score += 100
High:    score += 70
Medium:  score += 40
Low:     score += 20

# Carried over from previous sprint
if was_in_previous_cycle: score += 50

# Due date within cycle
if due_date and due_date <= cycle_end: score += 60

# Blocking other issues
if blocks_other_issues: score += 30

# All blockers resolved
if all_blockers_done: score += 20

# Part of active Epic
if parent_epic_in_progress: score += 25
```

Sort all backlog issues by score descending.

## Step 5: Suggest Scope

Assign issues to three categories by filling capacity top-down:

- **Must Complete**: Highest-scoring issues that fit within ~60% capacity
- **Should Complete**: Medium-scoring issues filling remaining capacity
- **Stretch Goals**: Overflow issues beyond capacity

Display the categorized plan with per-issue effort, total days used vs. capacity, and brief reasoning for each category boundary.

Show cross-project distribution (% of capacity per project) to flag imbalanced sprints.

## Step 6: Apply Plan

On user confirmation, assign issues to the cycle:

```
For each issue in accepted scope:
  mcp__linear__update_issue(
    id: "<issue_id>",
    cycle: "<cycle_id>",
    assignee: "me"
  )
```

If user requests edits before applying, adjust the scope and recalculate totals.

## Carry-Over Handling

If the current cycle has incomplete issues, list them with remaining effort estimates. Offer to auto-carry to next sprint, review individually, or move back to backlog.

## No Cycle Mode

If the team has no cycles configured, offer time-boxed planning (default 2 weeks) using the same scoring and capacity logic but without cycle assignment in Linear.
