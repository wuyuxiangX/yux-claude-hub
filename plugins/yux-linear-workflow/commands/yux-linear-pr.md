---
description: Create pull request with Linear integration
---

# Linear PR - Create Pull Request

Create a pull request with Linear issue integration.

**Usage**: `/yux-linear-pr [additional description]`

## Input

Additional PR description from: $ARGUMENTS (optional)

## Workflow

### Step 0: Load Team Configuration

1. **Read** `.claude/linear-config.json`
2. **If not exists**, prompt user:
   ```
   Linear configuration not found. Please run `/yux-linear-start` first to set up team/project.
   ```
3. Store `LINEAR_TEAM` and `LINEAR_PROJECT` for API calls

## Prerequisites Check

1. **Verify current branch**:
   ```bash
   git branch --show-current
   ```
   - Must NOT be on `main` or `master`
   - Should contain Linear issue ID (e.g., `LIN-123`)

2. **Check for commits**:
   ```bash
   git log origin/main..HEAD --oneline
   ```
   - Must have at least one commit

3. **Verify gh CLI**:
   ```bash
   gh auth status
   ```

### Step 1: Extract Issue Information

1. **Get current branch name**:
   ```bash
   BRANCH=$(git branch --show-current)
   ```

2. **Extract Linear issue ID**:
   - Parse branch name for pattern `LIN-\d+`
   - Example: `feat/LIN-456-user-auth` → `LIN-456`

3. **Fetch issue details from Linear**:
   ```
   mcp__linear__get_issue(id: "LIN-456")
   ```
   - Get title, description, labels

### Step 2: Gather Commit Information

1. **List all commits**:
   ```bash
   git log origin/main..HEAD --pretty=format:"%s" --reverse
   ```

2. **Generate changelog**:
   - Parse commit messages
   - Group by type (feat, fix, etc.)
   - Create bullet list

### Step 3: Generate PR Content

1. **Create PR title**:
   - Format: `[LIN-456] <Issue Title>`
   - Example: `[LIN-456] Implement user authentication`

2. **Create PR body** (based on configured language):

   > PR content language follows `.claude/yux-config.json` setting

   ```markdown
   ## Summary

   <Issue description from Linear>

   <Additional description from user if provided>

   ## Linear Issue

   Closes LIN-456

   ## Changes

   - feat(auth): add login component
   - feat(auth): add JWT token handling
   - test(auth): add authentication tests

   ## Test Plan

   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed

   ---
   Generated with Linear Workflow Plugin
   ```

### Step 4: Create Pull Request

1. **Push latest changes**:
   ```bash
   git push origin HEAD
   ```

2. **Create PR via gh CLI**:
   ```bash
   gh pr create \
     --title "[LIN-456] <title>" \
     --body "<generated body>" \
     --base main
   ```

3. **Get PR number and URL**:
   ```bash
   gh pr view --json number,url
   ```

### Step 5: Update Linear Issue

1. **Update status to "In Review"**:
   ```
   mcp__linear__update_issue(
     id: "LIN-456",
     state: "In Review"
   )
   ```

2. **Add PR link as comment**:
   ```
   mcp__linear__create_comment(
     issueId: "LIN-456",
     body: "Pull Request created: <PR URL>\n\nChanges:\n<commit list>"
   )
   ```

### Step 6: Check Initial CI Status (No Polling)

Display initial CI status once, then finish:

1. **Check CI status**:
   ```bash
   gh pr checks <pr-number> --json name,state,conclusion 2>/dev/null || echo "[]"
   ```

2. **Display initial status** (one-time, no polling):
   ```
   === CI Status ===
   ├── ○ lint (pending)
   ├── ○ build (pending)
   ├── ○ test (pending)
   └── ○ deploy-preview (pending)
   ```

   Or if no CI configured:
   ```
   CI Status: No checks configured
   ```

**Note**: This command does NOT poll for CI updates. Use `/yux-linear-merge` when ready to merge - it will check CI status at that time.

### Step 7: Output Summary

> Output language follows `.claude/yux-config.json` setting

```
=== Pull Request Created ===

PR:      #78 - [LIN-456] Implement user authentication
URL:     https://github.com/org/repo/pull/78
Branch:  feat/LIN-456-user-auth → main

Linear:  LIN-456 status updated to "In Review"

CI Status:
├── ○ lint (pending)
├── ○ build (pending)
├── ○ test (pending)
└── ○ deploy-preview (pending)

---
📋 Next Steps:

/yux-linear-status  - Check current status
/yux-linear-merge   - Merge the PR (will check CI at that time)
```

## Error Handling

- **On main branch**: "Cannot create PR from main. Use /yux-linear-start first"
- **No commits**: "No commits to create PR. Make some changes first"
- **No issue ID in branch**: Warning but allow PR creation
- **PR already exists**: Show existing PR info, ask to update

## Example

```
User: /yux-linear-pr

Claude: Creating pull request...

Current branch: feat/LIN-456-user-auth
Issue: LIN-456 - Implement user authentication

Commits to include:
- feat(auth): add login component
- feat(auth): add JWT token handling
- test(auth): add authentication tests

Creating PR...
✓ PR #78 created: https://github.com/org/repo/pull/78
✓ Linear LIN-456 updated to "In Review"

CI Status:
├── ○ lint (pending)
├── ○ build (pending)
├── ○ test (pending)
└── ○ deploy-preview (pending)

---
📋 Next Steps:

/yux-linear-status  - Check current status
/yux-linear-merge   - Merge the PR (will check CI at that time)
```
