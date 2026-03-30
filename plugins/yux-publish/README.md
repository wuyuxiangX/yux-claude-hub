# yux-publish

Multi-platform content publishing plugin for Claude Code. Publish articles to WeChat Official Account, Zhihu, and Xiaohongshu from a unified interface.

## Pipeline

```
Content (MDX/Markdown/HTML/Text)
        |
   yux-publish (router)
        |
   +---------+---------+
   |         |         |
WeChat    Zhihu    Xiaohongshu
(API/CDP)  (CDP)   (conversion)
```

## Skills

| Skill | Purpose | Triggers |
|-------|---------|----------|
| `yux-publish` | Platform router — choose where to publish | "publish", "发布文章", "多平台发布" |
| `yux-publish-wechat` | WeChat Official Account publishing | "发公众号", "post to wechat", "微信公众号" |
| `yux-publish-zhihu` | Zhihu article publishing | "发知乎", "post to zhihu", "知乎文章" |
| `yux-publish-xiaohongshu` | Xiaohongshu content conversion | "转小红书", "xiaohongshu", "小红书" |

## Quick Start

### Publish to WeChat

```
发布这篇文章到公众号: content/blog/my-article.mdx
```

### Publish to Zhihu

```
发知乎: content/blog/my-article.mdx
```

### Convert for Xiaohongshu

```
把这篇文章转成小红书风格
```

### Multi-platform

```
发布这篇文章到所有平台
```

## Configuration

### WeChat Credentials

Store in `.yux-publish/.env` (project-level) or `~/.yux-publish/.env` (user-level):

```
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret
```

### Per-Platform Preferences

Each platform supports EXTEND.md for customization:

| Platform | Config Path |
|----------|-------------|
| WeChat | `.yux-publish/yux-publish-wechat/EXTEND.md` |
| Zhihu | `.yux-publish/yux-publish-zhihu/EXTEND.md` |

## Prerequisites

| Platform | Requirements |
|----------|-------------|
| WeChat (API) | WeChat Official Account API credentials |
| WeChat (Browser) | Google Chrome, login session |
| Zhihu | Chrome DevTools MCP, browser with `--remote-debugging-port=9222` |
| Xiaohongshu | None (content conversion only) |

## File Structure

```
yux-publish/
├── .claude-plugin/plugin.json
├── skills/
│   ├── yux-publish/SKILL.md              # Router
│   ├── yux-publish-wechat/               # WeChat
│   │   ├── SKILL.md
│   │   └── references/
│   ├── yux-publish-zhihu/SKILL.md        # Zhihu
│   └── yux-publish-xiaohongshu/SKILL.md  # Xiaohongshu
├── scripts/
│   ├── wechat/                           # WeChat TypeScript scripts
│   │   ├── wechat-api.ts
│   │   ├── wechat-browser.ts
│   │   ├── wechat-article.ts
│   │   ├── md-to-wechat.ts
│   │   ├── check-permissions.ts
│   │   └── md/                           # Markdown render engine + themes
│   └── zhihu/
│       └── zhihu-publish.ts
└── README.md
```
