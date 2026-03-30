---
name: yux-linear-commit
description: Commit changes with auto-generated conventional commit messages and sync progress to Linear. Use when the user is on a Linear task branch (LIN-xxx) and wants to commit — e.g., "linear commit", "commit and sync to linear", "save progress", "提交代码", or "/yux-linear-commit". Auto-generates commit message, pushes to remote, and posts commit info as a Linear comment. Do NOT use for regular git commits outside of Linear workflow — only activate when on a LIN-xxx branch or when the user explicitly mentions Linear. When ready for review, use yux-linear-pr to create a pull request.
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

Analyze if changes should be split. If multiple unrelated groups detected, suggest splitting. If user declines to split, proceed with all changes in a single commit.

### Step 5: Generate Commit Message

Auto-determine from diff analysis:
- Emoji + type + scope + subject
- What/Why/Refs sections
- Language: detect from user input, default to English
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

If fails:
- Non-fast-forward: suggest `git pull --rebase origin HEAD`, then retry push
- Auth/network error: inform user and stop (commit is still saved locally)

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

```
=== Commit Synced ===

Commit:   abc1234 - feat(auth): add JWT token validation
Branch:   feat/LIN-456-user-auth
Files:    3 changed (+45, -12)
Push:     origin/feat/LIN-456-user-auth
Linear:   Comment posted to LIN-456

Next: /yux-linear-pr when ready for review
```
