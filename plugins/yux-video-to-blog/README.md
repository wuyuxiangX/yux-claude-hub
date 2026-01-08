# Video to Blog Plugin

Transform video content into blog articles. A complete pipeline for content creators.

## Features

- **Subtitle Download**: Extract subtitles from multiple platforms (YouTube, Bilibili, Twitter/X, etc.)
- **Video Summary**: Summarize video content into structured notes
- **Blog Generation**: Generate polished blog articles from summaries
- **Multi-language Support**: English, Chinese, Japanese, Korean

## Installation

Add this plugin to your Claude Code:

```bash
claude plugin add https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/yux-video-to-blog
```

Or manually add to `.claude/plugins.json`:

```json
{
  "plugins": [
    "https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/yux-video-to-blog"
  ]
}
```

## Skills

| Skill | Triggers | Function |
|-------|----------|----------|
| yux-video-subtitle | "download subtitle", "extract subtitle", "video subtitle", "transcript", "字幕下载", "提取字幕", "视频字幕" | Download video subtitles |
| yux-video-summary | "summarize video", "video summary", "content summary", "organize transcript", "整理视频", "视频摘要", "内容总结" | Create structured summary |
| yux-blog-writer | "write blog", "generate article", "create post", "blog from video", "写博客", "生成文章", "写文章" | Generate blog article |

## Command

### `/yux-video-to-blog <video-url>`

One-click pipeline: URL → Subtitles → Summary → Blog Article

```
User: /yux-video-to-blog https://youtube.com/watch?v=xxx
Claude: [Downloads subtitles → Summarizes → Generates blog]
```

## Usage Examples

### Download Video Subtitles

```
User: Download subtitles from https://youtube.com/watch?v=xxx
Claude: [Executes yux-video-subtitle skill]
```

### Summarize Video Content

```
User: Summarize the video transcript
Claude: [Executes yux-video-summary skill]
```

### Generate Blog Article

```
User: Write a blog from the summary
Claude: [Asks for style preference, then generates article]
```

### Full Pipeline

```
User: /yux-video-to-blog https://youtube.com/watch?v=xxx
Claude: [Downloads subtitles → Summarizes → Generates blog]
```

## Workflow

```
[Video URL] → [Subtitles] → [Summary] → [Blog Article]
     │            │             │             │
   Input      Download      Organize      Generate
```

## Supported Platforms

- YouTube
- Bilibili
- Twitter/X
- And more...

## File Structure

```
plugins/yux-video-to-blog/
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest
├── commands/
│   └── yux-video-to-blog.md      # Pipeline command
├── skills/
│   ├── yux-video-subtitle/
│   │   └── SKILL.md              # Subtitle download skill
│   ├── yux-video-summary/
│   │   └── SKILL.md              # Video summary skill
│   └── yux-blog-writer/
│       └── SKILL.md              # Blog generation skill
└── README.md                     # This file
```

## License

MIT

## Author

wuyuxiangX
