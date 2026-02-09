---
name: yux-nano-banana
description: Generate images using OpenRouter API. Triggers: "generate image", "create image", "draw", "nano banana", "生成图片", "画图", "画像生成", "이미지 생성".
allowed-tools: Bash(curl:*), Bash(base64:*), Bash(jq:*), Bash(which:*), Bash(ls:*), Bash(date:*), Bash(wc:*), Bash(uname:*), Bash(file:*), Read, Write, Glob, AskUserQuestion
---

# Nano Banana - Image Generation

Generate images using OpenRouter API with Google Gemini models.

## Configuration

Before generating output, read `.claude/yux-config.json`:
- If `language` is set, use that language for user-facing messages
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

## Step 3: Model Selection

| Shorthand | Model ID | When to use |
|-----------|----------|-------------|
| flash (default) | `google/gemini-2.5-flash-preview:image` | Default — fast and cost-effective |
| pro | `google/gemini-2.5-pro-preview:image` | User says "pro", "high quality", "best quality", "高质量", "高品質", "고품질" |

If the user does not specify a model, use **flash**.

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

### 5.2 Extract image data

```bash
jq -r '.choices[0].message.content[] | select(.type == "image_url") | .image_url.url' /tmp/nano-banana-response.json
```

This returns a data URI like `data:image/png;base64,iVBOR...`. If the result is empty or null, the content may have been safety-filtered — show `error.no_image` message.

If the above path returns nothing, also try the text content path — the model might return inline base64 in different structures. Check the raw response structure with:

```bash
jq '.choices[0].message' /tmp/nano-banana-response.json
```

### 5.3 Decode and save

Extract the base64 portion (everything after `base64,`) and decode:

```bash
# Generate output filename
FILENAME="nano-banana-$(date +%Y%m%d-%H%M%S).png"

# Extract base64 data (remove the data:image/...;base64, prefix)
jq -r '.choices[0].message.content[] | select(.type == "image_url") | .image_url.url' /tmp/nano-banana-response.json \
  | sed 's|^data:image/[^;]*;base64,||' \
  | base64 -D > "$FILENAME"   # Use -d on Linux
```

Verify the file was created and is non-empty:

```bash
ls -la "$FILENAME"
```

### 5.4 Cleanup

```bash
rm -f /tmp/nano-banana-response.json /tmp/nano-banana-request.json
```

## Step 6: Output Results

Display the result using the `result.success` message template:
- **File path**: Full path to the saved image
- **File size**: Human-readable size (e.g., "256 KB")
- **Model used**: The model ID that was used

## Error Handling Summary

| HTTP Code | Error | Action |
|-----------|-------|--------|
| 401 | Invalid API key | Show `error.auth_failed`, stop |
| 402 | Insufficient funds | Show `error.insufficient_funds`, stop |
| 429 | Rate limited | Show `error.rate_limited`, stop |
| 200 but no image | Safety filter | Show `error.no_image`, stop |
| Network failure | Connection error | Show `error.network`, stop |
