#!/usr/bin/env python3
"""Claude Code status line script for Linear workflow.

Displays current Linear task info at the bottom of Claude Code.

Usage in settings.json:
  "statusLine": "python3 /path/to/plugins/yux-linear-workflow/scripts/statusline.py"

Receives JSON on stdin from Claude Code with session data.
Outputs one line of text to display in the status bar.
"""

import json
import os
import re
import subprocess
import sys


def get_main_repo_root(cwd=None):
    """Get main repo root, even when inside a worktree."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-common-dir'],
            capture_output=True, text=True, timeout=3,
            cwd=cwd
        )
        if result.returncode == 0:
            git_common = os.path.abspath(os.path.join(cwd or '.', result.stdout.strip()))
            return os.path.dirname(git_common)
    except Exception:
        pass
    return None


def get_branch(session_data):
    """Extract current branch from session data or git."""
    branch = session_data.get('gitBranch', '')
    if branch:
        return branch
    # Fallback: worktree branch
    wt = session_data.get('worktree')
    if wt and isinstance(wt, dict):
        return wt.get('branch', '')
    return ''


def extract_linear_id(branch):
    """Extract LIN-xxx from branch name."""
    match = re.search(r'LIN-(\d+)', branch, re.IGNORECASE)
    return match.group(0) if match else None


def read_json_file(path):
    """Read and parse a JSON file, return None on failure."""
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def main():
    # Read session data from stdin
    try:
        session_data = json.loads(sys.stdin.read())
    except Exception:
        session_data = {}

    cwd = session_data.get('cwd', None)
    branch = get_branch(session_data)
    linear_id = extract_linear_id(branch)
    repo_root = get_main_repo_root(cwd)

    if not linear_id or not repo_root:
        # No Linear task — show minimal info
        display_branch = branch if branch else 'unknown'
        print(f"No Linear task · {display_branch}")
        return

    # Read task details
    tasks_file = os.path.join(repo_root, '.claude', 'linear-tasks.json')
    tasks_data = read_json_file(tasks_file)

    # Read project config
    config_file = os.path.join(repo_root, '.claude', 'linear-config.json')
    config_data = read_json_file(config_file)

    project_name = ''
    if config_data:
        project_name = config_data.get('project_name', config_data.get('team_name', ''))

    # Find task info
    task = None
    if tasks_data and isinstance(tasks_data.get('tasks'), dict):
        task = tasks_data['tasks'].get(linear_id)

    if task:
        title = task.get('title', '')
        status = task.get('linear_status', 'Unknown')
        pr = task.get('pr_number')

        parts = [linear_id, title[:30], status]
        if pr:
            parts.append(f"PR #{pr}")
        if project_name:
            parts.append(project_name)

        print(' · '.join(parts))
    else:
        # Branch has LIN-xxx but no task in tasks.json
        parts = [linear_id, branch]
        if project_name:
            parts.append(project_name)
        print(' · '.join(parts))


if __name__ == '__main__':
    main()
