---
name: yux-blog-image
description: Analyze articles for image insertion and generate images. Triggers: "analyze article images", "suggest images", "article image plan", "generate article images", "insert article images", "分析文章配图", "文章插图分析", "生成文章配图", "插入文章配图".
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion, Bash(curl:*), Bash(base64:*), Bash(jq:*), Bash(which:*), Bash(date:*), Bash(uname:*), Bash(file:*), Bash(wc:*), Bash(ls:*)
---

# Blog Image — Article Image Analysis & Generation

Analyze blog articles for optimal image placement, then generate AI images via OpenRouter API and insert them into the article.

## Configuration

Before generating output, read `.claude/yux-config.json`:
- If `language` is set, use that language for user-facing messages
- If file doesn't exist, detect from user input or default to English

## Step 1: Prerequisites Check

### 1.1 Verify required tools

Run `which curl jq base64` to confirm all tools are available. If any are missing, inform the user and stop.

### 1.2 Verify API key

Check if `$OPENROUTER_API_KEY` is set:

```bash
echo "${OPENROUTER_API_KEY:+set}"
```

If empty, inform the user: "Please set `OPENROUTER_API_KEY` in your environment to use image generation." and **stop immediately**.

## Step 2: Determine Phase

Parse the user's request to determine the operation phase:

| Phase | Trigger keywords (EN) | Trigger keywords (ZH) |
|-------|----------------------|----------------------|
| **Analyze** | "analyze article images", "suggest images", "article image plan" | "分析文章配图", "文章插图分析" |
| **Generate** | "generate article images", "insert article images" | "生成文章配图", "插入文章配图" |

- If the user's intent matches **Analyze** triggers → go to **Step 3**
- If the user's intent matches **Generate** triggers → go to **Step 5**
- If ambiguous, ask the user which phase they want

## Step 3: Analyze Article (Phase 1)

### 3.1 Get article path

If the user did not provide an article path, ask for it using AskUserQuestion. The article must be a markdown file.

### 3.2 Read and analyze article

Read the article file and analyze its structure:
- Parse headings (H1, H2, H3), sections, and key concepts
- Identify the article's topic, tone, and style
- Count total lines for accurate line references

### 3.3 Identify image insertion points

Determine optimal positions for images based on:
- After introductions or opening paragraphs
- Between major sections (before or after H2/H3 headings)
- Alongside key concepts, examples, or data points
- Before conclusions or summary sections

For each insertion point, determine:
- **insert_after_line**: The exact line number after which to insert the image
- **section**: The section name or heading this relates to
- **type**: Either `ai-generated` (can be created by Nano Banana) or `real` (user should provide a real photo/screenshot)
- **description**: What the image should depict
- **prompt**: If type is `ai-generated`, draft a detailed Nano Banana prompt optimized for the model (descriptive, specific about style and content)

### 3.4 Save plan

Save the analysis plan to `.claude/blog-image-plan.json`:

```json
{
  "article_path": "/absolute/path/to/article.md",
  "created_at": "2026-...",
  "images": [
    {
      "id": 1,
      "insert_after_line": 15,
      "section": "Introduction",
      "type": "ai-generated",
      "description": "A diagram showing the system architecture",
      "prompt": "A clean, minimalist system architecture diagram showing...",
      "status": "pending"
    },
    {
      "id": 2,
      "insert_after_line": 42,
      "section": "Results",
      "type": "real",
      "description": "Screenshot of the dashboard metrics",
      "prompt": "",
      "status": "pending"
    }
  ]
}
```

### 3.5 Display plan to user

Present the plan in a clear table format:

```
| # | Line | Section | Type | Description | Prompt |
|---|------|---------|------|-------------|--------|
| 1 | 15   | Intro   | AI   | System arch | A clean, minimalist... |
| 2 | 42   | Results | Real | Dashboard   | (user provides) |
```

### 3.6 Ask for confirmation

Use AskUserQuestion to ask the user to:
- Confirm the plan as-is
- Modify prompts or descriptions
- Change image types (ai-generated ↔ real)
- Remove or add insertion points

Apply any changes the user requests, then save the updated plan.

## Step 4: Transition

After the analyze phase is complete, inform the user they can run the generate phase when ready by saying "generate article images" or "生成文章配图".

## Step 5: Generate Images (Phase 2)

### 5.1 Read plan

Read `.claude/blog-image-plan.json`. If the file doesn't exist, inform the user to run the analyze phase first and stop.

### 5.2 Filter actionable images

Collect all images where:
- `type` is `ai-generated`
- `status` is `pending`

If none are found, inform the user and stop.

### 5.3 Confirm before proceeding

Display the count of images to generate and ask the user to confirm:
- "Found N AI-generated images to create. Proceed?"

### 5.4 Detect platform

```bash
uname -s
```

Use `-D` for base64 decode on macOS (Darwin), `-d` on Linux.

### 5.5 Generate each image

For each pending ai-generated image, call OpenRouter API:

```bash
curl -s -o /tmp/blog-image-response.json -w "%{http_code}" \
  https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "google/gemini-2.5-flash-preview:image",
    "messages": [
      {
        "role": "user",
        "content": "<PROMPT_FROM_PLAN>"
      }
    ]
  }'
```

**Important**: Always use `-o /tmp/blog-image-response.json` to save the response to a file. The response contains base64-encoded image data that would be truncated in stdout.

#### Parse response

Check the HTTP status code:
- **200**: Success — extract image
- **401**: Authentication failed — stop with error
- **402**: Insufficient funds — stop with error
- **429**: Rate limited — stop with error
- **Other non-200**: Show raw error, stop

#### Extract and save image

```bash
FILENAME="blog-image-<ID>-$(date +%Y%m%d-%H%M%S).png"

jq -r '.choices[0].message.content[] | select(.type == "image_url") | .image_url.url' /tmp/blog-image-response.json \
  | sed 's|^data:image/[^;]*;base64,||' \
  | base64 -D > "$FILENAME"   # Use -d on Linux
```

If the above jq path returns nothing, check the raw response structure:

```bash
jq '.choices[0].message' /tmp/blog-image-response.json
```

Verify the file was created and is non-empty with `ls -la "$FILENAME"`.

#### Update plan

After each successful generation, update the image entry in `.claude/blog-image-plan.json`:
- Set `status` to `"completed"`
- Add `"file_path"` with the saved image path

#### Cleanup temp files

```bash
rm -f /tmp/blog-image-response.json
```

### 5.6 Insert images into article

Read the article file. Process insertions **from bottom to top** (highest line number first) to avoid line number drift.

For each completed image, insert at the specified line:

```markdown
![description](./image-filename.png)
```

Write the updated article back to the original file.

### 5.7 Report results

Display a summary of all actions taken:
- List each inserted image with its file path and target section
- Note any images that were skipped (type `real` — user must provide these)
- Show the updated article path

## Error Handling

| Situation | Action |
|-----------|--------|
| Article file not found | Ask user for correct path |
| Plan file not found (generate phase) | Instruct user to run analyze phase first |
| API key not set | Show setup instructions, stop |
| API error (401/402/429) | Show specific error, stop |
| No image in API response | Likely safety-filtered — show warning, skip this image |
| Empty article | Inform user, stop |
