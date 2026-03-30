---
name: yux-linear-merge
description: Merge PR, clean up branch, and mark Linear issue as Done. Triggers on "linear merge", "merge this PR", "complete task", "合并PR".
allowed-tools: Read, Write, Bash(git:*), Bash(gh:*), Grep, mcp__linear__*, AskUserQuestion
---

# Linear Merge - Complete Workflow

Merge PR, clean up, and close Linear issue.

**Usage**: `/yux-linear-merge [--squash|--rebase|--merge]`

## Input

- `--squash` (default): Squash all commits
- `--rebase`: Rebase and merge
- `--merge`: Create merge commit

## Workflow

### Step 1: Pre-check

1. Load `.claude/linear-config.json`
2. Extract `LIN-xxx` from branch, fetch issue via `mcp__linear__get_issue()`
3. Check PR exists: `gh pr view --json number,state,mergeable,mergeStateStatus`

### Step 2: Collect Pending Issues

Gather from both GitHub and Linear:
- `gh pr view <number> --json reviews,comments,reviewDecision`
- `mcp__linear__list_comments(issueId: "<uuid>")`

Filter: only show CHANGES_REQUESTED reviews, unresolved questions, change suggestions.
Skip: APPROVED reviews, resolved threads, status updates.

Display if issues exist (skip section entirely if none).

### Step 3: User Confirmation (MANDATORY)

Use AskUserQuestion:
- If pending issues: "Proceed with merge" or "Cancel and address issues"
- If no issues: "Proceed with merge" or "Cancel"

### Step 4: Execute via linear-merge-executor Skill

Delegate to `linear-merge-executor` skill (runs in forked subagent) with:
- pr_number, issue_id, issue_uuid, merge_strategy, branch_name

The skill handles: CI polling -> merge validation -> execute merge -> cleanup -> Linear update.

### Step 5: Cleanup Task State

On success:
1. Remove task from `.claude/linear-tasks.json`
2. Set `active_task` to most recently active remaining task (or null)
3. Inform user: "Task completed. Say 'exit worktree' to clean up and return to main repo."

Do NOT call ExitWorktree proactively — let the user decide.

### Step 6: Display Result

- Success: show merge commit, cleanup status, suggest exiting worktree
- Blocked: show CI failure details and fix suggestions
- Failed: show conflict info and resolution steps
