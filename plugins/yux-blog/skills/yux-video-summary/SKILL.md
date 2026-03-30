---
name: yux-video-summary
description: Transform a video transcript file into a structured, organized summary with key points, timeline, and cleaned transcript. Use when the user has a transcript file (typically from yux-video-subtitle) and wants it summarized — e.g., "summarize this video", "organize the transcript", "video summary", "整理视频", "视频摘要", "内容总结". Supports bilingual output when video language differs from user language. Do NOT use for summarizing articles, documents, or non-video content. To convert the summary into a blog post, use yux-blog-writer.
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

Follow the templates in `references/summary-templates.md` for the exact output format:
- **SINGLE_FILE mode**: One combined file with summary + organized transcript
- **DUAL_FILE mode**: Separate summary file (user language) + transcript file (video language)

## Step 5: Save & Report

**SINGLE_FILE**: Save `<Title>-summary-<lang>.md`, report path and mode

**DUAL_FILE**: Save both files, report:
```
Generated:
1. Summary: <Title>-summary-<user_lang>.md
2. Transcript: <Title>-transcript-<video_lang>.md
Mode: Dual-file
```

## Step 6: Completion Report

```
=== Video Summary Generated ===

File(s):  <Title>-summary-<lang>.md [+ transcript file if DUAL_FILE]
Mode:     Single-file / Dual-file
Language: Video: <video_lang>, Summary: <user_lang>
Sections: Overview, Key Points (N topics), Timeline (N entries), Quotes (N)
```

## Error Handling

| Situation | Action |
|-----------|--------|
| Transcript file not found | Search for `*.txt` and `*-transcript*` in current directory. If none found, ask user for path |
| Transcript empty or under 100 words | Warn: "Transcript too short for meaningful summary." Ask user to confirm or provide a different file |
| Timestamp format inconsistent | Normalize to `[HH:MM:SS]` or `[MM:SS]` based on video length. If no timestamps, skip Timeline section |
| Language detection ambiguous | Default to English. Inform user of detected language and ask to confirm |

## Quality Guidelines

- Concise and accurate
- Structured hierarchy
- Natural translations
- Preserve meaning when removing fillers
