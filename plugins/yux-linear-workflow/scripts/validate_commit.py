#!/usr/bin/env python3
"""
Validate git commit messages follow Conventional Commits format.

Supports two formats:
1. Standard: <type>(<scope>): <description>
2. Extended: <emoji> <type>(<scope>): <subject (中文支持)>

Exit codes:
  0 - Allow operation
  2 - Block operation (invalid commit message)
"""

import json
import re
import sys

# Emoji mapping for commit types
VALID_EMOJIS = ['✨', '🐛', '📝', '💄', '♻️', '⚡️', '✅', '📦', '👷', '🔧']

# Conventional Commits pattern (supports optional emoji prefix and Chinese characters)
COMMIT_PATTERN = re.compile(
    r'^'
    r'(?:[✨🐛📝💄♻️⚡️✅📦👷🔧]\s+)?'  # Optional emoji prefix
    r'(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)'
    r'(\([a-zA-Z0-9_-]+\))?'
    r'!?'
    r': .{1,100}',
    re.UNICODE
)

# Pattern to extract commit message from git commit command
COMMIT_MSG_PATTERNS = [
    r'-m\s+"([^"]+)"',      # -m "message"
    r"-m\s+'([^']+)'",      # -m 'message'
    r'-m\s+([^\s]+)',       # -m message (no quotes, single word)
]

# Pattern for HEREDOC format: -m "$(cat <<'EOF' ... EOF )"
HEREDOC_PATTERN = re.compile(
    r'-m\s+"\$\(cat\s+<<[\'"]?EOF[\'"]?\s*\n(.*?)\nEOF\s*\)"',
    re.DOTALL
)


def extract_commit_message(command: str) -> str | None:
    """Extract commit message from git commit command."""
    # Try HEREDOC format first
    heredoc_match = HEREDOC_PATTERN.search(command)
    if heredoc_match:
        # Return only the first line (subject) for validation
        full_message = heredoc_match.group(1).strip()
        return full_message.split('\n')[0]

    # Try standard patterns
    for pattern in COMMIT_MSG_PATTERNS:
        match = re.search(pattern, command)
        if match:
            return match.group(1)
    return None


def is_git_commit_command(command: str) -> bool:
    """Check if command is a git commit."""
    # Normalize whitespace
    cmd = ' '.join(command.split())
    return 'git commit' in cmd and '-m' in cmd


def validate_commit_message(message: str) -> tuple[bool, str]:
    """Validate commit message format."""
    # Skip merge commits
    if message.startswith('Merge '):
        return True, ""

    # Skip fixup/squash commits
    if message.startswith(('fixup!', 'squash!')):
        return True, ""

    # Check conventional commits format
    if not COMMIT_PATTERN.match(message):
        return False, (
            f"Invalid commit format: '{message}'\n"
            f"Expected: [emoji] <type>(<scope>): <description>\n"
            f"Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert\n"
            f"Emojis: ✨ feat, 🐛 fix, 📝 docs, 💄 style, ♻️ refactor, ⚡️ perf, ✅ test, 🔧 chore\n"
            f"Examples:\n"
            f"  feat(auth): add login validation\n"
            f"  ✨ feat(auth): 添加登录验证"
        )

    return True, ""


def main():
    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If no valid JSON, allow operation
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")

    # Only validate Bash commands
    if tool_name != "Bash":
        sys.exit(0)

    command = input_data.get("tool_input", {}).get("command", "")

    # Check if it's a git commit command
    if not is_git_commit_command(command):
        sys.exit(0)

    # Extract commit message
    message = extract_commit_message(command)
    if not message:
        # Can't extract message (might be using -F or editor)
        sys.exit(0)

    # Validate message format
    is_valid, error_msg = validate_commit_message(message)

    if not is_valid:
        print(f"❌ {error_msg}", file=sys.stderr)
        sys.exit(2)

    # Valid commit message
    sys.exit(0)


if __name__ == "__main__":
    main()
