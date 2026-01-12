---
description: Initialize PM workspace and configure projects
---

# PM Init - Initialize PM Workspace

Initialize the PM workspace by selecting an Initiative and configuring sub-projects.

**Usage**: `/yux-pm-init`

## Prerequisites

1. Linear MCP must be configured and accessible
2. User must have access to Linear workspace

## Workflow

### Step 1: Verify Linear Connection

```
mcp__linear__list_teams()
```

If this fails, stop immediately:
```
Error: Linear connection failed.

Please ensure:
1. Linear MCP is configured in .mcp.json
2. You have authenticated with Linear

Run /yux-linear-setup to configure Linear.
```

### Step 2: Fetch Projects and Group by Initiative

```
mcp__linear__list_projects(team: "<team-id>", limit: 100)
```

Parse the results to:
1. Group projects by their `initiatives` field
2. Identify projects without an initiative (standalone projects)

### Step 3: Display Initiative Selection

> Output language follows `.claude/yux-config.json` setting

```
=== PM Workspace Setup ===

Select an Initiative to work with:

Initiatives:
  1. Subloom (5 projects)
     - subloom-api, subloom-web, subloom-extension, subloom-ml, subloom-obsidian

  2. (Standalone Projects)
     - Anvil, MediaFlow, PomoPal, Blog, Second Me, Feedback, Fitness

Enter choice (1-2):
```

### Step 4: Configure Selected Initiative

When user selects an Initiative:

1. Fetch all projects under that Initiative
2. For each project, detect its tech stack from the description:
   - Look for keywords: "Go", "Python", "TypeScript", "React", "Next.js", etc.
   - Categorize as: Backend, Frontend, Extension, ML, Mobile, etc.

When user selects "Standalone Projects":
1. Let user multi-select which projects to include
2. Treat them as a virtual Initiative

### Step 5: Save Configuration

Create `.claude/pm-config.json`:

```json
{
  "initiative": {
    "id": "<initiative-uuid or 'standalone'>",
    "name": "<Initiative Name>"
  },
  "projects": [
    {
      "id": "<project-uuid>",
      "name": "subloom-api",
      "tech": "Go/Backend",
      "description": "Backend API service"
    },
    {
      "id": "<project-uuid>",
      "name": "subloom-web",
      "tech": "Next.js/Frontend",
      "description": "Web application"
    }
  ],
  "team_id": "<team-uuid>",
  "team_name": "<Team Name>",
  "created_at": "<ISO timestamp>",
  "version": "1.0.0"
}
```

### Step 6: Output Summary

> Output language follows `.claude/yux-config.json` setting

```
=== PM Workspace Initialized ===

Initiative: Subloom
Team: Wyx

Sub-projects:
  - subloom-api (Go/Backend)
  - subloom-web (Next.js/Frontend)
  - subloom-extension (React/Extension)
  - subloom-ml (Python/ML)

Config saved to: .claude/pm-config.json

Next steps:
  /yux-pm-overview  - View project status
  /yux-pm-triage    - Process inbox issues
  /yux-pm-plan      - Plan next sprint
```

## Error Handling

### No Initiatives Found
```
No Initiatives found in your Linear workspace.

You can:
1. Create an Initiative in Linear to group related projects
2. Select "Standalone Projects" to work with individual projects
```

### No Projects Found
```
No projects found in your Linear workspace.

Please create at least one project in Linear before using this plugin.
```

### Config Already Exists
```
PM workspace already configured:
  Initiative: Subloom
  Projects: 4

What would you like to do?
1. Keep current config
2. Reconfigure (overwrite)
```

## Example

```
User: /yux-pm-init

Claude: === PM Workspace Setup ===

Select an Initiative to work with:

Initiatives:
  1. Subloom (5 projects)
  2. (Standalone Projects - 7 projects)

Enter choice: 1

Analyzing Subloom projects...

=== PM Workspace Initialized ===

Initiative: Subloom
Sub-projects:
  - subloom-api (Go/Backend)
  - subloom-web (Next.js/Frontend)
  - subloom-extension (React/Extension)
  - subloom-ml (Python/ML)

Config saved to: .claude/pm-config.json
Run /yux-pm-overview to see project status.
```
