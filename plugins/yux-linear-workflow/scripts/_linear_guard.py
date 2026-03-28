#!/usr/bin/env python3
"""
Shared guard module for Linear workflow hooks.

Determines if the current project is "Linear-active" by checking:
1. .claude/linear-config.json file exists
2. Current git branch matches LIN-* pattern

If none of these conditions are met, hooks should silently pass (exit 0).
"""

import json
import re
import subprocess
from pathlib import Path


def get_main_repo_root() -> Path | None:
    """Get the main repo root, even when inside a worktree."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-common-dir'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            git_common = Path(result.stdout.strip())
            return git_common.parent
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def is_linear_project() -> bool:
    """Check if the current project is Linear-active."""
    # Resolve paths relative to main repo root (worktree-aware)
    repo_root = get_main_repo_root()
    config_base = repo_root if repo_root else Path('.')

    # 1. Check for linear-config.json
    if (config_base / '.claude' / 'linear-config.json').is_file():
        return True

    # 2. Check for linear-tasks.json with active tasks
    tasks_file = config_base / '.claude' / 'linear-tasks.json'
    if tasks_file.is_file():
        try:
            data = json.loads(tasks_file.read_text())
            if data.get('tasks'):
                return True
        except (json.JSONDecodeError, KeyError):
            pass

    # 3. Check if current git branch matches LIN-* pattern
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            if re.search(r'LIN-\d+', branch, re.IGNORECASE):
                return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return False
