# mimi-video

AI 短剧/视频生成流水线插件。把"一个剧本"变成"一批可生成的视频"，全程靠**项目级单一事实源**约束一致性，**不绑定任何具体出图/视频模型**——模型在运行时由用户选。

## 使用方式

mimi-video 采用类似 Superpowers 的自然触发方式：插件会在合适的项目或对话中注入 `using-mimi-video` 编排 skill。你不需要记插件命令，直接说你想做什么即可：

- "我放了 ep01 剧本，开始做"
- "继续下一步"
- "帮我做 ep02 的服化道"
- "生成这一集的即梦投料单"
- "P03 情绪不对，帮我改"

首次在空项目使用时，可以直接说"初始化一个 mimi-video 项目"。制片人会创建轻量骨架：`CODESHELL.md`、`production-bible.md`、`script/`、`assets/`、`outputs/`。整条流水线没有插件命令，全部通过自然语言驱动。

## 流水线全貌

```
[第0步] production-bible.md（项目单一事实源：角色花名册 + 渲染规格）
            │  所有环节动手前先读它
            ▼
[阶段1] 导演讲戏 ── director-skill ──▶ 01-director-analysis.md（讲戏本+人物清单+场景清单）
            │  director agent 自审：script-analysis-review + compliance-review
            ▼
[阶段2] 服化道 ── art-design-skill ──▶ character-prompts.md / scene-prompts.md
            │  director agent 审核：art-direction-review + compliance-review
            ▼
[阶段3] 分镜 ── seedance-storyboard-skill ──▶ 02-seedance-prompts.md
            │  内含【生成计划】环节：确认出图/视频模型、每段分镜图张数、视频生成方式
            │  director agent 审核：seedance-prompt-review + compliance-review
            ▼
[阶段4] 用户按生成计划调工具出图/出视频 → 拼接成片
```

## 产出目录结构

````
outputs/
└─ ep03/
   ├─ 01-director-analysis.md     # 导演讲戏(散文 + 镜头要点必填块)
   ├─ 02-seedance-prompts.md      # 总览索引:素材对应表 + 分段索引
   ├─ 03-generation-plan.md       # 生成方式/张数(单一事实源)
   ├─ prompts/                    # 按段独立投料单,给即梦直接用
   │  ├─ P01.md                   #   投料单卡片 + ```text 提示词正文
   │  └─ …
   └─ assets/img/                 # 该集出图后按命名归档(ep03-char-*.png / ep03-scene-*.png)
production-bible.md                # 全局单一事实源(画幅/渲染规格/命名规范)
assets/                           # 跨集累积的提示词文本(character/scene-prompts.md)
````

定位"第N集第M镜":看 outputs/epNN/prompts/PMM.md(自含画幅+用图+正文);要回查素材图,按该集 02 对应表的「本地文件名」去 assets/img/ 找。

## 角色（agents）

| Agent | 职责 | 用到的 skill |
|-------|------|-------------|
| `director` | 剧本分析 + 讲戏 + 全程两步审核（业务 + 合规） | director-skill / 三个 review-skill / compliance-review-skill |
| `art-designer` | 设计人物/场景出图提示词 | art-design-skill |
| `storyboard-artist` | 编写分镜提示词 + 产出生成计划 | seedance-storyboard-skill |

## 技能（skills）

**执行类**（产出物）：`director-skill`、`art-design-skill`、`seedance-storyboard-skill`
**审查类**（把关）：`script-analysis-review-skill`、`art-direction-review-skill`、`seedance-prompt-review-skill`、`compliance-review-skill`

## 核心约定：production-bible.md

每个项目根放一份 `production-bible.md`（模板见 `templates/production-bible-template.md`），是整条流水线的唯一权威：

- **角色花名册**：规范名 + 别名 + 参考图路径。剧本层定名，全链统一，禁止自由命名。
- **渲染规格**：画幅 / 分辨率 / 视觉风格 / 调色板。一处锁定，下游引用。

> **为什么必须锁画幅**：图生视频以"首帧图"宽高比为准。首帧图比例不统一 → 成片横竖混排、无法直接拼接。所以画幅必须在**出图阶段**锁死，不能等生成视频时补救。

## 设计原则

1. **不绑定模型**：skill 只定义"该问用户哪些问题、如何按规则规划"，具体出图/视频模型运行时让用户选。
2. **单一事实源优先**：角色名、画幅、风格全部从 production-bible 取，冲突即错误。
3. **执行 + 审查双链**：每个执行环节都有对应的业务审查 + 合规审查，PASS 才进下一阶段。
