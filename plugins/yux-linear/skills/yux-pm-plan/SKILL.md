---
name: yux-pm-plan
description: Sprint planning with capacity calculation and scope suggestion. Triggers on "pm plan", "plan sprint", "sprint planning", "capacity planning", "排期".
allowed-tools: Read, Write, Glob, Grep, Bash(git:*), Bash(gh:*), mcp__linear__*
---

# PM Plan - Sprint/Cycle Planning

Usage: `/yux-pm-plan [next|current|cycle-name]`

Prerequisite: `.claude/linear-config.json` must exist. If missing, show:
  "Please run `/yux-linear-init` first."

## Step 1: Load Configuration

Read `.claude/linear-config.json`. Extract `team.id` and `project.id`.

## Step 2: Fetch Data

```
mcp__linear__list_cycles(teamId: "<team.id>", type: "next")
mcp__linear__list_cycles(teamId: "<team.id>", type: "current")

mcp__linear__list_issues(
  project: "<project.id>",
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

Score each issue using the algorithm in `../../references/issue-scoring.md` (base score + pm-plan additional bonuses). Sort all backlog issues by score descending.

## Step 5: Suggest Scope

Assign issues to three categories by filling capacity top-down:

- **Must Complete**: Highest-scoring issues that fit within ~60% capacity
- **Should Complete**: Medium-scoring issues filling remaining capacity
- **Stretch Goals**: Overflow issues beyond capacity

Display the categorized plan with per-issue effort, total days used vs. capacity.

Example output:

```
=== Sprint Plan: Sprint 24 (Mar 17 - Mar 28) ===

Capacity: 8 effective days (10 business days, 20% buffer)

Must Complete (4.75 days / 60% cap):
  WYX-101  [M] Fix auth token refresh       score: 190
  WYX-98   [S] Update error messages         score: 150
  WYX-105  [L] Search API endpoint           score: 140

Should Complete (2.5 days):
  WYX-110  [M] Dashboard filters             score: 95
  WYX-112  [S] Extension icon update         score: 80

Stretch Goals:
  WYX-115  [M] Analytics event tracking      score: 60
```

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

If the current cycle has incomplete issues, list them with remaining effort estimates. Use AskUserQuestion to offer: auto-carry all to next sprint, review individually, or move all back to backlog.

## No Cycle Mode

If the team has no cycles configured, offer time-boxed planning (default 2 weeks) using the same scoring and capacity logic but without cycle assignment in Linear.
