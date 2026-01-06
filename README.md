# yux-claude-hub

Claude Code Plugin Marketplace - Custom skills, commands, and extensions.

## Overview

yux-claude-hub is a Claude Code plugin repository providing:

- **Skills**: Auto-triggered intelligent modules
- **Commands**: Custom slash commands
- **Plugins**: Standalone installable extensions

## Available Plugins

### video-to-blog

Transform video content into blog articles. A complete pipeline for content creators.

**Features:**
- Download subtitles from multiple platforms (YouTube, Bilibili, Twitter/X, etc.)
- Summarize video content into structured notes
- Generate polished blog articles

**Skills included:**
| Skill | Triggers | Function |
|-------|----------|----------|
| video-subtitle | "download subtitle", "字幕下载" | Download video subtitles |
| video-summary | "summarize video", "视频摘要" | Create structured summary |
| blog-writer | "write blog", "写博客" | Generate blog article |

**Command:**
```
/video-to-blog <video-url>
```
One-click pipeline: URL → Subtitles → Summary → Blog Article

## Installation

### Option 1: Via Claude Code (Recommended)

1. Add this marketplace to Claude Code:
```bash
/plugin marketplace add wuyuxiangX/yux-claude-hub
```

2. Install the video-to-blog plugin:
```bash
/plugin install video-to-blog
```

### Option 2: Manual Installation

```bash
git clone https://github.com/wuyuxiangX/yux-claude-hub.git ~/.claude/plugins/yux-claude-hub
```

## Directory Structure

```
yux-claude-hub/
├── .claude-plugin              # Plugin identifier
├── plugins/
│   └── video-to-blog/          # Video to blog plugin
│       ├── .claude-plugin
│       ├── skills/
│       │   ├── video-subtitle/
│       │   ├── video-summary/
│       │   └── blog-writer/
│       └── commands/
│           └── video-to-blog.md
├── settings.json
├── LICENSE
└── README.md
```

## Usage Examples

### Download Video Subtitles
```
User: Download subtitles from https://youtube.com/watch?v=xxx
Claude: [Executes video-subtitle skill]
```

### Summarize Video Content
```
User: Summarize the video transcript
Claude: [Executes video-summary skill]
```

### Generate Blog Article
```
User: Write a blog from the summary
Claude: [Asks for style preference, then generates article]
```

### Full Pipeline
```
User: /video-to-blog https://youtube.com/watch?v=xxx
Claude: [Downloads subtitles → Summarizes → Generates blog]
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
- Test before submitting

## License

MIT License - See [LICENSE](LICENSE)

---

Created 2026 | yux-claude-hub
