#!/usr/bin/env python3
"""
Sync progress to Linear before context compaction.

This hook extracts the Linear issue ID from the current branch and
outputs a JSON instruction for Claude to post a progress summary.

Exit codes:
  0 - Always allow (this is informational only)
"""

import json
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
    if match:
        return match.group(1).upper()
    return None


def get_commit_count(base_branch: str = 'main') -> int:
    """Get number of commits on current branch since diverging from base."""
    try:
        result = subprocess.run(
            ['git', 'rev-list', '--count', f'{base_branch}..HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass
    return 0


def get_recent_commits(count: int = 5) -> list[str]:
    """Get recent commit messages."""
    try:
        result = subprocess.run(
            ['git', 'log', f'-{count}', '--pretty=format:%s'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


def main():
    # Read input from stdin (PreCompact payload)
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    # Skip if not a Linear-active project
    if not is_linear_project():
        sys.exit(0)

    # Get current branch
    branch = get_current_branch()
    if not branch:
        sys.exit(0)

    # Extract Linear issue ID
    issue_id = extract_linear_id(branch)
    if not issue_id:
        # Not on a Linear branch, skip sync
        sys.exit(0)

    # Gather progress info
    commit_count = get_commit_count()
    recent_commits = get_recent_commits(5)

    # Output instruction for Claude
    output = {
        "action": "sync_to_linear",
        "issue_id": issue_id,
        "branch": branch,
        "commit_count": commit_count,
        "recent_commits": recent_commits,
        "instruction": (
            f"Before context compaction, consider syncing progress to Linear issue {issue_id}.\n"
            f"Branch: {branch}\n"
            f"Commits: {commit_count}\n"
            f"Recent work:\n" + "\n".join(f"  - {c}" for c in recent_commits if c) + "\n\n"
            f"Use mcp__linear__create_comment to post a progress summary if significant work was done."
        )
    }

    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
