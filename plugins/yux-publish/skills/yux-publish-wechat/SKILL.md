---
name: yux-publish-wechat
description: |
  Post content to WeChat Official Account (微信公众号) via API or Chrome CDP.
  Supports article posting (文章) with HTML, markdown, MDX, or plain text input,
  and image-text posting (贴图/图文) with multiple images.
  Use when user mentions "发布公众号", "post to wechat", "微信公众号", "贴图", "图文", "发微信".
  Do NOT use for Zhihu or Xiaohongshu — use yux-publish-zhihu or yux-publish-xiaohongshu instead.
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
metadata:
  author: wuyuxiangX
  version: "1.0.0"
---

# Post to WeChat Official Account

## Language

**Match user's language**: Respond in the same language the user uses. If user writes in Chinese, respond in Chinese. If user writes in English, respond in English.

## Script Directory

**PLUGIN_DIR** is the root of this plugin (two levels above this SKILL.md directory).
Resolve: `PLUGIN_DIR = ${SKILL_DIR}/../..`

| Script | Path | Purpose |
|--------|------|---------|
| `wechat-api.ts` | `${PLUGIN_DIR}/scripts/wechat/wechat-api.ts` | Article posting via API (文章) |
| `wechat-browser.ts` | `${PLUGIN_DIR}/scripts/wechat/wechat-browser.ts` | Image-text posts (图文) |
| `wechat-article.ts` | `${PLUGIN_DIR}/scripts/wechat/wechat-article.ts` | Article posting via browser (文章) |
| `md-to-wechat.ts` | `${PLUGIN_DIR}/scripts/wechat/md-to-wechat.ts` | Markdown → WeChat HTML conversion |
| `check-permissions.ts` | `${PLUGIN_DIR}/scripts/wechat/check-permissions.ts` | Verify environment & permissions |

## Preferences (EXTEND.md)

Use Bash to check EXTEND.md existence (priority order):

```bash
# Check project-level first
test -f .yux-publish/yux-publish-wechat/EXTEND.md && echo "project"

# Then user-level
test -f "$HOME/.yux-publish/yux-publish-wechat/EXTEND.md" && echo "user"
```

| Path | Location |
|------|----------|
| `.yux-publish/yux-publish-wechat/EXTEND.md` | Project directory |
| `$HOME/.yux-publish/yux-publish-wechat/EXTEND.md` | User home |

| Result | Action |
|--------|--------|
| Found | Read, parse, apply settings |
| Not found | Run first-time setup ([references/config/first-time-setup.md](references/config/first-time-setup.md)) → Save → Continue |

**EXTEND.md Supports**: Default theme | Default publishing method (api/browser) | Default author | Default open-comment switch | Default fans-only-comment switch | Chrome profile path

**Minimum supported keys** (case-insensitive, accept `1/0` or `true/false`):

| Key | Default | Mapping |
|-----|---------|---------|
| `default_author` | empty | Fallback for `author` when CLI/frontmatter not provided |
| `need_open_comment` | `1` | `articles[].need_open_comment` in `draft/add` request |
| `only_fans_can_comment` | `0` | `articles[].only_fans_can_comment` in `draft/add` request |

**Recommended EXTEND.md example**:

```md
default_theme: default
default_publish_method: api
default_author: yux
need_open_comment: 1
only_fans_can_comment: 0
chrome_profile_path: /path/to/chrome/profile
```

**Value priority**:
1. CLI arguments
2. Frontmatter
3. EXTEND.md
4. Skill defaults

## Pre-flight Check (Optional)

Before first use, suggest running the environment check. User can skip if they prefer.

```bash
npx -y bun ${PLUGIN_DIR}/scripts/wechat/check-permissions.ts
```

Checks: Chrome, profile isolation, Bun, Accessibility, clipboard, paste keystroke, API credentials, Chrome conflicts.

**If any check fails**, provide fix guidance:

| Check | Fix |
|-------|-----|
| Chrome | Install Chrome or set `WECHAT_BROWSER_CHROME_PATH` env var |
| Profile dir | Ensure `~/.local/share/wechat-browser-profile` is writable |
| Bun runtime | `curl -fsSL https://bun.sh/install \| bash` |
| Accessibility (macOS) | System Settings → Privacy & Security → Accessibility → enable terminal app |
| Clipboard copy | Ensure Swift/AppKit available (macOS Xcode CLI tools: `xcode-select --install`) |
| Paste keystroke (macOS) | Same as Accessibility fix above |
| Paste keystroke (Linux) | Install `xdotool` (X11) or `ydotool` (Wayland) |
| API credentials | Follow guided setup in Step 5, or manually set in `.yux-publish/.env` |

## Image-Text Posting (图文)

For short posts with multiple images (up to 9):

```bash
npx -y bun ${PLUGIN_DIR}/scripts/wechat/wechat-browser.ts --markdown article.md --images ./images/
npx -y bun ${PLUGIN_DIR}/scripts/wechat/wechat-browser.ts --title "标题" --content "内容" --image img.png --submit
```

See [references/image-text-posting.md](references/image-text-posting.md) for details.

## Article Posting Workflow (文章)

Copy this checklist and check off items as you complete them:

```
Publishing Progress:
- [ ] Step 0: Load preferences (EXTEND.md)
- [ ] Step 1: Determine input type
- [ ] Step 1b: Handle interactive components (if MDX with React components)
- [ ] Step 2: Convert to HTML (built-in)
- [ ] Step 3: Validate metadata (title, summary, cover)
- [ ] Step 4: Select method and configure credentials
- [ ] Step 5: Publish to WeChat
- [ ] Step 6: Report completion
```

### Step 0: Load Preferences

Check and load EXTEND.md settings (see Preferences section above).

**CRITICAL**: If not found, complete first-time setup BEFORE any other steps or questions.

Resolve and store these defaults for later steps:
- `default_author`
- `need_open_comment` (default `1`)
- `only_fans_can_comment` (default `0`)

### Step 1: Determine Input Type

| Input Type | Detection | Action |
|------------|-----------|--------|
| HTML file | Path ends with `.html`, file exists | Skip to Step 3 |
| Markdown file | Path ends with `.md`, file exists | Continue to Step 2 |
| MDX file | Path ends with `.mdx`, file exists | Continue to Step 1b |
| Plain text | Not a file path, or file doesn't exist | Save to markdown, then Step 2 |

**Plain Text Handling**:

1. Generate slug from content (first 2-4 meaningful words, kebab-case)
2. Create directory and save file:

```bash
mkdir -p "$(pwd)/post-to-wechat/$(date +%Y-%m-%d)"
# Save content to: post-to-wechat/yyyy-MM-dd/[slug].md
```

3. Continue processing as markdown file

### Step 1b: Handle Interactive Components

**Skip if**: Input is `.html` file or plain `.md` (not `.mdx`)

For `.mdx` files that may contain interactive React components (React Flow diagrams, etc.) which WeChat cannot render:

1. **Scan** the MDX for self-closing capitalized component tags
2. **Filter out** standard components already handled by `preprocessMdx` (`BlogImage`, `VideoEmbed`, `QuoteCard`, `ArticleCard`, `GlossaryCard`, `ProfileCard`)
3. **Check** remaining components against `diagramImageMap` in `${PLUGIN_DIR}/scripts/wechat/wechat-api.ts`
4. **If all mapped** → Continue to Step 2
5. **If unmapped components found** → Follow the screenshot workflow in [references/interactive-components.md](references/interactive-components.md):
   - Start dev server → open page with Chrome DevTools MCP → screenshot each component → check PNG gamma → upload to OSS → update `diagramImageMap`

### Step 2: Convert to HTML

**Skip if**: Input is `.html` file

This plugin includes a built-in markdown-to-HTML converter. No external skill needed.

1. **Ask theme preference** (unless specified in EXTEND.md or CLI):

| Theme | Description |
|-------|-------------|
| `default` | Classic theme - traditional layout, centered titles with bottom border, colored heading backgrounds |
| `grace` | Elegant theme - text shadows, rounded cards, refined quote blocks |
| `simple` | Minimal theme - modern minimalist, asymmetric rounded corners, clean whitespace |

2. **Execute conversion**:

```bash
npx -y bun ${PLUGIN_DIR}/scripts/wechat/md-to-wechat.ts <markdown_file> --theme <theme>
```

3. **Parse JSON output** to get: `htmlPath`, `title`, `author`, `summary`, `contentImages`

### Step 3: Validate Metadata

Check extracted metadata from Step 2 (or HTML meta tags if direct HTML input).

| Field | If Missing |
|-------|------------|
| Title | Prompt: "Enter title, or press Enter to auto-generate from content" |
| Summary | Prompt: "Enter summary, or press Enter to auto-generate (recommended for SEO)" |
| Author | Use fallback chain: CLI `--author` → frontmatter `author` → EXTEND.md `default_author` |

**Auto-Generation Logic**:
- **Title**: First H1/H2 heading, or first sentence
- **Summary**: First paragraph, truncated to 120 characters

**Cover Image Check** (required for `article_type=news`):
1. Use CLI `--cover` if provided.
2. Else use frontmatter (`coverImage`, `featureImage`, `cover`, `image`).
3. Else check article directory default path: `imgs/cover.png`.
4. Else fallback to first inline content image.
5. If still missing, stop and request a cover image before publishing.

### Step 4: Select Publishing Method and Configure

**Ask publishing method** (unless specified in EXTEND.md or CLI):

| Method | Speed | Requirements |
|--------|-------|--------------|
| `api` (Recommended) | Fast | API credentials |
| `browser` | Slow | Chrome, login session |

**If API Selected - Check Credentials**:

```bash
# Check project-level
test -f .yux-publish/.env && grep -q "WECHAT_APP_ID" .yux-publish/.env && echo "project"

# Check user-level
test -f "$HOME/.yux-publish/.env" && grep -q "WECHAT_APP_ID" "$HOME/.yux-publish/.env" && echo "user"
```

**If Credentials Missing - Guide Setup**:

```
WeChat API credentials not found.

To obtain credentials:
1. Visit https://mp.weixin.qq.com
2. Go to: 开发 → 基本配置
3. Copy AppID and AppSecret

Where to save?
A) Project-level: .yux-publish/.env (this project only)
B) User-level: ~/.yux-publish/.env (all projects)
```

After location choice, prompt for values and write to `.env`:

```
WECHAT_APP_ID=<user_input>
WECHAT_APP_SECRET=<user_input>
```

### Step 5: Publish to WeChat

**API method**:

```bash
npx -y bun ${PLUGIN_DIR}/scripts/wechat/wechat-api.ts <html_file> [--title <title>] [--summary <summary>] [--author <author>] [--cover <cover_path>]
```

**`draft/add` payload rules**:
- Use endpoint: `POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=ACCESS_TOKEN`
- `article_type`: `news` (default) or `newspic`
- For `news`, include `thumb_media_id` (cover is required)
- Always resolve and send:
  - `need_open_comment` (default `1`)
  - `only_fans_can_comment` (default `0`)
- `author` resolution: CLI `--author` → frontmatter `author` → EXTEND.md `default_author`

If script parameters do not expose the two comment fields, still ensure final API request body includes resolved values.

**Browser method**:

```bash
npx -y bun ${PLUGIN_DIR}/scripts/wechat/wechat-article.ts --html <html_file>
```

### Step 6: Completion Report

**For API method**:

```
WeChat Publishing Complete!

Input: [type] - [path]
Method: API
Theme: [theme name]

Article:
• Title: [title]
• Summary: [summary]
• Images: [N] inline images
• Comments: [open/closed], [fans-only/all users]

Result:
✓ Draft saved to WeChat Official Account
• media_id: [media_id]

Next Steps:
→ Manage drafts: https://mp.weixin.qq.com (登录后进入「内容管理」→「草稿箱」)
```

**For Browser method**:

```
WeChat Publishing Complete!

Input: [type] - [path]
Method: Browser
Theme: [theme name]

Article:
• Title: [title]
• Summary: [summary]
• Images: [N] inline images

Result:
✓ Draft saved to WeChat Official Account
```

## Detailed References

| Topic | Reference |
|-------|-----------|
| Image-text parameters, auto-compression | [references/image-text-posting.md](references/image-text-posting.md) |
| Article themes, image handling | [references/article-posting.md](references/article-posting.md) |
| Interactive components (React Flow etc.) | [references/interactive-components.md](references/interactive-components.md) |

## Feature Comparison

| Feature | Image-Text | Article (API) | Article (Browser) |
|---------|------------|---------------|-------------------|
| Plain text input | No | Yes | Yes |
| HTML input | No | Yes | Yes |
| Markdown input | Title/content | Yes (built-in) | Yes (built-in) |
| Multiple images | Yes (up to 9) | Yes (inline) | Yes (inline) |
| Themes | No | Yes | Yes |
| Auto-generate metadata | No | Yes | Yes |
| Default cover fallback | No | Yes | No |
| Comment control | No | Yes | No |
| Requires Chrome | Yes | No | Yes |
| Requires API credentials | No | Yes | No |
| Speed | Medium | Fast | Slow |

## Prerequisites

**For API method**:
- WeChat Official Account API credentials
- Guided setup in Step 4, or manually set in `.yux-publish/.env`

**For Browser method**:
- Google Chrome
- First run: log in to WeChat Official Account (session preserved)

**Config File Locations** (priority order):
1. Environment variables
2. `<cwd>/.yux-publish/.env`
3. `~/.yux-publish/.env`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing API credentials | Follow guided setup in Step 4 |
| Access token error | Check if API credentials are valid and not expired |
| Not logged in (browser) | First run opens browser - scan QR to log in |
| Chrome not found | Set `WECHAT_BROWSER_CHROME_PATH` env var |
| Title/summary missing | Use auto-generation or provide manually |
| No cover image | Add frontmatter cover or place `imgs/cover.png` in article directory |
| Wrong comment defaults | Check `EXTEND.md` keys `need_open_comment` and `only_fans_can_comment` |
| Paste fails | Check system clipboard permissions |

## Extension Support

Custom configurations via EXTEND.md. See **Preferences** section for paths and supported options.
