---
description: Merge PR and close Linear issue
---

# Linear Merge - Merge Pull Request

Complete the workflow by merging the PR, cleaning up branches, and closing the Linear issue.

**Usage**: `/yux-linear-merge [--squash|--rebase|--merge]`

## Input

Merge strategy from: $ARGUMENTS (optional, default: squash)

Options:
- `--squash` (default): Squash all commits into one
- `--rebase`: Rebase and merge
- `--merge`: Create merge commit

## Overview

This command performs quick validation and confirmation in the main agent, then delegates the heavy merge workflow to the `linear-merge-executor` skill running in a forked subagent context.

## Workflow

### Step 0: Load Configuration

1. **Read** `.claude/linear-config.json`
2. **If not exists**, prompt user:
   ```
   Linear configuration not found. Please run `/yux-linear-start` first to set up team/project.
   ```

3. **Read local state file** `.claude/linear-tasks/<ISSUE_ID>.json` to get:
   - `issue_id`: Linear issue ID (e.g., "LIN-456")
   - `issue_uuid`: Linear issue UUID for API calls
   - `branch_name`: Current branch name

### Step 1: Quick Pre-check

Before delegating, do a quick validation:

```bash
gh pr view --json number,state,mergeable,mergeStateStatus
```

If PR doesn't exist or is already merged, inform user immediately.

### Step 1.5: Collect and Summarize Pending Issues

**IMPORTANT**: Before asking for merge confirmation, collect and display any pending issues from both GitHub PR and Linear issue.

**1. Get GitHub PR reviews and comments:**
```bash
gh pr view <pr_number> --json reviews,comments,reviewDecision
```

**2. Get Linear issue comments:**
```
mcp__linear__list_comments(issueId: "<issue_uuid>")
```

**3. Filter and summarize issues:**

Only extract and display:
- Reviews with `CHANGES_REQUESTED` state
- Comments containing questions (?)
- Comments suggesting changes/improvements
- Unresolved discussion threads

**Do NOT display:**
- `APPROVED` reviews with positive-only content (e.g., "LGTM", "Looks good", "+1")
- Already resolved discussions
- Pure status updates

**4. Display format (only if issues exist):**

```
=== Pending Issues Summary ===

From GitHub PR:
┌─────────────────────────────────────────────────────────────┐
│ [CHANGES_REQUESTED] @reviewer:                              │
│ "Please add error handling for the API call on line 45"     │
├─────────────────────────────────────────────────────────────┤
│ [Comment] @user:                                            │
│ "Should we add tests for this edge case?"                   │
└─────────────────────────────────────────────────────────────┘

From Linear:
┌─────────────────────────────────────────────────────────────┐
│ @pm_user:                                                   │
│ "Can you also update the documentation for this change?"    │
└─────────────────────────────────────────────────────────────┘
```

**5. If no issues found:**
- Skip this section entirely, proceed directly to confirmation
- Do NOT display "No issues found" message

**6. If more than 5 issues:**
- Display the most recent 5 issues
- Add note: "... and N more issues"

### Step 2: Ask User Confirmation (MANDATORY)

**CRITICAL**: You MUST use `AskUserQuestion` tool to get explicit user confirmation. Do NOT proceed without it.

**If pending issues exist:**

Display the issues summary from Step 1.5, then use AskUserQuestion:

```
=== Ready to Merge ===

PR:       #78 - [LIN-456] Implement user authentication
Strategy: squash (default)

⚠️  N pending issues shown above
```

Then call AskUserQuestion with:
- Question: "How would you like to proceed?"
- Options:
  - "Proceed with merge" - Continue merging despite pending issues
  - "Cancel and address issues" - Stop and handle the issues first

**If no pending issues:**

```
=== Ready to Merge ===

PR:       #78 - [LIN-456] Implement user authentication
Strategy: squash (default)

This will:
1. Merge PR into main
2. Delete the feature branch
3. Mark Linear issue as Done
```

Then call AskUserQuestion with:
- Question: "Ready to merge?"
- Options:
  - "Proceed with merge" - Execute the merge
  - "Cancel" - Abort the operation

**Handle user response:**
- If user selects "Cancel" or "Cancel and address issues": Display cancellation message and stop
- If user selects "Proceed with merge": Continue to Step 3

### Step 3: Execute via linear-merge-executor Skill

After user confirms, **use the linear-merge-executor skill** to execute the full merge workflow in a forked subagent context. Pass the following parameters:

- `pr_number`: The PR number
- `issue_id`: The Linear issue ID
- `issue_uuid`: The Linear issue UUID
- `merge_strategy`: squash, rebase, or merge
- `branch_name`: The current branch name

The skill will:
- Poll CI status until completion
- Gather merge context from Linear and GitHub
- Validate merge readiness
- Execute merge with specified strategy
- Clean up local and remote branches
- Update Linear issue status to Done

### Step 4: Handle Skill Result

Parse the structured result from the skill:

**Success result:**
```json
{
  "status": "success",
  "summary": "PR #78 merged to main via squash",
  "pr": { "number": 78, "merge_commit": "abc1234" },
  "issue": { "id": "LIN-456", "status": "Done" },
  "cleanup": { "remote_branch_deleted": true, "local_branch_deleted": true }
}
```

Display to user:
```
╔══════════════════════════════════════════════════════════════╗
║                     Task Completed!                           ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Issue: LIN-456 → Done                                        ║
║  PR: #78 merged to main (abc1234)                             ║
║  Method: Squash merge                                         ║
║                                                               ║
║  Cleanup:                                                     ║
║  ✓ Remote branch deleted                                      ║
║  ✓ Local branch deleted                                       ║
║  ✓ Switched to main branch                                    ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝

---
📋 Next Steps:

\`\`\`
/yux-linear-backlog
\`\`\`
View backlog and start the next task
```

**Blocked result:**
```json
{
  "status": "blocked",
  "summary": "Cannot merge: CI checks not passed",
  "error": { "type": "ci_failed", "message": "test check failed" },
  "action_required": { "type": "fix_ci", "suggestion": "Fix the failing tests and push again" }
}
```

Display to user:
```
Cannot merge: CI checks not passed

Error: test check failed

Suggestion: Fix the failing tests and push again
```

**Failed result:**
```json
{
  "status": "failed",
  "summary": "Merge failed",
  "error": { "type": "merge_conflict", "message": "Conflicts in src/auth.ts" }
}
```

Display to user:
```
Merge failed: Conflicts in src/auth.ts

To resolve:
1. git pull origin main
2. Resolve conflicts
3. git add . && git commit
4. git push
5. Run /yux-linear-merge again
```

## Error Handling

Blocking conditions are handled by the skill and returned as structured errors:

| Error Type | Message | Suggestion |
|------------|---------|------------|
| `ci_failed` | CI checks not passed | Fix and push |
| `merge_conflict` | Merge conflicts detected | Resolve conflicts |
| `review_pending` | Reviews not approved | Wait for reviews |
| `branch_protection` | Protection rules not met | Contact admin |

## Multi-language Support

> All output messages follow `.claude/yux-config.json` setting

Completion message and all status updates are displayed in the configured language.

## Skill Details

The merge executor skill (`linear-merge-executor`) is defined in:
`plugins/yux-linear-workflow/skills/linear-merge-executor/SKILL.md`

It runs with `context: fork` which ensures execution in an isolated subagent context.

This delegation reduces main agent context consumption from ~5000 tokens to ~500 tokens.

## Example

### Example: With Pending Issues

```
User: /yux-linear-merge

Claude:
=== Pending Issues Summary ===

From GitHub PR:
┌─────────────────────────────────────────────────────────────┐
│ [CHANGES_REQUESTED] @bob:                                   │
│ "Please add error handling for the API call on line 45"     │
└─────────────────────────────────────────────────────────────┘

From Linear:
┌─────────────────────────────────────────────────────────────┐
│ @pm_user:                                                   │
│ "Can you also update the documentation?"                    │
└─────────────────────────────────────────────────────────────┘

=== Ready to Merge ===

PR:       #78 - [LIN-456] Implement user authentication
Strategy: squash (default)

⚠️  2 pending issues shown above

[Claude uses AskUserQuestion tool - waits for user response]

User selects: "Cancel and address issues"

Claude: Merge cancelled. You can address the issues and run /yux-linear-merge again.
```

### Example: No Pending Issues

```
User: /yux-linear-merge

Claude:
=== Ready to Merge ===

PR:       #78 - [LIN-456] Implement user authentication
Strategy: squash (default)

This will:
1. Merge PR #78 into main
2. Delete branch feat/LIN-456-user-auth
3. Mark Linear issue LIN-456 as Done

[Claude uses AskUserQuestion tool - waits for user response]

User selects: "Proceed with merge"

Claude: Executing merge via linear-merge-executor skill...

[Skill executes in forked context: validate, merge, update Linear]

╔══════════════════════════════════════════════════════════════╗
║                     Task Completed!                           ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Issue: LIN-456 → Done                                        ║
║  PR: #78 merged to main (abc1234)                             ║
║  Method: Squash merge                                         ║
║                                                               ║
║  Cleanup:                                                     ║
║  ✓ Remote branch deleted                                      ║
║  ✓ Local branch deleted                                       ║
║  ✓ Switched to main branch                                    ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝

---
📋 Next Steps:

\`\`\`
/yux-linear-backlog
\`\`\`
View backlog and start the next task
```

### Example: Blocked by CI

```
User: /yux-linear-merge

Claude:
=== Ready to Merge ===

PR:       #78 - [LIN-456] Implement user authentication
Strategy: squash (default)

[Claude uses AskUserQuestion tool - waits for user response]

User selects: "Proceed with merge"

Claude: Executing merge via linear-merge-executor skill...

Cannot merge: CI checks not passed

Error: test check failed - 2 tests failing

Suggestion: Fix the failing tests and push again
```
