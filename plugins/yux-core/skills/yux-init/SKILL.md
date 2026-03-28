---
name: yux-init
description: "Initialize yux-claude-hub configuration for the current project. Creates .claude/yux-config.json with language and output directory settings. Use when: 'yux init', 'initialize config', 'setup yux', '/yux-init'."
allowed-tools: Read, Write, Glob, AskUserQuestion
---

# Initialize yux Configuration

Set up `.claude/yux-config.json` for the current project. All yux plugins read this file for language and output settings.

**Usage**: `/yux-init`

## Workflow

### Step 1: Check Existing Configuration

Check if `.claude/yux-config.json` exists. If so, show current settings and ask whether to keep or overwrite.

### Step 2: Language Selection

Use AskUserQuestion to select output language:
- English (default) → `"en"`
- 中文 → `"zh"`
- 日本語 → `"ja"`
- 한국어 → `"ko"`

### Step 3: Output Directory (Optional)

Use AskUserQuestion to set a custom output directory for generated files (images, etc.):
- Use current directory (default) → omit `output_dir`
- Custom path (e.g., `~/Desktop/blog-images`) → store as `output_dir`, support `~`

### Step 4: Save Configuration

Create `.claude/` directory if needed, then write `.claude/yux-config.json`:

```json
{
  "language": "zh",
  "output_dir": "~/Desktop/blog-images",
  "created_at": "2026-01-10T10:30:00Z",
  "version": "1.0.0"
}
```

`output_dir` is only included if user specified a custom path.

### Step 5: Confirm

Output confirmation in the selected language. Suggest next steps: `/yux-pm-init`, `/yux-linear-start`.
