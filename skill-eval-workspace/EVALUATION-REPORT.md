# Skill Quality Evaluation Report

**Date**: 2026-03-29
**Scope**: 4 plugins, 16 skills, 5 reference files

---

## Executive Summary

All 16 skills received comprehensive quality improvements across descriptions, body instructions, error handling, and structural organization. Ghost router conflicts in the installed cache were resolved.

---

## 1. Description Quality — Before vs After

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Skills with "Do NOT" guard | 6/16 (37%) | **16/16 (100%)** | +63% |
| Skills with pipeline hints | 0/16 (0%) | **10/16 (63%)** | +63% |
| Skills with mutual cross-references | 2/16 (12%) | **14/16 (88%)** | +75% |
| Description style: keyword list only | 16/16 | **0/16** | All upgraded to semantic |
| Ghost router conflicts | 5 active | **0** | Eliminated |

---

## 2. SKILL.md Body — Line Count Changes

| Skill | Before | After | Delta | Reason |
|-------|--------|-------|-------|--------|
| yux-blog-image | 371 | **347** | -24 | Extracted safety rules + common mistakes to reference |
| yux-nano-banana | 257 | **244** | -13 | Extracted safety rules + common mistakes to reference |
| yux-video-summary | 180 | **87** | -93 | Extracted 90-line output templates to reference |
| yux-linear-start | 130 | **113** | -17 | Extracted 18-line task schema to reference |
| yux-linear-status | 103 | **97** | -6 | Replaced inline scoring with reference |
| yux-pm-plan | 112 | **109** | -3 | Replaced inline scoring with reference (+output example) |
| yux-pm-init | 70 | **86** | +16 | Added output example + error handling |
| yux-pm-overview | 78 | **99** | +21 | Added output example |
| yux-pm-triage | 102 | **120** | +18 | Added output example + conflict resolution |
| yux-linear-commit | 82 | **94** | +12 | Added output example + better error handling |
| yux-linear-pr | 74 | **91** | +17 | Added output example + PR exists check |
| yux-blog-writer | 195 | **196** | +1 | Fixed error handling section |
| yux-blog-oss | 236 | 236 | 0 | No body changes needed |
| yux-video-subtitle | 122 | 122 | 0 | No body changes needed |
| yux-linear-merge | 64 | 64 | 0 | No body changes needed |
| yux-pm-prd | 108 | **109** | +1 | Added API fallback note |
| **Total** | **2284** | **2214** | **-70** | Net reduction despite adding output examples |

---

## 3. Shared References Created

| Reference File | Lines | Deduplicates From | Saves |
|---------------|-------|-------------------|-------|
| `image-data-safety.md` (x2) | 30 | blog-image + nano-banana (identical blocks) | ~37 lines per skill |
| `linear-tasks-schema.json` | 18 | yux-linear-start (used by 4 skills) | ~18 lines, single source of truth |
| `issue-scoring.md` | 48 | linear-status + pm-plan (overlapping logic) | Consolidates differences |
| `summary-templates.md` | 105 | video-summary (inline templates) | -93 lines from SKILL.md body |

**Total reference content**: 231 lines in 5 files
**Net SKILL.md body reduction**: 70 lines (with output examples added)
**Gross dedup savings**: ~156 lines of duplicated content eliminated

---

## 4. Quality Coverage Improvements

### Error Handling

| Skill | Before | After |
|-------|--------|-------|
| yux-video-summary | No error handling section | 4-case error table added |
| yux-linear-pr | No PR-exists check | Pre-creation check with `gh pr view` |
| yux-linear-start | No branch-exists handling | User prompt for existing branch |
| yux-blog-writer | "timeout" reference (invalid) | Fixed to ask-then-default pattern |
| yux-blog-writer | No minimum content check | 200-word threshold warning |
| yux-nano-banana | No source file validation (edit mode) | File existence + MIME check added |
| yux-pm-prd | No document API fallback | Local file fallback + Epic creation guard |
| yux-linear-commit | Generic push retry | Differentiated non-fast-forward vs auth error |

### Output Examples

| Skill | Before | After |
|-------|--------|-------|
| yux-linear-commit | Prose description | Concrete output block |
| yux-linear-pr | Prose description | Concrete output block |
| yux-pm-init | Prose description | Concrete output block |
| yux-pm-overview | Prose description | Concrete output block with dashboard layout |
| yux-pm-plan | Prose description | Concrete 3-category plan output |
| yux-pm-triage | Prose description | Concrete triage summary output |
| yux-nano-banana | Bullet list | Concrete output block |

### AskUserQuestion Consistency

| Skill | Before | After |
|-------|--------|-------|
| yux-pm-init | "ask user" (no tool specified) | Explicit AskUserQuestion for overwrite + tech detection |
| yux-pm-plan | "Offer to..." (no tool specified) | Explicit AskUserQuestion for carry-over |
| yux-pm-triage | "offer two options" (no tool specified) | Explicit AskUserQuestion for multi-project |

---

## 5. Cache & Installation

| Item | Before | After |
|------|--------|-------|
| Installed plugin versions | blog 1.0, pm 1.0, workflow 1.0, banana 1.1 | blog 1.3, pm 2.2, workflow 2.2, banana 1.3 |
| Ghost skills in cache | 5 (pm-workflow, linear-workflow, ci-monitor, backlog, note) | **0** |
| yux-core plugin | Still in installed_plugins.json | **Removed** |
| Marketplace mirror | At commit 7c1f3da (old) | Updated to dab8617 (latest remote) |
| Total skills loaded | ~22 (including ghosts) | **17** (clean) |
| Trigger keyword collisions | 8 high-severity pairs | **0** (ghost routers eliminated, guards added) |

---

## 6. Remaining Items (Future Work)

1. **run_eval.py adaptation**: The trigger evaluation script needs modification to handle already-installed plugins (currently creates temp commands that compete with real installed skills)
2. **Description auto-optimization**: Once run_eval.py is fixed, run `run_loop.py` for iterative description tuning with train/test split
3. **Additional style presets**: yux-nano-banana could benefit from more preset templates (moved to references/ when they grow)
