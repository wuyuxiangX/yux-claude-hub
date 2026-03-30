---
name: yux-pm-triage
description: Triage Linear inbox issues with AI classification. Triggers on "pm triage", "triage inbox", "classify issues", "process inbox", "处理反馈".
allowed-tools: Read, Write, Glob, Grep, Bash(git:*), Bash(gh:*), mcp__linear__*
---

# PM Triage

Process inbox issues: classify type, set priority/effort, structure descriptions, and move to Backlog.

Prerequisite: `.claude/linear-config.json` must exist. If missing, show:
  "Please run `/yux-linear-init` first."

## Workflow

### Step 1: Load Config and Labels

```
Read .claude/linear-config.json

mcp__linear__list_issue_labels(team: "<team.id>")
```

Parse labels into categories:
- **Type labels**: Feature, Bug, Epic, Chore, Improvement
- **Func labels**: Frontend, Backend, API, Extension, ML

### Step 2: Fetch Inbox

```
mcp__linear__list_issues(
  project: "<project.id>",
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

If multiple types match, prefer: Bug > Feature > Improvement > Chore.

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
- Detected type, priority, effort, labels
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
  project: "<project.id>",
  state: "Backlog"
)
```

### Step 6: Summary

After all items are processed, display summary:

```
=== Triage Complete ===

Processed: 5 issues

By Type:    Bug: 2  |  Feature: 2  |  Improvement: 1
By Priority: High: 1  |  Medium: 3  |  Low: 1

Moved to Backlog:
  WYX-120  [Bug/High]    Login crash on iOS
  WYX-121  [Feature/Med] Dark mode support
  WYX-122  [Bug/Med]     Typo in settings
```
