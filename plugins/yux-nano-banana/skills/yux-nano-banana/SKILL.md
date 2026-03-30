---
name: yux-nano-banana
description: Generate standalone images using OpenRouter API with Google Gemini models. Use for any general-purpose image generation or editing request — e.g., "generate an image of...", "create image", "draw a...", "nano banana", "make an infographic", "生成图片", "画图", "画一个...", "信息卡片", "科普卡片". Supports text-to-image, image editing, and style presets (infographic cards). This is the go-to skill for standalone image creation. Do NOT use when the user wants to add images to an existing blog article (use yux-blog-image instead).
allowed-tools: Bash(curl:*), Bash(base64:*), Bash(jq:*), Bash(which:*), Bash(ls:*), Bash(date:*), Bash(wc:*), Bash(uname:*), Bash(file:*), Read, Write, Glob, AskUserQuestion
---

# Nano Banana - Image Generation

Generate images using OpenRouter API with Google Gemini models.

## CRITICAL: Image Data Safety Rules

**Read `references/image-data-safety.md` before any API call.** It contains safety rules, the fixed API response structure, and common mistakes to avoid.

## Output Directory

Save generated images to the current working directory by default. If the user specifies a custom output path, use that instead (expand `~` to home directory; create directory if it doesn't exist using `mkdir -p`).

## Step 1: Prerequisites Check

### 1.1 Verify required tools

Run `which curl jq base64` to confirm all tools are available. If any are missing, inform the user and stop.

### 1.2 Verify API key

Check if `$OPENROUTER_API_KEY` is set:

```bash
echo "${OPENROUTER_API_KEY:+set}"
```

If empty, inform the user: "Please set `OPENROUTER_API_KEY` in your environment." and **stop immediately**. Never prompt the user to enter the key inline.

## Step 2: Parse User Intent

Determine the operation type and parameters from the user's request:

### 2.1 Operation type

- **Generate**: Create a new image from a text prompt (default)
- **Edit**: Modify an existing image — user provides an image file path and editing instructions

### 2.2 Extract parameters

- **prompt** (required): The text description for image generation/editing
- **model** (optional): User-specified model shorthand (see Model Table below)
- **source image** (optional, for edit): Path to an existing image file
- **aspect ratio / dimensions** (optional): Include in prompt if specified by user
- **style preset** (optional): A predefined style template (see Style Presets below)

## Step 2.5: Style Presets

When the user's request matches a style preset, wrap their content with the preset's prompt template. The user only needs to provide the **topic/content** — the style instructions are injected automatically.

### Available Presets

#### `infographic` — Hand-drawn Infographic Card

**Trigger keywords**: "infographic", "info card", "信息图", "信息卡片", "科普卡片", "手绘卡片", "インフォグラフィック", "인포그래픽"

**Prompt template** (wrap around the user's topic/content):

```
Create a hand-drawn style infographic card in landscape orientation (16:9 ratio).

Subject: {USER_CONTENT}

Style requirements:
- Hand-drawn / sketch illustration style with a warm, friendly, artisanal aesthetic
- Background: beige / cream color with subtle paper grain texture (NOT kraft paper, NO wrinkles or creases)
- NO border or frame around the edges of the card
- Clean, uncluttered layout with generous whitespace
- Use hand-drawn icons, diagrams, and illustrations as the primary way to convey information
- Minimal text — only short labels or annotations where necessary, the illustrations should tell the story
- Color palette: warm earth tones, muted pastels, with occasional accent colors for emphasis
- The overall feel should be like a beautifully illustrated notebook page — approachable and educational
```

**When this preset is detected**:
1. Extract the user's actual topic/content (the subject they want illustrated)
2. Replace `{USER_CONTENT}` in the template with their topic
3. Use the assembled prompt as the final prompt sent to the API
4. The user can still specify model choice (flash/pro) — pro is recommended for this style

## Step 3: Model Selection

| Shorthand | Model ID | When to use |
|-----------|----------|-------------|
| flash | `google/gemini-2.5-flash-image` | User says "flash", "fast", "quick", "快速" |
| pro (default) | `google/gemini-3-pro-image-preview` | Default — highest quality |

If the user does not specify a model, use **pro**.

## Step 4: Build and Execute API Call

### 4.1 Detect platform

```bash
uname -s
```

This determines the `base64` decode flag: `-D` on macOS (Darwin), `-d` on Linux.

### 4.2 Build request payload

For **text-to-image generation**:

```bash
curl -s -o /tmp/nano-banana-response.json -w "%{http_code}" \
  https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "<MODEL_ID>",
    "messages": [
      {
        "role": "user",
        "content": "<USER_PROMPT>"
      }
    ]
  }'
```

For **image editing** (user provides a source image):

1. First verify the source file exists and is a valid image:
   ```bash
   ls "$SOURCE_IMAGE" && file --mime-type "$SOURCE_IMAGE"
   ```
   If the file does not exist or is not an image, inform the user and stop.

2. Encode the source image to base64:
   ```bash
   base64 < /path/to/source.png | tr -d '\n'
   ```
   Store the result in a variable.

3. Then build the request with the image inline:
   ```bash
   curl -s -o /tmp/nano-banana-response.json -w "%{http_code}" \
     https://openrouter.ai/api/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     -d '{
       "model": "<MODEL_ID>",
       "messages": [
         {
           "role": "user",
           "content": [
             {
               "type": "image_url",
               "image_url": {
                 "url": "data:<MIME_TYPE>;base64,<BASE64_DATA>"
               }
             },
             {
               "type": "text",
               "text": "<EDITING_INSTRUCTIONS>"
             }
           ]
         }
       ]
     }'
   ```

**Important**: Always use `-o /tmp/nano-banana-response.json` to save the response to a file. The response contains base64-encoded image data that can be very large and would be truncated in stdout. Use `-w "%{http_code}"` to capture the HTTP status code in stdout.

**Important**: For large base64 payloads (image editing), write the JSON body to a temp file first and use `curl -d @/tmp/nano-banana-request.json` to avoid shell argument length limits.

## Step 5: Parse Response and Save Image

### 5.1 Check HTTP status

Check the HTTP status code returned by curl:

- **200**: Success — continue to extract image
- **401**: Authentication failed — stop
- **402**: Insufficient funds — stop
- **429**: Rate limited — stop
- **Other non-200**: Show the raw error from response, stop

### 5.2 Validate image exists in response

Validate image count (see `references/image-data-safety.md` for response structure):

```bash
jq -r '.choices[0].message.images | length' /tmp/nano-banana-response.json
```

- If `0`, `null`, or fails → safety-filtered. Inform the user and stop.
- If `1` or more → proceed to extraction.

### 5.3 Extract, decode, and save (single pipeline)

Extract the base64 data, strip the data-URI prefix, and decode — all in one pipeline redirected to a file. **No intermediate temp file needed.**

```bash
# OUTPUT_DIR defaults to "." (current directory). If user specified a custom path, expand ~ and ensure it exists:
#   OUTPUT_DIR=$(echo "$USER_SPECIFIED_PATH" | sed "s|^~|$HOME|")
#   mkdir -p "$OUTPUT_DIR"

FILENAME="$OUTPUT_DIR/nano-banana-$(date +%Y%m%d-%H%M%S).png"

jq -r '.choices[0].message.images[0].image_url.url' /tmp/nano-banana-response.json \
  | sed 's|^data:image/[^;]*;base64,||' \
  | base64 -D > "$FILENAME"   # Use -d on Linux
```

Verify the file was created and has reasonable size (should be >100KB for a real image):

```bash
wc -c < "$FILENAME"
```

If the file is 0 bytes or very small, extraction failed — inform the user and stop.

### 5.4 Cleanup

```bash
rm -f /tmp/nano-banana-response.json /tmp/nano-banana-request.json
```

## Step 6: Output Results

Display the result:

```
=== Image Generated ===

File:   /path/to/nano-banana-20260329-143022.png
Size:   256 KB
Model:  google/gemini-3-pro-image-preview
```

## Error Handling Summary

| HTTP Code | Error | Action |
|-----------|-------|--------|
| 401 | Invalid API key | Inform user, stop |
| 402 | Insufficient funds | Inform user, stop |
| 429 | Rate limited | Inform user, stop |
| 200 but no image | Safety filter | Inform user, stop. Do NOT explore alternative jq paths — the response structure is fixed |
| Network failure | Connection error | Inform user, stop |
