# mimi-video plugin 优化方案(2026-06-22)

> 来源:对 7 skill + 3 agent + 模板/例子做 4 维度并行深审,18 条发现经对抗式核实保留。按用户 4 个关切点分组,组内按 severity 排序、合并重复项。
>
> **前置提醒(所有改动共用):** 本 plugin 装在 `~/.code-shell/plugins/mimi-video/`(安装缓存路径),直接改这里**不会回流上游 `cjhyy/mimi-plugins`,重装即丢**。且上游 repo 当前**根本没有 mimi-video**(只有 media-downloader / model-fact-finder / skill-creator)。所以"改好后发出去" = 在上游 repo 新增 `plugins/mimi-video/` 目录 → commit → push → marketplace.json 登记。
>
> **外部事实待核实(高优先,动手前先查):** 多条 ① 类发现依赖"Nano Banana 2 已成默认""Seedance 支持 1080p"等**外部模型能力**,核实 agent 明确标注"无法从仓库证实,是外部断言"。这些**不直接采信**,先用 deep-research / 官方文档查准,再决定写什么数字。

---

## ① 例子过时(stale-examples)

### 【high·需先核实外部事实】图像模型选型整体过时
- **问题:** `gemini-image-prompt-guide.md` 模型选择只列老 Nano Banana(2.5 Flash,1024px 封顶)和 NB Pro(4K),漏掉据称已成默认的 Nano Banana 2 / Gemini 3.1 Flash Image。
- **冲突点(纯内部、可立即修):** 老 NB 1024px 出不了项目强制的 1536×1024,却和画幅硬约束两段并列、无冲突提示。
- **待核实:** NB2 是否真存在/真成默认/真原生 16:9+4K?(workflow 给的"快 3-5 倍/画质 95%"是未证实数字,**不要写死**)
- **修复方向:** 核实后新增 NB2 档为默认推荐 + frontmatter 同步;老 NB 条目标注"不满足 1536×1024,正式分镜图勿用"+ 画幅段加反向交叉引用。
- **文件:** `skills/art-design-skill/gemini-image-prompt-guide.md`

### 【high·分两步】Seedance 输出参数过时且与 16:9 冲突
- **问题:** `seedance-prompt-methodology.md` 第 57 行把输出上限写成 720p,且用 834×1112(3:4 竖屏)、640×640(1:1)等与项目 16:9 锁定矛盾的像素。
- **A(立即,纯内部一致性):** 删非 16:9 像素示例,改为只列档位名 + "最终画幅以首帧图 16:9 为准(见 art-design 1536×1024)"+ 补"画幅锁 16:9,禁竖屏/方形档位"。
- **B(需核实):** 是否补 1080p 档——**先核对当前接入的 fal/即梦 video provider(`resolveVideoProvider`/videoGen schema)实际可传分辨率**,证实后再按 16:9 给像素(1920×1080),不照抄外部数字。
- **文件:** `skills/seedance-storyboard-skill/seedance-prompt-methodology.md`

### 【medium】九宫格在 4K 模型下是清晰度反优化(但有意为之,勿删)
- **问题:** scene 例子把多场景塞 3×3 九宫格再逐格裁剪,4K 下每格有效分辨率仅约 1/9(≈1.3K)。
- **校正:** 九宫格"一次出图保证多场景风格统一"动机仍成立,定性为"4K 下的权衡",不删。
- **修复(两步法):** ① 保留九宫格作"风格/光影定调"中间产物 + 补清晰度代价提示;② 关键/特写场景基于宫格风格,用 NB Pro 单出 2K/4K 高分图;③ 下游 `@图片` 指向高分单图而非裁切格。
- **文件:** `skills/art-design-skill/examples/scene-prompt-examples.md`、`art-design-skill/SKILL.md`、`seedance-prompt-methodology.md`

### 【low】"Seedance 2.0" 版本号字面写死(~40 处)
- 与版本无关叙述改"Seedance";版本相关硬参数收进 `[平台约束]` 一节加版本标注。**一次改全 40 处**否则不一致。下次内容更新顺手做。
- **文件:** 全插件 `grep "Seedance 2\.0"` 命中处。

---

## ② 剧本环节信息不足(script-info-gap)

### 【high】导演阐述全熔进散文且明令"不要分条",下游无空字段暴露缺漏
- **问题:** 第四步要求景别/机位/光影"融合进叙述、不分条";下游要逐项提取 5 维,审核只能比同一段散文,"导演一开始就漏写"的项无法机械暴露。
- **校正:** 不推翻"散文讲戏"理念,加低成本结构化兜底。
- **修复:** 每个剧情点在散文之外加轻量**「镜头要点」必填清单**:景别 / 机位·运镜方向 / 主光源方向+色温·色调 / 核心情绪。散文讲戏,要点保零缺漏。审核 skill 加"整体性检查":逐点查景别/光源/色温是否齐备。
- **文件:** `director-skill/templates/director-analysis-template.md`、`director-skill/SKILL.md`、`seedance-prompt-review-skill/SKILL.md`

### 【medium】连贯性锚点 + 段间关系字段缺失(合并:剧情点元数据信息量不足)
- **2a 连贯性:** 角色服装/状态、场景时间·破坏度的**集内逐点演进**无字段。把已有"变体"机制从整集级**下沉到逐点粒度**(每点加可选「角色状态/服装」「场景状态」,仅变化时填);seedance 第三步补:@同一图时文字覆盖差异(`@图片1林薇,但此处左额带血痕`)。
- **2b 段间关系:** 元数据加**「与上段关系」枚举**(同场景续接/时空跳转/闪回进/闪回出/独立开场);seedance 第五步据此判续接 vs 新首帧。
- **文件:** `director-analysis-template.md`、`director-skill/SKILL.md`、`seedance-storyboard-skill/SKILL.md`、`script-analysis-review-skill/SKILL.md`

### 【medium】群演外观只散落散文、无定位锚点
- 对**有台词或近景/特写**的群演,要求导演用**括注**把外观紧贴称谓(`路人甲(尖脸眯缝眼、白袍学员)侧头低语`);纯背景群演维持散文。seedance 提取:优先读括注;缺则回退要导演补,不自行生成。
- **文件:** `director-skill/SKILL.md`、`director-analysis-template.md`、`seedance-storyboard-skill/SKILL.md`

### 【low】多镜头段缺子镜头秒数/节拍切分
- 仅对多镜头段把"镜头组"从计数升级为带切分清单(`镜头1 0-3s/1拍`…);秒数和=时长建议、遵守节拍上限。seedance 第5步:导演已给则沿用不重切,未给才回退推断。
- **文件:** `director-analysis-template.md`、`director-skill/SKILL.md`、`seedance-prompt-methodology.md`

---

## ③ 最终提示词不够详细(prompt-detail)

### 【high】视频审核"忠实度"以导演讲戏为天花板,均匀偏薄照样 PASS
- **问题:** 单条评分全锚"是否符合导演阐述";"风格统一"只查"详略一致"(一致地薄也过);一条"简洁但正确"的薄提示词可过关。
- **修复:** 新增**不依赖导演讲戏本的独立维度**「细节颗粒度/可执行充分度」:直接判动作分解/运镜/光影/声音是否细到 Seedance 可稳定复现;任一仅笼统/占位即评≤6 → 触发 FAIL。给最低锚点(每镜头≥1主体动作+1运镜+光影或声音任一)。
- **文件:** `seedance-prompt-review-skill/SKILL.md`

### 【medium】场景审核缺"细节完整性"维度
- 场景逐格补「□ 细节完整性」逐项核对八要素;逐格表加"细节"列,纳入"任一单项<6→FAIL"。
- **文件:** `art-direction-review-skill/SKILL.md`

### 【medium】视频段落缺"最小信息量"硬指标(图像分支已有,勿重复造轮子)
- methodology `[提示词结构]` 五段从"建议"升为"单镜头必含五维、每维≥1句、动作维≥2步";≥10s 段"分时段"改必须。review 加可勾选硬项"细节量达标"。**与 ③-high 同改 review skill,合并落地。**
- **文件:** `seedance-prompt-methodology.md`、`seedance-storyboard-skill/SKILL.md`、`seedance-prompt-review-skill/SKILL.md`

---

## ④ 产出组织不便外部使用(用户原始痛点,本次重点·多为 high)

### 【high】每集提示词全堆一个大文件,未按镜头拆分
- 每段额外落独立文件 `outputs/<集数>/prompts/P01.md…`,文件内**只含该段可直接复制的提示词正文**;保留 `02-seedance-prompts.md` 作带标题+素材对应表的**汇总/索引视图**(链向各 Pxx.md)。
- **文件:** `seedance-prompts-template.md`、`seedance-storyboard-skill/SKILL.md`、`generation-plan-template.md`

### 【high】提示词非"复制即贴"自包含单元(画幅/参数/参考图分散 4 处)
- 每段头部内联**投料单卡片**:生成方式(从 03 同步)/ 画幅·分辨率 16:9·1536×1024(从 production-bible 内联)/ 本段用图清单(`@图片1=<规范名>(本地文件名)`)。SKILL 第156行 16:9 从"可选"升为模板**硬性字段**。卡片是单一事实源的**投影回填**(第五步确认后),非用户手填。
- **文件:** `seedance-prompts-template.md`、`seedance-storyboard-skill/SKILL.md`

### 【high】@图片N 不映射用户手上的实际图片文件
- 约定统一**落盘目录与命名**:`outputs/<集数>/assets/img/`,人物 `ep01-char-<规范名>.png`、场景 `ep01-scene-NN-<场景名>.png`。素材对应表**加「本地文件名」列**,@图片N ↔ 文件名一一对应。明确是"用户出图后按此命名归档"的契约,非系统自动生成。
- **文件:** `seedance-storyboard-skill/SKILL.md`、`seedance-prompts-template.md`、`art-design-skill/SKILL.md`、`production-bible-template.md`、`seedance-prompt-review-skill/SKILL.md`

### 【medium】提示词正文未包裹代码块,无法一键复制
- 每段正文用 ` ```text ... ``` ` 包裹。**踩坑:** 模板输出格式本身已被一层 ` ```markdown ` 围栏包裹,内层再写 ``` 会冲突——外层示例围栏改**四反引号**,内层用三反引号。
- **文件:** `seedance-prompts-template.md`、`examples/seedance-prompt-examples.md`

### 【medium】无统一目录树文档
- ① README 增补真实 **outputs 目录树**(纯聚合,优先做)。② "每集自包含目录"降级为可选——art-design 把素材定为跨集累积是有意设计(跨集复用),勿强塞;在 README/production-bible 写明检索路径。
- **文件:** `README.md`、`production-bible-template.md`(仅文档补充,不移文件)

---

## 建议执行顺序

### 第一优先级 — 必改(high,直接对应痛点)

**批次 A:产出组织(价值最高,集中在 seedance-storyboard-skill,一次改完自洽)**
1. ④ 按镜头拆分独立文件(prompts/Pxx.md + 汇总索引)
2. ④ 自包含投料单卡片(内联生成方式/画幅/用图)
3. ④ @图片N ↔ 本地文件名映射(落盘命名 + 对应表加列)
4. ④ 提示词正文代码块包裹(medium,同文件顺手做)

**批次 B:质量下限(防"不够详细")**
5. ③ 视频审核加独立"细节颗粒度"维度 + 最小信息量基线(合并改 review skill)
6. ② 导演阐述加结构化「镜头要点」必填块

**批次 C:模型选型纠偏(⚠️动手前先核实外部事实)**
7. ① 图像模型选型更新(NB2 默认 + 老 NB 冲突标注)+ Seedance 输出参数去竖屏像素

### 第二优先级 — 可选(medium)
- ② 连贯性锚点 + 段间关系字段
- ② 群演括注外观
- ③ 场景审核"细节完整性"维度
- ① 九宫格两步法
- ④ README 目录树 + 检索路径

### 第三优先级 — 锦上添花(low)
- ② 多镜头子镜头秒数切分
- ① "Seedance 2.0" 版本号去字面化(~40 处一次改全)

---

## 推荐产出形态(满足"既按集独立给即梦、又有总览")

每集目录采用**「索引汇总 + 逐段独立 + 集内素材聚合」三层**:

```
outputs/
└─ ep03/
   ├─ 01-director-analysis.md     # 导演讲戏(散文 + 镜头要点必填块)
   ├─ 02-seedance-prompts.md      # ★总览索引:P01..Pn 标题 + @素材对应表(含本地文件名) + 链向各 Pxx.md
   ├─ 03-generation-plan.md       # 生成方式/张数(单一事实源)
   ├─ prompts/                    # ★按段独立,给即梦直接用
   │  ├─ P01.md                   #   投料单卡片(生成方式/画幅16:9/用图清单) + ```text 包裹的纯提示词正文
   │  └─ …
   └─ assets/img/                 # 该集出图后按命名归档
      ├─ ep03-char-林薇.png
      └─ ep03-scene-04-药铺.png
production-bible.md                # 全局单一事实源(画幅/渲染规格/命名规范)
assets/                           # 跨集累积的提示词文本(character/scene-prompts.md)
```

- **总览文件** = 人看的索引:全集一览、@图片↔文件名对应表、逐段链接。
- **逐段文件** = 即梦直接投料:每个文件就是一次即梦任务的完整投料单,正文代码块一键复制,无需跨文件反查。
- **关键约束:** 单一事实源不漂移——画幅来自 production-bible、生成方式来自 03,逐段卡片是二者第五步确认后的**投影回填**,不让用户手动跨 4 文件拼装。
