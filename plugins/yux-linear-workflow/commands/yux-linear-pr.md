# Linear PR - Create Pull Request

Create a pull request with Linear issue integration and CI/CD monitoring.

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
   mcp__linear__getIssue(issueId: "LIN-456")
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

2. **Create PR body**:
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
   mcp__linear__updateIssue(
     issueId: "LIN-456",
     stateId: "<in-review-state-id>"
   )
   ```

2. **Add PR link as comment**:
   ```
   mcp__linear__createComment(
     issueId: "LIN-456",
     body: "Pull Request created: <PR URL>\n\nChanges:\n<commit list>"
   )
   ```

### Step 6: Monitor CI/CD

Trigger CI monitoring (invoke yux-ci-monitor skill):

1. **Initial status check**:
   ```bash
   gh pr checks <pr-number> --json name,state,conclusion
   ```

2. **Display initial status**:
   ```
   === CI Status ===
   ├── ○ lint (pending)
   ├── ○ build (pending)
   ├── ○ test (pending)
   └── ○ deploy-preview (pending)

   Monitoring CI... (will update every 15 seconds)
   ```

3. **Poll for updates** until all checks complete or timeout (30 min)

4. **On completion**:
   - All passed → Prompt for merge
   - Any failed → Show error details

### Step 7: Output Summary

**Success output**:
```
=== Pull Request Created ===

PR:      #78 - [LIN-456] Implement user authentication
URL:     https://github.com/org/repo/pull/78
Branch:  feat/LIN-456-user-auth → main

Linear:  LIN-456 status updated to "In Review"

CI Status: Monitoring...
├── ✓ lint (passed)
├── ✓ build (passed)
├── ○ test (running)
└── ○ deploy-preview (pending)

---
📋 Next Steps:

\`\`\`
/yux-linear-status
\`\`\`
Monitor CI status

\`\`\`
/yux-linear-merge
\`\`\`
Merge the PR when CI passes
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

=== CI Monitoring ===
├── ○ lint (queued)
├── ○ build (queued)
├── ○ test (queued)
└── ○ deploy-preview (queued)

Waiting for CI to start...
```
