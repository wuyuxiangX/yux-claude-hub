---
description: Add note to Linear issue or project
---

# Linear Note - Save Important Information

Save notes, scripts, or important information to Linear as project documents.

**Usage**: `/yux-linear-note [--important] [description]`

## Input

From: $ARGUMENTS (optional)

- `description`: What to save (e.g., "migration script", "deployment notes")
- `--important` flag: Also append summary to Issue description

Examples:
```
/yux-linear-note                           # Interactive mode
/yux-linear-note 记录迁移脚本               # Save migration scripts
/yux-linear-note --important 部署注意事项   # Important: also update Issue description
```

## Workflow

### Step 0: Load Context

1. **Read** `.claude/linear-config.json`:
   ```json
   {
     "team": "Wyx",
     "project": "subloom-api"
   }
   ```

2. **Get current Issue ID** from branch name:
   ```bash
   git branch --show-current
   # Extract: feat/WYX-239-xxx → WYX-239
   ```

3. **Get Issue details**:
   ```
   mcp__linear__get_issue(id: "WYX-239")
   ```

4. **If no description provided**, ask user:
   ```
   What would you like to save to Linear?

   Examples:
   - "migration script" - Database migration files
   - "API changes" - API endpoint modifications
   - "config notes" - Configuration details
   - "deployment warning" - Deployment considerations
   ```

### Step 1: Analyze and Gather Content

Based on user's description, intelligently analyze the codebase to find relevant content.

**Content Analysis Matrix**:

| User Description | Analysis Actions |
|-----------------|------------------|
| migration, 迁移 | Find `migrations/`, `db/migrate/`, SQL files, schema changes |
| API, 接口 | Analyze `git diff` for handler/router changes, find new endpoints |
| config, 配置 | Read config files, environment variables, `.env.example` |
| warning, 注意, 小心 | Summarize breaking changes, edge cases, known issues |
| script, 脚本 | Find shell scripts, deployment scripts, build scripts |
| schema, 模型 | Find model definitions, database schemas, type definitions |

**Analysis Process**:

1. **Identify content type** from description keywords
2. **Search relevant files**:
   ```bash
   # For migrations
   find . -path "*/migrations/*" -name "*.sql" -o -name "*.go"

   # For API changes
   git diff origin/main..HEAD --name-only | grep -E "(handler|router|api)"
   ```
3. **Read and extract** relevant content
4. **Format as markdown** with code blocks

### Step 2: Create Project Document

Create a new document in the project:

```
mcp__linear__create_document(
  title: "[WYX-239] <Type> - <Brief Description>",
  project: "<PROJECT_ID>",
  content: "<content in markdown>",
  icon: "<type-specific-icon>"
)
```

**Title Format**: `[ISSUE_ID] <Type> - <Brief Description>`

**Icon Selection**:

| Type | Icon | Keywords |
|------|------|----------|
| Migration | :floppy_disk: | migration, 迁移, schema, database |
| Config | :gear: | config, 配置, env, settings |
| API | :electric_plug: | api, endpoint, 接口, handler |
| Warning | :warning: | warning, 注意, caution, breaking |
| Script | :scroll: | script, 脚本, deploy, build |
| Note | :memo: | note, 笔记, general |

**Document Content Template**:

```markdown
# <Title>

> Created from Issue [WYX-239](linear_url) on YYYY-MM-DD

## Overview

<Brief description of what this document contains>

## Content

<Main content with code blocks, tables, etc.>

## Related Files

- `path/to/file1.go`
- `path/to/file2.sql`

## Notes

<Any additional context or considerations>
```

### Step 3: Add Issue Comment with Link

Add a comment to the Issue referencing the document:

```
mcp__linear__create_comment(
  issueId: "<ISSUE_UUID>",
  body: "📄 **Document Created**: [<title>](<doc_url>)\n\n**Type**: <type>\n**Summary**: <brief summary>"
)
```

### Step 4: Update Issue Description (if --important)

If `--important` flag is present, append to Issue description:

1. **Get current description**:
   ```
   mcp__linear__get_issue(id: "WYX-239")
   # Extract: issue.description
   ```

2. **Append important notes**:
   ```
   mcp__linear__update_issue(
     id: "<ISSUE_UUID>",
     description: "<existing>\n\n---\n\n## ⚠️ Important Notes\n\n<summary of content>\n\n📄 See: [Full Document](<doc_url>)"
   )
   ```

### Step 5: Output Confirmation

**Success output**:

```
╔══════════════════════════════════════════════════════════════╗
║                    Note Saved Successfully                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Document                                                     ║
║  ──────────────────────────────────────────────────────────  ║
║  Title:   [WYX-239] Migration - capture API schema           ║
║  Type:    Migration                                           ║
║  URL:     https://linear.app/wyx/document/xxx                ║
║                                                               ║
║  Content Saved                                                ║
║  ──────────────────────────────────────────────────────────  ║
║  Files analyzed: 3                                            ║
║  - migrations/001_create_bookmarks.sql                        ║
║  - migrations/002_add_capture_fields.sql                      ║
║  - internal/bookmark/model.go                                 ║
║                                                               ║
║  Issue Updated                                                ║
║  ──────────────────────────────────────────────────────────  ║
║  ✓ Comment added with document link                          ║
║  ✓ Description updated (--important)                         ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝

---
📋 View document: <URL>
```

## Error Handling

### No Issue Context

```
Error: Cannot determine current Issue

You're not on a feature branch associated with a Linear issue.
Please run `/yux-linear-start` first or switch to a feature branch.

Current branch: main
Expected format: feat/WYX-xxx-description
```

### No Relevant Content Found

```
Warning: No relevant content found for "migration script"

Searched locations:
- migrations/ (not found)
- db/migrate/ (not found)
- *.sql files (0 found)

Would you like to:
1. Create an empty document and add content manually
2. Specify different search criteria
3. Cancel
```

### Document Creation Failed

```
Error: Failed to create document

Reason: Project not found or no permission
Project ID: <id>

Please verify:
1. Project exists in Linear
2. You have write access to the project
```

## Multi-language Support

> All output messages follow `.claude/yux-config.json` setting

## Example

```
User: /yux-linear-note 记录迁移脚本

Claude: Analyzing codebase for migration scripts...

Found 2 migration files:
- migrations/001_create_bookmarks.sql
- migrations/002_add_capture_fields.sql

Creating document...

╔══════════════════════════════════════════════════════════════╗
║                    Note Saved Successfully                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Document                                                     ║
║  ──────────────────────────────────────────────────────────  ║
║  Title:   [WYX-239] Migration - capture API schema           ║
║  Type:    Migration                                           ║
║  URL:     https://linear.app/wyx/document/xxx                ║
║                                                               ║
║  Issue Updated                                                ║
║  ──────────────────────────────────────────────────────────  ║
║  ✓ Comment added with document link                          ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝

---
📋 View document: https://linear.app/wyx/document/xxx
```

### Example: Important Note

```
User: /yux-linear-note --important 部署前需要先执行数据库迁移

Claude: Creating important note...

╔══════════════════════════════════════════════════════════════╗
║                    Note Saved Successfully                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Document                                                     ║
║  ──────────────────────────────────────────────────────────  ║
║  Title:   [WYX-239] Warning - Deployment Prerequisites       ║
║  Type:    Warning                                             ║
║  URL:     https://linear.app/wyx/document/xxx                ║
║                                                               ║
║  Issue Updated                                                ║
║  ──────────────────────────────────────────────────────────  ║
║  ✓ Comment added with document link                          ║
║  ✓ Description updated with important notes                  ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝

Issue description now includes:

---
## ⚠️ Important Notes

部署前需要先执行数据库迁移

📄 See: [Full Document](url)
```
