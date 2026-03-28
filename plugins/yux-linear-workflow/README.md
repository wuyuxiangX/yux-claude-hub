# Linear Workflow Plugin

Complete Linear workflow integration for Claude Code with parallel development via worktrees, multi-task management, background CI monitoring, and multi-language support.

## Features

- **Issue Management**: Search existing or create new Linear issues with smart resolution
- **Parallel Development**: Work on multiple issues simultaneously using git worktrees
- **Multi-Task Management**: Track, switch between, and manage multiple in-flight tasks
- **Backlog View**: View all issues with AI-powered task recommendations
- **Branch Automation**: Auto-detect branch type from issue labels and title
- **Commit Validation**: Enforce Conventional Commits with auto-push
- **PR Creation**: Generate PRs with draft support and Linear issue linking
- **Background CI Monitoring**: Automatic CI polling after PR creation
- **Auto-Merge**: One-command merge with worktree cleanup
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

## Skills (6 total)

All functionality is provided as skills — each works as both a slash command and auto-triggers from natural language.

### Core Workflow (5 user-facing skills)

| Skill | Slash Command | Triggers On |
|-------|--------------|-------------|
| `yux-linear-start` | `/yux-linear-start` | "start task", "work on issue", "LIN-xxx" |
| `yux-linear-commit` | `/yux-linear-commit` | "commit", "save progress" |
| `yux-linear-pr` | `/yux-linear-pr` | "create PR", "submit for review" |
| `yux-linear-merge` | `/yux-linear-merge` | "merge", "complete task" |
| `yux-linear-status` | `/yux-linear-status` | "status", "tasks", "backlog", "what to work on" |

### Internal (1 skill)

| Skill | Purpose |
|-------|---------|
| `linear-merge-executor` | Forked subagent for CI polling + merge execution |

### Usage Examples

**Start a task (always creates worktree):**
```
/yux-linear-start LIN-456              # Direct issue lookup
/yux-linear-start fix login page       # Search + auto-match
/yux-linear-start                       # Interactive mode
```

**Commit + push:**
```
/yux-linear-commit                      # Auto-generate message, auto-push
/yux-linear-commit --no-push            # Skip auto-push
```

**Create PR:**
```
/yux-linear-pr                          # Standard PR
/yux-linear-pr --draft                  # Draft PR for early feedback
```

**Status hub (unified dashboard):**
```
/yux-linear-status                      # Current task + all active tasks
/yux-linear-status backlog              # View backlog with AI recommendations
/yux-linear-status backlog urgent       # Filter by priority
/yux-linear-status tasks                # Compact task list
```

**Merge + cleanup:**
```
/yux-linear-merge                       # Default squash merge
/yux-linear-merge --rebase              # Rebase merge
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
| Paused | In Progress | Task paused, working on another task |
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

1. `.claude/linear-config.json` file exists
2. `.claude/linear-tasks.json` file exists with active tasks
3. Current git branch matches `LIN-*` pattern (e.g., `feat/LIN-123-feature`)

All config file paths are resolved relative to the main repo root using `git rev-parse --git-common-dir`, ensuring correct behavior when running inside a git worktree.

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
├── skills/
│   ├── yux-linear-start/
│   │   └── SKILL.md              # Start task (worktree support)
│   ├── yux-linear-commit/
│   │   └── SKILL.md              # Commit + auto-push
│   ├── yux-linear-pr/
│   │   └── SKILL.md              # Create PR (draft support)
│   ├── yux-linear-merge/
│   │   └── SKILL.md              # Merge + cleanup
│   ├── yux-linear-status/
│   │   └── SKILL.md              # Status hub (tasks/backlog)
│   └── linear-merge-executor/
│       └── SKILL.md              # Internal merge executor (forked)
├── hooks/
│   └── hooks.json                # Hook configurations
├── scripts/
│   ├── statusline.py             # Status line script for Claude Code
│   ├── _linear_guard.py          # Shared guard (worktree + multi-task aware)
│   ├── validate_commit.py        # Commit message validator
│   ├── check_branch.py           # Branch protection check
│   ├── verify_linear_task.py     # Linear task context (multi-task display)
│   ├── sync_progress.py          # Progress sync extractor
│   ├── post_command.py           # Post-command analyzer
│   ├── prompt_linear_reminder.py # Guarded Linear workflow reminder
│   └── prompt_sync_reminder.py   # Guarded sync reminder before compaction
└── README.md                     # This file
```

## License

MIT

## Author

wuyuxiangX

## Contributing

Issues and pull requests welcome at [GitHub](https://github.com/wuyuxiangX/yux-claude-hub).
