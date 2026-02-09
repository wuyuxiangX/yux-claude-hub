#!/usr/bin/env python3
"""
Output Linear workflow reminder prompt if the project is Linear-active.

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
        "Check if Linear workflow is relevant:\n"
        "1. If user mentions task/issue/feature work, remind about /yux-linear-start\n"
        "2. If on a Linear branch (LIN-xxx), acknowledge the context\n"
        "3. If discussing PR/merge, remind about /yux-linear-pr or /yux-linear-merge\n"
        "Only add reminders if truly relevant."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
