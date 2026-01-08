---
name: yux-ci-monitor
description: Monitor CI/CD status for pull requests with error reporting. Triggers: "check CI", "CI status", "workflow status", "monitor CI", "检查CI", "CI状态", "查看构建".
allowed-tools: Read, Bash(gh:*)
---

# CI/CD Monitor

Monitor GitHub Actions and other CI/CD checks for pull requests, with detailed error reporting and merge prompts.

## Overview

This skill provides:
1. Real-time CI status monitoring
2. Detailed error logs when checks fail
3. Automatic merge prompts when all checks pass
4. Progress visualization

## Usage

Triggered automatically after PR creation, or manually via:
- "check CI status"
- "what's the CI status"
- "检查CI状态"

## Workflow

### Step 1: Get PR Information

```bash
gh pr view --json number,headRefName,state
```

If no PR found:
```
No pull request found for current branch.
Use /yux-linear-pr to create one.
```

### Step 2: Fetch CI Status

```bash
gh pr checks <pr-number> --json name,state,conclusion,startedAt,completedAt,detailsUrl
```

Parse results:

| State | Conclusion | Display |
|-------|------------|---------|
| `queued` | - | ○ pending |
| `in_progress` | - | ○ running |
| `completed` | `success` | ✓ passed |
| `completed` | `failure` | ✗ failed |
| `completed` | `skipped` | ⊘ skipped |
| `completed` | `cancelled` | ⊘ cancelled |

### Step 3: Display Status

**Running checks**:
```
=== CI Status (Running) ===

PR #78: [LIN-456] Implement user authentication

├── ✓ lint          (12s)
├── ✓ build         (45s)
├── ○ test          (running... 1m 30s)
├── ○ e2e           (pending)
└── ○ deploy-preview (pending)

Progress: 2/5 checks passed
Estimated time remaining: ~5 minutes
```

**All passed**:
```
=== CI Status (Passed) ===

PR #78: [LIN-456] Implement user authentication

├── ✓ lint          (12s)
├── ✓ build         (45s)
├── ✓ test          (2m 30s)
├── ✓ e2e           (5m 12s)
└── ✓ deploy-preview (1m 8s)

All 5 checks passed!

Preview: https://preview-78.example.com

Ready to merge! Use /yux-linear-merge or say "merge".
```

### Step 4: Handle Failures

When checks fail:

1. **Identify failed check**:
   ```bash
   gh pr checks <pr-number> --json name,conclusion | jq '.[] | select(.conclusion == "failure")'
   ```

2. **Get run ID**:
   ```bash
   gh pr checks <pr-number> --json name,conclusion,detailsUrl
   ```

3. **Fetch error logs**:
   ```bash
   gh run view <run-id> --log-failed
   ```

4. **Parse and display errors**:

```
=== CI Status (Failed) ===

PR #78: [LIN-456] Implement user authentication

├── ✓ lint          (12s)
├── ✓ build         (45s)
├── ✗ test          (failed)
├── ⊘ e2e           (skipped)
└── ⊘ deploy-preview (skipped)

Failed: test

┌─────────────────────────────────────────────────────────────┐
│ Error Details                                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ FAIL src/auth/login.test.ts                                 │
│                                                              │
│ ● login › should return valid token                         │
│                                                              │
│   expect(received).toBe(expected)                           │
│                                                              │
│   Expected: "valid-token"                                   │
│   Received: undefined                                       │
│                                                              │
│   at src/auth/login.test.ts:25:18                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Suggestion:
The login function is not returning the token.
Check src/auth/login.ts around line 25.

Fix the issue and push to re-run CI.
```

### Step 5: Polling Mode

For active monitoring:

1. **Initial check**: Immediate status display
2. **Poll interval**: 15 seconds
3. **Max duration**: 30 minutes
4. **Early exit**: When all checks complete (pass or fail)

```
Monitoring CI... (press Ctrl+C to stop)

[12:45:30] ○ test running (1m 15s)
[12:45:45] ○ test running (1m 30s)
[12:46:00] ✓ test passed (1m 45s)
[12:46:15] ○ e2e running (0s)
...
```

## Error Analysis

### Common Error Patterns

| Pattern | Cause | Suggestion |
|---------|-------|------------|
| `npm ERR!` | Dependency issue | Run `npm install` |
| `ENOENT` | File not found | Check file paths |
| `TypeError` | Type mismatch | Review type definitions |
| `timeout` | Test too slow | Increase timeout or optimize |
| `ENOMEM` | Out of memory | Reduce test parallelism |

### Intelligent Suggestions

Based on error content, provide actionable suggestions:

**Test failure**:
```
Suggestion: Test assertion failed.
- Review the test expectation
- Check if the implementation matches the test
- Run locally: npm test -- --grep "login"
```

**Build failure**:
```
Suggestion: Build compilation error.
- Check TypeScript errors
- Run locally: npm run build
- Fix import/export issues
```

**Lint failure**:
```
Suggestion: Code style violation.
- Run: npm run lint:fix
- Or manually fix the reported issues
```

## Status Symbols

| Symbol | Meaning |
|--------|---------|
| ✓ | Check passed |
| ✗ | Check failed |
| ○ | Running or pending |
| ⊘ | Skipped or cancelled |

## Multi-language Support

### English
```
All 5 checks passed! Ready to merge.
```

### Chinese
```
全部 5 项检查通过！准备合并。
```

### Japanese
```
全5件のチェックが完了しました！マージ可能です。
```

## Integration with Linear

When CI fails, optionally update Linear issue:

```
mcp__linear__createComment(
  issueId: "LIN-456",
  body: "CI failed: test\n\nError: ...\n\nWorking on fix."
)
```

When CI passes:

```
mcp__linear__createComment(
  issueId: "LIN-456",
  body: "All CI checks passed! Ready for review and merge."
)
```

## Output Examples

### Polling Update
```
[14:32:15] CI Update
├── ✓ lint (passed)
├── ✓ build (passed)
├── ○ test (2m 15s elapsed)
└── ○ e2e (waiting)

Still running... next check in 15s
```

### Final Success
```
=== CI Complete ===

All checks passed in 8m 32s

├── ✓ lint          12s
├── ✓ build         45s
├── ✓ test          3m 20s
├── ✓ e2e           4m 5s
└── ✓ deploy        10s

Preview URL: https://preview.example.com

Merge now? [Y/n]
```

### Final Failure
```
=== CI Failed ===

3 of 5 checks passed

├── ✓ lint
├── ✓ build
├── ✗ test         ← Click for details
├── ⊘ e2e          (skipped due to test failure)
└── ⊘ deploy       (skipped)

See error details above. Fix and push to retry.
```
