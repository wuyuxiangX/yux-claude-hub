# Image Data Safety Rules

The API response contains ~1MB base64-encoded image data. If this data is printed to stdout, Claude Code's bash tool will attempt to process it as an image, causing `"Could not process image"` API errors and task failure.

## Rules

1. **NEVER** output raw base64/data-URI content to stdout — always redirect jq output to a file
2. **NEVER** use `head`, `cat`, `less`, or `tail` on files containing base64 image data
3. **NEVER** run jq commands that extract `image_url.url` without redirecting to a file (e.g., `> /tmp/file.txt`)
4. **Validate** image extraction by checking **file size** (`wc -c`), not by inspecting content
5. **NEVER** explore the response structure with commands like `jq '.choices[0].message | keys'` — the structure is documented below and does not vary

## API Response Structure (fixed, does NOT vary)

- `choices[0].message.content` = empty string (NOT an array — do not try `content[0]`)
- `choices[0].message.images` = array of image objects
- Each image object: `{ "image_url": { "url": "data:image/jpeg;base64,..." } }`

Validate image count (outputs only a safe integer):
```bash
jq -r '.choices[0].message.images | length' /tmp/response.json
```

## Common Mistakes — DO NOT DO THESE

| Anti-pattern | Why it fails | Correct approach |
|-------------|-------------|-----------------|
| `jq -r '.choices[0].message.images[0].image_url.url' response.json` (no redirect) | Outputs ~1MB base64 to stdout → Claude tries to process as image → API error | Always pipe to `sed` + `base64 -D > file` |
| `jq ... \| head -c 50` to "peek" at data | Even 50 chars of `data:image/...` triggers image processing | Validate with `jq '... \| length'` (returns integer) |
| `jq '.choices[0].message \| keys'` to explore structure | Encourages further exploration; structure is fixed | Trust the documented path: `.choices[0].message.images[0].image_url.url` |
| `jq -r '.choices[0].message.content[0]...'` | `content` is an empty string, NOT an array | Use `.choices[0].message.images[0].image_url.url` |
| `cat /tmp/image-b64.txt` | Dumps base64 to stdout | Use `wc -c < file` to check size |
