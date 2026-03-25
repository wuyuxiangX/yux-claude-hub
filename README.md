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
| [yux-core](./plugins/yux-core/) | Core configuration management for all yux plugins | [README](./plugins/yux-core/README.md) |
| [yux-blog](./plugins/yux-blog/) | Blog content toolkit: video-to-article pipeline, image analysis & generation | [README](./plugins/yux-blog/README.md) |
| [yux-linear-workflow](./plugins/yux-linear-workflow/) | Linear integration with CI/CD monitoring | [README](./plugins/yux-linear-workflow/README.md) |
| [yux-linear-pm](./plugins/yux-linear-pm/) | Product management workflow for Linear | [README](./plugins/yux-linear-pm/README.md) |
| [yux-nano-banana](./plugins/yux-nano-banana/) | Image generation via OpenRouter API with Gemini models | [README](./plugins/yux-nano-banana/README.md) |

## Installation

### Option 1: Via Claude Code (Recommended)

1. Add this marketplace to Claude Code:
```bash
/plugin marketplace add wuyuxiangX/yux-claude-hub
```

2. Install a plugin:
```bash
/plugin install yux-core
/plugin install yux-blog
/plugin install yux-linear-workflow
/plugin install yux-linear-pm
/plugin install yux-nano-banana
```

### Option 2: Manual Installation

```bash
git clone https://github.com/wuyuxiangX/yux-claude-hub.git ~/.claude/plugins/yux-claude-hub
```

Or add individual plugins to `.claude/plugins.json`:

```json
{
  "plugins": [
    "https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/yux-core",
    "https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/yux-blog",
    "https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/yux-linear-workflow",
    "https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/yux-linear-pm",
    "https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/yux-nano-banana"
  ]
}
```

## Directory Structure

```
yux-claude-hub/
├── plugins/
│   ├── yux-core/               # Core configuration management
│   ├── yux-blog/               # Blog content toolkit
│   ├── yux-linear-workflow/    # Linear workflow integration
│   ├── yux-linear-pm/         # Linear product management
│   └── yux-nano-banana/       # Image generation
├── .claude-plugin/             # Plugin marketplace registry
├── settings.json
├── LICENSE
└── README.md                   # This file
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
