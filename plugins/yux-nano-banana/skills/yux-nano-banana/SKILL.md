---
name: yux-nano-banana
description: Generate images using OpenRouter API. Triggers: "generate image", "create image", "draw", "nano banana", "infographic", "info card", "生成图片", "画图", "信息图", "信息卡片", "科普卡片", "手绘卡片", "画像生成", "インフォグラフィック", "이미지 생성", "인포그래픽".
allowed-tools: Bash(curl:*), Bash(base64:*), Bash(jq:*), Bash(which:*), Bash(ls:*), Bash(date:*), Bash(wc:*), Bash(uname:*), Bash(file:*), Read, Write, Glob, AskUserQuestion
---

# Nano Banana - Image Generation

Generate images using OpenRouter API with Google Gemini models.

## CRITICAL: Image Data Safety Rules

The API response contains ~1MB base64-encoded image data. If this data is printed to stdout, Claude Code's bash tool will attempt to process it as an image, causing `"Could not process image"` API errors and task failure.

**Rules:**
1. **NEVER** output raw base64/data-URI content to stdout — always redirect jq output to a file
2. **NEVER** use `head`, `cat`, `less`, or `tail` on files containing base64 image data
3. **NEVER** run jq commands that extract `image_url.url` without redirecting to a file (e.g., `> /tmp/file.txt`)
4. **Validate** image extraction by checking **file size** (`wc -c`), not by inspecting content
5. **NEVER** explore the response structure with commands like `jq '.choices[0].message | keys'` — the structure is documented below and does not vary

## Configuration

Before generating output, read `.claude/yux-config.json`:
- If `language` is set, use that language for user-facing messages
- If `output_dir` is set, save generated images to that directory (expand `~` to home directory; create directory if it doesn't exist using `mkdir -p`)
- If `output_dir` is not set, save to the current working directory
- If file doesn't exist, detect from user input or default to English
- Load message templates from `templates/messages.json` in this plugin directory

## Step 1: Prerequisites Check

### 1.1 Verify required tools

Run `which curl jq base64` to confirm all tools are available. If any are missing, inform the user with the `setup.missing_tools` message and stop.

### 1.2 Verify API key

Check if `$OPENROUTER_API_KEY` is set:

```bash
echo "${OPENROUTER_API_KEY:+set}"
```

If empty, display the `setup.missing_api_key` message and **stop immediately**. Never prompt the user to enter the key inline.

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

1. First encode the source image to base64:
   ```bash
   base64 < /path/to/source.png | tr -d '\n'
   ```
   Store the result in a variable. Detect the MIME type using `file --mime-type`.

2. Then build the request with the image inline:
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
- **401**: Authentication failed — show `error.auth_failed` message, stop
- **402**: Insufficient funds — show `error.insufficient_funds` message, stop
- **429**: Rate limited — show `error.rate_limited` message, stop
- **Other non-200**: Show `error.network` message with the raw error from response, stop

### 5.2 Validate image exists in response

The API response structure is fixed and does NOT vary:
- `choices[0].message.content` = empty string (NOT an array — do not try `content[0]`)
- `choices[0].message.images` = array of image objects
- Each image object: `{ "image_url": { "url": "data:image/jpeg;base64,..." } }`

Validate that the response contains images (this outputs only a safe integer):

```bash
jq -r '.choices[0].message.images | length' /tmp/nano-banana-response.json
```

- If the result is `0`, `null`, or the command fails → the content was safety-filtered. Show `error.no_image` message and stop.
- If the result is `1` or more → proceed to extraction.

**DO NOT** run any other jq commands to explore the response structure. The path is always `.choices[0].message.images[0].image_url.url`.

### 5.3 Extract, decode, and save (single pipeline)

Extract the base64 data, strip the data-URI prefix, and decode — all in one pipeline redirected to a file. **No intermediate temp file needed.**

```bash
# Determine output directory from config (output_dir) or use current directory
# If output_dir is set in .claude/yux-config.json, expand ~ and ensure directory exists:
#   OUTPUT_DIR=$(echo "$OUTPUT_DIR_FROM_CONFIG" | sed "s|^~|$HOME|")
#   mkdir -p "$OUTPUT_DIR"
# Otherwise: OUTPUT_DIR="."

FILENAME="$OUTPUT_DIR/nano-banana-$(date +%Y%m%d-%H%M%S).png"

jq -r '.choices[0].message.images[0].image_url.url' /tmp/nano-banana-response.json \
  | sed 's|^data:image/[^;]*;base64,||' \
  | base64 -D > "$FILENAME"   # Use -d on Linux
```

Verify the file was created and has reasonable size (should be >100KB for a real image):

```bash
wc -c < "$FILENAME"
```

If the file is 0 bytes or very small, extraction failed — show `error.no_image` message.

### 5.4 Cleanup

```bash
rm -f /tmp/nano-banana-response.json /tmp/nano-banana-request.json
```

## Step 6: Output Results

Display the result using the `result.success` message template:
- **File path**: Full path to the saved image
- **File size**: Human-readable size (e.g., "256 KB")
- **Model used**: The model ID that was used

## Common Mistakes — DO NOT DO THESE

| Anti-pattern | Why it fails | Correct approach |
|-------------|-------------|-----------------|
| `jq -r '.choices[0].message.images[0].image_url.url' response.json` (no redirect) | Outputs ~1MB base64 to stdout → Claude tries to process as image → API error | Always pipe to `sed` + `base64 -D > file` |
| `jq ... \| head -c 50` to "peek" at data | Even 50 chars of `data:image/...` triggers image processing | Validate with `jq '... \| length'` (returns integer) |
| `jq '.choices[0].message \| keys'` to explore structure | Encourages further exploration; structure is fixed | Trust the documented path: `.choices[0].message.images[0].image_url.url` |
| `jq -r '.choices[0].message.content[0]...'` | `content` is an empty string, NOT an array | Use `.choices[0].message.images[0].image_url.url` |
| `cat /tmp/nano-banana-b64.txt` | Dumps base64 to stdout | Use `wc -c < file` to check size |

## Error Handling Summary

| HTTP Code | Error | Action |
|-----------|-------|--------|
| 401 | Invalid API key | Show `error.auth_failed`, stop |
| 402 | Insufficient funds | Show `error.insufficient_funds`, stop |
| 429 | Rate limited | Show `error.rate_limited`, stop |
| 200 but no image | Safety filter | Show `error.no_image`, stop. Do NOT explore alternative jq paths — the response structure is fixed |
| Network failure | Connection error | Show `error.network`, stop |
