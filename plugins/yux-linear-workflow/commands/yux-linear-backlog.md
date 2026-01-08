# Linear Backlog - View & Recommend Issues

View current project issues and get AI-powered recommendations for what to work on next.

**Usage**: `/yux-linear-backlog [filter]`

## Input

Optional filter from: $ARGUMENTS
- `all` - All non-completed issues (default)
- `mine` - Issues assigned to me
- `urgent` - High priority issues
- `unassigned` - Issues without assignee

## Workflow

### Step 1: Load Team Configuration

1. **Check cached config** in `.claude/linear-config.json`
2. **If no config**, run team discovery (same as `/yux-linear-start` Step 2)
3. Store `LINEAR_TEAM` for API calls

### Step 2: Fetch Issues

Retrieve issues from Linear:

```
mcp__linear__list_issues(
  team: "<LINEAR_TEAM>",
  state: "backlog,todo,in_progress",  // Exclude completed/cancelled
  limit: 50,
  orderBy: "updatedAt"
)
```

For specific filters:
- `mine`: Add `assignee: "me"`
- `urgent`: Add filter for priority 1-2
- `unassigned`: Filter where assignee is null

### Step 3: Enrich Issue Data

For each issue, gather:
- **Priority**: 1=Urgent, 2=High, 3=Medium, 4=Low, 0=None
- **Due date**: If set
- **Cycle**: Current sprint membership
- **Labels**: Bug, Feature, etc.
- **Estimate**: Story points if available
- **Age**: Days since created
- **Comments**: Activity level

### Step 4: Display Issues

Format issues in a table (in user's language):

**English**:
```
=== Linear Backlog (Wyx Team) ===

| # | ID       | Title                        | Priority | Status      | Assignee | Due      |
|---|----------|------------------------------|----------|-------------|----------|----------|
| 1 | LIN-456  | Implement user auth          | Urgent   | In Progress | @you     | Jan 10   |
| 2 | LIN-789  | Fix login page crash         | High     | Todo        | -        | Jan 8    |
| 3 | LIN-123  | Add dark mode support        | Medium   | Backlog     | @alice   | -        |
| 4 | LIN-234  | Refactor API endpoints       | Low      | Todo        | -        | Jan 15   |
| 5 | LIN-567  | Update documentation         | None     | Backlog     | -        | -        |

Total: 5 issues (1 urgent, 1 high, 1 medium, 1 low, 1 none)
```

**Chinese**:
```
=== Linear 待办列表 (Wyx 团队) ===

| # | 编号     | 标题                         | 优先级   | 状态        | 负责人   | 截止日期 |
|---|----------|------------------------------|----------|-------------|----------|----------|
| 1 | LIN-456  | 实现用户认证                 | 紧急     | 进行中      | @你      | 1月10日  |
| 2 | LIN-789  | 修复登录页面崩溃             | 高       | 待办        | -        | 1月8日   |
...

共 5 个问题 (1 紧急, 1 高, 1 中, 1 低, 1 无)
```

### Step 5: AI Recommendation

Analyze issues and provide smart recommendation based on:

**Scoring Algorithm**:
```
score = 0

# Priority weight (highest impact)
if priority == 1 (Urgent): score += 100
if priority == 2 (High):   score += 70
if priority == 3 (Medium): score += 40
if priority == 4 (Low):    score += 20

# Due date urgency
if due_date:
    days_until_due = (due_date - today).days
    if days_until_due < 0:  score += 80  # Overdue!
    if days_until_due <= 1: score += 60
    if days_until_due <= 3: score += 40
    if days_until_due <= 7: score += 20

# Current cycle bonus
if in_current_cycle: score += 30

# Already started bonus (continuity)
if status == "in_progress" and assignee == "me": score += 50

# Bug priority (bugs often block others)
if has_label("bug"): score += 15

# Unassigned penalty (might need discussion first)
if not assignee: score -= 10

# Blocked penalty
if is_blocked: score -= 100
```

**Recommendation Output**:

```
=== Recommended Next Task ===

Based on priority, deadlines, and current sprint:

1. [LIN-789] Fix login page crash
   Priority: High | Due: Tomorrow | Status: Todo
   Reason: High priority bug with imminent deadline

   -> Use `/yux-linear-start LIN-789` to begin

Alternative options:
2. [LIN-456] Implement user auth (already in progress)
3. [LIN-234] Refactor API endpoints (in current sprint)
```

**Chinese**:
```
=== 推荐下一个任务 ===

基于优先级、截止日期和当前迭代分析：

1. [LIN-789] 修复登录页面崩溃
   优先级: 高 | 截止: 明天 | 状态: 待办
   推荐理由: 高优先级 Bug，截止日期临近

   -> 使用 `/yux-linear-start LIN-789` 开始

备选任务:
2. [LIN-456] 实现用户认证 (已在进行中)
3. [LIN-234] 重构 API 端点 (在当前迭代中)
```

### Step 6: Interactive Options

Offer quick actions:

```
What would you like to do?
1. Start recommended task (LIN-789)
2. Start a different task (enter ID)
3. View issue details
4. Refresh list

Enter choice:
```

## Cycle Integration

If the team uses cycles/sprints, also show:

```
=== Current Cycle: Sprint 23 (Jan 1 - Jan 14) ===

Progress: ████████░░ 80% (8/10 issues)
- Completed: 6
- In Progress: 2
- Todo: 2

Sprint issues shown first in the list.
```

## Examples

### Basic usage
```
User: /yux-linear-backlog

Claude: Loading backlog for Wyx team...

=== Linear Backlog ===
[displays table]

=== Recommended ===
[LIN-789] Fix login page crash - High priority, due tomorrow
```

### Filter by assignment
```
User: /yux-linear-backlog mine

Claude: Loading your assigned issues...

=== My Issues (3 total) ===
[displays filtered table]
```

### Urgent only
```
User: /yux-linear-backlog urgent

Claude: Loading urgent issues...

=== Urgent Issues (2 total) ===
[displays high priority items]
```

## Error Handling

- **No issues found**: "Your backlog is empty! Great job, or time to plan new work."
- **Linear not configured**: Guide to setup
- **API error**: Show error and suggest retry
