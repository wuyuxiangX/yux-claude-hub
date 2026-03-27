# Linear Workflow Plugin

Complete Linear workflow integration for Claude Code with CI/CD monitoring and multi-language support.

## Features

- **Issue Management**: Search existing or create new Linear issues
- **Backlog View**: View all issues with AI-powered task recommendations
- **Branch Automation**: Auto-generate branches following naming conventions
- **Commit Validation**: Enforce Conventional Commits format (code-based hooks)
- **PR Creation**: Generate PRs with Linear issue linking
- **CI/CD Monitoring**: Real-time status with error details
- **Auto-Merge**: One-command merge with cleanup
- **Multi-language**: Auto-detect user language (English, Chinese, Japanese, Korean)

## Installation

1. Add the marketplace:

```bash
claude plugin marketplace add https://github.com/wuyuxiangX/yux-claude-hub
```

2. Install the plugin:

```bash
claude plugin install yux-linear-workflow
```
```

## Prerequisites

1. **Linear MCP Server**: Configure Linear OAuth
   ```bash
   # In Claude Code
   /mcp
   # Add Linear MCP server
   ```

2. **GitHub CLI**: Install and authenticate
   ```bash
   brew install gh
   gh auth login
   ```

3. **Git Repository**: Must be inside a git repo

## Commands

### `/yux-linear-start [description]`

Start a new task with Linear integration.

```
User: /yux-linear-start implement user authentication

Claude: Starting Linear workflow...

How would you like to proceed?
1. Search existing Linear issues
2. Create a new issue

User: 2

Claude: Creating issue...
Issue LIN-456 created: Implement user authentication
Branch created: feat/LIN-456-user-auth
Status updated: In Progress

=== Task Started ===
Issue:   LIN-456 - Implement user authentication
Branch:  feat/LIN-456-user-auth

You can now start coding!
```

### `/yux-linear-commit [description]`

Stage commit with file selection and Linear sync.

```
User: /yux-linear-commit

Claude:
=== 当前变更 ===

📁 新增文件 (1):
   [1] src/components/LoginForm.tsx

📝 修改文件 (2):
   [2] src/App.tsx
   [3] src/routes/index.ts

请选择要提交的文件：
1. 提交所有变更 (3 个文件)
2. 选择特定文件
3. 排除特定文件
4. 取消

User: 1

Claude:
生成的提交信息：
feat(auth): add LoginForm component with routing integration

确认？(y/修改/n)

User: y

Claude:
✓ 已提交 3 个文件
✓ 已同步到 Linear: LIN-456

=== 提交完成 ===
提交哈希: a1b2c3d
关联 Issue: LIN-456
```

**Features**:
- Display changed files by category (new/modified/deleted)
- User selects which files to commit (not automatic)
- Auto-generate commit message (user input is reference only)
- **Mandatory** sync to Linear issue

### `/yux-linear-pr`

Create a pull request with CI monitoring.

```
User: /yux-linear-pr

Claude: Creating pull request...

PR #78 created: https://github.com/org/repo/pull/78
Linear LIN-456 updated to: In Review

=== CI Monitoring ===
├── ✓ lint (passed)
├── ✓ build (passed)
├── ○ test (running)
└── ○ deploy-preview (pending)
```

### `/yux-linear-status`

Check current workflow status.

```
User: /yux-linear-status

Claude:
=== Linear Workflow Status ===

Issue:    LIN-456 - Implement user authentication
Status:   In Review
Branch:   feat/LIN-456-user-auth

PR:       #78 - Open
CI:       All 5 checks passed

Next Step: Ready to merge! Use /yux-linear-merge
```

### `/yux-linear-backlog [filter]`

View project issues with AI-powered recommendations.

**Filters**: `all` (default), `mine`, `urgent`, `unassigned`

```
User: /yux-linear-backlog

Claude:
=== Linear Backlog (Wyx Team) ===

| # | ID      | Title                    | Priority | Status  | Due     |
|---|---------|--------------------------|----------|---------|---------|
| 1 | LIN-789 | Fix login page crash     | High     | Todo    | Jan 8   |
| 2 | LIN-456 | Implement user auth      | Medium   | Backlog | Jan 10  |
| 3 | LIN-234 | Refactor API endpoints   | Low      | Todo    | Jan 15  |

Total: 3 issues

=== Recommended Next Task ===

[LIN-789] Fix login page crash
Priority: High | Due: Tomorrow | Status: Todo
Reason: High priority bug with imminent deadline

-> Use `/yux-linear-start LIN-789` to begin
```

### `/yux-linear-merge`

Merge PR and complete the workflow.

```
User: /yux-linear-merge

Claude: Checking merge readiness...

All checks passed.
Ready to merge?

User: Y

Claude:
PR #78 merged to main
Branch feat/LIN-456-user-auth deleted
Linear LIN-456 marked as Done

=== Task Completed! ===
Duration: 5h 15m
```

## Complete Workflow

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Linear Workflow Plugin                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│   │ Backlog  │───▶│  Start   │───▶│  PR      │───▶│  Merge   │            │
│   │ /backlog │    │  /start  │    │  /pr     │    │  /merge  │            │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘            │
│        │               │               │               │                   │
│        ▼               ▼               ▼               ▼                   │
│   ┌─────────────────────────────────────────────────────────────────┐     │
│   │                        Hooks Layer (Python)                      │     │
│   │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │     │
│   │  │check_branch│ │validate_   │ │sync_       │ │post_       │   │     │
│   │  │    .py     │ │commit.py   │ │progress.py │ │command.py  │   │     │
│   │  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │     │
│   └─────────────────────────────────────────────────────────────────┘     │
│                                    │                                       │
│                                    ▼                                       │
│   ┌─────────────────────────────────────────────────────────────────┐     │
│   │                      Linear MCP + GitHub CLI                     │     │
│   └─────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: View Backlog (`/yux-linear-backlog`)

```
┌───────────────────────────────────────┐
│         Load Team Config              │
│  .claude/linear-config.json           │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│      mcp: list_issues(team)           │
│  Fetch all non-completed issues       │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│         AI Recommendation             │
│  Score by: priority + deadline +      │
│  sprint + status + labels             │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│         Display Results               │
│  Table + Top recommendation           │
└───────────────────────────────────────┘
```

### Phase 2: Start Task (`/yux-linear-start`)

```
┌───────────────────────────────────────┐
│         Team Discovery                │
│  1. Check .claude/linear-config.json  │
│  2. Or: mcp: list_teams()             │
│  3. Auto-select or ask user           │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│         Issue Selection               │
│  1. Search existing issues            │
│  2. Create new issue                  │
└───────────────────┬───────────────────┘
                    │
       ┌────────────┴────────────┐
       ▼                         ▼
┌─────────────┐           ┌─────────────┐
│ mcp: list_  │           │ mcp: create │
│ issues()    │           │ Issue()     │
└──────┬──────┘           └──────┬──────┘
       └────────────┬────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│         Create Branch                 │
│  git checkout -b feat/LIN-xxx-desc    │
│  git push -u origin <branch>          │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│         Update Linear                 │
│  mcp: updateIssue → In Progress       │
│  mcp: createComment → Branch info     │
└───────────────────────────────────────┘
```

### Phase 3: Development & Commit (`/yux-linear-commit`)

```
┌───────────────────────────────────────┐
│           Write/Edit Files            │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│    Hook: check_branch.py              │
│                                       │
│  if branch == 'main':                 │
│      ⚠️ WARNING: On main branch       │
│  else:                                │
│      ✓ Working on LIN-xxx             │
└───────────────────┬───────────────────┘
                    │ exit 0 (allow)
                    ▼
┌───────────────────────────────────────┐
│       /yux-linear-commit              │
│                                       │
│  1. Show changed files by category    │
│  2. User selects files to commit      │
│  3. Auto-generate commit message      │
│  4. git add + git commit              │
│  5. Sync to Linear (mandatory)        │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│    Hook: validate_commit.py           │
│                                       │
│  ✓ feat(auth): add login API          │
│  ✗ "fix bug" → exit 2 (BLOCKED)       │
└───────────────────────────────────────┘
```

### Phase 4: Create PR (`/yux-linear-pr`)

```
┌───────────────────────────────────────┐
│         Generate PR Content           │
│  Title: [LIN-xxx] Issue Title         │
│  Body: Summary + Test Plan            │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│  gh pr create --title "..." --body ...│
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│    Hook: post_command.py              │
│                                       │
│  Detected: gh pr create               │
│  → Remind: Update Linear to In Review │
│  → Suggest: Monitor CI with /status   │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│         CI Monitoring                 │
│  gh pr checks → Real-time status      │
│  ├── ✓ lint (passed)                  │
│  ├── ✓ build (passed)                 │
│  ├── ○ test (running)                 │
│  └── ○ deploy (pending)               │
└───────────────────────────────────────┘
```

### Phase 5: Merge & Complete (`/yux-linear-merge`)

```
┌───────────────────────────────────────┐
│         Check Merge Readiness         │
│  - All CI checks passed?              │
│  - Reviews approved?                  │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│  gh pr merge --squash --delete-branch │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│    Hook: post_command.py              │
│                                       │
│  Detected: gh pr merge                │
│  → Remind: Update Linear to Done      │
│  → Suggest: Delete local branch       │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│         Complete Cleanup              │
│  - git checkout main                  │
│  - git pull origin main               │
│  - git branch -d <branch>             │
│  - mcp: updateIssue → Done            │
│  - mcp: createComment → Completed     │
└───────────────────────────────────────┘
```

### Linear Status Flow

```
┌─────────┐    ┌─────────┐    ┌───────────┐    ┌───────────┐    ┌──────┐
│ Backlog │───▶│  Todo   │───▶│In Progress│───▶│ In Review │───▶│ Done │
└─────────┘    └─────────┘    └───────────┘    └───────────┘    └──────┘
     │              │              │                 │              │
  Issue          Branch          Start             PR            Merge
  Created        Created        Coding           Created        Completed
                                                     │
                                                     ▼
                                              ┌───────────┐
                                              │ CI Failed │
                                              │ → Back to │
                                              │In Progress│
                                              └───────────┘
```

### Data Persistence

All key information is written to Linear issue comments:

```markdown
# Issue LIN-456 Comment History

[Auto] Started working on this issue.
Branch: `feat/LIN-456-user-auth`

[Auto] PR created: https://github.com/org/repo/pull/78
CI Status: All checks passed

[Auto] Merged to main.
Duration: 3h 25m
Commits: 5
```

### Workflow States

| Stage | Linear Status | Description |
|-------|---------------|-------------|
| Issue Created | Backlog | New issue, no branch |
| Branch Created | Todo | Ready to start |
| In Development | In Progress | Active coding |
| PR Created | In Review | Awaiting review |
| CI Failed | In Progress | Needs fix |
| Ready to Merge | In Review | All checks passed |
| Merged | Done | Task complete |

## Branch Naming

Format: `<type>/LIN-<id>-<description>`

| Type | Use Case |
|------|----------|
| `feat` | New features |
| `fix` | Bug fixes |
| `docs` | Documentation |
| `refactor` | Code refactoring |
| `test` | Tests |
| `chore` | Maintenance |

Examples:
- `feat/LIN-123-user-auth`
- `fix/LIN-456-login-bug`
- `docs/LIN-789-api-docs`

## Commit Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

Refs: LIN-xxx
```

Examples:
- `feat(auth): add JWT token validation`
- `fix(ui): correct button alignment`
- `docs(api): update endpoint documentation`

## CI/CD Monitoring

When CI fails, the plugin shows detailed error information:

```
=== CI Status (Failed) ===

├── ✓ lint (passed)
├── ✓ build (passed)
├── ✗ test (failed)
└── ⊘ deploy-preview (skipped)

┌─────────────────────────────────────┐
│ Error Details                        │
├─────────────────────────────────────┤
│ FAIL src/auth/login.test.ts         │
│                                      │
│ ● login › should return token        │
│   Expected: "valid-token"            │
│   Received: undefined                │
│                                      │
│   at src/auth/login.test.ts:25:18   │
└─────────────────────────────────────┘

Suggestion: Check the return value in login function.
```

## Multi-language Support

The plugin automatically detects user language:

- **English**: Default
- **Chinese**: 中文支持
- **Japanese**: 日本語サポート
- **Korean**: 한국어 지원

Language is detected from user input and applied to all messages.

## Configuration

### Environment Variables

Set in `.claude/settings.json`:

```json
{
  "env": {
    "LINEAR_TEAM": "your-team-id",
    "LINEAR_PROJECT": "your-project-id"
  }
}
```

### Linear MCP

The plugin uses Linear MCP for API access. Configure via `/mcp` command.

## Project-Level Activation Guard

All hooks include a project-level guard that prevents them from interfering with non-Linear projects. A project is considered "Linear-active" if **any** of the following conditions are met:

1. `.claude/linear-tasks/` directory exists
2. `.claude/linear-config.json` file exists
3. Current git branch matches `LIN-*` pattern (e.g., `feat/LIN-123-feature`)

When none of these conditions are met, all hooks silently pass (`exit 0`) — no warnings, no commit blocking, no prompt injection.

This guard is implemented in `scripts/_linear_guard.py` and imported by every hook script.

## Hooks

The plugin uses **code-based hooks** (Python scripts) for reliable, deterministic validation:

| Hook | Event | Script | Function |
|------|-------|--------|----------|
| UserPromptSubmit | Prompt submit | (prompt) | Remind about workflow |
| PreToolUse (Write/Edit) | File modify | `check_branch.py` | Warn if on main branch |
| PreToolUse (Bash) | Git commit | `validate_commit.py` | **Block** invalid commit format |
| PreCompact | Context compact | `sync_progress.py` | Extract progress for Linear |
| PostToolUse (Bash) | After gh commands | `post_command.py` | Detect PR/merge, suggest updates |

### Hook Exit Codes

| Exit Code | Behavior |
|-----------|----------|
| `0` | Allow operation |
| `2` | **Block operation**, show error to Claude |

### Hook Scripts

```python
# Example: validate_commit.py blocks invalid commits
if not re.match(COMMIT_PATTERN, message):
    print("❌ Invalid commit format", file=sys.stderr)
    sys.exit(2)  # Blocks the git commit
```

## File Structure

```
plugins/yux-linear-workflow/
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest
├── .mcp.json                     # Linear MCP config
├── commands/
│   ├── yux-linear-start.md       # Start task command
│   ├── yux-linear-commit.md      # Stage commit command
│   ├── yux-linear-backlog.md     # View & recommend issues
│   ├── yux-linear-pr.md          # Create PR command
│   ├── yux-linear-status.md      # Check status command
│   └── yux-linear-merge.md       # Merge PR command
├── skills/
│   ├── yux-linear-workflow/
│   │   └── SKILL.md              # Main workflow skill
│   └── yux-ci-monitor/
│       └── SKILL.md              # CI monitoring skill
├── hooks/
│   └── hooks.json                # Hook configurations
├── scripts/
│   ├── _linear_guard.py          # Shared project-level activation guard
│   ├── validate_commit.py        # Commit message validator
│   ├── check_branch.py           # Branch protection check
│   ├── verify_linear_task.py     # Linear task context detector
│   ├── sync_progress.py          # Progress sync extractor
│   ├── post_command.py           # Post-command analyzer
│   ├── prompt_linear_reminder.py # Guarded Linear workflow reminder
│   └── prompt_sync_reminder.py   # Guarded sync reminder before compaction
├── templates/
│   └── messages.json             # Multi-language messages
└── README.md                     # This file
```

## Comparison with Reference Project

| Aspect | Reference (bahamoth) | This Plugin |
|--------|---------------------|-------------|
| Structure | Hooks/skills scattered | Unified in plugin dir |
| Hook Implementation | Python scripts | **Python scripts** (code-based) |
| Commands | None | 4 dedicated commands |
| CI/CD | None | Full monitoring + errors |
| Completion | PR creation | After merge |
| Multi-language | None | Auto-detect |

## License

MIT

## Author

wuyuxiangX

## Contributing

Issues and pull requests welcome at [GitHub](https://github.com/wuyuxiangX/yux-claude-hub).
