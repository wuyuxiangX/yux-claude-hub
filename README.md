# yux-claude-hub

Claude Code Plugin Marketplace - Custom skills, commands, and extensions.

## Overview

yux-claude-hub is a Claude Code plugin repository providing:

- **Skills**: Auto-triggered intelligent modules
- **Commands**: Custom slash commands
- **Plugins**: Standalone installable extensions

## Available Plugins

| Plugin | Description | Details |
|--------|-------------|---------|
| [yux-video-to-blog](./plugins/yux-video-to-blog/) | Transform video content into blog articles | [README](./plugins/yux-video-to-blog/README.md) |
| [yux-linear-workflow](./plugins/yux-linear-workflow/) | Linear integration with CI/CD monitoring | [README](./plugins/yux-linear-workflow/README.md) |

## Installation

### Option 1: Via Claude Code (Recommended)

1. Add this marketplace to Claude Code:
```bash
/plugin marketplace add wuyuxiangX/yux-claude-hub
```

2. Install a plugin:
```bash
/plugin install yux-video-to-blog
# or
/plugin install yux-linear-workflow
```

### Option 2: Manual Installation

```bash
git clone https://github.com/wuyuxiangX/yux-claude-hub.git ~/.claude/plugins/yux-claude-hub
```

Or add individual plugins to `.claude/plugins.json`:

```json
{
  "plugins": [
    "https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/yux-video-to-blog",
    "https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/yux-linear-workflow"
  ]
}
```

## Directory Structure

```
yux-claude-hub/
├── plugins/
│   ├── yux-video-to-blog/      # Video to blog plugin
│   │   └── README.md           # Detailed documentation
│   └── yux-linear-workflow/    # Linear workflow plugin
│       └── README.md           # Detailed documentation
├── .claude-plugin/         # Plugin identifier
├── settings.json
├── LICENSE
└── README.md               # This file
```

## Contributing

Contributions welcome!

1. Fork this repository
2. Create a feature branch
3. Add your skills/commands
4. Submit a PR

### Guidelines

- Write all SKILL.md content in English
- Include clear trigger keywords
- Provide usage examples
- Add a README.md in your plugin directory
- Test before submitting

## License

MIT License - See [LICENSE](LICENSE)

---

Created 2026 | yux-claude-hub
