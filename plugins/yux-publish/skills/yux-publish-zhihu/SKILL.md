---
name: yux-publish-zhihu
description: Publish articles to Zhihu (知乎专栏) via automated browser. Triggers on "发知乎", "post to zhihu", "知乎专栏", "zhihu publish", "发布知乎", "知乎文章".
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - mcp__chrome-devtools__navigate_page
  - mcp__chrome-devtools__take_snapshot
  - mcp__chrome-devtools__take_screenshot
  - mcp__chrome-devtools__click
  - mcp__chrome-devtools__fill
  - mcp__chrome-devtools__press_key
  - mcp__chrome-devtools__evaluate_script
  - mcp__chrome-devtools__wait_for
  - mcp__chrome-devtools__type_text
metadata:
  author: wuyuxiangX
  version: "1.0.0"
---

# Zhihu Article Publishing

## Language

**Match user's language**: Respond in the same language the user uses.

## Script Directory

**PLUGIN_DIR** is the root of this plugin (two levels above this SKILL.md directory).
Resolve: `PLUGIN_DIR = ${SKILL_DIR}/../..`

| Script | Path | Purpose |
|--------|------|---------|
| `zhihu-publish.ts` | `${PLUGIN_DIR}/scripts/zhihu/zhihu-publish.ts` | MDX/Markdown → Zhihu HTML conversion + clipboard copy |

## Prerequisites

- **Chrome DevTools MCP**: Must be configured. Browser (Arc/Chrome) must have remote debugging port enabled.
- **Bun runtime**: Scripts run via `npx -y bun`
- **macOS**: Clipboard functionality depends on macOS Swift/AppKit

## Preferences (EXTEND.md)

Check `${SKILL_DIR}/EXTEND.md` or user config path for settings:

```bash
# Check project-level first
test -f .yux-publish/yux-publish-zhihu/EXTEND.md && echo "project"

# Then user-level
test -f "$HOME/.yux-publish/yux-publish-zhihu/EXTEND.md" && echo "user"
```

**Supported settings**:

| Key | Default | Description |
|-----|---------|-------------|
| `default_theme` | `zhihu` | HTML rendering theme |
| `default_tags` | empty | Default topic tags (comma-separated) |
| `default_action` | `draft` | Default action: `draft` or `publish` |

**Priority**: CLI arguments > Frontmatter > EXTEND.md > Skill defaults

## Article Publishing Workflow

Copy this checklist and check off items as you complete them:

```
Publishing Progress:
- [ ] Step 0: Load preferences (EXTEND.md)
- [ ] Step 1: Convert content → HTML
- [ ] Step 2: Validate metadata
- [ ] Step 3: Dry-run checkpoint
- [ ] Step 4: Ensure browser debug port
- [ ] Step 5: Check Zhihu login status
- [ ] Step 6: Navigate to article editor
- [ ] Step 7: Fill title
- [ ] Step 8: Paste content into editor
- [ ] Step 9: Add topic tags
- [ ] Step 10: Save draft or publish
- [ ] Step 11: Report completion
```

### Step 0: Load Preferences

Read EXTEND.md and parse configuration.

### Step 1: Convert Content to HTML

**Input type detection**:

| Input Type | Detection | Action |
|------------|-----------|--------|
| MDX file | Path ends with `.mdx` | Run conversion script |
| Markdown file | Path ends with `.md` | Run conversion script |
| HTML file | Path ends with `.html` | Use directly, skip to Step 2 |

**Execute conversion**:

```bash
npx -y bun ${PLUGIN_DIR}/scripts/zhihu/zhihu-publish.ts <file> --dry-run
```

Parse JSON output to get: `title`, `description`, `tags`, `htmlPath`, `htmlContentPath`, `contentLength`, `imageCount`

### Step 2: Validate Metadata

| Field | If Missing |
|-------|------------|
| Title | Prompt user or auto-extract from content |
| Description | Auto-extract from first paragraph (truncate to 120 chars) |
| Tags | Use EXTEND.md defaults, or prompt user |

### Step 3: Dry-Run Checkpoint

If user specified `--dry-run`, show metadata summary and stop:

```
Zhihu Article Preview:
  Title: [title]
  Description: [description]
  Tags: [tag list]
  Content Length: [character count]
  Images: [image count]
  HTML Preview: [htmlPath]
```

### Step 4: Ensure Browser Debug Port

Check if browser debug port is available:

```bash
curl -s http://127.0.0.1:9222/json/version
```

**If unavailable**:

1. Prompt user to start browser with debug port
2. Arc browser:
   ```bash
   /Applications/Arc.app/Contents/MacOS/Arc --remote-debugging-port=9222
   ```
3. Chrome:
   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
   ```
4. Wait for port to be ready

### Step 5: Check Zhihu Login Status

1. `mcp__chrome-devtools__navigate_page` → `https://www.zhihu.com`
2. `mcp__chrome-devtools__take_snapshot` → check page content
3. Determine login status:
   - **Logged in**: Page contains user avatar, profile link
   - **Not logged in**: Page contains login/register buttons

**If not logged in**:

```
Zhihu not logged in. Please log in manually:
1. Open https://www.zhihu.com/signin in the browser
2. Log in via SMS code or QR scan
3. Tell me when done
```

Use `mcp__chrome-devtools__wait_for` to detect login completion (user avatar appears).

### Step 6: Navigate to Article Editor

```
mcp__chrome-devtools__navigate_page({ url: "https://zhuanlan.zhihu.com/write" })
```

Wait for editor to load:
- `mcp__chrome-devtools__wait_for` — wait for title input to appear
- `mcp__chrome-devtools__take_snapshot` — confirm editor DOM structure

### Step 7: Fill Title

1. `mcp__chrome-devtools__take_snapshot` — find title input area
2. `mcp__chrome-devtools__click` — click title input
3. `mcp__chrome-devtools__fill` or `mcp__chrome-devtools__type_text` — enter title

**Zhihu title limit**: Max 100 characters. If too long, truncate and prompt user.

### Step 8: Paste Content into Editor

**Primary method — Clipboard paste**:

1. Run script to copy HTML to clipboard:
   ```bash
   npx -y bun ${PLUGIN_DIR}/scripts/zhihu/zhihu-publish.ts <file> --copy-html
   ```
2. `mcp__chrome-devtools__take_snapshot` — find content editor area
3. `mcp__chrome-devtools__click` — click editor area
4. `mcp__chrome-devtools__press_key({ key: "Meta+a" })` — select all (clear placeholder)
5. `mcp__chrome-devtools__press_key({ key: "Meta+v" })` — paste

**Verify paste result**:

6. `mcp__chrome-devtools__take_snapshot` — check editor content is filled
7. If editor is still empty, switch to fallback method

**Fallback method — JavaScript ClipboardEvent simulation (recommended)**:

If clipboard paste fails, read `htmlContentPath` file content and inject via `evaluate_script`.

**CRITICAL**: Zhihu editor is based on Draft.js. Content injection priority:
1. **ClipboardEvent simulation** (recommended) — Draft.js correctly parses HTML, preserving headings, tables, code blocks
2. **execCommand('insertHTML')** — Enables publish button but loses all formatting
3. **innerHTML** — Completely unusable, Draft.js won't recognize it

```javascript
mcp__chrome-devtools__evaluate_script({
  function: "() => { const editor = document.querySelector('[contenteditable=\"true\"]'); if (!editor) return 'editor_not_found'; editor.focus(); document.execCommand('selectAll'); document.execCommand('delete'); const html = decodeURIComponent('ENCODED_HTML'); const dt = new DataTransfer(); dt.setData('text/html', html); dt.setData('text/plain', ''); const evt = new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true }); editor.dispatchEvent(evt); return 'ok'; }"
})
```

Note: URL-encode HTML content before passing to `decodeURIComponent`. `dispatchEvent` returning `false` is normal (Draft.js calls `preventDefault()` to handle paste).

**If Chrome DevTools MCP connection times out** (common with many tabs), use CDP REST API + WebSocket directly:

```bash
# 1. Open new tab
curl --noproxy '*' -s -X PUT 'http://127.0.0.1:9222/json/new?https://zhuanlan.zhihu.com/write'

# 2. Use Runtime.evaluate via WebSocket
```

### Step 9: Add Topic Tags

1. `mcp__chrome-devtools__take_snapshot` — find topic tag area
2. Usually at editor bottom, with "添加话题" button or input
3. For each tag:
   a. Click topic input area
   b. `mcp__chrome-devtools__type_text` — enter tag text
   c. `mcp__chrome-devtools__wait_for` — wait for autocomplete dropdown
   d. `mcp__chrome-devtools__take_snapshot` — view dropdown options
   e. `mcp__chrome-devtools__click` — click matching option
   f. If no exact match, press Enter for custom tag

**Zhihu limit**: Max 5 topic tags.

### Step 10: Save Draft or Publish

Based on `default_action` or user instruction:

**Save as draft** (default):
1. `mcp__chrome-devtools__take_snapshot` — find "保存草稿" button
2. `mcp__chrome-devtools__click` — click save
3. `mcp__chrome-devtools__wait_for` — wait for success message

**Publish**:
1. `mcp__chrome-devtools__take_snapshot` — find "发布" button
2. `mcp__chrome-devtools__click` — click publish
3. May show confirmation dialog, need to confirm again
4. `mcp__chrome-devtools__wait_for` — wait for publish success

**IMPORTANT**: Always save as draft by default, unless user explicitly says "发布"/"直接发布"/"publish".

### Step 11: Report Completion

```
Zhihu Publishing Complete!

Input: [file type] - [file path]

Article:
  Title: [title]
  Description: [description]
  Tags: [tag list]
  Images: [N] images
  Content: [character count] characters

Result:
  [Saved as draft / Published]

Next Steps:
  Manage articles: https://zhuanlan.zhihu.com/write
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Browser debug port unavailable | Close existing browser process, restart with debug mode |
| Zhihu login expired | Prompt user to manually re-login in browser |
| Editor load timeout | Refresh page and retry, check network connection |
| Clipboard paste loses formatting | Switch to JavaScript injection method |
| Topic tag no match | Use closest suggestion, or press Enter for custom tag |
| Title exceeds 100 chars | Truncate and prompt user to confirm |
| Images fail to load | Zhihu auto-downloads images — takes time, check in editor after saving draft |
| Content style abnormal | Zhihu editor overrides some styles, check actual result after publishing |
