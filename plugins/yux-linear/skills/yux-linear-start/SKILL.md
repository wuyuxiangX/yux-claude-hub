---
name: yux-linear-start
description: Start working on a Linear issue with worktree isolation. Triggers on "start task", "linear start", "work on LIN-123", "begin task", "开始任务".
allowed-tools: Read, Write, Bash(git:*), Bash(gh:*), Glob, Grep, mcp__linear__*, AskUserQuestion, EnterWorktree
---

# Start Linear Task

Start a new task with Linear issue tracking. Every task runs in its own worktree for isolation.

**Usage**: `/yux-linear-start [LIN-xxx | task description]`

## Input

- `LIN-xxx`: Directly start working on a specific issue
- Text description: Search or create an issue matching the description
- No args: Interactive mode

## Prerequisites

1. **Linear MCP**: Must be configured and connected
2. **GitHub CLI**: `gh auth status` must pass
3. **Git repo**: Must be inside a git repository

## Workflow

### Step 1: Verify Linear Connection

```
mcp__linear__list_teams()
```

If fails: show error and stop. Do NOT proceed without Linear.

### Step 2: Load Configuration

1. Check `.claude/linear-config.json`:
   - If exists with `team` and `project` fields: use cached values
   - If missing or incomplete: show error and stop:
     "Linear not initialized. Please run `/yux-linear-init` first to set up your project."

### Step 3: Smart Issue Resolution

1. **If args match `LIN-\d+`**: directly call `mcp__linear__get_issue()`, skip dialog
2. **If args contain text**: auto-search `mcp__linear__list_issues(query: "<text>")`, suggest best match
3. **If no args**: show interactive search/create dialog

### Step 4: Create or Select Issue

**Search path**: Display results, let user pick or create new
**Create path**: Collect title/description/priority, call `mcp__linear__create_issue()`, verify with `mcp__linear__get_issue()`

### Step 5: Create Worktree and Branch

1. **Auto-detect branch type** from issue labels/title:
   - bug/crash/broken/error → `fix/`
   - docs/readme/documentation → `docs/`
   - refactor/cleanup/chore → `refactor/`
   - Default → `feat/`

2. **Detect if already in a worktree**:
   ```bash
   git rev-parse --is-inside-work-tree && git rev-parse --git-common-dir
   ```
   Compare `--git-common-dir` with `--git-dir`. If they differ, we're inside a worktree.

   - **If NOT in a worktree** (normal case — starting from main repo):
     ```
     EnterWorktree(name: "LIN-<id>")
     ```
     Session automatically switches to `.claude/worktrees/LIN-<id>/`

   - **If already in a worktree** (e.g., user resumed a kept worktree session, or opened Claude Code inside one):
     Skip EnterWorktree. Work directly in current directory.

3. **Create and switch to proper branch**:
   ```bash
   git checkout -b <type>/LIN-<id>-<short-description> origin/main
   ```
   If the branch already exists (e.g., from a prior incomplete run), ask the user: switch to the existing branch or create a fresh one with a suffix.

4. **Push branch to remote**:
   ```bash
   git push -u origin <branch-name>
   ```

### Step 6: Update Linear

```
mcp__linear__update_issue(id: "<uuid>", state: "In Progress")
mcp__linear__create_comment(issueId: "<uuid>", body: "Started working.\nBranch: `<branch>`")
```

### Step 7: Register Task State

Write to `.claude/linear-tasks.json` (resolved relative to main repo root via `git rev-parse --git-common-dir`). See `../../references/linear-tasks-schema.json` for the full schema.

Set `active_task` to the new issue ID, add the task entry with `status: "in_progress"`.

Note: tasks.json is shared across all worktrees (lives in main repo's `.claude/` directory).

### Step 8: Output Summary

```
=== Task Started ===

Issue:     LIN-456 - <title>
Branch:    feat/LIN-456-<desc>
Worktree:  .claude/worktrees/LIN-456/
Status:    In Progress
URL:       <linear-url>

You are now working in an isolated worktree.
```
