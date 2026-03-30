# yux-linear

Complete Linear integration for Claude Code -- from feature planning to shipped code in a single plugin.

## Overview

yux-linear provides a full lifecycle workflow: triage inbox issues, plan features with PRDs, sprint planning, worktree-isolated development, conventional commits, PR creation, and auto-merge with cleanup.

## Full Pipeline

```
pm-triage --> pm-prd --> pm-plan --> linear-start --> linear-commit
                                                        |
                                                        v
                                      linear-merge <-- linear-pr
```

**Typical flow:**

1. `linear-init` -- Initialize project (first time only)
2. `pm-triage` -- Classify and structure incoming issues
3. `pm-prd` -- Plan a feature with PRD and task breakdown
4. `pm-plan` -- Select tasks for the sprint based on capacity
5. `linear-start` -- Pick a task and begin development in an isolated worktree
6. `linear-commit` -- Commit with conventional format and sync to Linear
7. `linear-pr` -- Create a PR linked to the Linear issue
8. `linear-merge` -- Merge after CI passes, clean up worktree, mark Done

## Skills

### Setup

| Skill | Slash Command | Triggers On |
|-------|--------------|-------------|
| `yux-linear-init` | `/yux-linear-init` | "linear init", "setup linear", "初始化linear" |

### Planning

| Skill | Slash Command | Triggers On |
|-------|--------------|-------------|
| `yux-pm-triage` | `/yux-pm-triage` | "pm triage", "triage inbox", "classify issues" |
| `yux-pm-prd` | `/yux-pm-prd` | "pm prd", "create prd", "plan feature" |
| `yux-pm-plan` | `/yux-pm-plan` | "pm plan", "plan sprint", "sprint planning" |

### Development

| Skill | Slash Command | Triggers On |
|-------|--------------|-------------|
| `yux-linear-start` | `/yux-linear-start` | "start task", "work on issue", "LIN-xxx" |
| `yux-linear-commit` | `/yux-linear-commit` | "commit", "save progress" |
| `yux-linear-pr` | `/yux-linear-pr` | "create PR", "submit for review" |
| `yux-linear-merge` | `/yux-linear-merge` | "merge", "complete task" |
| `yux-linear-status` | `/yux-linear-status` | "status", "tasks", "backlog" (3 modes) |

### Internal

| Skill | Purpose |
|-------|---------|
| `linear-merge-executor` | Forked subagent for CI polling and merge execution |

## Quick Start

### 0. Initialize (first time only)

```
/yux-linear-init
```

3-step wizard: select team, bind project, choose dev mode (solo/team).

### 1. Triage incoming issues

```
/yux-pm-triage
```

AI classifies inbox items by type (bug/feature/improvement), sets priority and effort.

### 2. Plan a feature

```
/yux-pm-prd User authentication
```

Generates a PRD and creates an Epic with sub-issues in the current project.

### 3. Plan the sprint

```
/yux-pm-plan
```

Calculates capacity in business days, scores backlog items, and suggests Must/Should/Stretch categories.

### 4. Check project status

```
/yux-linear-status backlog
```

Shows project backlog with health summary, blocked/overdue counts, and AI-recommended next task.

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

Project configuration created by `/yux-linear-init`. Stores team, project binding, dev mode, and user info.

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
│   └── plugin.json               # Plugin manifest (v3.2.0)
├── .mcp.json                     # Linear MCP config
├── skills/
│   ├── yux-linear-init/          # Setup: Project initialization wizard
│   ├── yux-pm-triage/            # Planning: Inbox triage
│   ├── yux-pm-prd/               # Planning: PRD generation
│   ├── yux-pm-plan/              # Planning: Sprint planning
│   ├── yux-linear-start/         # Dev: Start task (worktree)
│   ├── yux-linear-commit/        # Dev: Commit + push
│   ├── yux-linear-pr/            # Dev: Create PR
│   ├── yux-linear-merge/         # Dev: Merge + cleanup
│   ├── yux-linear-status/        # Dev: Status dashboard (3 modes)
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
