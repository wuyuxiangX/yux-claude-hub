# yux-linear

Complete Linear integration for Claude Code -- product management and development workflow unified in a single plugin.

## Overview

yux-linear combines strategic planning (PM layer) and tactical execution (Dev layer) into one seamless workflow. The PM layer handles initiative-centric planning: triaging inbox issues, generating PRDs with cross-project task decomposition, and sprint planning with capacity-based scoping. The Dev layer handles the full development cycle: worktree-isolated task execution, conventional commits, PR creation with CI monitoring, and auto-merge with cleanup.

Together they form a continuous pipeline from idea to shipped code.

## Full Pipeline

The plugin provides a complete lifecycle across two layers:

```
PM Layer (Strategic)                    Dev Layer (Tactical)
--------------------------              ---------------------------------
pm-triage --> pm-prd --> pm-plan --> linear-start --> linear-commit
                                                        |
                                                        v
                                      linear-merge <-- linear-pr
```

**Typical flow:**

1. `pm-triage` -- Classify and structure incoming issues
2. `pm-prd` -- Decompose a feature into cross-project tasks
3. `pm-plan` -- Select tasks for the sprint based on capacity
4. `linear-start` -- Pick a task and begin development in an isolated worktree
5. `linear-commit` -- Commit with conventional format and sync to Linear
6. `linear-pr` -- Create a PR linked to the Linear issue
7. `linear-merge` -- Merge after CI passes, clean up worktree, mark Done

## Skills

### PM Skills (Strategic Planning)

| Skill | Slash Command | Triggers On |
|-------|--------------|-------------|
| `yux-pm-triage` | `/yux-pm-triage` | "pm triage", "triage inbox", "classify issues" |
| `yux-pm-prd` | `/yux-pm-prd` | "pm prd", "create prd", "decompose feature" |
| `yux-pm-plan` | `/yux-pm-plan` | "pm plan", "plan sprint", "sprint planning" |

### Setup

| Skill | Slash Command | Triggers On |
|-------|--------------|-------------|
| `yux-linear-init` | `/yux-linear-init` | "linear init", "setup linear", "初始化linear" |

### Dev Skills (Tactical Execution)

| Skill | Slash Command | Triggers On |
|-------|--------------|-------------|
| `yux-linear-start` | `/yux-linear-start` | "start task", "work on issue", "LIN-xxx" |
| `yux-linear-commit` | `/yux-linear-commit` | "commit", "save progress" |
| `yux-linear-pr` | `/yux-linear-pr` | "create PR", "submit for review" |
| `yux-linear-merge` | `/yux-linear-merge` | "merge", "complete task" |
| `yux-linear-status` | `/yux-linear-status` | "status", "tasks", "backlog", "what to work on", "pm overview", "pm dashboard", "initiative status" (4 modes: default/backlog/tasks/pm) |

### Internal

| Skill | Purpose |
|-------|---------|
| `linear-merge-executor` | Forked subagent for CI polling and merge execution |

## Quick Start

### 0. Initialize (first time only)

```
/yux-linear-init
```

Step-by-step wizard that connects your repo to Linear: select team, bind project, choose dev mode (solo/team), and optionally enable PM features (Initiative management).

### 1. Triage incoming issues

```
/yux-pm-triage
```

AI classifies inbox items by type (bug/feature/improvement), assigns to sub-projects, and sets priority and effort. Requires PM features enabled via `/yux-linear-init`.

### 2. Create a feature with PRD

```
/yux-pm-prd User authentication
```

Generates a PRD and decomposes the feature into tasks across relevant sub-projects (e.g., api + web + extension).

### 3. Plan the sprint

```
/yux-pm-plan
```

Calculates capacity in business days, scores backlog items, and suggests Must/Should/Stretch categories.

### 4. Check PM status

```
/yux-linear-status pm
```

Displays the initiative dashboard with health score, sprint progress, project breakdown, and attention items.

### 5. Start development

```
/yux-linear-start LIN-456
```

Creates an isolated worktree, checks out a branch, and sets the Linear issue to In Progress.

### 6. Commit and push

```
/yux-linear-commit
```

Auto-generates a conventional commit message, pushes to remote, and syncs progress to Linear.

### 7. Create PR

```
/yux-linear-pr
```

Generates a PR with Linear issue linking and updates the issue status to In Review.

### 8. Merge and complete

```
/yux-linear-merge
```

Validates CI, merges (squash by default), cleans up the worktree, and marks the Linear issue as Done.

## Configuration

The plugin uses two configuration files, stored in `.claude/`:

### linear-config.json

Unified project configuration created by `/yux-linear-init`. Stores team, project binding, dev mode, user info, and optional PM settings.

```json
{
  "version": "1.0.0",
  "created_at": "2026-03-30T10:00:00Z",
  "team": {
    "id": "uuid",
    "name": "Wyx"
  },
  "project": {
    "id": "uuid",
    "name": "Subloom"
  },
  "mode": "solo",
  "user": {
    "id": "uuid",
    "name": "吾宇翔"
  },
  "pm": {
    "enabled": true,
    "initiative": {
      "id": "uuid",
      "name": "Product Launch"
    },
    "projects": [
      { "id": "uuid", "name": "subloom-api", "tech": "Go/Backend" },
      { "id": "uuid", "name": "subloom-web", "tech": "Next.js/Frontend" }
    ]
  }
}
```

### linear-tasks.json

Tracks active in-flight tasks for multi-task management. Managed automatically by the plugin.

## Effort Estimation

The plugin uses T-shirt sizing for task estimation:

| Size | Duration | Example |
|------|----------|---------|
| XS | < 2 hours | Config change, typo fix |
| S | 2-8 hours | Small bug, minor feature |
| M | 1-3 days | Medium feature, complex bug |
| L | 3-7 days | Large feature, refactoring |
| XL | > 1 week | Epic-level work |

## Prerequisites

1. **Linear MCP Server** -- Configure Linear OAuth via the `/mcp` command in Claude Code
2. **GitHub CLI** -- Install (`brew install gh`) and authenticate (`gh auth login`)
3. **Git repository** -- Must be run inside a git repo
4. **Project initialization** -- Run `/yux-linear-init` once per repository

## Language Support

- All plugin code and skill definitions are in English
- Runtime output language is auto-detected from user input
- Supported languages: English, Chinese, Japanese, Korean

## File Structure

```
plugins/yux-linear/
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest (v3.1.0)
├── .mcp.json                     # Linear MCP config
├── skills/
│   ├── yux-linear-init/          # Setup: Project initialization wizard
│   ├── yux-pm-triage/            # PM: Inbox triage
│   ├── yux-pm-prd/               # PM: PRD generation
│   ├── yux-pm-plan/              # PM: Sprint planning
│   ├── yux-linear-start/         # Dev: Start task (worktree)
│   ├── yux-linear-commit/        # Dev: Commit + push
│   ├── yux-linear-pr/            # Dev: Create PR
│   ├── yux-linear-merge/         # Dev: Merge + cleanup
│   ├── yux-linear-status/        # Dev: Status + PM dashboard (4 modes)
│   └── linear-merge-executor/    # Internal: CI poll + merge
├── hooks/
│   └── hooks.json                # Hook configurations
├── scripts/
│   ├── _linear_guard.py          # Shared activation guard
│   ├── statusline.py             # Status line for Claude Code
│   ├── validate_commit.py        # Commit message validator
│   ├── check_branch.py           # Branch protection check
│   ├── verify_linear_task.py     # Linear task context
│   ├── sync_progress.py          # Progress sync extractor
│   ├── post_command.py           # Post-command analyzer
│   ├── prompt_linear_reminder.py # Workflow reminder
│   └── prompt_sync_reminder.py   # Sync reminder before compaction
├── references/
│   └── prd-template.md           # PRD template
└── README.md
```

## License

MIT
