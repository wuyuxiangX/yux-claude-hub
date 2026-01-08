---
name: linear-workflow
description: Complete Linear workflow automation for development tasks. Triggers: "linear workflow", "start task", "work on issue", "create pr", "merge pr", "开始任务", "处理Issue", "创建PR", "合并PR".
allowed-tools: Read, Write, Glob, Grep, Bash(git:*), Bash(gh:*), mcp__linear__*
---

# Linear Workflow

Automate the complete development workflow with Linear issue tracking, from task start to merge completion.

## Overview

This skill provides end-to-end workflow automation:
1. Issue creation/selection
2. Branch management
3. Status synchronization
4. PR creation with CI monitoring
5. Merge and cleanup

## Language Detection

Detect user language from input:
- Chinese characters (Unicode `\u4e00-\u9fff`) > 30% → `zh`
- Japanese hiragana/katakana → `ja`
- Korean hangul → `ko`
- Default → `en`

Apply detected language to all output messages.

## Workflow States

| State | Linear Status | Description |
|-------|---------------|-------------|
| `INIT` | - | Workflow not started |
| `ISSUE_CREATED` | Backlog | Issue created, no branch |
| `BRANCH_CREATED` | Todo | Branch created, ready to work |
| `IN_PROGRESS` | In Progress | Active development |
| `PR_CREATED` | In Review | PR submitted, awaiting review |
| `CI_RUNNING` | In Review | CI checks in progress |
| `CI_FAILED` | In Progress | CI failed, needs fix |
| `READY_TO_MERGE` | In Review | All checks passed |
| `MERGED` | Done | PR merged, task complete |

## Core Functions

### 1. Start Task

When user wants to start a new task:

1. **Check prerequisites**:
   ```bash
   gh auth status
   git rev-parse --is-inside-work-tree
   ```

2. **Search or create Linear issue**:
   - Use `mcp__linear__searchIssues` for search
   - Use `mcp__linear__createIssue` for new issues

3. **Create branch**:
   - Format: `<type>/LIN-<id>-<description>`
   - Types: feat, fix, docs, refactor, test, chore
   ```bash
   git checkout -b <branch-name>
   git push -u origin <branch-name>
   ```

4. **Update Linear status**:
   ```
   mcp__linear__updateIssue(issueId, stateId: "in-progress")
   ```

### 2. Development Tracking

During active development:

1. **Validate commits** follow Conventional Commits:
   - Pattern: `<type>(<scope>): <description>`
   - Valid types: feat, fix, docs, style, refactor, test, chore, perf

2. **Sync progress** periodically:
   - Add comments to Linear issue with progress updates
   - Track blockers and decisions

### 3. Create Pull Request

When ready for review:

1. **Generate PR content**:
   - Title: `[LIN-xxx] <Issue Title>`
   - Body: Summary + changelog + test plan

2. **Create PR**:
   ```bash
   gh pr create --title "<title>" --body "<body>" --base main
   ```

3. **Update Linear**:
   - Status: In Review
   - Add PR link as comment

4. **Monitor CI**:
   - Invoke ci-monitor skill
   - Report status to user

### 4. Merge Completion

When CI passes and reviews approved:

1. **Merge PR**:
   ```bash
   gh pr merge <number> --squash --delete-branch
   ```

2. **Cleanup**:
   ```bash
   git checkout main
   git pull origin main
   git branch -d <branch-name>
   ```

3. **Update Linear**:
   - Status: Done
   - Add completion comment

## Branch Naming Convention

Format: `<type>/LIN-<issue-id>-<short-description>`

| Type | Use Case |
|------|----------|
| `feat` | New features |
| `fix` | Bug fixes |
| `docs` | Documentation |
| `refactor` | Code refactoring |
| `test` | Test additions |
| `chore` | Maintenance |

Examples:
- `feat/LIN-123-user-auth`
- `fix/LIN-456-login-bug`
- `docs/LIN-789-api-docs`

## Commit Message Format

Follow Conventional Commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
Refs: LIN-xxx
```

Examples:
- `feat(auth): add JWT token validation`
- `fix(ui): correct button alignment`
- `docs(api): update endpoint documentation`

## Error Handling

### Linear Not Configured
```
Linear MCP is not configured.

To set up Linear:
1. Run /mcp in Claude Code
2. Add the Linear MCP server
3. Complete OAuth authorization
```

### Not in Git Repository
```
Not inside a git repository.

Please navigate to your project directory and try again.
```

### Branch Already Exists
```
Branch <name> already exists.

Options:
1. Switch to existing branch
2. Create branch with different name
3. Delete existing branch and recreate
```

### CI Failed
```
CI checks failed.

Failed: <check-name>
Error: <error-message>

To fix:
1. Review the error details
2. Make necessary changes
3. Push fixes
4. CI will re-run automatically
```

## Integration Points

### Linear MCP Functions

| Function | Purpose |
|----------|---------|
| `searchIssues` | Find existing issues |
| `createIssue` | Create new issue |
| `getIssue` | Get issue details |
| `updateIssue` | Update status/fields |
| `createComment` | Add progress comments |

### GitHub CLI (gh)

| Command | Purpose |
|---------|---------|
| `gh auth status` | Verify authentication |
| `gh pr create` | Create pull request |
| `gh pr view` | Get PR details |
| `gh pr checks` | Check CI status |
| `gh pr merge` | Merge pull request |
| `gh run view` | Get CI run details |

## Output Examples

### Task Started (English)
```
=== Task Started ===

Issue:   LIN-456 - Implement user authentication
Status:  In Progress
Branch:  feat/LIN-456-user-auth

You can now start coding!
```

### Task Started (Chinese)
```
=== 任务已启动 ===

Issue:   LIN-456 - 实现用户认证
状态:    进行中
分支:    feat/LIN-456-user-auth

现在可以开始编码了！
```

### Task Completed (English)
```
=== Task Completed! ===

Issue:   LIN-456 - Implement user authentication
Status:  Done
PR:      #78 merged to main

Great work! Use /linear-start for your next task.
```

### Task Completed (Chinese)
```
=== 任务完成！===

Issue:   LIN-456 - 实现用户认证
状态:    已完成
PR:      #78 已合并到 main

恭喜！使用 /linear-start 开始下一个任务。
```
