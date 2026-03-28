---
name: yux-pm-prd
description: "Generate PRD with smart cross-project task decomposition for Linear PM initiatives. Analyzes feature requirements, identifies relevant sub-projects by tech stack matching, creates Epic + sub-issues in Linear. Use when: 'pm prd', 'create prd', 'decompose feature', 'feature prd', 'linear pm prd', '/yux-pm-prd'."
allowed-tools: Read, Write, Glob, Grep, Bash(git:*), Bash(gh:*), mcp__linear__*
---

# PM PRD - Feature PRD with Cross-Project Task Decomposition

Usage: `/yux-pm-prd [topic|issue-id]`

Prerequisite: `.claude/pm-config.json` must exist (run `/yux-pm-init` if missing).

## Input Modes

- **Issue ID** (e.g., `WYX-123`): Fetch via `mcp__linear__get_issue(id: "<issue_id>")`, use title and description as seed.
- **Topic text** (e.g., `User authentication`): Use as seed directly.
- **No args**: Conduct interactive interview -- ask problem, target user, expected outcome, technical constraints, and priority.

## Step 1: Load Configuration

Read `.claude/pm-config.json`. Extract initiative info, available projects with tech stacks, and team ID.

## Step 2: Gather Requirements

Collect requirements from the chosen input mode. For interactive mode, ask concise questions and accept "skip" for optional fields.

## Step 3: Project Relevance Detection

```
For each project in Initiative:
  relevance_score = 0

  # Tech stack matching
  if feature_needs_api and project.tech contains "Backend":
    relevance_score += 80
  if feature_needs_ui and project.tech contains "Frontend":
    relevance_score += 80
  if feature_needs_extension and project.tech contains "Extension":
    relevance_score += 60
  if feature_needs_ml and project.tech contains "ML":
    relevance_score += 70

  # Keyword matching from feature description
  for keyword in project_keywords[project.name]:
    if keyword in feature_description:
      relevance_score += 20

  if relevance_score > 50:
    include_project(project)
```

## Step 4: Complexity Detection

- **High** (3+ projects, L/XL effort): Generate full PRD document + Epic + sub-issues
- **Medium** (1-2 projects, M effort): Create structured issues with detailed descriptions, no PRD doc
- **Low** (single project, S/XS effort): Create single well-described issue

## Step 5: High Complexity Path

Generate PRD content following the template in `references/prd-template.md`.

Create Linear document and issues:

```
# Create PRD document
mcp__linear__create_document(
  title: "PRD: <feature_title>",
  content: "<prd_content>",
  project: "<primary_project_id>"
)

# Create parent Epic issue
mcp__linear__create_issue(
  title: "<feature_title>",
  description: "Epic for <feature>.\n\nPRD: <document_link>",
  team: "<team_id>",
  labels: ["Epic"],
  priority: <priority>,
  assignee: "me"
)

# Create sub-issues per relevant project
For each relevant_project:
  mcp__linear__create_issue(
    title: "[<project_name>] <task_title>",
    description: "<task_description>",
    team: "<team_id>",
    project: "<project_id>",
    parentId: "<epic_issue_id>",
    labels: ["<type_label>", "<func_label>"],
    priority: <priority>,
    assignee: "me"
  )
```

## Step 6: Medium/Low Complexity Path

Skip PRD document creation. Create issues directly with structured descriptions containing Goal, Tasks checklist, and Acceptance Criteria sections. For medium complexity, create a parent issue with sub-issues per project using `parentId`.

## Summary Output

After creation, display:
- Document link (if created)
- Epic issue ID and title
- All sub-issues with project, effort, and priority
- Suggested next actions (`/yux-pm-plan`, `/yux-linear-start`)

See `references/prd-template.md` for PRD document template.
