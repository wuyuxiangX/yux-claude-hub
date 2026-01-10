---
name: linear-merge-executor
description: Execute merge workflow with CI checking and context gathering. Use when merging a PR with full Linear and GitHub context. Handles CI polling, merge validation, execution, cleanup, and status updates. Triggered by /yux-linear-merge command.
context: fork
agent: general-purpose
allowed-tools: Read, Bash, Grep
model: sonnet
---

# Merge Executor Skill

You are a specialized merge workflow executor. Your job is to check CI status, gather merge context, validate conditions, execute the merge, and update Linear status.

## Input

You will receive:
- `pr_number`: The PR number to merge
- `issue_id`: The Linear issue ID (e.g., "LIN-456")
- `issue_uuid`: The Linear issue UUID for API calls
- `merge_strategy`: One of "squash" (default), "rebase", or "merge"
- `branch_name`: The current branch name

## Workflow

### Step 1: Poll CI Status

Poll GitHub Actions status until all checks complete or timeout:

```bash
gh pr checks <pr_number> --json name,state,conclusion,startedAt,completedAt,detailsUrl
```

**Polling rules:**
- Poll every 15 seconds
- Maximum duration: 30 minutes
- Stop when all checks have conclusion (not pending/in_progress)

**If any check failed:**
1. Get the failed check's run ID from detailsUrl
2. Fetch error logs:
   ```bash
   gh run view <run-id> --log-failed
   ```
3. Return immediately with `blocked` status and error details

**If no CI checks configured:**
- Continue to merge validation (no blocking)

### Step 2: Validate Merge Readiness

```bash
gh pr view <pr_number> --json state,mergeable,mergeStateStatus,headRefName
```

Check for blocking conditions:
- `mergeable: false` → Merge conflicts
- `mergeStateStatus: BLOCKED` → Branch protection rules

If blocked, return immediately with `blocked` status.

### Step 3: Gather Context (for summary only)

**Fetch Linear issue comments:**
```
mcp__linear__list_comments(issueId: "<issue_uuid>")
```

**Fetch GitHub PR reviews:**
```bash
gh pr view <pr_number> --json reviews,comments
```

Summarize the context (do not output full content):
- Number of Linear comments
- Number of PR reviews and their status
- Any unresolved review comments

### Step 4: Execute Merge

```bash
gh pr merge <pr_number> --<strategy> --delete-branch
```

Where `<strategy>` is squash, rebase, or merge.

### Step 5: Verify Merge Success

```bash
gh pr view <pr_number> --json state,mergedAt,mergeCommit
```

### Step 6: Clean Up Local Branch

```bash
git checkout main
git pull origin main
git branch -d <branch_name>
```

### Step 7: Update Linear Issue

**Update status to "Done":**
```
mcp__linear__update_issue(
  id: "<issue_id>",
  state: "Done"
)
```

**Add completion comment:**
```
mcp__linear__create_comment(
  issueId: "<issue_uuid>",
  body: "Task completed!\n\nPR #<pr_number> merged to main.\nMerge commit: <sha>"
)
```

### Step 8: Return Structured Result

Always return a JSON result:

```json
{
  "status": "success|blocked|failed",
  "summary": "Human-readable one-line summary",
  "pr": {
    "number": 78,
    "title": "[LIN-456] Implement authentication",
    "merge_commit": "abc1234",
    "merged_at": "2024-01-15T15:45:00Z"
  },
  "issue": {
    "id": "LIN-456",
    "status": "Done"
  },
  "context_summary": {
    "linear_comments": 5,
    "pr_reviews": 2,
    "review_status": "approved"
  },
  "cleanup": {
    "remote_branch_deleted": true,
    "local_branch_deleted": true,
    "switched_to_main": true
  },
  "error": null | {
    "type": "merge_conflict|ci_failed|review_pending|branch_protection",
    "message": "Error description"
  },
  "action_required": null | {
    "type": "...",
    "suggestion": "What the user should do"
  }
}
```

## Result Status Codes

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| `success` | Merge completed successfully | None |
| `blocked` | Cannot merge due to conditions | See action_required |
| `failed` | Merge attempted but failed | Check error |

## Blocking Conditions

| Condition | Error Type | Suggestion |
|-----------|------------|------------|
| Merge conflicts | `merge_conflict` | Resolve conflicts and push |
| CI not passed | `ci_failed` | Fix CI issues first |
| Reviews pending | `review_pending` | Wait for review approval |
| Branch protection | `branch_protection` | Contact admin |

## Important Notes

1. **Context efficiency**: Gather context but only return summaries, not full content
2. **Atomic operations**: If any step fails, report current state and stop
3. **Cleanup safety**: Only delete local branch if merge succeeded
4. **Linear sync**: Always update Linear status after successful merge
