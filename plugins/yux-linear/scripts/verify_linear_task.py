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

    # Show multi-task context if available
    from _linear_guard import get_main_repo_root
    repo_root = get_main_repo_root()
    config_base = repo_root if repo_root else os.getcwd()
    tasks_file = os.path.join(str(config_base), '.claude', 'linear-tasks.json')
    if os.path.isfile(tasks_file):
        import json
        try:
            with open(tasks_file) as f:
                data = json.load(f)
            tasks = data.get('tasks', {})
            if len(tasks) > 1:
                print()
                print(f"[{len(tasks)} Active Tasks]")
                for tid, task in tasks.items():
                    pr_info = f"  PR #{task['pr_number']}" if task.get('pr_number') else ""
                    print(f"  {tid}  {task.get('branch', '?'):<40s} {task.get('linear_status', '?')}{pr_info}")
        except (json.JSONDecodeError, KeyError):
            pass
    else:
        print(f"")
        print(f"To load full context: mcp__linear__get_issue(id: \"{linear_id}\")")

    sys.exit(0)


if __name__ == "__main__":
    main()
