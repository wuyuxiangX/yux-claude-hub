---
name: video-summary
description: Organize video transcript into structured summary. Triggers: "summarize video", "video summary", "content summary", "organize transcript", "整理视频", "视频摘要", "内容总结".
allowed-tools: Read, Write, Glob, Grep
---

# Video Content Summary

Input: Transcript file path from $ARGUMENTS

## Step 1: Load & Detect Languages

1. Read transcript file (`.txt` in current directory if not specified)
2. **Detect video_language**: Chinese chars > 30% → `zh`, else → `en`
3. **Detect user_language**: From user's input message, same rule
4. **Output mode**: Same language → SINGLE_FILE, Different → DUAL_FILE
5. Inform user: "视频语言: [X], 用户语言: [Y], 模式: [Combined/Dual-file]"

## Step 2: Identify Video Type

| Type | Indicators |
|------|------------|
| Interview/Podcast | Multiple speakers, Q&A format |
| Talk/Lecture | Single speaker, educational |
| Tutorial/Review/News | Instructions, evaluation, reporting |

## Step 3: Extract & Clean Content

### 3a. Extract Key Information
- Main topics and themes
- Key points and arguments
- Timeline highlights with timestamps
- Notable quotes
- Speaker identification (for interviews)

### 3b. Clean Transcript (Filler Word Removal)

**English**: um, uh, er, ah, you know, I mean, kind of, sort of, like, basically, actually, literally, right, okay

**Chinese**: 嗯, 啊, 呃, 哦, 那个, 这个, 就是, 然后, 所以说, 对吧, 是吧, 懂吗, 其实, 怎么说呢

**Rules**: Remove fillers, merge broken sentences, organize by topic/timeline sections

## Step 4: Generate Output

### SINGLE_FILE Mode (same language)

**Filename**: `<Title>-summary-<lang>.md`

```markdown
# 视频摘要 / Video Summary: [Title]

## 概览 / Overview
| 项目 | 内容 |
|------|------|
| 类型 | [Type] |
| 时长 | [Duration] |
| 语言 | [Language] |
| 主题 | [Topics] |
| 发言人 | [Speakers] (if applicable) |

## 执行摘要 / Executive Summary
[2-3 paragraphs in user_language]

## 关键要点 / Key Points
### [Topic 1]
- Point 1
- Point 2

### [Topic 2]
- Point 1

## 时间线 / Timeline
- [00:00] [Description]
- [05:30] [Description]

## 重要引用 / Notable Quotes
> "Quote 1" - [Speaker]

> "Quote 2" - [Speaker]

## 核心收获 / Key Takeaways
1. Takeaway 1
2. Takeaway 2
3. Takeaway 3

## 推荐资源 / Resources Mentioned
- 📖 [Book/Tool/Link]

---

# 原文整理 / Organized Transcript

> 已清理语气词，按主题整理。

## [00:00] 开场 / Introduction
[Cleaned content...]

## [05:30] [Topic Title]
[Cleaned content...]

## 结语 / Closing
[Cleaned content...]
```

### DUAL_FILE Mode (different languages)

**File 1**: `<Title>-summary-<user_lang>.md`

```markdown
# 视频摘要 / Video Summary: [Title]

> 原视频语言: [video_lang], 本摘要语言: [user_lang]
> 原文整理见: `<Title>-transcript-<video_lang>.md`

## 概览 / Overview
[Same structure as above, content in user_language]

## 执行摘要 / Executive Summary
[In user_language]

## 关键要点 / Key Points
[In user_language]

## 时间线 / Timeline
[Descriptions in user_language]

## 重要引用 / Notable Quotes
> "[Original quote in video_language]"
> *翻译: [Translation in user_language]*

## 核心收获 / Key Takeaways
[In user_language]

## 相关文件 / Related Files
- 原文整理: `<Title>-transcript-<video_lang>.md`
```

**File 2**: `<Title>-transcript-<video_lang>.md`

```markdown
# 原文整理 / Organized Transcript: [Title]

> 已清理语气词，按主题整理。原语言保留。

## 视频信息 / Metadata
| 项目 | 值 |
|------|---|
| 原语言 | [video_lang] |
| 时长 | [Duration] |
| 发言人 | [Speakers] |

## [00:00] 开场 / Introduction
[Cleaned original content...]

## [05:30] [Topic Title]
[Cleaned original content...]

## 结语 / Closing
[Cleaned original content...]
```

## Step 5: Save & Report

**SINGLE_FILE**: Save `<Title>-summary-<lang>.md`, report path and mode

**DUAL_FILE**: Save both files, report:
```
Generated:
1. Summary: <Title>-summary-<user_lang>.md
2. Transcript: <Title>-transcript-<video_lang>.md
Mode: Dual-file
```

## Quality Guidelines

- Concise and accurate
- Structured hierarchy
- Natural translations
- Preserve meaning when removing fillers
