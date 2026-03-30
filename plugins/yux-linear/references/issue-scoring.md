# Issue Scoring Algorithm

Shared scoring logic used by yux-linear-status (backlog recommendations) and yux-pm-plan (sprint scoping).

## Base Score

All skills use this base scoring:

```
score = 0

# Priority weight
Urgent:  score += 100
High:    score += 70
Medium:  score += 40
Low:     score += 20

# Due date urgency
if overdue:                    score += 80
elif due_date <= 1 day away:   score += 60
elif due_date <= 3 days away:  score += 40

# Current cycle bonus
if in_current_cycle:           score += 30

# In-progress continuity
if status == "In Progress":    score += 50

# Bug label bonus
if has_label("Bug"):           score += 15

# Blocked penalty
if is_blocked:                 score -= 100
```

## Additional Scoring (yux-pm-plan only)

Sprint planning adds these bonuses on top of the base score:

```
# Carried over from previous sprint
if was_in_previous_cycle:      score += 50

# Due date within cycle
if due_date and due_date <= cycle_end: score += 60

# Blocking other issues
if blocks_other_issues:        score += 30

# All blockers resolved
if all_blockers_done:          score += 20

# Part of active Epic
if parent_epic_in_progress:    score += 25
```

## Usage

Sort all issues by score descending. The highest-scoring issue is the recommended next action.
