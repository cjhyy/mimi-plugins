# mimi-video Superpowers-style 自然编排实施计划(2026-06-23)

> **执行说明:** 在 mimi-video worktree `feat/mimi-video-optimize` 内执行，根目录为 `plugins/mimi-video/`。本轮不做插件命令，改为 bootstrap skill + lifecycle hook。

**Goal:** 让 mimi-video 像 Superpowers 一样自然触发：用户说"我放了 ep01 剧本，开始做"或"继续下一步"，agent 自动加载制片人流程门禁、检测状态、调度专业 agent、执行审核闭环。

**Architecture:** 新增 `using-mimi-video` skill 作为制片人 bootstrap；新增 SessionStart/UserPromptSubmit hook 条件注入该 skill；README 更新为自然语言入口。命令不参与主路径。

---

## 文件结构

| 文件 | 责任 |
|---|---|
| `skills/using-mimi-video/SKILL.md` | 制片人 bootstrap skill：触发条件、状态检测、agent handoff、review hard gate |
| `hooks/hooks.json` | 注册 SessionStart / UserPromptSubmit hook |
| `hooks/inject-mimi-video-context.mjs` | 判断项目/提示词是否相关，相关时注入 `using-mimi-video` |
| `.claude-plugin/plugin.json` | 版本 0.2.0 -> 0.3.0 |
| `README.md` | 说明自然语言入口，不要求命令 |

---

## Task 1: 新增 using-mimi-video skill

**Files:**
- Create: `skills/using-mimi-video/SKILL.md`

- [x] 写 frontmatter：
  - `name: using-mimi-video`
  - `description` 只写触发条件：短剧、剧本、分镜、Seedance、即梦、服化道、production-bible、script/assets/outputs 等。

- [x] 写 body：
  - Hard gate：主 agent 不直接写导演讲戏/服化道/分镜提示词。
  - Operating model：producer 调度三个 agent。
  - First Action Checklist。
  - Project State Detection。
  - Natural Language Router。
  - Handoff Packet 模板。
  - 三阶段 workflow。
  - Review Loop。
  - Project Scaffold。
  - Anti-rationalization table。

- [x] 验证：

```bash
rg -n "~init|commands/init" skills/using-mimi-video/SKILL.md
```

Expected: no output.

```bash
rg -n "Resume agent|agent-state" skills/using-mimi-video/SKILL.md
```

Expected: only negative rules such as "Do not use ..."; no workflow step should instruct the agent to create or use them.

---

## Task 2: 新增 hook 条件注入

**Files:**
- Create: `hooks/hooks.json`
- Create: `hooks/inject-mimi-video-context.mjs`

- [x] `hooks.json` 注册：
  - `SessionStart`
  - `UserPromptSubmit`

- [x] 注入脚本逻辑：
  - 跳过 `isSubAgent === true`。
  - SessionStart：只有项目看起来像 mimi-video 时注入。
  - UserPromptSubmit：项目像 mimi-video 或 prompt 命中关键词时注入。
  - 输出 `{ "additionalContext": "..." }`。

- [x] 项目识别：
  - `production-bible.md` + `script/` / `assets/` / `outputs/`
  - 或 `CODESHELL.md` / `.codeshell/CODESHELL.md` / `CLAUDE.md` / `.claude/CLAUDE.md` 包含 mimi-video、Seedance、短剧、制片人等词。

- [x] 验证：

```bash
printf '{"eventName":"user_prompt_submit","data":{"prompt":"我放了 ep01 剧本，开始做","cwd":"%s","isSubAgent":false}}' "$PWD" \
  | CODESHELL_PLUGIN_ROOT="$PWD/plugins/mimi-video" CODESHELL_HOOK_EVENT=user_prompt_submit node plugins/mimi-video/hooks/inject-mimi-video-context.mjs
```

Expected: JSON with `additionalContext`.

---

## Task 3: 文档和版本

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `README.md`

- [x] bump version `0.2.0` -> `0.3.0`。
- [x] README 顶部新增自然语言使用方式。
- [x] 明确 `~start` / `~design` / `~prompt` 是别名，不是主入口。

---

## Final Validation

Run:

```bash
git status --short
node -c plugins/mimi-video/hooks/inject-mimi-video-context.mjs
printf '{"eventName":"user_prompt_submit","data":{"prompt":"帮我生成分镜投料单","cwd":"%s","isSubAgent":false}}' "$PWD" \
  | CODESHELL_PLUGIN_ROOT="$PWD/plugins/mimi-video" CODESHELL_HOOK_EVENT=user_prompt_submit node plugins/mimi-video/hooks/inject-mimi-video-context.mjs
```

Expected:

- changed files include skill, hooks, docs, README, manifest.
- Node syntax check passes.
- hook emits JSON containing `using-mimi-video`.
