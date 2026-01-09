#!/usr/bin/env python3
"""
Check branch protection: warn when modifying files on main/master branch.

This hook doesn't block operations but outputs a warning message.
The warning is shown to Claude who should then warn the user.

Exit codes:
  0 - Allow operation (with optional warning in stdout)
  2 - Block operation (reserved for future strict mode)
"""

import json
import re
import subprocess
import sys
from pathlib import Path

PROTECTED_BRANCHES = ['main', 'master', 'develop', 'release']


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


def is_linear_branch(branch: str) -> bool:
    """Check if branch follows Linear naming convention (contains LIN-xxx)."""
    return bool(re.search(r'LIN-\d+', branch, re.IGNORECASE))


def extract_linear_id(branch: str) -> str | None:
    """Extract Linear issue ID from branch name."""
    match = re.search(r'(LIN-\d+)', branch, re.IGNORECASE)
    return match.group(1).upper() if match else None


def check_local_state_exists(linear_id: str) -> bool:
    """Check if the local state file exists for the given issue ID."""
    state_file = Path(f'.claude/linear-tasks/{linear_id}.json')
    return state_file.exists()


def main():
    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")

    # Only check Write and Edit operations
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    # Get current branch
    branch = get_current_branch()
    if not branch:
        # Not in a git repo or can't determine branch
        sys.exit(0)

    # Check if on protected branch
    if branch.lower() in [b.lower() for b in PROTECTED_BRANCHES]:
        # Output warning (this goes to Claude, not blocking)
        warning = (
            f"[Branch Warning]\n"
            f"You are on the '{branch}' branch.\n"
            f"Consider using /yux-linear-start to create a feature branch.\n"
            f"Direct commits to {branch} may bypass code review."
        )
        print(warning)  # stdout - informational
        # Note: We allow the operation but Claude sees the warning

    # If on a Linear branch, check for local state
    elif is_linear_branch(branch):
        linear_id = extract_linear_id(branch)
        if linear_id and check_local_state_exists(linear_id):
            print(f"[Linear Branch] Working on: {branch}")
        else:
            warning = (
                f"[Linear Branch - No Local State]\n"
                f"Branch: {branch}\n"
                f"Issue: {linear_id}\n"
                f"No local state file found at: .claude/linear-tasks/{linear_id}.json\n"
                f"Run /yux-linear-status to sync state from Linear."
            )
            print(warning)

    sys.exit(0)


if __name__ == "__main__":
    main()
