# yux-blog

Blog content toolkit for Claude Code. Video-to-article pipeline, article image analysis and generation.

## Features

- **Subtitle Download**: Extract subtitles from multiple platforms (YouTube, Bilibili, Twitter/X, etc.)
- **Video Summary**: Summarize video content into structured notes
- **Blog Generation**: Generate polished blog articles from summaries
- **Article Image Analysis**: Analyze articles for optimal image placement
- **Image Generation**: Generate AI images via OpenRouter API and insert them into articles
- **OSS Upload**: Upload images to Alibaba Cloud OSS and replace local paths with CDN URLs
- **Multi-language Support**: English, Chinese, Japanese, Korean

## Installation

Add this plugin to your Claude Code:

```bash
claude plugin add https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/yux-blog
```

Or manually add to `.claude/plugins.json`:

```json
{
  "plugins": [
    "https://github.com/wuyuxiangX/yux-claude-hub/tree/main/plugins/yux-blog"
  ]
}
```

## Skills

| Skill | Triggers | Function |
|-------|----------|----------|
| yux-video-subtitle | "download subtitle", "extract subtitle", "video subtitle", "transcript", "字幕下载", "提取字幕", "视频字幕" | Download video subtitles |
| yux-video-summary | "summarize video", "video summary", "content summary", "organize transcript", "整理视频", "视频摘要", "内容总结" | Create structured summary |
| yux-blog-writer | "write blog", "generate article", "create post", "blog from video", "写博客", "生成文章", "写文章" | Generate blog article |
| yux-blog-image | "analyze article images", "suggest images", "article image plan", "generate article images", "insert article images", "分析文章配图", "生成文章配图" | Analyze articles for image placement and generate AI images |
| yux-blog-oss | "upload to oss", "upload images to oss", "oss upload", "上传到oss", "上传图片到oss", "上传博客图片" | Upload images to Alibaba Cloud OSS and update article with CDN URLs |

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

### Analyze Article Images

```
User: Analyze article images for ./my-article.md
Claude: [Reads article, identifies insertion points, saves plan]
```

### Generate Article Images

```
User: Generate article images
Claude: [Reads plan, generates images via OpenRouter, inserts into article]
```

### Upload Images to OSS

```
User: Upload to oss
Claude: [Reads plan, uploads completed images to Alibaba Cloud OSS, updates article with CDN URLs]
```

```
User: Upload ./image1.png ./image2.png to oss
Claude: [Uploads specified files to OSS, returns CDN URLs]
```

### Full Pipeline

```
User: /yux-video-to-blog https://youtube.com/watch?v=xxx
Claude: [Downloads subtitles → Summarizes → Generates blog]
```

## Workflow

### Video to Blog Pipeline

```
[Video URL] → [Subtitles] → [Summary] → [Blog Article]
     │            │             │             │
   Input      Download      Organize      Generate
```

### Article Image Pipeline

```
[Article] → [Analyze] → [Image Plan] → [Generate] → [Insert] → [Upload to OSS]
    │           │            │              │            │             │
  Input     Structure    Placement      OpenRouter   Markdown     CDN URLs
```

## Supported Platforms

- YouTube
- Bilibili
- Twitter/X
- And more...

## File Structure

```
plugins/yux-blog/
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest
├── skills/
│   ├── yux-video-subtitle/
│   │   └── SKILL.md              # Subtitle download skill
│   ├── yux-video-summary/
│   │   └── SKILL.md              # Video summary skill
│   ├── yux-blog-writer/
│   │   └── SKILL.md              # Blog generation skill
│   ├── yux-blog-image/
│   │   └── SKILL.md              # Article image analysis & generation skill
│   └── yux-blog-oss/
│       └── SKILL.md              # OSS upload skill
└── README.md                     # This file
```

## License

MIT

## Author

wuyuxiangX
