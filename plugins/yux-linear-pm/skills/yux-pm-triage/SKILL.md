---
name: yux-pm-triage
description: "Triage Linear inbox issues with AI classification — detect type (bug/feature/improvement), assign to sub-projects, set priority and effort, structure descriptions, move from Triage to Backlog. Use when: 'pm triage', 'triage inbox', 'classify issues', 'process inbox', 'linear pm triage', '/yux-pm-triage'."
allowed-tools: Read, Write, Glob, Grep, Bash(git:*), Bash(gh:*), mcp__linear__*
---

# PM Triage

Process inbox issues: classify type, assign to sub-projects, set priority/effort, structure descriptions, and move to Backlog.

Prerequisite: `.claude/pm-config.json` must exist (created by yux-pm-init). If missing, instruct user to run pm init.

## Workflow

### Step 1: Load Config and Labels

```
Read .claude/pm-config.json

mcp__linear__list_issue_labels(team: "<team_id>")
```

Parse labels into categories:
- **Type labels**: Feature, Bug, Epic, Chore, Improvement
- **Func labels**: Frontend, Backend, API, Extension, ML

### Step 2: Fetch Inbox

```
mcp__linear__list_issues(
  team: "<team_id>",
  state: "Triage",
  limit: 20,
  orderBy: "createdAt"
)
```

If empty, report clean inbox and stop.

Display inbox summary table (ID, title, created date) and ask user to process all or select specific items.

### Step 3: AI Analysis

For each selected issue, analyze these factors:

**Type Detection** (keyword-based):
- Bug: "crash", "error", "fail", "broken", "崩溃", "错误", "失败"
- Feature: "add", "new", "support", "希望", "能不能", "新增"
- Improvement: "improve", "better", "optimize", "优化", "改进"
- Chore: "update", "upgrade", "migrate", "更新", "升级"

**Project Assignment** (keyword-based):
- Frontend: "page", "UI", "button", "style", "页面", "显示", "样式"
- Backend: "API", "database", "server", "接口", "数据库"
- Extension: "popup", "extension", "插件", "扩展"
- ML: "model", "prediction", "recommend", "模型", "推荐", "分析"

**Priority Assessment**:
- Urgent: Security issues, data loss, complete feature broken
- High: Core flow affected, many users impacted
- Medium: Feature request with clear value, non-critical bugs
- Low: Nice-to-have, cosmetic issues

**Effort Estimation** (T-shirt sizing):
- XS: < 2 hours (typo fix, config change)
- S: 2-8 hours (small bug, minor feature)
- M: 1-3 days (medium feature, complex bug)
- L: 3-7 days (large feature, refactoring)
- XL: > 1 week (epic-level work)

### Step 4: Confirm Per Issue

For each issue, display:
- Detected type, project(s), priority, effort, labels
- Structured description (Problem / Context / Acceptance Criteria)

Ask user to apply, reject, or edit before proceeding.

### Step 5: Apply Changes

On confirmation, update the issue in Linear:

```
mcp__linear__update_issue(
  id: "<issue_id>",
  description: "<structured_description>",
  priority: <priority_number>,
  labels: ["<type_label_id>", "<func_label_id>"],
  project: "<primary_project_id>",
  state: "Backlog"
)
```

### Step 6: Multi-Project Issues

If an issue affects multiple projects, offer two options:
1. **Keep as Epic** in the primary project — sub-issues created later via prd workflow.
2. **Create sub-issues now** — one per affected project, linked to the parent.

### Step 7: Summary

After all items are processed, display: total processed count, breakdown by type and priority, and list of issues moved to Backlog with their assigned projects.
