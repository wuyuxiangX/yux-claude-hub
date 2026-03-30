#!/bin/bash
# Run trigger evaluations for all 16 skills
# Results saved to skill-eval-workspace/results/

SCRIPT_DIR="/Users/wyx/.claude/skills/skill-creator"
WORKSPACE="/Users/wyx/code/Project/yux-claude-hub/skill-eval-workspace"
PLUGINS="/Users/wyx/code/Project/yux-claude-hub/plugins"
RESULTS_DIR="$WORKSPACE/results"

mkdir -p "$RESULTS_DIR"

# Mapping: eval-file -> skill-path
declare -A SKILL_MAP=(
  ["trigger-eval-blog-image"]="$PLUGINS/yux-blog/skills/yux-blog-image"
  ["trigger-eval-blog-oss"]="$PLUGINS/yux-blog/skills/yux-blog-oss"
  ["trigger-eval-blog-writer"]="$PLUGINS/yux-blog/skills/yux-blog-writer"
  ["trigger-eval-video-subtitle"]="$PLUGINS/yux-blog/skills/yux-video-subtitle"
  ["trigger-eval-video-summary"]="$PLUGINS/yux-blog/skills/yux-video-summary"
  ["trigger-eval-linear-commit"]="$PLUGINS/yux-linear-workflow/skills/yux-linear-commit"
  ["trigger-eval-linear-merge"]="$PLUGINS/yux-linear-workflow/skills/yux-linear-merge"
  ["trigger-eval-linear-pr"]="$PLUGINS/yux-linear-workflow/skills/yux-linear-pr"
  ["trigger-eval-linear-start"]="$PLUGINS/yux-linear-workflow/skills/yux-linear-start"
  ["trigger-eval-linear-status"]="$PLUGINS/yux-linear-workflow/skills/yux-linear-status"
  ["trigger-eval-nano-banana"]="$PLUGINS/yux-nano-banana/skills/yux-nano-banana"
  ["trigger-eval-pm-init"]="$PLUGINS/yux-linear-pm/skills/yux-pm-init"
  ["trigger-eval-pm-overview"]="$PLUGINS/yux-linear-pm/skills/yux-pm-overview"
  ["trigger-eval-pm-plan"]="$PLUGINS/yux-linear-pm/skills/yux-pm-plan"
  ["trigger-eval-pm-prd"]="$PLUGINS/yux-linear-pm/skills/yux-pm-prd"
  ["trigger-eval-pm-triage"]="$PLUGINS/yux-linear-pm/skills/yux-pm-triage"
)

TOTAL=${#SKILL_MAP[@]}
COUNT=0

for eval_name in "${!SKILL_MAP[@]}"; do
  COUNT=$((COUNT + 1))
  skill_path="${SKILL_MAP[$eval_name]}"
  eval_file="$WORKSPACE/${eval_name}.json"
  result_file="$RESULTS_DIR/${eval_name}-result.json"

  echo "[$COUNT/$TOTAL] Running: $eval_name"

  cd "$SCRIPT_DIR" && python -m scripts.run_eval \
    --eval-set "$eval_file" \
    --skill-path "$skill_path" \
    --runs-per-query 1 \
    --num-workers 8 \
    --timeout 30 \
    --verbose \
    > "$result_file" 2>&1

  # Extract summary from result
  if [ -f "$result_file" ]; then
    echo "  Done: $(tail -5 "$result_file" | head -3)"
  fi
  echo ""
done

echo "=== All evaluations complete ==="
echo "Results in: $RESULTS_DIR/"
