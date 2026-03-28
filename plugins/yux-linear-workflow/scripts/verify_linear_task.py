#!/usr/bin/env python3
"""
Verify current Linear task context at session start.

This hook runs on UserPromptSubmit to detect if:
1. The current branch is a Linear branch (contains LIN-xxx)
2. Display branch context and suggest Linear API lookup

Exit codes:
  0 - Always (informational only, never blocks)
"""

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _linear_guard import is_linear_project


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


def main():
    # Skip if not a Linear-active project
    if not is_linear_project():
        sys.exit(0)

    # Get current branch
    branch = get_current_branch()
    if not branch:
        sys.exit(0)

    # Check if this is a Linear branch
    linear_id = extract_linear_id(branch)
    if not linear_id:
        sys.exit(0)

    # Output branch context and suggest Linear API lookup
    print(f"[Linear Branch Detected]")
    print(f"Branch: {branch}")
    print(f"Issue:  {linear_id}")
    print(f"")
    print(f"To load full context: mcp__linear__get_issue(id: \"{linear_id}\")")

    sys.exit(0)


if __name__ == "__main__":
    main()
