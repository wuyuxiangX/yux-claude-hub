---
name: yux-ci-monitor
description: Monitor CI/CD status for pull requests with error reporting. Triggers: "check CI", "CI status", "workflow status", "monitor CI", "检查CI", "CI状态", "查看构建".
allowed-tools: Read, Bash(gh:*)
---

# CI/CD Monitor

Check GitHub Actions and other CI/CD status for the current pull request.

## Overview

This skill provides a one-time CI status check. For continuous monitoring during merge, use `/yux-linear-merge` which handles polling automatically via subagent.

## Configuration

Before generating output, read `.claude/yux-config.json`:
- If `language` is set, output in that language
- If file doesn't exist, detect from user input or default to English

## Usage

Triggered manually via:
- "check CI status"
- "what's the CI status"
- "检查CI状态"

## Workflow

### Step 1: Get PR Information

```bash
gh pr view --json number,headRefName,state
```

If no PR found:
```
No pull request found for current branch.
Use /yux-linear-pr to create one.
```

### Step 2: Check CI Status

```bash
gh pr checks <pr-number> --json name,state,conclusion,startedAt,completedAt
```

### Step 3: Display Status

**All passed:**
```
=== CI Status ===

All 5 checks passed

├── ✓ lint          12s
├── ✓ build         45s
├── ✓ test          3m 20s
├── ✓ e2e           4m 5s
└── ✓ deploy        10s

Ready to merge! Use /yux-linear-merge
```

**Some running:**
```
=== CI Status ===

3 of 5 checks complete

├── ✓ lint          12s
├── ✓ build         45s
├── ○ test          (running)
├── ○ e2e           (pending)
└── ○ deploy        (pending)

CI is still running. Use /yux-linear-merge when ready - it will wait for CI to complete.
```

**Failed:**
```
=== CI Status ===

test check failed

├── ✓ lint          12s
├── ✓ build         45s
├── ✗ test          ← Failed
├── ⊘ e2e           (skipped)
└── ⊘ deploy        (skipped)

Fix the failing tests and push again.
```

**No CI configured:**
```
No CI checks configured for this repository.
You can proceed with /yux-linear-merge directly.
```

## Status Symbols

| Symbol | Meaning |
|--------|---------|
| ✓ | Check passed |
| ✗ | Check failed |
| ○ | Running or pending |
| ⊘ | Skipped or cancelled |

## Multi-language Support

> Output language follows `.claude/yux-config.json` setting

All status messages and suggestions are output in the configured language.

## Note

This skill only shows current CI status once. It does NOT poll for updates.

For merge operations that need to wait for CI, use `/yux-linear-merge` - it delegates to a subagent that handles CI polling automatically.
