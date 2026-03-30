# Skill 触发审查报告

**日期**: 2026-03-29
**范围**: yux-claude-hub 所有 4 个插件、17 个 SKILL.md、安装缓存中的幽灵 skill

---

## 一、已完成的改进（本轮）

所有 16 个 skill 的 description 已从简短的关键词列表升级为完整的语义描述：
- 增加了 "Use when..." 正向触发说明
- 增加了 "Do NOT use..." 反向限定（14/16 已有）
- 增加了中英文示例短语
- 增加了互相引用的消歧说明
- 版本号已同步 bump

---

## 二、关键问题

### P0 — 幽灵 Router 冲突（最高优先级）

安装缓存中存在 5 个 skill **不在** 当前 repo 源码中：

| Ghost Skill | 来源 | 冲突 |
|---|---|---|
| `yux-pm-workflow` | yux-linear-pm 旧版 | 复制了全部 5 个 PM skill 的触发关键词 |
| `yux-linear-workflow` | yux-linear-workflow 旧版 | 复制了 start/commit/pr/merge/status 的触发关键词 |
| `yux-ci-monitor` | yux-linear-workflow 旧版 | "workflow status" 过于宽泛 |
| `yux-linear-backlog` | yux-linear-workflow 旧版 | 与 yux-linear-status 的 backlog 功能重叠 |
| `yux-linear-note` | yux-linear-workflow 旧版 | 可能不再需要 |

**影响**: Claude 看到 30+ 个 skill 竞争同一组关键词，导致：
- "start task" 同时���配 `yux-linear-workflow` (router) + `yux-linear-start`
- "create pr" 同时匹配 `yux-linear-workflow` (router) + `yux-linear-pr`
- "triage inbox" 同时匹配 `yux-pm-workflow` (router) + `yux-pm-triage`
- "project status" 三方碰撞：`yux-pm-overview` + `yux-pm-workflow` + `yux-linear-status`

**修复方案**: 重新安装插件以清除旧缓存，或在 plugin.json 中显式排除这些 ghost skill。

### P1 — Description 消歧缺失

| Skill | 问题 |
|---|---|
| `yux-pm-prd` | 缺少 Do NOT 子句，"feature planning" 与 pm-workflow router 冲突 |
| `yux-pm-init` | 缺少 Do NOT 子句（低风险，因触发词独特） |
| `yux-linear-status` | 缺少对 yux-pm-overview 的反向引用 |

### P2 — 跨 Skill 管道缺少链接

yux-blog 的 5 个 skill 形成管道：`subtitle → summary → writer → image → oss`
yux-linear-workflow 形成管道：`start → commit → pr → merge`

但各 skill description 中缺少"下一步"引导，Claude 不容易自动推荐管道中的下一个操作。

---

## 三、具体改进方案

### 方案 A：清除幽灵 Router（P0，推荐立即执行）

需要重新安装所有插件以刷新缓存。如果 ghost skill 是通过 commands/ 目录注册的，检查并删除对应的 command 文件。

### 方案 B：补充消歧说明（P1）

**yux-pm-prd** — 添加:
```
Do NOT use for planning an existing sprint cycle (use yux-pm-plan) or triaging existing issues (use yux-pm-triage).
```

**yux-linear-status** — 添加:
```
For initiative-level or PM-level project status, use yux-pm-overview instead.
```

### 方案 C：添加管道引导（P2，可选）

在每个 skill description 末尾添加一句 "Next step" 提示：
- `yux-video-subtitle`: "After downloading, use yux-video-summary to organize the transcript."
- `yux-video-summary`: "To convert into a blog post, use yux-blog-writer."
- `yux-blog-writer`: "To add images, use yux-blog-image."
- `yux-blog-image`: "To publish images to CDN, use yux-blog-oss."
- `yux-linear-commit`: "When ready for review, use yux-linear-pr."
- `yux-linear-pr`: "When approved, use yux-linear-merge."

注意：管道引导放在 description 中会增加长度，也可以考虑只放在 SKILL.md body 中。

---

## 四、Eval 基础设施说明

为 16 个 skill 创建了触发测试文件（`skill-eval-workspace/trigger-eval-*.json`），每个包含 ~20 个 should_trigger/should_not_trigger 测试用例。

**发现的限制**: `run_eval.py` 通过创建临时 command 文件并运行 `claude -p` 测试触发。但对已安装的插件 skill，Claude 会触发真实的已安装版本（如 `yux-nano-banana:yux-nano-banana`）而非测试的临时 command（`yux-nano-banana-skill-xxxxx`），导致所有 should_trigger 用例被误判为未触发。

**建议**: `run_eval.py` 需要适配已安装插件的场景 — 在测试时临时禁用或卸载竞争 skill，或修改检测逻辑以同时识别已安装 skill 的触发。

---

## 五、最终推荐执行顺序

1. **[立即]** 重新安装 4 个插件，清除幽灵 router/skill 缓存
2. **[立即]** 应用方案 B — 补充 yux-pm-prd 和 yux-linear-status 的消歧说���
3. **[可选]** 应用方案 C — 在 SKILL.md body（非 description）中添加管道引导
4. **[后续]** 修复 run_eval.py 的已安装插件检测问题后，重新运行全量触发测试
