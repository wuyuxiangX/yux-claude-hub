---
name: yux-pm-prd
description: Generate PRD and create Linear issues for a feature. Triggers on "pm prd", "create prd", "plan feature", "feature planning", "创建PRD".
allowed-tools: Read, Write, Glob, Grep, Bash(git:*), Bash(gh:*), mcp__linear__*
---

# PM PRD - Feature Planning with Task Decomposition

Usage: `/yux-pm-prd [topic|issue-id]`

Prerequisite: `.claude/linear-config.json` must exist. If missing, show:
  "Please run `/yux-linear-init` first."

## Input Modes

- **Issue ID** (e.g., `WYX-123`): Fetch via `mcp__linear__get_issue(id: "<issue_id>")`, use title and description as seed.
- **Topic text** (e.g., `User authentication`): Use as seed directly.
- **No args**: Conduct interactive interview -- ask problem, target user, expected outcome, technical constraints, and priority.

## Step 1: Load Configuration

Read `.claude/linear-config.json`. Extract `team.id` and `project.id`.

## Step 2: Gather Requirements

Collect requirements from the chosen input mode. For interactive mode, ask concise questions and accept "skip" for optional fields.

## Step 3: Complexity Detection

- **High** (L/XL effort): Generate full PRD document + Epic + sub-issues
- **Medium** (M effort): Create parent issue with sub-issues, detailed descriptions
- **Low** (S/XS effort): Create single well-described issue

## Step 4: High Complexity Path

Generate PRD content following the template in `../../references/prd-template.md`.

Create Linear document and issues:

```
# Create PRD document (fallback: save as docs/prd-<slug>.md if API fails)
mcp__linear__create_document(
  title: "PRD: <feature_title>",
  content: "<prd_content>",
  project: "<project.id>"
)

# Create parent Epic issue
mcp__linear__create_issue(
  title: "<feature_title>",
  description: "Epic for <feature>.\n\nPRD: <document_link>",
  team: "<team.id>",
  project: "<project.id>",
  labels: ["Epic"],
  priority: <priority>,
  assignee: "me"
)

# Create sub-issues (task breakdown)
For each task:
  mcp__linear__create_issue(
    title: "<task_title>",
    description: "<task_description>\n\n## Acceptance Criteria\n- [ ] ...",
    team: "<team.id>",
    project: "<project.id>",
    parentId: "<epic_issue_id>",
    labels: ["<type_label>"],
    priority: <priority>,
    assignee: "me"
  )
```

## Step 5: Medium/Low Complexity Path

Skip PRD document creation. Create issues directly with structured descriptions containing Goal, Tasks checklist, and Acceptance Criteria sections. For medium complexity, create a parent issue with sub-issues using `parentId`.

## Summary Output

After creation, display:
- Document link (if created)
- Epic issue ID and title
- All sub-issues with effort and priority
- Suggested next actions (`/yux-pm-plan`, `/yux-linear-start`)

See `../../references/prd-template.md` for PRD document template.
