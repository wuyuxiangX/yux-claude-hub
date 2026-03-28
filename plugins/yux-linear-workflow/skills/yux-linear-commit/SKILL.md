---
name: yux-linear-commit
description: Commit changes with auto-generated messages and Linear sync. Use when user says "commit", "linear commit", "stage changes", "save progress", or "/yux-linear-commit". Auto-generates conventional commit messages, pushes to remote, and syncs commit info to Linear issue.
allowed-tools: Read, Write, Bash(git:*), Bash(gh:*), Glob, Grep, mcp__linear__*, AskUserQuestion
---

# Linear Commit

Make incremental commits during development, linking to Linear issue and syncing progress.

**Usage**: `/yux-linear-commit [--no-push] [description]`

## Input

- `description`: Reference for commit message generation (Claude auto-generates)
- `--no-push`: Skip auto-push after commit

## Workflow

### Step 1: Detect Context

1. Get branch: `git branch --show-current`
2. Extract `LIN-xxx` from branch name. If not on Linear branch -> prompt `/yux-linear-start`
3. Fetch issue via `mcp__linear__get_issue(id: "LIN-xxx")`
4. Check changes: `git status --porcelain`. If clean -> exit

### Step 2: Display Changes

Categorize files (new/modified/deleted), flag sensitive files (.env, credentials).

### Step 3: File Selection

Use AskUserQuestion: commit all, select specific, exclude specific, or cancel.

### Step 4: Atomic Check

Analyze if changes should be split. If multiple unrelated groups detected, suggest splitting.

### Step 5: Generate Commit Message

Auto-determine from diff analysis:
- Emoji + type + scope + subject
- What/Why/Refs sections
- Language follows `.claude/yux-config.json`
- Format: `<emoji> <type>(<scope>): <subject>`
- Include `Refs: LIN-xxx` and `Co-Authored-By` line

Show for confirmation. User can modify or approve.

### Step 6: Execute

```bash
git add <files>
git commit -m "<message>"
```

### Step 7: Auto-Push (default on)

```bash
git push origin HEAD
```

If fails: `git push -u origin $(git branch --show-current)`

Skip if `--no-push` flag passed.

### Step 8: Update Task State

If `.claude/linear-tasks.json` exists, update `last_active_at`.

### Step 9: Sync to Linear (Required)

```
mcp__linear__create_comment(
  issueId: "<uuid>",
  body: "**Commit**: `<hash>`\n```\n<message>\n```\nFiles: <count>"
)
```

### Step 10: Summary

Show commit hash, message, files, Linear sync status, and next steps.
