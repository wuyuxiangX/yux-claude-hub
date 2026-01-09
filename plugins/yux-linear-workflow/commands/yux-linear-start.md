# Linear Start - Begin New Task

Start a new task with Linear issue tracking and proper branch management.

**Usage**: `/yux-linear-start [task description]`

## Input

Task description from: $ARGUMENTS

If no description is provided, ask the user what they want to work on.

## Prerequisites Check

Before starting, verify:

1. **Linear MCP availability**:
   - Check if Linear MCP server is configured
   - If not configured, guide user to set up Linear OAuth

2. **GitHub CLI (gh)**:
   ```bash
   gh auth status
   ```
   - If not authenticated, prompt: "Please run `gh auth login` first"

3. **Git repository**:
   ```bash
   git rev-parse --is-inside-work-tree
   ```
   - Must be inside a git repository

## Workflow

### Step 0: Mandatory Linear Connection Verification

**This step is REQUIRED before proceeding. If Linear is not available, the workflow MUST stop.**

1. **Test Linear MCP connection**:
   ```
   mcp__linear__list_teams()
   ```

2. **If the call fails or returns empty**:
   - Output error message and stop immediately
   - **DO NOT proceed with the workflow**

   **English**:
   ```
   ❌ Linear Connection Failed

   Cannot connect to Linear. Please check:
   1. Linear MCP server is configured
   2. OAuth authorization is valid

   Run /linear-tools:setup to configure Linear.
   ```

   **Chinese**:
   ```
   ❌ Linear 连接失败

   无法连接到 Linear，请检查：
   1. Linear MCP 是否已配置
   2. OAuth 授权是否有效

   运行 /linear-tools:setup 进行配置
   ```

3. **Only if connection succeeds**: Proceed to Step 1

### Step 1: Detect User Language

Analyze user input to determine preferred language:
- Chinese characters > 30% → `zh`
- Japanese hiragana/katakana → `ja`
- Korean hangul → `ko`
- Default → `en`

Store as `USER_LANG` for all subsequent messages.

### Step 2: Discover Team & Project

**This step is critical for Linear API calls.**

1. **Check for cached config** in `.claude/linear-config.json`:
   ```json
   {
     "team_id": "cfef1fd0-...",
     "team_name": "Wyx",
     "project_id": "optional-project-id"
   }
   ```

2. **If no config exists**, discover automatically:
   ```
   mcp__linear__list_teams()
   ```

3. **Team selection logic**:
   - If only 1 team → use it automatically
   - If multiple teams → ask user to choose:
     ```
     Found multiple Linear teams:
     1. Wyx (cfef1fd0-...)
     2. Engineering (abc123...)

     Which team should we use?
     ```

4. **Optionally discover projects** in the team:
   ```
   mcp__linear__list_projects(team: "<team-id>")
   ```
   - If user's task mentions a project name, try to match it
   - Otherwise, issues will be created without a project

5. **MUST save config** to `.claude/linear-config.json`:
   ```bash
   mkdir -p .claude
   ```
   ```json
   {
     "team_id": "cfef1fd0-...",
     "team_name": "Wyx",
     "project_id": "abc123...",
     "project_name": "subloom-api",
     "created_at": "2024-01-15T10:30:00Z"
   }
   ```
   - Create `.claude/` directory if not exists
   - This file is **REQUIRED** for other Linear commands to work correctly
   - `project_id` and `project_name` are optional but recommended

Store as `LINEAR_TEAM` and `LINEAR_PROJECT` for subsequent calls.

### Step 3: Issue Selection

Present options to user (in detected language):

**English**:
```
How would you like to proceed?
1. Search existing Linear issues
2. Create a new issue

Enter your choice:
```

**Chinese**:
```
请选择操作方式：
1. 搜索现有 Linear Issue
2. 创建新 Issue

请输入选择：
```

### Step 4a: Search Existing Issues

If user chooses to search:

1. Get search query from user (or use task description)
2. Use Linear MCP to search within the team:
   ```
   mcp__linear__list_issues(
     team: "<LINEAR_TEAM>",
     query: "<search terms>"
   )
   ```
3. Display results in a formatted list:
   ```
   Found issues:
   1. [LIN-123] User authentication flow
   2. [LIN-124] Fix login button styling
   3. [LIN-125] Add password reset feature

   Enter issue number to select, or 'n' for new issue:
   ```
4. If user selects an issue:
   - **MANDATORY: Verify the selected issue exists**:
     ```
     mcp__linear__get_issue(id: "<issue-uuid>")
     ```
   - Store issue details:
     - `ISSUE_ID`: e.g., "LIN-123"
     - `ISSUE_UUID`: The full UUID
     - `ISSUE_TITLE`: The issue title
     - `LINEAR_URL`: The Linear issue URL
   - Proceed to Step 5

### Step 4b: Create New Issue

If user chooses to create:

1. **Collect issue details**:
   - Title (required): Use task description or ask user
   - Description (optional): Ask for additional context
   - Priority (optional): Urgent, High, Medium, Low, None

2. **Create issue via Linear MCP** (use team from Step 2):
   ```
   mcp__linear__create_issue(
     title: "<title>",
     description: "<description>",
     team: "<LINEAR_TEAM>",
     project: "<LINEAR_PROJECT>",  // optional
     priority: <priority_number>
   )
   ```

3. **Get the created issue ID** (e.g., `LIN-456`)

4. **MANDATORY: Verify issue creation succeeded**:
   ```
   mcp__linear__get_issue(id: "<issue-uuid>")
   ```
   - If verification fails, output error and **stop the workflow**:
   ```
   ❌ Issue creation failed

   The issue was not created in Linear. Please try again.
   ```
   - Only proceed if the issue is confirmed to exist

5. **Store issue details for later use**:
   - `ISSUE_ID`: e.g., "LIN-456"
   - `ISSUE_UUID`: The full UUID returned by Linear
   - `ISSUE_TITLE`: The issue title
   - `LINEAR_URL`: The Linear issue URL

### Step 5: Create Git Branch

1. **Determine branch type** based on task:
   - `feat/` - New features
   - `fix/` - Bug fixes
   - `docs/` - Documentation
   - `refactor/` - Code refactoring
   - `test/` - Test additions
   - `chore/` - Maintenance tasks

2. **Generate branch name**:
   - Format: `<type>/LIN-<issue-id>-<short-description>`
   - Example: `feat/LIN-456-user-login`
   - Sanitize description: lowercase, replace spaces with hyphens, max 30 chars

3. **Create and checkout branch**:
   ```bash
   git checkout -b <branch-name>
   ```

4. **Push branch to remote**:
   ```bash
   git push -u origin <branch-name>
   ```

### Step 6: Update Linear Issue Status & Save Local State

1. **Update the issue status to "In Progress"**:
   ```
   mcp__linear__update_issue(
     id: "<issue-uuid>",
     state: "In Progress"
   )
   ```

2. **Add a comment to track the start**:
   ```
   mcp__linear__create_comment(
     issueId: "<issue-uuid>",
     body: "Started working on this issue.\nBranch: `<branch-name>`"
   )
   ```

3. **MANDATORY: Save local state file**:

   Create the directory if needed:
   ```bash
   mkdir -p .claude/linear-tasks
   ```

   Write state to `.claude/linear-tasks/<ISSUE_ID>.json`:
   ```json
   {
     "issue_id": "LIN-456",
     "issue_uuid": "cfef1fd0-...",
     "issue_title": "User login implementation",
     "branch_name": "feat/LIN-456-user-login",
     "status": "in_progress",
     "linear_url": "https://linear.app/team/issue/LIN-456",
     "started_at": "2026-01-09T10:30:00Z",
     "verified": true
   }
   ```

   **Note**: This file will be tracked by git and persists across sessions.

### Step 7: Output Summary

Display completion message with verification status (in user's language):

**English**:
```
=== Task Started ===

✓ Linear issue verified: LIN-456
✓ Status updated: In Progress
✓ Local state saved: .claude/linear-tasks/LIN-456.json

Issue:   LIN-456 - User login implementation
Status:  In Progress
Branch:  feat/LIN-456-user-login
URL:     https://linear.app/team/issue/LIN-456

You can now start coding!

---
📋 Next Steps:

\`\`\`
/yux-linear-status
\`\`\`
Check current workflow status

\`\`\`
/yux-linear-pr
\`\`\`
Create a Pull Request when ready
```

**Chinese**:
```
=== 任务已启动 ===

✓ Linear issue 已验证: LIN-456
✓ 状态已更新: In Progress
✓ 本地状态已保存: .claude/linear-tasks/LIN-456.json

Issue:   LIN-456 - 用户登录实现
状态:    In Progress
分支:    feat/LIN-456-user-login
URL:     https://linear.app/team/issue/LIN-456

现在可以开始编码了！

---
📋 下一步 / Next Steps:

\`\`\`
/yux-linear-status
\`\`\`
查看当前工作流状态

\`\`\`
/yux-linear-pr
\`\`\`
准备好后创建 Pull Request
```

## Error Handling

- **Linear not configured**: Guide to `/mcp` setup
- **Not in git repo**: Ask user to navigate to project directory
- **Branch exists**: Ask if user wants to switch to existing branch
- **Network error**: Suggest retry with specific error message

## Example

```
User: /yux-linear-start implement user authentication

Claude: Starting Linear workflow...

How would you like to proceed?
1. Search existing Linear issues
2. Create a new issue

User: 2

Claude: Creating new issue...

Please provide a brief description (or press Enter to use default):
"Implement user authentication with JWT tokens"

User: Implement login/logout with session management

Claude: Creating issue...
✓ Issue created: LIN-456 - Implement user authentication

Select branch type:
1. feat (new feature)
2. fix (bug fix)
3. refactor (code refactoring)

User: 1

Claude: Creating branch...
✓ Branch created: feat/LIN-456-user-auth
✓ Linear status updated: In Progress

=== Task Started ===

Issue:   LIN-456 - Implement user authentication
Status:  In Progress
Branch:  feat/LIN-456-user-auth

You can now start coding!
```
