# PM Init Flow

Auto-initialization flow for PM workspace. Triggered when a PM skill detects that `.claude/pm-config.json` is missing.

## Step 1: Verify Linear Connection

Call `mcp__linear__list_teams()`. If it fails, stop and instruct the user to configure Linear MCP in `.mcp.json`.

## Step 2: Fetch Projects and Group by Initiative

```
mcp__linear__list_projects(team: "<team-id>", limit: 100)
```

Parse results:
- Group projects by their `initiatives` field.
- Identify standalone projects (no initiative).

## Step 3: Initiative Selection

Present numbered list of Initiatives with project counts. Include a "Standalone Projects" option for ungrouped projects.

If user selects an Initiative, proceed with all its projects. If user selects Standalone, let them multi-select which projects to include (treated as a virtual Initiative).

If no Initiatives exist, inform the user they can create one in Linear or select Standalone.

## Step 4: Tech Stack Detection

For each project in the selected Initiative, detect tech stack from the project description:
- Keywords: "Go", "Python", "TypeScript", "React", "Next.js", "Swift", "Kotlin", etc.
- Categorize as: Backend, Frontend, Extension, ML, Mobile, etc.
- If a project description is empty, use AskUserQuestion to ask the user to specify its tech stack (or accept "Unknown").

## Step 5: Save Configuration

If `.claude/pm-config.json` already exists, use AskUserQuestion: "keep" = exit without changes, "overwrite" = re-run the entire init flow.

Write `.claude/pm-config.json` with this schema:

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
    }
  ],
  "team_id": "<team-uuid>",
  "team_name": "<Team Name>",
  "created_at": "<ISO timestamp>",
  "version": "1.0.0"
}
```

## Step 6: Confirm

Display the saved configuration summary:

```
=== PM Workspace Initialized ===

Initiative:  Product Launch v2
Team:        Engineering
Config:      .claude/pm-config.json

Projects:
  subloom-api       Go/Backend
  subloom-web       TypeScript/Frontend
  subloom-ext       TypeScript/Extension
```
