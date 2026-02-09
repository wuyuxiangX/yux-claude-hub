---
name: yux-blog-oss
description: Upload images to Alibaba Cloud OSS. Triggers: "upload to oss", "upload images to oss", "oss upload", "上传到oss", "上传图片到oss", "上传博客图片".
allowed-tools: Read, Write, Glob, Bash(curl:*), Bash(openssl:*), Bash(jq:*), Bash(which:*), Bash(date:*), Bash(uname:*), Bash(file:*), Bash(ls:*), Bash(wc:*), Bash(basename:*), Bash(printf:*), AskUserQuestion
---

# Blog OSS — Upload Images to Alibaba Cloud OSS

Upload images to Alibaba Cloud OSS via REST API. Supports two modes: automatic batch upload from blog-image-plan.json, or manual upload of specific files.

## Configuration

Before generating output, read `.claude/yux-config.json`:
- If `language` is set, use that language for user-facing messages
- If file doesn't exist, detect from user input or default to English

## Step 1: Prerequisites Check

### 1.1 Verify required tools

Run `which curl openssl jq` to confirm all tools are available. If any are missing, inform the user and stop.

### 1.2 Verify environment variables

Check the following required environment variables:

```bash
echo "${ALIYUN_OSS_ACCESS_KEY_ID:+set}"
echo "${ALIYUN_OSS_ACCESS_KEY_SECRET:+set}"
echo "${ALIYUN_OSS_BUCKET:+set}"
echo "${ALIYUN_OSS_ENDPOINT:+set}"
```

All four must be set. If any are missing, display the setup guide below and **stop immediately**:

```
Missing OSS credentials. Add them to ~/.claude/settings.json:

{
  "env": {
    "ALIYUN_OSS_ACCESS_KEY_ID": "LTAI5t...",
    "ALIYUN_OSS_ACCESS_KEY_SECRET": "your-secret",
    "ALIYUN_OSS_BUCKET": "my-blog-bucket",
    "ALIYUN_OSS_ENDPOINT": "oss-cn-hangzhou.aliyuncs.com",
    "ALIYUN_OSS_CDN_DOMAIN": "cdn.myblog.com"  // optional
  }
}
```

Optional variable:
- `ALIYUN_OSS_CDN_DOMAIN`: Custom CDN domain for cleaner URLs. If not set, URLs use `https://{BUCKET}.{ENDPOINT}/{ObjectName}`.

## Step 2: Determine Upload Mode

Parse the user's request to determine the upload mode:

| Mode | Condition | Source |
|------|-----------|--------|
| **A: Blog plan** | No explicit file paths provided AND `.claude/blog-image-plan.json` exists | Upload all images with `status: "completed"` from the plan |
| **B: Specific files** | User provides explicit file paths (e.g., "upload ./img1.png ./img2.png to oss") | Upload the specified files |

Decision logic:
1. If the user provided explicit file paths → **Mode B**
2. If no explicit paths and `.claude/blog-image-plan.json` exists → **Mode A**
3. If no explicit paths and no plan file → inform the user: "No files to upload. Provide file paths or run 'analyze article images' first." and stop

## Step 3: Collect and Validate Files

### Mode A: From blog plan

Read `.claude/blog-image-plan.json` and extract file paths:

```bash
jq -r '.images[] | select(.status == "completed") | .file_path' .claude/blog-image-plan.json
```

If no completed images are found, inform the user: "No completed images found in the plan. Run 'generate article images' first." and stop.

### Mode B: From user input

Parse the file paths from the user's message.

### Validate all files

For each file:

1. Verify the file exists:
   ```bash
   ls -la "$FILE_PATH"
   ```
   If the file does not exist, warn the user and skip this file.

2. Detect MIME type:
   ```bash
   file --mime-type -b "$FILE_PATH"
   ```
   Expected types: `image/png`, `image/jpeg`, `image/gif`, `image/webp`, `image/svg+xml`.

## Step 4: Upload Each File via OSS REST API

For each validated file, perform the following:

### 4.1 Generate object name

```bash
FILENAME=$(basename "$FILE_PATH")
OBJECT_NAME="blog-images/$(date +%Y%m%d-%H%M%S)-${FILENAME}"
```

### 4.2 Compute date header

Generate an RFC 2822 formatted date:

```bash
DATE=$(date -u '+%a, %d %b %Y %H:%M:%S GMT')
```

### 4.3 Detect MIME type

```bash
CONTENT_TYPE=$(file --mime-type -b "$FILE_PATH")
```

### 4.4 Build signature string

Per OSS V1 signature spec, the StringToSign is:

```
PUT\n\n{Content-Type}\n{Date}\n/{Bucket}/{ObjectName}
```

Note: The second line (Content-MD5) is empty.

### 4.5 Compute HMAC-SHA1 signature

```bash
SIGNATURE=$(printf "PUT\n\n${CONTENT_TYPE}\n${DATE}\n/${ALIYUN_OSS_BUCKET}/${OBJECT_NAME}" \
  | openssl dgst -sha1 -hmac "$ALIYUN_OSS_ACCESS_KEY_SECRET" -binary \
  | openssl base64 -A)
```

### 4.6 Execute upload

```bash
HTTP_CODE=$(curl -s -o /tmp/oss-upload-response.xml -w "%{http_code}" \
  -X PUT \
  -T "$FILE_PATH" \
  -H "Date: ${DATE}" \
  -H "Content-Type: ${CONTENT_TYPE}" \
  -H "Authorization: OSS ${ALIYUN_OSS_ACCESS_KEY_ID}:${SIGNATURE}" \
  "https://${ALIYUN_OSS_BUCKET}.${ALIYUN_OSS_ENDPOINT}/${OBJECT_NAME}")
```

### 4.7 Check response

- **200 or 204**: Upload successful
- **403**: Authentication error — check the response body for details:
  ```bash
  cat /tmp/oss-upload-response.xml
  ```
  Common causes: wrong credentials, clock skew, incorrect endpoint. Show the error and stop.
- **404**: Bucket not found — "Bucket '${ALIYUN_OSS_BUCKET}' not found. Check ALIYUN_OSS_BUCKET and ALIYUN_OSS_ENDPOINT." and stop.
- **Other non-2xx**: Show the response body and stop.

### 4.8 Build public URL

```bash
if [ -n "$ALIYUN_OSS_CDN_DOMAIN" ]; then
  URL="https://${ALIYUN_OSS_CDN_DOMAIN}/${OBJECT_NAME}"
else
  URL="https://${ALIYUN_OSS_BUCKET}.${ALIYUN_OSS_ENDPOINT}/${OBJECT_NAME}"
fi
```

### 4.9 Cleanup

```bash
rm -f /tmp/oss-upload-response.xml
```

## Step 5: Update Article (Mode A Only)

This step only applies when uploading from the blog plan.

### 5.1 Read article

Read the article file from the plan's `article_path`:

```bash
jq -r '.article_path' .claude/blog-image-plan.json
```

### 5.2 Replace local image paths

For each uploaded image, replace the local path in the article with the CDN URL:

- Find: `![description](./local-filename.png)` (or relative path)
- Replace with: `![description](https://cdn-url/object-name)`

Match by filename — the local path in the article should correspond to the `file_path` in the plan.

### 5.3 Update plan file

For each uploaded image, update its entry in `.claude/blog-image-plan.json`:
- Set `status` to `"uploaded"`
- Add `"cdn_url"` field with the public URL
- Add `"uploaded_at"` field with the current ISO 8601 timestamp

Write the updated plan back to `.claude/blog-image-plan.json`.

### 5.4 Save article

Write the updated article content back to the original article file.

## Step 6: Display Results

Present a summary table:

```
| # | File | Size | CDN URL | Status |
|---|------|------|---------|--------|
| 1 | blog-image-1.png | 245 KB | https://cdn.example.com/blog-images/... | uploaded |
| 2 | blog-image-2.png | 182 KB | https://cdn.example.com/blog-images/... | uploaded |
```

For Mode A, also note: "Article updated with CDN URLs: {article_path}"

## Error Handling

| Error | Action |
|-------|--------|
| Missing env vars | Show `~/.claude/settings.json` setup guide, stop |
| Missing tools (curl/openssl/jq) | List missing tools, stop |
| HTTP 403 (SignatureDoesNotMatch) | "Check credentials and endpoint region", stop |
| HTTP 404 (NoSuchBucket) | "Bucket not found — verify ALIYUN_OSS_BUCKET and ALIYUN_OSS_ENDPOINT", stop |
| File not found | Skip file, warn user, continue with remaining files |
| Plan file missing (Mode A) | "No image plan found. Run 'analyze article images' first.", stop |
| No completed images in plan | "No completed images to upload. Run 'generate article images' first.", stop |
| Network error | Show curl error output, stop |
