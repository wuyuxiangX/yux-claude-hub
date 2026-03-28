---
name: yux-linear-pr
description: Create pull request with Linear issue linking and status sync. Use when the user is on a Linear task branch and wants to open a PR — e.g., "create PR", "linear PR", "submit for review", "开PR", or "/yux-linear-pr". Generates PR title/body from Linear issue and commits, supports draft mode, and updates Linear status to In Review. Do NOT use for PRs unrelated to Linear issues. When the PR is approved, use yux-linear-merge to merge and close the issue.
allowed-tools: Read, Write, Bash(git:*), Bash(gh:*), Glob, Grep, mcp__linear__*, AskUserQuestion
---

# Linear PR - Create Pull Request

Create a pull request with Linear issue integration and optional draft mode.

**Usage**: `/yux-linear-pr [--draft] [additional description]`

## Input

- `--draft`: Create as draft PR (early feedback before full review)
- Additional text: Extra context for PR description

## Prerequisites

- Not on main/master branch
- Has commits ahead of main: `git log origin/main..HEAD --oneline`
- `gh auth status` passes

## Workflow

### Step 1: Extract Issue Info

1. Parse `LIN-xxx` from branch name
2. Fetch details: `mcp__linear__get_issue(id: "LIN-xxx")`

### Step 2: Gather Commits

```bash
git log origin/main..HEAD --pretty=format:"%s" --reverse
```

Group by type for changelog.

### Step 3: Generate PR Content

- **Title**: `[LIN-456] <Issue Title>`
- **Body**: Summary + Linear issue link (`Closes LIN-456`) + changes + test plan
- Language: detect from user input, default to English

### Step 4: Create PR

```bash
git push origin HEAD
gh pr create --title "<title>" --body "<body>" --base main [--draft]
```

### Step 5: Update Task State

If `.claude/linear-tasks.json` exists:
- Set `pr_number`, `status` to `pr_created`, update `last_active_at`

### Step 6: Update Linear

```
mcp__linear__update_issue(id: "<uuid>", state: "In Review")
mcp__linear__create_comment(issueId: "<uuid>", body: "PR created: <url>")
```

### Step 7: Check Initial CI

```bash
gh pr checks <number> --json name,state,conclusion 2>/dev/null
```

Display one-time status snapshot.

### Step 8: Summary

Show PR number, URL, branch, Linear status, CI snapshot, and next steps.
