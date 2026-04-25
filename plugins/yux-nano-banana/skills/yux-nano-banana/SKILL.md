---
name: yux-nano-banana
description: Generate images via OpenRouter API with user-selected models. Supports any OpenRouter image model (Gemini, Flux, etc.), prompt optimization, text-to-image, and image editing. Triggers on "generate image", "create image", "draw", "nano banana", "image generation", "生成图片", "画图", "图像生成", "信息卡片".
allowed-tools: Bash(curl:*), Bash(base64:*), Bash(jq:*), Bash(which:*), Bash(ls:*), Bash(date:*), Bash(wc:*), Bash(uname:*), Bash(file:*), Read, Write, Glob, AskUserQuestion
---

# Nano Banana - Universal Image Generation

Generate images through OpenRouter using any supported image-generation model. The user chooses the model for every run (no silent default), and short or abstract prompts can be optimized into richer visual descriptions before the API call.

## CRITICAL: Image Data Safety Rules

**Read `references/image-data-safety.md` before any API call.** It contains safety rules, the fixed API response structure, and common mistakes to avoid.

## Output Directory

Save generated images to the current working directory by default. If the user specifies a custom output path, use that instead (expand `~` to home directory; create directory if it doesn't exist using `mkdir -p`).

## Step 1: Prerequisites Check

### 1.1 Verify required tools

Run `which curl jq base64` to confirm all tools are available. If any are missing, inform the user and stop.

### 1.2 Verify API key

Resolve the image-generation key, preferring the image-specific variable and falling back to the legacy one for backward compatibility:

```bash
IMAGE_KEY="${OPENROUTER_IMAGE_API_KEY:-$OPENROUTER_API_KEY}"
[ -n "$IMAGE_KEY" ] && echo set
```

If empty, inform the user: "Please set `OPENROUTER_IMAGE_API_KEY` in your environment." and **stop immediately**. Never prompt the user to enter the key inline.

If `$OPENROUTER_IMAGE_API_KEY` is unset but `$OPENROUTER_API_KEY` is set (fallback path), print a one-line deprecation notice: "Using legacy `OPENROUTER_API_KEY`. Please migrate to `OPENROUTER_IMAGE_API_KEY`." and continue.

All subsequent API calls use `Authorization: Bearer $IMAGE_KEY`.

## Step 2: Parse User Intent

Determine the operation type and parameters from the user's request:

### 2.1 Operation type

- **Generate**: Create a new image from a text prompt (default)
- **Edit**: Modify an existing image — user provides an image file path and editing instructions

### 2.2 Extract parameters

- **prompt** (required): The text description for image generation/editing
- **model** (optional): Either a shorthand (`flash`, `pro`) or a full OpenRouter model ID (e.g., `black-forest-labs/flux-1.1-pro`). If not provided, the user is prompted to choose in Step 3 — **there is no silent default**.
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
4. The user still chooses the model in Step 3 — `pro` is recommended for this style

## Step 2.6: Prompt Quality Check & Optimization

Before model selection, evaluate whether the prompt would benefit from optimization. **Skip this step entirely if a style preset (e.g., `infographic`) was applied** — presets already produce rich prompts.

### When to offer optimization

Offer optimization if ANY of these hold:

- Prompt length is under 20 characters
- Prompt lacks visual descriptors (no style, lighting, composition, color, material, or mood keywords)
- Prompt is abstract (e.g., "a beautiful landscape", "a cute animal", "a cool car")
- User explicitly asked to optimize ("优化 prompt", "润色提示词", "make the prompt better", etc.)

Skip optimization when the prompt is already detailed (typically >60 characters with clear visual elements).

### Optimization workflow

1. Produce an enriched prompt that adds visual elements — art style, lighting, composition, color palette, mood, material/texture, and level of detail — while **preserving the user's original subject and intent** (do not change what is being depicted).
2. Use `AskUserQuestion` to show the user both versions with three options:
   - **Use optimized** — proceed with the enriched prompt
   - **Use original** — proceed with the unmodified prompt
   - **Let me edit** — user supplies their own revision (use the optimized version as a starting suggestion)
3. Remember whether the final prompt is `original` or `optimized` for Step 6 output.

### Example

- User: `a cat`
- Optimized: `A photorealistic portrait of a fluffy orange tabby cat sitting on a wooden windowsill, bathed in warm golden-hour sunlight, shallow depth of field, detailed fur texture, soft bokeh background, cozy mood`

## Step 3: Model Selection

The user must choose a model for every run — **do not pick a silent default**.

### 3.1 If the user specified a model

Resolve `$MODEL_ID`:

- **Shorthand** → map to full ID:

  | Shorthand | Model ID |
  |-----------|----------|
  | `flash` | `google/gemini-2.5-flash-image` |
  | `pro` | `google/gemini-3-pro-image-preview` |

- **Full model ID** (contains `/`) → use as-is. Any valid OpenRouter image-generation model works (e.g., `black-forest-labs/flux-1.1-pro`, `google/gemini-2.5-flash-image`). The skill forwards the string directly to OpenRouter; if OpenRouter rejects it, surface the API error to the user.

### 3.2 If the user did NOT specify a model

Use `AskUserQuestion` to require a choice — do not proceed without one. Offer three options:

1. **flash** — `google/gemini-2.5-flash-image` (fast and cost-effective)
2. **pro** — `google/gemini-3-pro-image-preview` (Gemini, highest quality)
3. **Custom** — ask the user for a full OpenRouter model ID in the form `provider/model-name`

Store the resolved value as `$MODEL_ID` for Step 4.

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
  -H "Authorization: Bearer $IMAGE_KEY" \
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
     -H "Authorization: Bearer $IMAGE_KEY" \
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
Model:  <MODEL_ID>
Prompt: <final prompt sent to the API>   [optimized]
```

Append ` [optimized]` to the `Prompt:` line only if Step 2.6 produced an enriched version that the user accepted (or edited from the optimized base). Omit the tag when the original prompt was used.

## Error Handling Summary

| HTTP Code | Error | Action |
|-----------|-------|--------|
| 401 | Invalid API key | Inform user, stop |
| 402 | Insufficient funds | Inform user, stop |
| 429 | Rate limited | Inform user, stop |
| 200 but no image | Safety filter | Inform user, stop. Do NOT explore alternative jq paths — the response structure is fixed |
| Network failure | Connection error | Inform user, stop |
