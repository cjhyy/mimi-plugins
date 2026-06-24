# mimi-video Superpowers-style 自然编排设计稿(2026-06-23)

## 背景与痛点

`mimi-video` 已经有 7 个 skill 和 3 个 agent，但缺一个像 Superpowers 那样的 bootstrap 层。旧方案准备做 `~init`、`~start`、`~design`、`~prompt` 等命令，让用户通过命令驱动流水线。

用户反馈是对的：这会让体验像"背口令"。`mimi-video` 更适合做成自然触发流程：用户说"我放了 ep01 剧本，开始做"、"继续下一步"、"生成分镜投料单"，agent 就能自动进入制片人编排。

## 目标

用类似 Superpowers 的机制实现：

1. 会话/提示词触发时注入 `using-mimi-video`。
2. `using-mimi-video` 作为制片人流程门禁，约束 agent 不直接写内容，而是调度专业 agent。
3. 状态放在项目文件里，不依赖命令、不依赖 resume、不维护 `.agent-state.json`。
4. 命令只作为可选别名，不作为主路径。

## 设计决策

### 1. 不做插件命令

不新增 `commands/init.md`。初始化也走自然语言：

```text
初始化一个 mimi-video 项目
我想用 mimi-video 做短剧
我有一个剧本目录，帮我搭好流水线
```

触发后由 `using-mimi-video` 指示 agent 创建轻量骨架：

```text
CODESHELL.md
production-bible.md
script/
assets/
outputs/
```

注意：CodeShell 自动读取的是项目根 `CODESHELL.md` 或 `.codeshell/CODESHELL.md`，不是 `.code-shell/CODESHELL.md`。

### 2. 新增 bootstrap skill

新增：

```text
skills/using-mimi-video/SKILL.md
```

它承担 Superpowers 里 `using-superpowers` 的角色，但面向视频流水线：

- 说明何时触发 mimi-video。
- 要求先检查项目状态。
- 要求用 Handoff Packet 调 agent。
- 禁止主 agent 直接写导演讲戏/服化道/分镜提示词。
- 定义 director/art-designer/storyboard-artist 的阶段路由。
- 定义业务审核 + 合规审核 hard gate。

### 3. 新增 hook 注入

新增：

```text
hooks/hooks.json
hooks/inject-mimi-video-context.mjs
```

hook 触发：

- `SessionStart`：如果 cwd 看起来是 mimi-video 项目，注入 `using-mimi-video`。
- `UserPromptSubmit`：如果当前项目像 mimi-video，或用户 prompt 命中短剧/剧本/分镜/Seedance/即梦/服化道等关键词，注入 `using-mimi-video`。

为了避免污染所有项目，hook 必须有项目/关键词门禁，不像 Superpowers 那样全局强注入。

### 4. 状态仍然只放文件

不引入中心化 workflow state，不保存 agentId。

状态检测依据：

```text
production-bible.md
script/*.md
assets/character-prompts.md
assets/scene-prompts.md
outputs/<ep>/01-director-analysis.md
outputs/<ep>/02-seedance-prompts.md
outputs/<ep>/03-generation-plan.md
outputs/<ep>/prompts/Pxx.md
```

### 5. 编排靠 skill 文档，而不是 DAG 引擎

`using-mimi-video` 写清楚阶段跳转和 required review：

```text
导演分析 -> director review + compliance
服化道设计 -> director review + compliance
分镜编写 -> director review + compliance
```

这就是 Superpowers 风格的"文档驱动 workflow"。

## 验收

- 自然提示 "我放了 ep01 剧本，开始做" 会触发 `using-mimi-video`。
- 自然提示 "继续下一步" 会先检查文件状态再路由。
- 没有新增插件命令。
- 不生成 `.agent-state.json`。
- 不要求用户输入 `~start` / `~design` / `~prompt`，但这些词仍可被当作别名识别。
- 空项目初始化写根目录 `CODESHELL.md`，不是 `.code-shell/CODESHELL.md`。
