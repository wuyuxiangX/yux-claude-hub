---
name: yux-publish
description: |
  Multi-platform content publishing hub. Routes to the right platform for publishing content.
  Use when user says "publish", "distribute", "post to", "发布文章", "多平台发布",
  "publish this article", "post to all platforms", "发布到所有平台".
  Do NOT use for platform-specific commands like "发知乎" or "发公众号" — those trigger platform skills directly.
user-invocable: true
allowed-tools:
  - Read
  - AskUserQuestion
metadata:
  author: wuyuxiangX
  version: "1.0.0"
---

# Multi-Platform Publishing Hub

## Language

**Match user's language**: Respond in the same language the user uses.

## Available Platforms

| Platform | Skill | Trigger Keywords |
|----------|-------|-----------------|
| WeChat Official Account (微信公众号) | `yux-publish-wechat` | "发公众号", "post to wechat", "微信公众号" |
| Zhihu (知乎专栏) | `yux-publish-zhihu` | "发知乎", "post to zhihu", "知乎文章" |
| Xiaohongshu (小红书) | `yux-publish-xiaohongshu` | "转小红书", "convert to xiaohongshu", "小红书" |

## Workflow

### Step 1: Detect Content

Check user's input:
1. If a file path is provided, determine type (MDX, Markdown, HTML)
2. If plain text, note it for downstream platform skills

### Step 2: Select Platform(s)

Ask user to choose target platform(s):

```
Which platform(s) do you want to publish to?

A) WeChat Official Account (微信公众号)
B) Zhihu (知乎专栏)
C) Xiaohongshu (小红书)
D) All of the above
```

### Step 3: Route to Platform Skill(s)

For each selected platform, invoke the corresponding skill:

| Selection | Action |
|-----------|--------|
| WeChat | Invoke `yux-publish-wechat` skill with the content |
| Zhihu | Invoke `yux-publish-zhihu` skill with the content |
| Xiaohongshu | Invoke `yux-publish-xiaohongshu` skill with the content |
| All | Execute each platform skill sequentially |

**Sequential execution order** (when "All"):
1. WeChat (API-based, fastest)
2. Zhihu (browser automation)
3. Xiaohongshu (content conversion only)

### Step 4: Summary Report

After all platforms are processed, provide a combined report:

```
Multi-Platform Publishing Complete!

Content: [file/text description]

Results:
  WeChat:      ✓ Draft saved (media_id: xxx)
  Zhihu:       ✓ Draft saved
  Xiaohongshu: ✓ Content converted

Next Steps:
  → WeChat: https://mp.weixin.qq.com (内容管理 → 草稿箱)
  → Zhihu: https://zhuanlan.zhihu.com/write
  → Xiaohongshu: Copy converted text to app
```
