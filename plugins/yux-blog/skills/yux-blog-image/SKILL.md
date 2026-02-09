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
- If `output_dir` is set, save generated images to that directory (expand `~` to home directory; create directory if it doesn't exist using `mkdir -p`)
- If `output_dir` is not set, save to the current working directory
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

## File Organization

All plans and images are organized **per article** using a slug derived from the article filename:

```
article filename: my-awesome-article.md → slug: my-awesome-article
```

### Directory structure

```
{output_dir}/
└── {article-slug}/
    ├── blog-image-1.png
    ├── blog-image-2.png
    └── ...

.claude/
└── blog-image-plans/
    └── {article-slug}.json        # one plan per article
```

- **Plan files**: `.claude/blog-image-plans/{slug}.json` — each article has its own plan file
- **Image files**: `{output_dir}/{slug}/` — each article's images are in a dedicated subdirectory
- Re-analyzing the same article **updates** its existing plan (preserves completed images, resets only pending ones)
- `output_dir` comes from `.claude/yux-config.json`; defaults to current working directory if not set

### Slug derivation

Strip the `.md` extension and use the filename (not path) as the slug:
- `/path/to/my-article.md` → `my-article`
- `/path/to/2026-01-15-deep-dive.md` → `2026-01-15-deep-dive`

## Step 2: Determine Phase

Parse the user's request to determine the operation phase:

| Phase | Trigger keywords (EN) | Trigger keywords (ZH) |
|-------|----------------------|----------------------|
| **Analyze** | "analyze article images", "suggest images", "article image plan" | "分析文章配图", "文章插图分析" |
| **Generate** | "generate article images", "insert article images" | "生成文章配图", "插入文章配图" |
| **List** | "list image plans", "show plans" | "查看配图计划", "列出计划" |

- If the user's intent matches **Analyze** triggers → go to **Step 3**
- If the user's intent matches **Generate** triggers → go to **Step 5**
- If the user's intent matches **List** triggers → go to **Step 2.5**
- If ambiguous, ask the user which phase they want

### Step 2.5: List Plans

Glob `.claude/blog-image-plans/*.json` and display a summary table:

```
| Article | Created | AI Images | Completed | Pending |
|---------|---------|-----------|-----------|---------|
| my-article | 2026-02-09 | 3 | 2 | 1 |
| deep-dive  | 2026-02-08 | 5 | 5 | 0 |
```

If the user then selects an article, load that plan and go to Step 5 (generate) for any pending images.

## Step 3: Analyze Article (Phase 1)

### 3.1 Get article path

If the user did not provide an article path, ask for it using AskUserQuestion. The article must be a markdown file.

### 3.2 Derive slug and check existing plan

Derive the slug from the article filename. Check if `.claude/blog-image-plans/{slug}.json` already exists:
- If exists and has `completed` images: inform user, ask whether to **keep completed images and re-analyze pending** or **start fresh**
- If exists and all pending: overwrite with new analysis
- If not exists: proceed normally

### 3.3 Read and analyze article

Read the article file and analyze its structure:
- Parse headings (H1, H2, H3), sections, and key concepts
- Identify the article's topic, tone, and style
- Count total lines for accurate line references

### 3.4 Identify image insertion points

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

### 3.5 Save plan

Create directory `.claude/blog-image-plans/` if not exists. Save the plan to `.claude/blog-image-plans/{slug}.json`:

```json
{
  "article_path": "/absolute/path/to/my-article.md",
  "slug": "my-article",
  "created_at": "2026-02-09T...",
  "updated_at": "2026-02-09T...",
  "images": [
    {
      "id": 1,
      "insert_after_line": 15,
      "section": "Introduction",
      "type": "ai-generated",
      "description": "A diagram showing the system architecture",
      "prompt": "A clean, minimalist system architecture diagram showing...",
      "status": "pending",
      "file_path": null
    },
    {
      "id": 2,
      "insert_after_line": 42,
      "section": "Results",
      "type": "real",
      "description": "Screenshot of the dashboard metrics",
      "prompt": "",
      "status": "pending",
      "file_path": null
    }
  ]
}
```

### 3.6 Display plan to user

Present the plan in a clear table format:

```
Article: my-article.md
Plan: .claude/blog-image-plans/my-article.json
Images dir: {output_dir}/my-article/

| # | Line | Section | Type | Description | Status |
|---|------|---------|------|-------------|--------|
| 1 | 15   | Intro   | AI   | System arch | pending |
| 2 | 42   | Results | Real | Dashboard   | pending |
```

### 3.7 Ask for confirmation

Use AskUserQuestion to ask the user to:
- Confirm the plan as-is
- Modify prompts or descriptions
- Change image types (ai-generated ↔ real)
- Remove or add insertion points

Apply any changes the user requests, update `updated_at`, and save.

## Step 4: Transition

After the analyze phase is complete, inform the user they can run the generate phase when ready by saying "generate article images" or "生成文章配图".

## Step 5: Generate Images (Phase 2)

### 5.1 Read plan

Determine which plan to use:
1. If the user specifies an article path or slug → load `.claude/blog-image-plans/{slug}.json`
2. If only one plan exists → load it automatically
3. If multiple plans exist and user didn't specify → list plans (Step 2.5) and ask user to choose

If no plan file found, inform the user to run the analyze phase first and stop.

### 5.2 Prepare output directory

```bash
# Determine base output dir from config, then create article subdirectory
# OUTPUT_DIR from .claude/yux-config.json (expand ~), default to "."
# ARTICLE_DIR="$OUTPUT_DIR/{slug}"
mkdir -p "$ARTICLE_DIR"
```

### 5.3 Filter actionable images

Collect all images where:
- `type` is `ai-generated`
- `status` is `pending`

If none are found, inform the user (all images already generated or only `real` type) and stop.

### 5.4 Confirm before proceeding

Display the count of images to generate and ask the user to confirm:
- "Found N pending AI images for '{slug}'. Proceed?"

### 5.5 Detect platform

```bash
uname -s
```

Use `-D` for base64 decode on macOS (Darwin), `-d` on Linux.

### 5.6 Generate each image

For each pending ai-generated image, call OpenRouter API:

```bash
curl -s -o /tmp/blog-image-response.json -w "%{http_code}" \
  https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "google/gemini-3-pro-image-preview",
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
FILENAME="$ARTICLE_DIR/blog-image-<ID>.png"

jq -r '.choices[0].message.images[0].image_url.url' /tmp/blog-image-response.json \
  | sed 's|^data:image/[^;]*;base64,||' \
  | base64 -D > "$FILENAME"   # Use -d on Linux
```

If the above jq path returns nothing, check the raw response structure:

```bash
jq '.choices[0].message | keys' /tmp/blog-image-response.json
```

Verify the file was created and is non-empty with `ls -la "$FILENAME"`.

#### Update plan

After each successful generation, update the image entry in `.claude/blog-image-plans/{slug}.json`:
- Set `status` to `"completed"`
- Set `"file_path"` to the saved image path
- Update `updated_at` timestamp

#### Cleanup temp files

```bash
rm -f /tmp/blog-image-response.json
```

### 5.7 Insert images into article

Read the article file. Process insertions **from bottom to top** (highest line number first) to avoid line number drift.

For each completed image, insert at the specified line using a **relative path** from the article's directory to the image file:

```markdown
![description](./relative/path/to/blog-image-1.png)
```

Write the updated article back to the original file.

### 5.8 Report results

Display a summary of all actions taken:

```
=== Generation Complete: my-article ===

| # | Section | Status | File |
|---|---------|--------|------|
| 1 | Intro   | completed | {output_dir}/my-article/blog-image-1.png |
| 2 | Results | skipped (real) | — |
| 3 | Conclusion | completed | {output_dir}/my-article/blog-image-3.png |

Images inserted into: /path/to/my-article.md
Plan updated: .claude/blog-image-plans/my-article.json
```

## Error Handling

| Situation | Action |
|-----------|--------|
| Article file not found | Ask user for correct path |
| Plan file not found (generate phase) | Instruct user to run analyze phase first |
| Multiple plans, user didn't specify | List plans and ask user to choose |
| API key not set | Show setup instructions, stop |
| API error (401/402/429) | Show specific error, stop all remaining images |
| No image in API response | Likely safety-filtered — show warning, skip this image, continue with next |
| Empty article | Inform user, stop |
