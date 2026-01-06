# Video to Blog - Full Pipeline

Transform a video URL into a complete blog article in one command.

**Usage**: `/video-to-blog <video-url>`

This command executes the complete video-to-blog workflow:
1. Download subtitles from the video
2. Summarize the video content
3. Generate a blog article

## Input

Video URL from: $ARGUMENTS

If no URL is provided, ask the user to provide one.

## Workflow

### Phase 1: Download Subtitles

Execute the **video-subtitle** skill:

1. Verify yt-dlp is installed
2. Download subtitles from the video URL
3. Save transcript as `<Video Title>.txt`

**Checkpoint**: Confirm transcript file was created before proceeding.

If subtitle download fails:
- Inform user of the issue
- Ask if they want to provide a transcript file manually
- If yes, proceed with their provided file
- If no, stop execution

### Phase 2: Summarize Content

Execute the **video-summary** skill:

1. Read the transcript file from Phase 1
2. **Detect languages**:
   - Video source language (from transcript content)
   - User's preferred language (from their input)
3. Analyze and structure the content
4. Clean transcript (remove filler words, organize by topic)
5. **Generate output based on language match**:
   - **Same language** (user = video): Save `<Video Title>-summary-<lang>.md` (combined summary + organized transcript)
   - **Different languages** (user ≠ video): Save both:
     - `<Video Title>-summary-<user_lang>.md` (summary in user's language)
     - `<Video Title>-transcript-<video_lang>.md` (organized transcript in original language)

**Checkpoint**: Confirm summary file(s) were created before proceeding.

### Phase 3: Generate Blog Article

Execute the **blog-writer** skill:

1. Read the summary file from Phase 2
2. **Ask user to choose writing style**:
   - Technical Blog (professional, in-depth)
   - Casual Explainer (easy to understand)
   - News Style (objective, concise)
3. Generate the blog article
4. Save as `YYYY-MM-DD-<slug>.md`

## Final Output

Report the complete results:

```
Video to Blog Pipeline Complete!

Source: [Video URL]
Video Title: [Title]

Language Detection:
- Video Language: [detected video language]
- User Language: [detected user language]
- Mode: [Combined/Dual-file]

Generated Files:
1. Transcript (raw): <filename>.txt
2. Summary: <filename>-summary-<lang>.md
3. Organized Transcript: <filename>-transcript-<lang>.md (if dual-file mode)
4. Blog Article: <filename>.md

Blog Details:
- Style: [Selected Style]
- Word Count: [count]
- Reading Time: ~[X] minutes

All files saved to: [current directory]
```

## Error Handling

- **Invalid URL**: Ask user to verify the URL
- **No subtitles**: Offer manual transcript upload option
- **Tool missing**: Provide installation instructions
- **Network error**: Suggest retry

## Example

### Example 1: Same Language (Chinese user, Chinese video)

```
User: /video-to-blog https://www.bilibili.com/video/BV123456

Claude: Starting Video to Blog pipeline...

[Phase 1] Downloading subtitles...
✓ Transcript saved: "如何构建AI应用.txt"
  Language code: zh

[Phase 2] Summarizing content...
  Video language: zh (Chinese)
  User language: zh (Chinese)
  Mode: Combined (single file)
✓ Summary saved: "如何构建AI应用-summary-zh.md"

[Phase 3] Generating blog article...
Please choose a writing style:
1. Technical Blog
2. Casual Explainer
3. News Style

User: 2

Claude: Generating casual explainer article...
✓ Article saved: "2024-01-15-如何构建AI应用.md"

Pipeline complete! All files are in your current directory.
```

### Example 2: Different Languages (Chinese user, English video)

```
User: /video-to-blog https://www.youtube.com/watch?v=abc123

Claude: Starting Video to Blog pipeline...

[Phase 1] Downloading subtitles...
✓ Transcript saved: "How to Build AI Apps.txt"
  Language code: en

[Phase 2] Summarizing content...
  Video language: en (English)
  User language: zh (Chinese)
  Mode: Dual-file (separate summary and transcript)
✓ Summary saved: "How to Build AI Apps-summary-zh.md" (Chinese summary)
✓ Transcript saved: "How to Build AI Apps-transcript-en.md" (English organized transcript)

[Phase 3] Generating blog article...
Please choose a writing style:
1. Technical Blog
2. Casual Explainer
3. News Style

User: 2

Claude: Generating casual explainer article...
✓ Article saved: "2024-01-15-how-to-build-ai-apps.md"

Pipeline complete! All files are in your current directory.
```
