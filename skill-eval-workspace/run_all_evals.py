#!/usr/bin/env python3
"""Run trigger evaluations for all 20 skills and aggregate results."""

import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/Users/wyx/code/Project/yux-claude-hub/skill-eval-workspace")
PLUGINS = Path("/Users/wyx/code/Project/yux-claude-hub/plugins")
SCRIPT_DIR = Path("/Users/wyx/.claude/skills/skill-creator")
RESULTS_DIR = WORKSPACE / "results"
RESULTS_DIR.mkdir(exist_ok=True)

SKILL_MAP = {
    "trigger-eval-blog-image": PLUGINS / "yux-blog/skills/yux-blog-image",
    "trigger-eval-blog-oss": PLUGINS / "yux-blog/skills/yux-blog-oss",
    "trigger-eval-blog-writer": PLUGINS / "yux-blog/skills/yux-blog-writer",
    "trigger-eval-video-subtitle": PLUGINS / "yux-blog/skills/yux-video-subtitle",
    "trigger-eval-video-summary": PLUGINS / "yux-blog/skills/yux-video-summary",
    "trigger-eval-linear-commit": PLUGINS / "yux-linear-workflow/skills/yux-linear-commit",
    "trigger-eval-linear-merge": PLUGINS / "yux-linear-workflow/skills/yux-linear-merge",
    "trigger-eval-linear-pr": PLUGINS / "yux-linear-workflow/skills/yux-linear-pr",
    "trigger-eval-linear-start": PLUGINS / "yux-linear-workflow/skills/yux-linear-start",
    "trigger-eval-linear-status": PLUGINS / "yux-linear-workflow/skills/yux-linear-status",
    "trigger-eval-nano-banana": PLUGINS / "yux-nano-banana/skills/yux-nano-banana",
    "trigger-eval-pm-init": PLUGINS / "yux-linear-pm/skills/yux-pm-init",
    "trigger-eval-pm-overview": PLUGINS / "yux-linear-pm/skills/yux-pm-overview",
    "trigger-eval-pm-plan": PLUGINS / "yux-linear-pm/skills/yux-pm-plan",
    "trigger-eval-pm-prd": PLUGINS / "yux-linear-pm/skills/yux-pm-prd",
    "trigger-eval-pm-triage": PLUGINS / "yux-linear-pm/skills/yux-pm-triage",
    "trigger-eval-publish": PLUGINS / "yux-publish/skills/yux-publish",
    "trigger-eval-publish-wechat": PLUGINS / "yux-publish/skills/yux-publish-wechat",
    "trigger-eval-publish-zhihu": PLUGINS / "yux-publish/skills/yux-publish-zhihu",
    "trigger-eval-publish-xiaohongshu": PLUGINS / "yux-publish/skills/yux-publish-xiaohongshu",
}

all_results = {}
total = len(SKILL_MAP)

for i, (eval_name, skill_path) in enumerate(SKILL_MAP.items(), 1):
    eval_file = WORKSPACE / f"{eval_name}.json"
    result_file = RESULTS_DIR / f"{eval_name}-result.json"

    print(f"[{i}/{total}] {eval_name}...", file=sys.stderr, flush=True)

    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "scripts.run_eval",
                "--eval-set", str(eval_file),
                "--skill-path", str(skill_path),
                "--runs-per-query", "1",
                "--num-workers", "8",
                "--timeout", "30",
                "--verbose",
            ],
            capture_output=True,
            text=True,
            cwd=str(SCRIPT_DIR),
            timeout=300,
        )

        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            result_file.write_text(json.dumps(data, indent=2))
            all_results[eval_name] = data
            s = data["summary"]
            print(f"  -> {s['passed']}/{s['total']} passed", file=sys.stderr, flush=True)
        else:
            print(f"  -> FAILED: {result.stderr[-200:]}", file=sys.stderr, flush=True)
            all_results[eval_name] = {"error": result.stderr[-500:]}

    except subprocess.TimeoutExpired:
        print(f"  -> TIMEOUT", file=sys.stderr, flush=True)
        all_results[eval_name] = {"error": "timeout"}
    except Exception as e:
        print(f"  -> ERROR: {e}", file=sys.stderr, flush=True)
        all_results[eval_name] = {"error": str(e)}

# Aggregate summary
print("\n" + "=" * 60, file=sys.stderr)
print("TRIGGER EVALUATION SUMMARY", file=sys.stderr)
print("=" * 60, file=sys.stderr)

total_passed = 0
total_cases = 0
tp_passed = 0
tp_total = 0
tn_passed = 0
tn_total = 0
skill_scores = []

for name, data in sorted(all_results.items()):
    if "error" in data:
        print(f"  {name}: ERROR - {data['error'][:80]}", file=sys.stderr)
        continue

    s = data["summary"]
    total_passed += s["passed"]
    total_cases += s["total"]

    # Break down by should_trigger
    for r in data["results"]:
        if r["should_trigger"]:
            tp_total += 1
            if r["pass"]:
                tp_passed += 1
        else:
            tn_total += 1
            if r["pass"]:
                tn_passed += 1

    rate = s["passed"] / s["total"] * 100 if s["total"] > 0 else 0
    skill_scores.append((name, rate, s["passed"], s["total"]))
    status = "PASS" if rate >= 80 else "WARN" if rate >= 60 else "FAIL"
    print(f"  [{status}] {name}: {s['passed']}/{s['total']} ({rate:.0f}%)", file=sys.stderr)

print(f"\nOverall: {total_passed}/{total_cases} ({total_passed/total_cases*100:.1f}%)" if total_cases > 0 else "", file=sys.stderr)
print(f"True Positive (should trigger):  {tp_passed}/{tp_total} ({tp_passed/tp_total*100:.1f}%)" if tp_total > 0 else "", file=sys.stderr)
print(f"True Negative (should NOT trigger): {tn_passed}/{tn_total} ({tn_passed/tn_total*100:.1f}%)" if tn_total > 0 else "", file=sys.stderr)

# Write aggregate JSON
aggregate = {
    "summary": {
        "total_skills": len([d for d in all_results.values() if "error" not in d]),
        "total_cases": total_cases,
        "total_passed": total_passed,
        "overall_rate": round(total_passed / total_cases * 100, 1) if total_cases > 0 else 0,
        "true_positive_rate": round(tp_passed / tp_total * 100, 1) if tp_total > 0 else 0,
        "true_negative_rate": round(tn_passed / tn_total * 100, 1) if tn_total > 0 else 0,
    },
    "per_skill": {name: data for name, data in sorted(all_results.items())},
}
(RESULTS_DIR / "aggregate.json").write_text(json.dumps(aggregate, indent=2, ensure_ascii=False))
print(f"\nResults saved to {RESULTS_DIR}/", file=sys.stderr)
