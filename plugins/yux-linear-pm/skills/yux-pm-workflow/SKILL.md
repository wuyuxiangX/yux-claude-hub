---
name: yux-pm-workflow
description: "Auto-triggers for PM workflow. Triggers: 'triage inbox', 'process feedback', 'plan sprint', 'create PRD', 'feature planning', 'initiative overview', 'project status', 'what should I work on', 'prioritize backlog', 'decompose feature'"
allowed-tools:
  - Read
  - Write
  - Bash
  - mcp__linear__*
---

# PM Workflow Skill

Intelligent routing for Product Manager workflows on Linear.

## Trigger Detection

This skill activates when the user's intent matches PM activities:

| Intent Pattern | Suggested Command |
|----------------|-------------------|
| "triage inbox", "process feedback", "classify issues" | `/yux-pm-triage` |
| "plan sprint", "what's next", "capacity planning" | `/yux-pm-plan` |
| "create PRD", "new feature", "decompose feature" | `/yux-pm-prd` |
| "project status", "overview", "how are we doing" | `/yux-pm-overview` |
| "setup PM", "configure initiative" | `/yux-pm-init` |

## Workflow

### Step 1: Check Configuration

First, verify PM workspace is initialized:

```
Check if .claude/pm-config.json exists
```

If not configured:
```
PM workspace not initialized.

Would you like to set it up now? This will:
1. Connect to your Linear workspace
2. Select an Initiative (e.g., Subloom)
3. Configure sub-projects

Run /yux-pm-init to get started.
```

### Step 2: Route to Appropriate Command

Based on detected intent, suggest or execute the relevant command:

**Inbox Processing**:
```
User: "I need to process some feedback"

Detected intent: Inbox triage

Running /yux-pm-triage...
```

**Sprint Planning**:
```
User: "What should I work on next sprint?"

Detected intent: Sprint planning

Running /yux-pm-plan...
```

**Feature Creation**:
```
User: "I want to add user authentication"

Detected intent: New feature PRD

Running /yux-pm-prd "User authentication"...
```

**Status Check**:
```
User: "How's the project going?"

Detected intent: Project overview

Running /yux-pm-overview...
```

### Step 3: Context Awareness

The skill maintains context about:
- Current Initiative and projects
- Recent triage/planning sessions
- In-progress features

This enables follow-up actions:
```
User: "Now add that to the sprint"

Context: Just created PRD for WYX-200

Running /yux-pm-plan with WYX-200 pre-selected...
```

## Quick Actions

For common operations, the skill provides shortcuts:

| Shortcut | Action |
|----------|--------|
| "triage" | `/yux-pm-triage` |
| "plan" | `/yux-pm-plan` |
| "prd" | `/yux-pm-prd` |
| "status" | `/yux-pm-overview` |

## Language Handling

All internal operations use English. User-facing output follows:

```
Read .claude/yux-config.json
language = config.language || "en"
```

Output messages adapt to configured language while keeping code and Linear API calls in English.

## Error Recovery

If a command fails, the skill provides contextual help:

```
Linear connection failed.

Troubleshooting:
1. Check Linear MCP configuration in .mcp.json
2. Verify authentication: /yux-linear-setup
3. Check network connectivity

Would you like to:
1. Retry the operation
2. View configuration
3. Get help
```

## Integration Points

This skill coordinates with:
- **yux-linear-workflow**: Branch creation, PR management after PM planning
- **yux-core**: Language configuration, shared settings

Typical workflow:
1. `/yux-pm-triage` → Process feedback
2. `/yux-pm-prd` → Create feature with decomposed tasks
3. `/yux-pm-plan` → Add to sprint
4. `/yux-linear-start` → Begin development (from yux-linear-workflow)
