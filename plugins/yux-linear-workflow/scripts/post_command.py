#!/usr/bin/env python3
"""
Post-command hook to detect PR/merge operations and remind about Linear status updates.

This hook analyzes the output of gh commands and provides guidance
for updating Linear issue status accordingly.

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
    """Extract Linear issue ID from branch name."""
    match = re.search(r'(LIN-\d+)', branch, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def detect_pr_create(command: str, output: str) -> dict | None:
    """Detect if a PR was created and extract info."""
    if 'gh pr create' not in command:
        return None

    # Extract PR URL from output
    url_match = re.search(r'(https://github\.com/[^\s]+/pull/\d+)', output)
    if url_match:
        pr_url = url_match.group(1)
        pr_number = pr_url.split('/')[-1]
        return {
            "action": "pr_created",
            "pr_url": pr_url,
            "pr_number": pr_number
        }
    return None


def detect_pr_merge(command: str, output: str) -> dict | None:
    """Detect if a PR was merged."""
    if 'gh pr merge' not in command:
        return None

    # Check for successful merge indicators
    if any(x in output.lower() for x in ['merged', 'successfully merged', 'pull request #']):
        return {
            "action": "pr_merged"
        }
    return None


def detect_git_push(command: str, output: str) -> dict | None:
    """Detect git push operations."""
    if not ('git push' in command or command.startswith('git push')):
        return None

    return {
        "action": "pushed"
    }


def main():
    # Read input from stdin (PostToolUse payload)
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # Skip if not a Linear-active project
    if not is_linear_project():
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")

    # Only process Bash commands
    if tool_name != "Bash":
        sys.exit(0)

    command = input_data.get("tool_input", {}).get("command", "")
    output = input_data.get("tool_output", {}).get("stdout", "")

    # Get branch and Linear ID
    branch = get_current_branch()
    issue_id = extract_linear_id(branch) if branch else None

    # Detect command type
    result = None

    if pr_info := detect_pr_create(command, output):
        result = pr_info
        result["recommendation"] = (
            f"PR #{pr_info['pr_number']} created!\n"
            f"URL: {pr_info['pr_url']}\n"
        )
        if issue_id:
            result["recommendation"] += (
                f"\n📋 Update Linear issue {issue_id}:\n"
                f"  - Status → In Review\n"
                f"  - Add PR link as comment\n"
                f"Use /yux-linear-status to monitor CI."
            )
            result["issue_id"] = issue_id

    elif merge_info := detect_pr_merge(command, output):
        result = merge_info
        result["recommendation"] = "PR merged successfully!\n"
        if issue_id:
            result["recommendation"] += (
                f"\n✅ Complete Linear workflow for {issue_id}:\n"
                f"  - Status → Done\n"
                f"  - Add completion comment\n"
                f"  - Delete local branch: git branch -d {branch}"
            )
            result["issue_id"] = issue_id

    elif push_info := detect_git_push(command, output):
        result = push_info
        if issue_id:
            result["recommendation"] = (
                f"Code pushed to {branch}.\n"
                f"If a PR exists, CI will run automatically."
            )
            result["issue_id"] = issue_id

    # Output recommendation if any
    if result:
        print(json.dumps(result, indent=2))

    sys.exit(0)


if __name__ == "__main__":
    main()
