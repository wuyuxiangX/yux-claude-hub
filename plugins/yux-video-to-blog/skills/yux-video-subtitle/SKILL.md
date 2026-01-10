---
name: yux-video-subtitle
description: Download subtitles/transcripts from video platforms. Triggers: "download subtitle", "extract subtitle", "video subtitle", "transcript", "字幕下载", "提取字幕", "视频字幕".
allowed-tools: Read, Write, Glob, Grep, Bash(yt-dlp:*), Bash(which:*), Bash(ls:*), Bash(cat:*)
---

# Video Subtitle Download

Extract subtitles/transcripts from video URLs and save them as local text files.

Supported platforms: YouTube, Bilibili, Twitter/X, Vimeo, TikTok, and all other platforms supported by yt-dlp.

Input Video URL: $ARGUMENTS

## Configuration

Before generating output, read `.claude/yux-config.json`:
- If `language` is set, output messages in that language
- If file doesn't exist, detect from user input or default to English

## Step 1: Verify Tool Availability

1. **Check yt-dlp installation**:
   ```bash
   which yt-dlp
   ```

   - If `yt-dlp` is **found**, proceed to Step 2.
   - If `yt-dlp` is **NOT found**, notify user:
     "yt-dlp is not installed. Please install it first: `brew install yt-dlp` or `pip install yt-dlp`"
     Then **STOP** execution.

## Step 2: Get Video Information

1. **Get video title**:
   ```bash
   yt-dlp --get-title "[VIDEO_URL]"
   ```

   - If this fails with authentication error, try with cookies:
     ```bash
     yt-dlp --cookies-from-browser chrome --get-title "[VIDEO_URL]"
     ```

   - If browser cookie extraction fails, ask user to specify their browser (firefox, safari, edge) and retry.

2. **Store the video title** for file naming (sanitize special characters).

## Step 3: Download Subtitles

1. **Attempt subtitle download** with language priority (Chinese first, then English):

   ```bash
   yt-dlp --write-auto-sub --write-sub --sub-lang zh-Hans,zh-Hant,zh,en --skip-download --sub-format vtt --output "<Video Title>.%(ext)s" "[VIDEO_URL]"
   ```

   - For platforms requiring authentication (YouTube, Bilibili, etc.), add cookies:
     ```bash
     yt-dlp --cookies-from-browser chrome --write-auto-sub --write-sub --sub-lang zh-Hans,zh-Hant,zh,en --skip-download --sub-format vtt --output "<Video Title>.%(ext)s" "[VIDEO_URL]"
     ```

2. **Handle platform-specific cases**:

   - **Bilibili**: May require `--cookies-from-browser` for member-only videos
   - **YouTube**: Use `--write-auto-sub` for auto-generated subtitles
   - **Twitter/X**: Subtitles may not be available for all videos

3. **Verify download**:
   - Check if `.vtt` or `.srt` file was created
   - If no subtitle file found, inform user that subtitles are not available for this video

## Step 4: Convert to Plain Text

1. **Read the downloaded subtitle file** (`.vtt` or `.srt`)

2. **Extract and clean content**:
   - Remove timing information
   - Remove duplicate lines
   - Remove formatting tags
   - Keep only the actual transcript text

3. **Format output**:
   - Each line: `[Timestamp] Text content`
   - Or plain text without timestamps if user prefers

## Step 5: Detect Language and Save

1. **Detect source language**:
   - **From subtitle filename**: Check the downloaded file extension
     - `.zh-Hans.vtt`, `.zh-Hant.vtt`, `.zh.vtt` → `zh`
     - `.en.vtt`, `.en-US.vtt`, `.en-GB.vtt` → `en`
     - `.ja.vtt` → `ja`
     - `.ko.vtt` → `ko`
   - **From content analysis** (if filename doesn't indicate language):
     - Count Chinese characters (Unicode range `\u4e00-\u9fff`)
     - Calculate ratio: Chinese chars / Total chars
     - If ratio > 0.3 → `zh`
     - Otherwise → `en`

2. **Store the detected language code**: `video_language` (e.g., `zh`, `en`)

3. **Save the transcript** to: `<Video Title>.txt`

4. **Report completion with language info**:
   - File path
   - **Language code**: `[zh/en/ja/ko]`
   - Language name (e.g., Chinese, English)
   - Total number of lines
   - File size

## Error Handling

- **No subtitles available**: Inform user and suggest alternative (manual transcription or audio extraction)
- **Authentication required**: Guide user to set up cookies or login
- **Network error**: Suggest retry or check URL validity
- **Unsupported platform**: List supported platforms and suggest alternatives

## Output Format

```
File saved: <Video Title>.txt
Language code: zh
Language: Chinese (auto-generated)
Lines: 245
Size: 12.5 KB
```

The language code (`zh`, `en`, etc.) will be used by the yux-video-summary skill for multi-language output generation.
