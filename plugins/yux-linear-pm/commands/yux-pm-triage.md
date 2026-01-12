---
description: Triage and classify inbox issues
---

# PM Triage - Process Inbox Issues

Process inbox/triage issues: classify type, assign to projects, set priority, and structure descriptions.

**Usage**: `/yux-pm-triage`

## Prerequisites

1. PM workspace initialized via `/yux-pm-init`
2. Config file exists at `.claude/pm-config.json`

## Workflow

### Step 1: Load Configuration and Labels

```
# Load PM config
Read .claude/pm-config.json

# Fetch available labels for classification
mcp__linear__list_issue_labels(team: "<team_id>")
```

Parse labels into categories:
- **Type labels**: Feature, Bug, Epic, Chore, Improvement, etc.
- **Func labels**: Frontend, Backend, API, Extension, ML, etc.

### Step 2: Fetch Inbox Issues

```
mcp__linear__list_issues(
  team: "<team_id>",
  state: "Triage",
  limit: 20,
  orderBy: "createdAt"
)
```

If no inbox items:
```
=== Inbox Empty ===

No items to triage. Your inbox is clean!

Next actions:
  /yux-pm-overview - View project status
  /yux-pm-plan     - Plan next sprint
```

### Step 3: Display Inbox Summary

> Output language follows `.claude/yux-config.json` setting

```
=== Inbox Triage (<count> items) ===

| # | ID      | Title                        | Created    |
|---|---------|------------------------------|------------|
| 1 | WYX-123 | 希望支持深色模式             | 2 days ago |
| 2 | WYX-124 | 登录页面有时候会崩溃         | 1 day ago  |
| 3 | WYX-125 | 能不能加个数据导出功能       | 3 days ago |

Process all? (y) or select specific items (1,2,3):
```

### Step 4: AI Analysis for Each Issue

For each selected issue, AI analyzes and suggests:

**Analysis Factors**:
1. **Type Detection**: Keywords → Bug/Feature/Improvement/Chore
   - "崩溃", "错误", "失败", "crash", "error" → Bug
   - "希望", "能不能", "新增", "add", "new" → Feature
   - "优化", "改进", "improve", "better" → Improvement
   - "更新", "升级", "update", "upgrade" → Chore

2. **Project Assignment**: Analyze which sub-projects are affected
   - Frontend keywords: "页面", "UI", "显示", "样式", "page", "button"
   - Backend keywords: "API", "接口", "数据库", "database", "server"
   - Extension keywords: "插件", "扩展", "popup", "extension"
   - ML keywords: "模型", "推荐", "分析", "model", "prediction"

3. **Priority Assessment**:
   - Urgent: Security issues, data loss, complete feature broken
   - High: Core flow affected, many users impacted
   - Medium: Feature request with clear value, non-critical bugs
   - Low: Nice-to-have, cosmetic issues

4. **Effort Estimation** (T-shirt sizing):
   - XS: < 2 hours (typo fix, config change)
   - S: 2-8 hours (small bug, minor feature)
   - M: 1-3 days (medium feature, complex bug)
   - L: 3-7 days (large feature, refactoring)
   - XL: > 1 week (epic-level work)

### Step 5: Display Analysis Result

```
=== WYX-124: 登录页面有时候会崩溃 ===

AI Analysis:
┌────────────────────────────────────────────────┐
│ Type:     Bug                                  │
│ Projects: subloom-web, subloom-api             │
│           (Frontend crash may involve API)     │
│ Priority: High (Core flow affected)            │
│ Effort:   S (1 day)                            │
│ Labels:   Type→Bug, Func→Frontend              │
└────────────────────────────────────────────────┘

Structured Description:
┌────────────────────────────────────────────────┐
│ ## Problem                                     │
│ Login page occasionally crashes, affecting     │
│ user experience and blocking core workflow.    │
│                                                │
│ ## Context                                     │
│ - Reported frequency: Intermittent             │
│ - Affected area: Login flow                    │
│ - User impact: Cannot complete login           │
│                                                │
│ ## Acceptance Criteria                         │
│ - [ ] Login flow stable with no crashes        │
│ - [ ] Error states handled gracefully          │
│ - [ ] Add error logging for debugging          │
└────────────────────────────────────────────────┘

Apply? (y/n/edit):
```

### Step 6: Apply Changes to Linear

When user confirms:

```
mcp__linear__update_issue(
  id: "<issue_id>",
  description: "<structured_description>",
  priority: <priority_number>,
  labels: ["<type_label_id>", "<func_label_id>"],
  project: "<primary_project_id>",
  state: "Backlog",
  assignee: "me"
)
```

Output:
```
✓ WYX-124 updated:
  - Type: Bug
  - Project: subloom-web
  - Priority: High
  - State: Backlog
  - Labels: Type→Bug, Func→Frontend

Processing next item...
```

### Step 7: Handle Multi-Project Issues

If an issue affects multiple projects:

```
=== WYX-126: 用户认证功能 ===

AI Analysis:
┌────────────────────────────────────────────────┐
│ Type:     Epic (Cross-project feature)         │
│ Projects: subloom-api, subloom-web,            │
│           subloom-extension                    │
│ Priority: High                                 │
│ Effort:   L (5-7 days)                         │
└────────────────────────────────────────────────┘

This issue spans multiple projects. Options:

1. Keep as Epic in primary project (subloom-api)
   → Sub-issues created later via /yux-pm-prd

2. Create sub-issues now for each project
   → WYX-126-1 [api] Backend auth
   → WYX-126-2 [web] Frontend auth
   → WYX-126-3 [ext] Extension auth

Choose (1/2):
```

### Step 8: Triage Summary

After processing all items:

```
=== Triage Complete ===

Processed: 3 items

Summary:
  - 1 Bug (High priority)
  - 1 Feature (Medium priority)
  - 1 Epic (decomposed to 3 sub-issues)

Issues moved to Backlog:
  - WYX-123 → subloom-web (Feature)
  - WYX-124 → subloom-web (Bug)
  - WYX-125 → subloom-api (Feature)

Next actions:
  /yux-pm-overview - View updated status
  /yux-pm-plan     - Add issues to sprint
```

## Edit Mode

When user selects "edit":

```
Edit WYX-124:

Current analysis:
  Type: Bug → [enter to keep, or type new]
  Project: subloom-web → [enter to keep, or type new]
  Priority: High → [enter to keep, or 1-4]

Description preview:
[shows structured description]

Edit description? (y/n):
```

## Batch Mode

For quick processing without individual confirmation:

```
User: /yux-pm-triage --batch

Claude: === Batch Triage Mode ===

Processing 3 items with AI defaults...

| ID      | Type    | Project     | Priority | Effort |
|---------|---------|-------------|----------|--------|
| WYX-123 | Feature | subloom-web | Medium   | M      |
| WYX-124 | Bug     | subloom-web | High     | S      |
| WYX-125 | Feature | subloom-api | Medium   | M      |

Apply all? (y/n/review specific):
```

## Error Handling

### No Labels Found
```
Warning: No Type/Func labels found in your Linear workspace.

Continuing without label assignment.
Consider creating labels in Linear for better organization:
  - Type: Bug, Feature, Epic, Chore, Improvement
  - Func: Frontend, Backend, API, etc.
```

### Issue Update Failed
```
Error updating WYX-124: <error message>

Options:
1. Retry
2. Skip this issue
3. Cancel triage

Choose:
```

### Config Not Found
```
PM workspace not initialized.

Run /yux-pm-init to configure your Initiative and sub-projects.
```

## Examples

### Basic usage
```
User: /yux-pm-triage

Claude: === Inbox Triage (3 items) ===

| # | ID      | Title                    | Created    |
|---|---------|--------------------------|------------|
| 1 | WYX-123 | 希望支持深色模式         | 2 days ago |
| 2 | WYX-124 | 登录页面有时候会崩溃     | 1 day ago  |
| 3 | WYX-125 | 能不能加个数据导出功能   | 3 days ago |

Process all? (y) or select specific (1,2,3): y

Processing WYX-123...

=== WYX-123: 希望支持深色模式 ===

AI Analysis:
┌────────────────────────────────────────────────┐
│ Type:     Feature                              │
│ Projects: subloom-web, subloom-extension       │
│ Priority: Low (Nice-to-have)                   │
│ Effort:   M (2-3 days)                         │
│ Labels:   Type→Feature, Func→Frontend          │
└────────────────────────────────────────────────┘

...
```

### Select specific items
```
User: /yux-pm-triage

Claude: === Inbox Triage (5 items) ===
...
Process all? (y) or select specific (1,2,3): 2,3

Processing WYX-124...
```
