---
name: yux-linear-init
description: Initialize Linear integration for current project. Triggers on "linear init", "初始化linear", "setup linear", "configure linear", "连接linear".
user-invocable: true
allowed-tools: Read, Write, Bash(git:*), Glob, Grep, mcp__linear__*, AskUserQuestion
---

# Linear Init - Project Setup Wizard

Step-by-step initialization wizard that binds the current git repository to a Linear team and project. Creates `.claude/linear-config.json` with all necessary configuration.

**Usage**: `/yux-linear-init`

## Prerequisites

1. **Linear MCP**: Must be configured in Claude Code
2. **Git repo**: Must be inside a git repository

## Workflow

### Step 1: Verify Connection

```
mcp__linear__list_teams()
mcp__linear__get_authenticated_user()
```

If `list_teams` fails: show error and stop.
```
Linear MCP is not connected. Please configure it first:
  1. Run /mcp in Claude Code
  2. Add Linear MCP server
  3. Complete OAuth authentication
  4. Then run /yux-linear-init again
```

Greet the user with their name from `get_authenticated_user`.

### Step 2: Select Team

- **Single team**: Auto-select and inform user.
- **Multiple teams**: Display numbered list, let user choose.

```
Step 1/5 — Team

Detected team: Wyx
Using team "Wyx" automatically.
```

### Step 3: Bind Project

```
mcp__linear__list_projects(team: "<team-id>", includeArchived: false)
```

Display numbered list with project name and summary:

```
Step 2/5 — Project

Which Linear project does this repository belong to?

  1. Subloom         — 对话式个人收藏平台
  2. Slideck         — React presentation framework
  3. Claude Code Monitor — Raycast extension for monitoring
  4. Anvil           — 统一服务的基石
  5. Blog            — 个人博客和管理相关项目
  ...

Enter the number of your project:
```

Use AskUserQuestion to let user select.

### Step 4: Development Mode

Use AskUserQuestion to ask:

```
Step 3/5 — Development Mode

How do you work on this project?

  1. Solo — Issues auto-assigned to me
  2. Team — Keep manual assignee selection
```

- `solo`: Save user info, future `/yux-linear-start` auto-assigns to self
- `team`: No auto-assignment

### Step 5: PM Setup (Optional)

Use AskUserQuestion to ask:

```
Step 4/5 — PM Features (Optional)

Enable PM features? (Initiative management, sprint planning, cross-project triage)

  1. Yes — Set up Initiative and multi-project management
  2. No  — Skip, I only need dev workflow
```

**If Yes:**

1. Fetch initiatives:
   ```
   mcp__linear__list_initiatives()
   ```

2. If initiatives exist, display numbered list for selection. If none, inform user and set `pm.enabled: false`.

3. For the selected initiative, fetch its associated projects:
   ```
   mcp__linear__list_projects(initiative: "<initiative-id>")
   ```

4. For each project, detect tech stack from project description:
   - Keywords: "Go", "Python", "TypeScript", "React", "Next.js", "Swift", "Kotlin", etc.
   - Categorize as: Backend, Frontend, Extension, ML, Mobile, etc.
   - If description is empty, use AskUserQuestion to ask user for tech stack (or accept "Unknown").

5. Save to `pm` field in config.

**If No:** Set `pm: { "enabled": false }`.

### Step 6: Save & Confirm

1. If `.claude/linear-config.json` already exists, use AskUserQuestion:
   - "Overwrite" = proceed with new config
   - "Keep" = exit without changes

2. Ensure `.claude/` directory exists.

3. Write `.claude/linear-config.json`:

```json
{
  "version": "1.0.0",
  "created_at": "<ISO timestamp>",
  "team": {
    "id": "<team-uuid>",
    "name": "<Team Name>"
  },
  "project": {
    "id": "<project-uuid>",
    "name": "<Project Name>"
  },
  "mode": "solo",
  "user": {
    "id": "<user-uuid>",
    "name": "<User Name>"
  },
  "pm": {
    "enabled": true,
    "initiative": {
      "id": "<initiative-uuid>",
      "name": "<Initiative Name>"
    },
    "projects": [
      { "id": "<uuid>", "name": "subloom-api", "tech": "Go/Backend" },
      { "id": "<uuid>", "name": "subloom-web", "tech": "Next.js/Frontend" }
    ]
  }
}
```

4. Display confirmation:

```
=== Linear Initialized ===

User:       吾宇翔
Team:       Wyx
Project:    Subloom
Mode:       Solo
PM:         Enabled (Initiative: Product Launch)
Config:     .claude/linear-config.json

Next steps:
  /yux-linear-status backlog   View project backlog
  /yux-linear-start LIN-xxx   Start a task
  /yux-linear-status pm        PM dashboard (if PM enabled)
```

## Re-initialization

Running `/yux-linear-init` on a project that already has config will prompt to overwrite or keep existing configuration. This allows changing project binding or enabling/disabling PM features.

## Multi-language Support

Output language is auto-detected from user input. Default to English.
