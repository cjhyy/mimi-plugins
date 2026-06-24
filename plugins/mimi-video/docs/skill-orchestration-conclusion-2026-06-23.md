# Skill 编排结论：mimi-video 采用 Superpowers-style 自然触发

## 结论

`mimi-video` 不需要新增插件命令。更合适的做法是把它设计成 Superpowers-style 的编排层：

1. 用一个 bootstrap skill 作为"制片人"入口。
2. 用 hook 在合适的会话或用户输入时自动注入这个 skill。
3. 用项目文件作为状态总线，而不是保存 agent 会话或中心化 workflow state。
4. 用 Handoff Packet 把上下文交给子代理。
5. 用 hard gate 约束每个阶段必须审核通过后才能进入下一阶段。

也就是说，`mimi-video` 的主入口不是 `~start`、`~design`、`~prompt` 这类命令，而是自然语言：

```text
我放了 ep01 剧本，开始做
继续下一步
帮我做 ep02 的服化道
生成这一集的即梦投料单
P03 情绪不对，帮我改
```

命令可以保留为别名，但不能成为主路径。

## 为什么不做插件命令

插件命令会把用户体验变成"记口令"：

```text
~init
~start ep01
~design ep01
~prompt ep01
```

这对 `mimi-video` 不理想，因为它真正难的不是命令解析，而是：

- 什么时候该进入哪个阶段。
- 子代理该读哪些文件。
- 子代理该写哪些文件。
- 上一阶段是否已经审核通过。
- 修订时该回到哪个责任代理。
- 怎样避免主 agent 直接越权写提示词。

这些问题应该写进 skill 的过程文档和门禁里，而不是暴露成用户要记的命令。

## 编排结构

```text
User prompt / SessionStart
        │
        ▼
hooks/inject-mimi-video-context.mjs
        │
        ▼
skills/using-mimi-video/SKILL.md
        │
        ▼
producer/orchestrator main agent
        │
        ├─ director agent
        │    ├─ director-skill
        │    ├─ script-analysis-review-skill
        │    ├─ art-direction-review-skill
        │    ├─ seedance-prompt-review-skill
        │    └─ compliance-review-skill
        │
        ├─ art-designer agent
        │    └─ art-design-skill
        │
        └─ storyboard-artist agent
             └─ seedance-storyboard-skill
```

主 agent 只做制片人：

- 检查项目状态。
- 判断当前阶段。
- 生成 Handoff Packet。
- 调度对应子代理。
- 汇总 review 结果。
- 决定是否进入下一阶段。

主 agent 不直接写：

- 导演讲戏。
- 服化道提示词。
- 分镜提示词。
- 生成计划。

## 状态放在哪里

状态只放项目文件：

```text
CODESHELL.md
production-bible.md
script/
assets/
outputs/
```

阶段判断依据：

```text
script/<ep>.md
outputs/<ep>/01-director-analysis.md
assets/character-prompts.md
assets/scene-prompts.md
outputs/<ep>/02-seedance-prompts.md
outputs/<ep>/03-generation-plan.md
outputs/<ep>/prompts/Pxx.md
```

不做：

- `.agent-state.json`
- `Resume agent`
- 保存 agent id
- 复制插件里的 agent/skill 到项目目录

子代理是无状态的。每次调用都通过 Handoff Packet 明确告诉它读哪些文件、写哪些文件、遵守哪些约束。

## Handoff Packet 是核心接口

每次调子代理都传同一种结构：

```markdown
# Handoff Packet

## Task
[具体任务]

## Episode
epNN

## Read First
- production-bible.md
- script/epNN.md
- outputs/epNN/01-director-analysis.md
- assets/character-prompts.md

## Write
- outputs/epNN/prompts/Pxx.md

## Constraints
- 角色名以 production-bible.md 为准。
- 画幅、分辨率、视觉风格以 production-bible.md 为准。
- 不绑定具体出图/视频模型。
- 中文输出。

## Review Feedback
[修订时才填]

## Expected Return
- 写入/修改了哪些文件
- 是否完成
- 需要用户确认什么
```

这就是子代理之间的上下文交接协议。

## Hook 的职责

hook 只做一件事：在合适的时候把 `using-mimi-video` 注入上下文。

触发策略：

- `SessionStart`：当前项目看起来像 `mimi-video` 项目时注入。
- `UserPromptSubmit`：当前项目像 `mimi-video`，或用户输入命中短剧/剧本/分镜/Seedance/即梦/服化道等关键词时注入。
- 子代理里不注入，避免噪声和递归污染。

这相当于 Superpowers 的 `using-superpowers`，但作用域更窄，只在相关项目或相关请求里生效。

## 关键 hard gate

每个阶段都必须经过业务审核 + 合规审核：

```text
导演分析 -> script-analysis-review + compliance-review
服化道   -> art-direction-review + compliance-review
分镜提示 -> seedance-prompt-review + compliance-review
```

任何一个 review 失败：

1. 合并问题清单。
2. 发回原生产子代理。
3. 子代理读当前文件后修订。
4. 再跑双 review。
5. 两个都 PASS 才进入下一阶段。

## 当前实现文件

- `skills/using-mimi-video/SKILL.md`
- `hooks/hooks.json`
- `hooks/inject-mimi-video-context.mjs`
- `docs/natural-workflow-design-2026-06-23.md`
- `docs/natural-workflow-plan-2026-06-23.md`

## 一句话

`mimi-video` 的 skill 编排不是"多几个命令"，而是"一个自然触发的制片人 skill + 文件状态总线 + 子代理 Handoff Packet + 审核 hard gate"。
