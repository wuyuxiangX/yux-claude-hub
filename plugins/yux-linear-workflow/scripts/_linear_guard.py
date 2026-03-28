#!/usr/bin/env python3
"""
Shared guard module for Linear workflow hooks.

Determines if the current project is "Linear-active" by checking:
1. .claude/linear-config.json file exists
2. Current git branch matches LIN-* pattern

If none of these conditions are met, hooks should silently pass (exit 0).
"""

import re
import subprocess
from pathlib import Path


def is_linear_project() -> bool:
    """Check if the current project is Linear-active."""
    # 1. Check for linear-config.json
    if Path('.claude/linear-config.json').is_file():
        return True

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
