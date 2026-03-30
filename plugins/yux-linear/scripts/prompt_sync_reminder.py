#!/usr/bin/env python3
"""
Output Linear sync reminder prompt if the project is Linear-active.

Replaces the inline "type": "prompt" hook in hooks.json with a guarded
"type": "command" that silently exits for non-Linear projects.

Exit codes:
  0 - Always (outputs prompt text to stdout if Linear-active)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _linear_guard import is_linear_project


def main():
    if not is_linear_project():
        sys.exit(0)

    print(
        "If the sync_progress script returned an issue_id, consider posting "
        "a progress summary to Linear using mcp__linear__create_comment "
        "before context compaction."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
