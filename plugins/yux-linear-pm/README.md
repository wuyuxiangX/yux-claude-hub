# yux-linear-pm

Product Manager workflow plugin for Linear. Initiative-centric planning with automatic task decomposition across sub-projects.

## Features

- **Initiative-centric**: Work at Initiative level (e.g., Subloom), auto-distribute tasks to sub-projects
- **Smart decomposition**: "Login feature" → creates issues in api + web + extension automatically
- **AI-powered triage**: Classify inbox items by type, priority, and relevant projects
- **Sprint planning**: Capacity calculation and AI-suggested scope
- **PRD generation**: Full PRDs for complex features with cross-project breakdown

## Commands

| Command | Description |
|---------|-------------|
| `/yux-pm-init` | Initialize workspace - select Initiative, configure sub-projects |
| `/yux-pm-overview` | Dashboard view - progress, status, alerts |
| `/yux-pm-triage` | Process inbox - classify, assign projects, set priority |
| `/yux-pm-plan` | Sprint planning - capacity, scope, assign to cycle |
| `/yux-pm-prd [topic]` | Generate PRD with cross-project task decomposition |

## Quick Start

1. **Initialize your workspace**:
   ```
   /yux-pm-init
   ```
   Select your Initiative (e.g., "Subloom") and configure sub-projects.

2. **Check status**:
   ```
   /yux-pm-overview
   ```
   View dashboard with health score, sprint progress, and alerts.

3. **Process feedback**:
   ```
   /yux-pm-triage
   ```
   AI classifies and structures inbox items.

4. **Plan your sprint**:
   ```
   /yux-pm-plan
   ```
   Get AI-suggested scope based on capacity and priorities.

5. **Create new features**:
   ```
   /yux-pm-prd User authentication
   ```
   Generates PRD and creates decomposed tasks across relevant projects.

## Initiative Structure

This plugin is designed for projects organized under Initiatives in Linear:

```
Initiative: Subloom
├── subloom-api (Go/Backend)
├── subloom-web (Next.js/Frontend)
├── subloom-extension (React/Extension)
├── subloom-ml (Python/ML)
└── subloom-obsidian (Obsidian Plugin)
```

When you create a feature, the plugin automatically identifies which sub-projects are affected and creates linked issues in each.

## Configuration

After running `/yux-pm-init`, configuration is saved to `.claude/pm-config.json`:

```json
{
  "initiative": {
    "id": "uuid",
    "name": "Subloom"
  },
  "projects": [
    {"id": "uuid", "name": "subloom-api", "tech": "Go/Backend"},
    {"id": "uuid", "name": "subloom-web", "tech": "Next.js/Frontend"}
  ],
  "team_id": "uuid",
  "team_name": "Wyx",
  "created_at": "2026-01-10T...",
  "version": "1.0.0"
}
```

## Language Support

- All code and files are in English
- Runtime output follows `.claude/yux-config.json` language setting
- Supports English (`en`) and Chinese (`zh`)

## Prerequisites

- Linear MCP configured (see `.mcp.json`)
- Linear workspace access
- yux-core plugin for language configuration

## Integration

Works with `yux-linear-workflow` for the full development cycle:

1. `/yux-pm-triage` → Process feedback
2. `/yux-pm-prd` → Create feature with decomposed tasks
3. `/yux-pm-plan` → Add to sprint
4. `/yux-linear-start` → Begin development (from yux-linear-workflow)
5. `/yux-linear-pr` → Create PR when done

## Effort Estimation

The plugin uses T-shirt sizing:

| Size | Duration | Example |
|------|----------|---------|
| XS | < 2 hours | Config change, typo fix |
| S | 2-8 hours | Small bug, minor feature |
| M | 1-3 days | Medium feature, complex bug |
| L | 3-7 days | Large feature, refactoring |
| XL | > 1 week | Epic-level work |

## License

MIT
