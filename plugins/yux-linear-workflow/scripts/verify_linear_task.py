#!/usr/bin/env python3
"""
Verify current Linear task context at session start.

This hook runs on UserPromptSubmit to detect if:
1. The current branch is a Linear branch (contains LIN-xxx)
2. A corresponding local state file exists
3. Display task context to help Claude understand the current work

Exit codes:
  0 - Always (informational only, never blocks)
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def get_current_branch() -> str | None:
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def extract_linear_id(branch: str) -> str | None:
    """Extract Linear issue ID from branch name (e.g., LIN-123)."""
    match = re.search(r'(LIN-\d+)', branch, re.IGNORECASE)
    return match.group(1).upper() if match else None


def get_state_file(linear_id: str) -> Path:
    """Get the path to the local state file for a given issue ID."""
    return Path(f'.claude/linear-tasks/{linear_id}.json')


def load_state(state_file: Path) -> dict | None:
    """Load and parse the state file."""
    try:
        if state_file.exists():
            return json.loads(state_file.read_text())
    except (json.JSONDecodeError, IOError):
        pass
    return None


def main():
    # Get current branch
    branch = get_current_branch()
    if not branch:
        # Not in a git repo or can't determine branch
        sys.exit(0)

    # Check if this is a Linear branch
    linear_id = extract_linear_id(branch)
    if not linear_id:
        # Not a Linear branch, nothing to report
        sys.exit(0)

    # Look for local state file
    state_file = get_state_file(linear_id)
    state = load_state(state_file)

    if state:
        # State file exists and matches
        print(f"[Linear Task Context]")
        print(f"Issue:  {linear_id} - {state.get('issue_title', 'Unknown')}")
        print(f"Branch: {branch}")
        print(f"Status: {state.get('status', 'unknown')}")
        if state.get('linear_url'):
            print(f"URL:    {state.get('linear_url')}")
        print(f"")
        print(f"To verify Linear status: mcp__linear__get_issue(id: \"{state.get('issue_uuid')}\")")
    else:
        # Linear branch but no local state
        print(f"[Linear Branch Detected]")
        print(f"Branch: {branch}")
        print(f"Issue:  {linear_id}")
        print(f"")
        print(f"No local state file found at: {state_file}")
        print(f"Run /yux-linear-status to sync state from Linear.")

    sys.exit(0)


if __name__ == "__main__":
    main()
