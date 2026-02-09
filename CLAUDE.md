# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

yux-claude-hub is a Claude Code plugin marketplace containing custom skills, commands, and extensions. This is a **content-only repository** with no build system, tests, or runtime code - it consists entirely of markdown files and JSON configurations that Claude Code interprets.

## Architecture

### Plugin Structure

Each plugin lives in `plugins/<plugin-name>/` with this structure:
```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, description)
├── commands/
│   └── <command>.md         # Slash command definitions
├── skills/
│   └── <skill-name>/
│       └── SKILL.md         # Skill definition with triggers and instructions
└── README.md                # Plugin documentation
```

### Key Components

- **Skills** (`SKILL.md`): Auto-triggered modules. The frontmatter defines:
  - `name`: Skill identifier
  - `description`: Trigger keywords that activate the skill
  - `allowed-tools`: Tools the skill can use

- **Commands** (`.md` files in `commands/`): Slash commands users invoke explicitly (e.g., `/yux-video-to-blog`)

- **Marketplace** (`.claude-plugin/marketplace.json`): Root-level registry listing all available plugins

## Current Plugins

| Plugin | Purpose |
|--------|---------|
| `yux-core` | Core configuration management for all yux plugins |
| `yux-video-to-blog` | Video-to-article pipeline: subtitles → summary → blog |
| `yux-linear-workflow` | Linear integration with branch automation and CI monitoring |
| `yux-nano-banana` | Image generation via OpenRouter API with Gemini models |

## Adding a New Plugin

1. Create `plugins/<name>/` directory
2. Add `.claude-plugin/plugin.json` with manifest
3. Add skills in `skills/<skill-name>/SKILL.md`
4. Add commands in `commands/<command>.md`
5. Create `README.md` with detailed documentation
6. Register in root `.claude-plugin/marketplace.json`

## Conventions

- All SKILL.md content must be in English
- Skills must include clear trigger keywords in the `description` frontmatter
- Branch naming: `<type>/LIN-<id>-<description>` (when using yux-linear-workflow)
- Commits follow Conventional Commits format
