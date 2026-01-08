# Linear Workflow Plugin

Complete Linear workflow integration for Claude Code with CI/CD monitoring and multi-language support.

## Features

- **Issue Management**: Search existing or create new Linear issues
- **Branch Automation**: Auto-generate branches following naming conventions
- **Commit Validation**: Enforce Conventional Commits format
- **PR Creation**: Generate PRs with Linear issue linking
- **CI/CD Monitoring**: Real-time status with error details
- **Auto-Merge**: One-command merge with cleanup
- **Multi-language**: Auto-detect user language (English, Chinese, Japanese, Korean)

## Installation

Add this plugin to your Claude Code settings:

```bash
claude plugin add https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/linear-workflow
```

Or manually add to `.claude/plugins.json`:

```json
{
  "plugins": [
    "https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/linear-workflow"
  ]
}
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

### `/linear-start [description]`

Start a new task with Linear integration.

```
User: /linear-start implement user authentication

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

### `/linear-pr`

Create a pull request with CI monitoring.

```
User: /linear-pr

Claude: Creating pull request...

PR #78 created: https://github.com/org/repo/pull/78
Linear LIN-456 updated to: In Review

=== CI Monitoring ===
├── ✓ lint (passed)
├── ✓ build (passed)
├── ○ test (running)
└── ○ deploy-preview (pending)
```

### `/linear-status`

Check current workflow status.

```
User: /linear-status

Claude:
=== Linear Workflow Status ===

Issue:    LIN-456 - Implement user authentication
Status:   In Review
Branch:   feat/LIN-456-user-auth

PR:       #78 - Open
CI:       All 5 checks passed

Next Step: Ready to merge! Use /linear-merge
```

### `/linear-merge`

Merge PR and complete the workflow.

```
User: /linear-merge

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

```
[Start] → [Issue] → [Branch] → [Develop] → [Commit] → [PR] → [CI Check] → [Merge] → [Done]
   │         │         │          │           │         │         │           │         │
 Verify   Search/    Auto      Status      Format    Link     Monitor      Confirm   Close
 Env      Create    Name       Sync       Validate   Issue    Status       Merge    Issue
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

## Hooks

The plugin includes hooks for:

| Hook | Event | Function |
|------|-------|----------|
| UserPromptSubmit | Prompt submit | Remind about workflow |
| PreToolUse (Write/Edit) | File modify | Verify not on main |
| PreToolUse (Bash) | Git commit | Validate commit format |
| PreCompact | Context compact | Sync progress to Linear |
| PostToolUse (Bash) | After gh commands | Update Linear status |

## File Structure

```
plugins/linear-workflow/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── .mcp.json                  # Linear MCP config
├── commands/
│   ├── linear-start.md       # Start task command
│   ├── linear-pr.md          # Create PR command
│   ├── linear-status.md      # Check status command
│   └── linear-merge.md       # Merge PR command
├── skills/
│   ├── linear-workflow/
│   │   └── SKILL.md          # Main workflow skill
│   └── ci-monitor/
│       └── SKILL.md          # CI monitoring skill
├── hooks/
│   └── hooks.json            # Hook configurations
├── templates/
│   └── messages.json         # Multi-language messages
└── README.md                 # This file
```

## Comparison with Reference Project

| Aspect | Reference (bahamoth) | This Plugin |
|--------|---------------------|-------------|
| Structure | Hooks/skills scattered | Unified in plugin dir |
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
