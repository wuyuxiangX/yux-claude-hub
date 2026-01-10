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

### Step 2: Ask User Confirmation

Display merge summary (without fetching full context):

```
=== Ready to Merge ===

PR:       #78 - [LIN-456] Implement user authentication
Strategy: squash (default)

This will:
1. Merge PR #78 into main
2. Delete branch feat/LIN-456-user-auth
3. Mark Linear issue LIN-456 as Done

Proceed with merge? [Y/n]
```

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
  "context_summary": { "linear_comments": 5, "pr_reviews": 2 },
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

Proceed with merge? [Y/n]

User: Y

Claude: Executing merge via linear-merge-executor skill...

[Skill executes in forked context: gather context, validate, merge, update Linear]

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

Proceed with merge? [Y/n]

User: Y

Claude: Executing merge via linear-merge-executor skill...

Cannot merge: CI checks not passed

Error: test check failed - 2 tests failing

Suggestion: Fix the failing tests and push again
```
