# Linear Start - Begin New Task

Start a new task with Linear issue tracking and proper branch management.

**Usage**: `/linear-start [task description]`

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

### Step 1: Detect User Language

Analyze user input to determine preferred language:
- Chinese characters > 30% → `zh`
- Japanese hiragana/katakana → `ja`
- Korean hangul → `ko`
- Default → `en`

Store as `USER_LANG` for all subsequent messages.

### Step 2: Issue Selection

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

### Step 3a: Search Existing Issues

If user chooses to search:

1. Get search query from user
2. Use Linear MCP to search:
   ```
   mcp__linear__searchIssues(query: "<search terms>")
   ```
3. Display results in a formatted list:
   ```
   Found issues:
   1. [LIN-123] User authentication flow
   2. [LIN-124] Fix login button styling
   3. [LIN-125] Add password reset feature

   Enter issue number to select, or 'n' for new issue:
   ```
4. If user selects an issue, proceed to Step 4

### Step 3b: Create New Issue

If user chooses to create:

1. **Collect issue details**:
   - Title (required): Use task description or ask user
   - Description (optional): Ask for additional context
   - Priority (optional): Urgent, High, Medium, Low, None

2. **Create issue via Linear MCP**:
   ```
   mcp__linear__createIssue(
     title: "<title>",
     description: "<description>",
     priority: <priority_number>
   )
   ```

3. **Get the created issue ID** (e.g., `LIN-456`)

### Step 4: Create Git Branch

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

### Step 5: Update Linear Issue Status

Update the issue status to "In Progress":
```
mcp__linear__updateIssue(
  issueId: "<issue-id>",
  stateId: "<in-progress-state-id>"
)
```

Add a comment to track the start:
```
mcp__linear__createComment(
  issueId: "<issue-id>",
  body: "Started working on this issue.\nBranch: `<branch-name>`"
)
```

### Step 6: Output Summary

Display completion message (in user's language):

**English**:
```
=== Task Started ===

Issue:   LIN-456 - User login implementation
Status:  In Progress
Branch:  feat/LIN-456-user-login

You can now start coding!

Useful commands:
- /linear-status  - Check current status
- /linear-pr      - Create pull request when ready
```

**Chinese**:
```
=== 任务已启动 ===

Issue:   LIN-456 - 用户登录实现
状态:    In Progress
分支:    feat/LIN-456-user-login

现在可以开始编码了！

常用命令：
- /linear-status  - 查看当前状态
- /linear-pr      - 准备好后创建 PR
```

## Error Handling

- **Linear not configured**: Guide to `/mcp` setup
- **Not in git repo**: Ask user to navigate to project directory
- **Branch exists**: Ask if user wants to switch to existing branch
- **Network error**: Suggest retry with specific error message

## Example

```
User: /linear-start implement user authentication

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
