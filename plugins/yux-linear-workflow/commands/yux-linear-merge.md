# Linear Merge - Merge Pull Request

Complete the workflow by merging the PR, cleaning up branches, and closing the Linear issue.

**Usage**: `/yux-linear-merge [--squash|--rebase|--merge]`

## Input

Merge strategy from: $ARGUMENTS (optional, default: squash)

Options:
- `--squash` (default): Squash all commits into one
- `--rebase`: Rebase and merge
- `--merge`: Create merge commit

## Prerequisites Check

1. **Verify PR exists**:
   ```bash
   gh pr view --json number,state,mergeable
   ```

2. **Check CI status**:
   ```bash
   gh pr checks --json state,conclusion
   ```
   - All checks must pass

3. **Check merge eligibility**:
   - No merge conflicts
   - Required reviews approved (if configured)

## Workflow

### Step 1: Validate Merge Readiness

1. **Get PR details**:
   ```bash
   gh pr view --json number,title,state,mergeable,mergeStateStatus,headRefName
   ```

2. **Verify all CI checks passed**:
   ```bash
   gh pr checks --json name,state,conclusion
   ```

3. **Check for blocking conditions**:
   - `mergeable: false` → "Merge conflicts detected"
   - `mergeStateStatus: BLOCKED` → "Branch protection rules not satisfied"
   - Required reviewers not approved → "Waiting for review approval"

### Step 2: Confirm with User

Display merge summary:

```
=== Ready to Merge ===

PR:       #78 - [LIN-456] Implement user authentication
Commits:  5
CI:       All checks passed

Merge strategy: squash (default)

This will:
1. Merge PR #78 into main
2. Delete branch feat/LIN-456-user-auth
3. Close Linear issue LIN-456

Proceed with merge? [Y/n]
```

### Step 3: Execute Merge

1. **Merge the PR**:
   ```bash
   gh pr merge <number> --squash --delete-branch
   ```

   Or with other strategies:
   ```bash
   gh pr merge <number> --rebase --delete-branch
   gh pr merge <number> --merge --delete-branch
   ```

2. **Verify merge success**:
   ```bash
   gh pr view <number> --json state,mergedAt,mergeCommit
   ```

### Step 4: Clean Up Local Branch

1. **Switch to main**:
   ```bash
   git checkout main
   ```

2. **Pull latest changes**:
   ```bash
   git pull origin main
   ```

3. **Delete local branch**:
   ```bash
   git branch -d <branch-name>
   ```

### Step 5: Update Linear Issue

1. **Update status to "Done"**:
   ```
   mcp__linear__updateIssue(
     issueId: "LIN-456",
     stateId: "<done-state-id>"
   )
   ```

2. **Add completion comment**:
   ```
   mcp__linear__createComment(
     issueId: "LIN-456",
     body: "Task completed!\n\nPR #78 merged to main.\nMerge commit: <sha>"
   )
   ```

### Step 6: Output Completion Report

**Success output**:

```
╔══════════════════════════════════════════════════════════════╗
║                     Task Completed!                           ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Issue                                                        ║
║  ──────────────────────────────────────────────────────────  ║
║  LIN-456: Implement user authentication                       ║
║  Status:  ✓ Done                                              ║
║                                                               ║
║  Pull Request                                                 ║
║  ──────────────────────────────────────────────────────────  ║
║  PR #78: Merged to main                                       ║
║  Commit: abc1234                                              ║
║  Method: Squash merge                                         ║
║                                                               ║
║  Cleanup                                                      ║
║  ──────────────────────────────────────────────────────────  ║
║  ✓ Remote branch deleted                                      ║
║  ✓ Local branch deleted                                       ║
║  ✓ Switched to main branch                                    ║
║                                                               ║
║  Summary                                                      ║
║  ──────────────────────────────────────────────────────────  ║
║  Started:   2024-01-15 10:30                                  ║
║  Completed: 2024-01-15 15:45                                  ║
║  Duration:  5h 15m                                            ║
║  Commits:   5 (squashed to 1)                                 ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝

Great work! Ready for the next task?
Use /yux-linear-start to begin a new task.
```

## Error Handling

### CI Not Passed
```
Cannot merge: CI checks not passed

Failed checks:
├── ✗ test - 3 tests failed
└── ✗ e2e - Timeout error

Fix the issues and push again, or use /yux-linear-status to check details.
```

### Merge Conflicts
```
Cannot merge: Merge conflicts detected

Conflicting files:
- src/auth/login.ts
- src/components/LoginForm.tsx

To resolve:
1. git pull origin main
2. Resolve conflicts
3. git add . && git commit
4. git push
5. Run /linear-merge again
```

### Missing Reviews
```
Cannot merge: Required reviews not approved

Review status:
- @reviewer1: Pending
- @reviewer2: Pending

Required: 2 approvals
Current:  0 approvals

Please wait for reviews or request reviews from your team.
```

### Branch Protection
```
Cannot merge: Branch protection rules not satisfied

Missing requirements:
- Status checks must pass
- Required reviewers must approve

Contact repository admin if you believe this is an error.
```

## Multi-language Support

**Chinese completion message**:
```
╔══════════════════════════════════════════════════════════════╗
║                       任务完成！                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Issue: LIN-456 - 实现用户认证                                ║
║  状态:  ✓ 已完成                                              ║
║                                                               ║
║  PR #78 已合并到 main 分支                                    ║
║  分支已清理完毕                                               ║
║                                                               ║
║  用时: 5小时15分钟                                            ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝

恭喜完成任务！
使用 /yux-linear-start 开始下一个任务。
```

## Example

```
User: /yux-linear-merge

Claude: Checking merge readiness...

PR #78: [LIN-456] Implement user authentication
CI Status: All 5 checks passed
Reviews: 2/2 approved
Conflicts: None

=== Ready to Merge ===

This will:
1. Squash merge PR #78 into main
2. Delete branch feat/LIN-456-user-auth
3. Mark LIN-456 as Done

Proceed? [Y/n]

User: Y

Claude: Merging...
✓ PR #78 merged to main
✓ Remote branch deleted
✓ Local branch deleted
✓ Linear LIN-456 marked as Done

=== Task Completed! ===

LIN-456: Implement user authentication
Status: Done
Duration: 5h 15m

Great work! Use /yux-linear-start for your next task.
```
