---
description: Create feature PRD with task decomposition
---

# PM PRD - Generate PRD with Cross-Project Task Decomposition

Generate Product Requirements Document with automatic task decomposition across sub-projects.

**Usage**: `/yux-pm-prd [topic|issue-id]`

## Input

From $ARGUMENTS:
- `<topic>` - Free-form topic for new feature (e.g., "User authentication")
- `<issue-id>` - Existing issue ID to expand into PRD (e.g., "WYX-123")
- No argument - Start interactive interview

## Key Feature

**Smart Cross-Project Decomposition**: A single feature like "Login" automatically creates issues across multiple relevant projects (api + web + extension).

## Prerequisites

1. PM workspace initialized via `/yux-pm-init`
2. Config file exists at `.claude/pm-config.json`

## Workflow

### Step 1: Load Configuration

```
Read .claude/pm-config.json
```

Extract:
- Initiative info
- Available projects with tech stack
- Team ID

### Step 2: Gather Requirements

**Option A: From Issue ID**
```
mcp__linear__get_issue(id: "<issue_id>")
```

Extract existing title and description as starting point.

**Option B: From Topic**
Use provided topic as starting point.

**Option C: Interactive Interview**

> Output language follows `.claude/yux-config.json` setting

```
=== PRD: New Feature ===

Let's define your feature. Answer these questions:

1. What problem are you solving?
   > [user input]

2. Who is the target user?
   > [user input or "skip" for default: all users]

3. What's the expected outcome/goal?
   > [user input]

4. Any technical constraints or requirements?
   > [user input or "skip"]

5. What's the rough priority? (high/medium/low)
   > [user input]
```

### Step 3: AI Analysis and Decomposition

Based on gathered requirements and Initiative projects:

**Project Relevance Detection**:
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

**Complexity Detection**:
- **High** (needs full PRD): Epic-level, 3+ projects, L/XL effort
- **Medium** (structured description): 1-2 projects, M effort
- **Low** (simple description): Single project, S/XS effort

### Step 4: Display Decomposition Preview

```
=== PRD: User Authentication ===

Based on your Initiative (Subloom), this feature involves:

┌─ subloom-api (Go/Backend) ──────────────────┐
│ Tasks:                                       │
│ • OAuth callback endpoint implementation    │
│ • JWT token generation and validation       │
│ • User model and database schema            │
│ • Session management                        │
│                                              │
│ Effort: M (2-3 days)                        │
└──────────────────────────────────────────────┘

┌─ subloom-web (Next.js/Frontend) ────────────┐
│ Tasks:                                       │
│ • Login page UI with OAuth buttons          │
│ • OAuth redirect flow handling              │
│ • Auth state management (context/store)     │
│ • Protected route wrapper                   │
│                                              │
│ Effort: M (2-3 days)                        │
└──────────────────────────────────────────────┘

┌─ subloom-extension (React/Extension) ───────┐
│ Tasks:                                       │
│ • Sync auth token from web app              │
│ • Show login status in popup                │
│ • Handle token refresh                      │
│                                              │
│ Effort: S (1 day)                           │
└──────────────────────────────────────────────┘

Total Effort: L (5-7 days)
Complexity: High → Full PRD will be generated

Create PRD and issues? (y/n/edit):
```

### Step 5: Generate PRD Document

For High complexity, create Linear Document:

```markdown
# User Authentication

## Overview
Enable users to authenticate using Google OAuth to access personalized features.

## Problem Statement
Users cannot access personalized features without authentication. Current
anonymous-only access limits feature scope.

## Goals
- Allow users to sign in with Google OAuth
- Persist authentication across sessions
- Sync auth state across web and extension

## Non-Goals
- Email/password authentication (future)
- Multi-factor authentication (future)
- Social login other than Google (future)

## User Stories
1. As a user, I want to sign in with my Google account
2. As a user, I want to stay signed in across browser sessions
3. As a user, I want the extension to recognize my logged-in state

## Technical Design

### Backend (subloom-api)
- OAuth callback endpoint: `GET /auth/callback`
- JWT generation with RS256
- User table schema with google_id field

### Frontend (subloom-web)
- Login page at `/login`
- AuthContext for state management
- ProtectedRoute HOC

### Extension (subloom-extension)
- Token sync via chrome.storage
- Auth status in popup header

## Acceptance Criteria
- [ ] User can sign in with Google
- [ ] JWT token issued and stored securely
- [ ] Token refreshes before expiry
- [ ] Extension syncs auth state from web
- [ ] Logout clears all sessions

## Timeline
- Backend: 2-3 days
- Frontend: 2-3 days
- Extension: 1 day
- Integration & Testing: 1 day

Total: ~1 week

## Open Questions
1. Token expiry duration?
2. Rate limiting on auth endpoints?
```

### Step 6: Create in Linear

```
# Create Linear Document (PRD)
mcp__linear__create_document(
  title: "PRD: User Authentication",
  content: "<prd_content>",
  project: "<primary_project_id>"
)

# Create parent Epic issue
mcp__linear__create_issue(
  title: "User Authentication",
  description: "Epic for user authentication feature.\n\nPRD: <document_link>",
  team: "<team_id>",
  labels: ["Epic"],
  priority: 2,
  assignee: "me"
)

# Create sub-issues for each project
For each relevant_project:
  mcp__linear__create_issue(
    title: "[<project_name>] <task_title>",
    description: "<task_description>\n\n**Parent Epic**: <epic_link>",
    team: "<team_id>",
    project: "<project_id>",
    parentId: "<epic_issue_id>",
    labels: ["<type_label>", "<func_label>"],
    priority: 2,
    assignee: "me"
  )
```

### Step 7: Output Summary

```
✓ PRD created!

Document: https://linear.app/wyx/document/prd-user-auth-xxx

Epic: WYX-200 (User Authentication)

Sub-issues created:
┌──────────────────────────────────────────────┐
│ WYX-201 [subloom-api] OAuth & JWT impl       │
│         Effort: M | Priority: High           │
│                                              │
│ WYX-202 [subloom-web] Login page & auth flow │
│         Effort: M | Priority: High           │
│                                              │
│ WYX-203 [subloom-extension] Auth token sync  │
│         Effort: S | Priority: Medium         │
└──────────────────────────────────────────────┘

All issues linked to Epic WYX-200.

Next actions:
  /yux-pm-plan       - Add to sprint
  /yux-linear-start WYX-201 - Start first task
```

## Medium/Low Complexity Handling

For simpler features, skip full PRD:

```
=== Feature: Dark Mode Support ===

Complexity: Medium (2 projects, M effort)
→ Creating structured issues (no PRD document)

┌─ subloom-web ────────────────────────────────┐
│ Title: Implement dark mode toggle            │
│ Description:                                 │
│   ## Goal                                    │
│   Add dark mode support with system pref    │
│   detection                                  │
│                                              │
│   ## Tasks                                   │
│   - [ ] Add theme toggle in settings        │
│   - [ ] Implement CSS variables for themes  │
│   - [ ] Persist preference in localStorage  │
│                                              │
│ Effort: M | Priority: Low                   │
└──────────────────────────────────────────────┘

┌─ subloom-extension ──────────────────────────┐
│ Title: Sync dark mode from web               │
│ Description:                                 │
│   ## Goal                                    │
│   Sync theme preference from web app         │
│                                              │
│   ## Tasks                                   │
│   - [ ] Read theme from chrome.storage      │
│   - [ ] Apply theme to popup                │
│                                              │
│ Effort: S | Priority: Low                   │
└──────────────────────────────────────────────┘

Create these issues? (y/n/edit):
```

## Edit Mode

When user selects "edit":

```
Edit PRD: User Authentication

What would you like to edit?
1. Scope (add/remove projects)
2. Tasks for specific project
3. Priority/Effort estimates
4. Requirements/Goals

Choose:
```

Example for scope edit:
```
Current projects: subloom-api, subloom-web, subloom-extension

Available projects:
  [x] subloom-api
  [x] subloom-web
  [x] subloom-extension
  [ ] subloom-ml
  [ ] subloom-obsidian

Toggle with project name, or 'done' to finish:
> subloom-obsidian
Added subloom-obsidian

> done
Regenerating decomposition with new scope...
```

## Examples

### From topic
```
User: /yux-pm-prd User authentication

Claude: Analyzing "User authentication" for Subloom Initiative...

[displays decomposition]

Create PRD and issues? (y/n/edit): y

✓ PRD created!
[displays summary]
```

### From existing issue
```
User: /yux-pm-prd WYX-150

Claude: Loading issue WYX-150...

Issue: "Add export functionality"
Current description: "Users want to export their data"

Expanding into full PRD...

[displays decomposition based on existing issue]
```

### Interactive mode
```
User: /yux-pm-prd

Claude: === New Feature PRD ===

Let's define your feature.

1. What problem are you solving?
> Users can't share their content with others

2. Who is the target user?
> Content creators

...

Analyzing requirements...
[displays decomposition]
```

## Error Handling

### Issue Not Found
```
Issue WYX-999 not found.

Please check the issue ID and try again, or start fresh:
  /yux-pm-prd "Your feature topic"
```

### No Projects Match
```
Warning: Could not identify relevant projects for this feature.

The feature may be:
1. Infrastructure/DevOps (not project-specific)
2. Too broad to decompose
3. Outside current Initiative scope

Options:
1. Create single issue in primary project
2. Manually select projects
3. Cancel and refine requirements

Choose:
```

### Config Not Found
```
PM workspace not initialized.

Run /yux-pm-init to configure your Initiative.
```
