# Linear Status - Check Workflow Status

Display comprehensive status of the current Linear workflow including issue, branch, PR, and CI status.

**Usage**: `/yux-linear-status`

## Workflow

### Step 1: Gather Git Information

1. **Get current branch**:
   ```bash
   git branch --show-current
   ```

2. **Extract Linear issue ID** from branch name:
   - Pattern: `LIN-\d+`
   - If not found, check for any open issue context

3. **Get commit count**:
   ```bash
   git rev-list --count origin/main..HEAD
   ```

4. **Get uncommitted changes**:
   ```bash
   git status --porcelain | wc -l
   ```

### Step 2: Fetch Linear Issue Details

If issue ID found:
```
mcp__linear__getIssue(issueId: "LIN-xxx")
```

Extract:
- Title
- Status (Backlog, Todo, In Progress, In Review, Done)
- Priority
- Assignee
- Labels
- Created date
- Recent comments

### Step 3: Check PR Status

1. **Find associated PR**:
   ```bash
   gh pr list --head <current-branch> --json number,title,state,url
   ```

2. **If PR exists, get details**:
   ```bash
   gh pr view <number> --json state,reviews,mergeable,mergeStateStatus
   ```

### Step 4: Check CI/CD Status

If PR exists:
```bash
gh pr checks <pr-number> --json name,state,conclusion,startedAt,completedAt
```

Parse results:
- `queued` → ○ (pending)
- `in_progress` → ○ (running)
- `completed` + `success` → ✓ (passed)
- `completed` + `failure` → ✗ (failed)
- `completed` + `skipped` → ⊘ (skipped)

### Step 5: Generate Status Report

**Full status display**:

```
╔══════════════════════════════════════════════════════════════╗
║                    Linear Workflow Status                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Issue                                                        ║
║  ──────────────────────────────────────────────────────────  ║
║  ID:       LIN-456                                            ║
║  Title:    Implement user authentication                      ║
║  Status:   In Review                                          ║
║  Priority: High                                               ║
║  Created:  2024-01-15 10:30                                   ║
║                                                               ║
║  Branch                                                       ║
║  ──────────────────────────────────────────────────────────  ║
║  Name:     feat/LIN-456-user-auth                            ║
║  Commits:  5 ahead of main                                    ║
║  Changes:  2 uncommitted files                                ║
║                                                               ║
║  Pull Request                                                 ║
║  ──────────────────────────────────────────────────────────  ║
║  PR:       #78 - [LIN-456] Implement user authentication     ║
║  URL:      https://github.com/org/repo/pull/78               ║
║  Status:   Open                                               ║
║  Reviews:  0/2 approved                                       ║
║  Merge:    Ready (no conflicts)                               ║
║                                                               ║
║  CI/CD                                                        ║
║  ──────────────────────────────────────────────────────────  ║
║  ├── ✓ lint          (12s)                                   ║
║  ├── ✓ build         (45s)                                   ║
║  ├── ✓ test          (2m 30s)                                ║
║  ├── ✓ e2e           (5m 12s)                                ║
║  └── ✓ deploy-preview (1m 8s)                                ║
║                                                               ║
║  Status: All 5 checks passed                                  ║
║                                                               ║
║  Timeline                                                     ║
║  ──────────────────────────────────────────────────────────  ║
║  10:30  Issue created                                         ║
║  10:32  Branch created                                        ║
║  12:45  PR created                                            ║
║  12:50  CI started                                            ║
║  12:58  CI passed                                             ║
║                                                               ║
║  Next Steps                                                   ║
║  ──────────────────────────────────────────────────────────  ║
║  → Ready to merge! Use /yux-linear-merge                      ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
```

### Simplified Output (when not on task branch)

```
=== Linear Workflow Status ===

Current branch: main

No active Linear task detected.
Use /yux-linear-start to begin a new task.
```

### Status Indicators

| Symbol | Meaning |
|--------|---------|
| ✓ | Passed/Complete |
| ✗ | Failed |
| ○ | Running/Pending |
| ⊘ | Skipped |
| → | Next action |

### Next Steps Suggestions

Based on current state, suggest appropriate actions:

| State | Suggestion |
|-------|------------|
| No branch | "Use /yux-linear-start to begin" |
| No commits | "Make some changes and commit" |
| No PR | "Use /yux-linear-pr to create PR" |
| CI running | "Waiting for CI to complete..." |
| CI failed | "Fix the failing checks, then push" |
| CI passed | "Use /yux-linear-merge to merge" |
| Needs review | "Waiting for code review approval" |

## Error Handling

- **Not in git repo**: "Please navigate to a git repository"
- **Linear not configured**: "Linear MCP not available. Run /mcp to configure"
- **No issue found**: Show available info (branch, commits) without Linear details

## Multi-language Support

Detect user language and display messages accordingly:

**Chinese**:
```
=== Linear 工作流状态 ===

Issue:    LIN-456 - 实现用户认证
状态:     审核中
分支:     feat/LIN-456-user-auth

下一步:   → 准备合并！使用 /yux-linear-merge
```
