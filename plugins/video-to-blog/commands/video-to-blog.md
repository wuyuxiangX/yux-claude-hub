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
2. Analyze and structure the content
3. Extract key points and quotes
4. Save summary as `<Video Title>-summary.md`

**Checkpoint**: Confirm summary file was created before proceeding.

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

Generated Files:
1. Transcript: <filename>.txt
2. Summary: <filename>-summary.md
3. Blog Article: <filename>.md

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

```
User: /video-to-blog https://www.youtube.com/watch?v=abc123

Claude: Starting Video to Blog pipeline...

[Phase 1] Downloading subtitles...
✓ Transcript saved: "How to Build AI Apps.txt"

[Phase 2] Summarizing content...
✓ Summary saved: "How to Build AI Apps-summary.md"

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
