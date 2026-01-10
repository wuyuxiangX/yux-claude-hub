# yux-core

Core configuration management plugin for yux-claude-hub. Provides unified language settings and cross-plugin configuration.

## Features

- **Language Configuration**: Set output language for all yux plugins
- **Project-level Settings**: Configuration stored in `.claude/yux-config.json`
- **Multi-language Support**: English, Chinese, Japanese, Korean

## Installation

```bash
claude install yux-core
```

## Usage

### Initialize Configuration

```bash
/yux-init
```

This creates `.claude/yux-config.json` with your language preference.

### Change Settings

Use natural language:
- "set language to Chinese"
- "change config to Japanese"
- "设置语言为英文"

## Configuration File

Location: `.claude/yux-config.json`

```json
{
  "language": "zh",
  "created_at": "2026-01-10T10:00:00Z",
  "version": "1.0.0"
}
```

### Options

| Field | Description | Values |
|-------|-------------|--------|
| `language` | Output language | `en`, `zh`, `ja`, `ko` |

## For Plugin Developers

### Reading Configuration

Add this to your SKILL.md:

```markdown
## Configuration

Before generating output, read `.claude/yux-config.json`:
- If `language` is set, output in that language
- If file doesn't exist, detect from user input or default to English
- Load messages from `templates/messages.json` for the configured language
```

### Messages File Structure

Create `templates/messages.json` in your plugin:

```json
{
  "en": {
    "success": "Operation completed successfully",
    "error": "An error occurred"
  },
  "zh": {
    "success": "操作成功完成",
    "error": "发生错误"
  }
}
```

## Commands

| Command | Description |
|---------|-------------|
| `/yux-init` | Initialize configuration for current project |

## Skills

| Skill | Triggers |
|-------|----------|
| yux-config | "config", "settings", "配置", "设置" |

## License

MIT
