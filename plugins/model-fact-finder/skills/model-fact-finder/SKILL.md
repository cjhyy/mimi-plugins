---
name: model-fact-finder
description: 当用户想往 codeshell 里加/接入一个 AI 模型或 provider(「加个模型入口」「接入 XX 模型」「我想用 YY」),或需要查准一个模型的接入事实——支持哪些模态(文本/图片/视频/vision)、有哪些可调参数及每个参数怎么传(字段名、取值、落到请求体哪里)、上下文窗口多大、怎么鉴权——时使用。它先把事实查准,再(若用户是要接进来用)指引落地:写 catalog → 去连接页填 key 配置。典型场景:接入一个新模型,或核实某模型的参数/上下文是否填对。
---

# Model Fact Finder — 把一家模型的接入事实查准

核心职责是产出**一份结构化的模型事实报告**:这个模型支持什么模态、有哪些参数、每个参数怎么传、上下文多大、怎么鉴权。**查准事实永远是第一步,也是最重要的一步**(铁律见下)。

如果用户的意图是把这个模型**接进 codeshell 来用**(而不只是问问事实),那么查准之后,再按文末「接入落地」一节把它落进 catalog 并引导用户去连接页配置——查 → 写 catalog → 配置,是一条链。如果用户只是想了解事实,出完报告即止,别擅自写文件。

**铁律:绝不凭记忆答。** 模型型号、上下文窗口、参数字段名、API id 都是**会过期、会出错**的事实——必须先 WebSearch 找到该 provider 官方 API 文档,WebFetch 读,再下结论。凭记忆的后果(真实踩过):型号根本不存在、id 拼错、上下文填错、把不支持的参数当支持。查不到就如实说查不到,不要编。

## 查证清单(逐项去官方文档核实)

对目标模型/provider,逐项查实:

1. **真实模型 id** —— API `model` 字段实际接受的字符串。
   - 用当前在售版本,别用记忆里的旧版本或营销名。
   - 网关(OpenRouter 等)的 slug **不等于**原生 id——查网关自己的 models 列表(如 OpenRouter `/api/v1/models`),它可能带日期或有 `~latest` 路由别名。

2. **支持的模态** —— 输入/输出各支持什么:
   - 输入:纯文本?接受图片(vision)?音频?
   - 输出:文本?图片生成?视频生成?
   - vision 要逐模型确认(同家有的支持有的不支持)。

3. **上下文窗口 + 最大输出** —— context window(token 数)和 max output tokens。去官方 pricing/models 文档查准确数值,别估。

4. **可调参数 —— 每个参数查清三样**:
   - **名字 + 语义**:这个参数干什么。
   - **类型/取值**:枚举(列全合法值)、数值(范围/最小值)、布尔开关、自由文本。
   - **怎么传到请求体**:字段名是什么、嵌套在哪。各家差异大,举例:
     - reasoning/思考:OpenAI 是 `reasoning_effort`(枚举 minimal/low/medium/high,gpt-5.5+ 加 xhigh);Anthropic 是 `thinking` 对象(预算 token 数或自适应);DeepSeek 是 `thinking.type` 开关;OpenRouter 归一成统一 `reasoning` 对象(effort 枚举 或 max_tokens 二选一)。
     - 图片:size/quality 的合法枚举值;图生图怎么传参考图。
   - **关键:逐模型判断,别一刀切**。同一家不同模型参数不同(有的有 reasoning、有的没有);不支持某参数就明确标"不支持",别假设。
   - 找文档里的「supported parameters」「API reference」「capabilities」章节;OpenRouter 看 `/api/v1/models` 的 `supported_parameters`(逐模型 string[])。

5. **鉴权 + 端点** —— baseUrl、鉴权方式(Bearer key / 自定义 header / 环境变量)、获取 key 的页面。

## 输出格式

查完按这个结构汇报(每条标注**出处链接**,让人能复核):

```
模型: <显示名> (id: <真实 model id>)
Provider: <家> | 协议: <OpenAI 兼容 / Anthropic 原生 / …>
模态: 输入[文本/图片/…] 输出[文本/图片/视频]
上下文: <context window> | 最大输出: <max output>
鉴权: <方式> | baseUrl: <端点> | 获取 key: <链接>
参数:
  - <名>: <类型> <取值/范围> → 请求体字段 <field>  // <语义/怎么用>
  - <名>: 不支持
出处: <官方文档 URL 列表>
```

不确定的项标「未在文档确认」,不要填猜测值。

## 不要做

- ❌ 凭记忆给型号/上下文/参数(会过期会错——这是本 skill 存在的全部理由)。
- ❌ 把营销名或旧版本当 model id;把网关 slug 当原生 id。
- ❌ 一刀切「这家所有模型都支持 X」——逐模型确认。
- ❌ **事实没查准就跳去写 catalog**——查准永远是第一步,落地基于查准的事实,不基于记忆。
- ❌ 用户只是问事实时擅自写文件——是否落地看用户意图(要不要"接进来用")。
- ❌ 用工具自动写 API key——key 敏感,贴 key 让用户/AI 用通用 Edit 工具手填(走 Edit 审批可见),`EditModelCatalog` 绝不碰 key。

## 接入落地(仅当用户要把模型接进来用)

事实查准后,把它落进 codeshell 的 catalog,这样连接页就能渲染出添加表单。三步:

1. **写 catalog entry** —— 用内置工具 **`EditModelCatalog`**,按刚查到的事实造一条 `CatalogEntry`(by id,增/改 `~/.code-shell/model-catalog.user.json`):
   - `tag` = text / image / video(按查到的输出模态);`adapterKind` 复用现有(openai/google/fal/anthropic 等兼容协议,别造新的)。
   - `modelPresets[]` 每个模型一条,带它自己的 `params`(把查到的可调参数转成通用 ParamSpec:`{name, control: enum|number|toggle|text, options?, min?, max?, default?, doc?, wire?}`)。
   - `paramsDoc` 写清每个参数怎么传(会注入到 GenerateImage/GenerateVideo 等工具描述)。
   - 工具 `permissionDefault: ask`,调用时用户会看到审批。
   - **写完必复述**:`EditModelCatalog` 返回一份「写入摘要」(列出每个 model preset 的全部参数 options/default/范围 + 落盘路径)。把这份摘要**原样转述给用户**,并明确请他**核对各参数取值是否与官方文档一致**——尤其枚举档位(常见坑:把网关的输入别名当成了模型原生档位,比如 GLM 真实只有 high/max,却被填成 7 档)。哪里不对,用 Edit 改这个文件或让你改。

   **配置文件落在哪(可直接用 Read/Edit 看和改)**:
   - `~/.code-shell/model-catalog.user.json` —— **模型模板(catalog)**。`EditModelCatalog` 写的就是这个文件;它是纯数据,你也可以直接用 **Read** 看现状、用 **Edit** 微调(改参数、改 paramsDoc、删条目)。同 id 覆盖内置模板。
   - `~/.code-shell/settings.json` —— **填了 key 的连接实例 + 凭证**:`credentials[]`(独立存 API key)、`modelConnections[]`(连接,按 credentialId 引用凭证)、`defaults`(聊天/aux/视频各自的默认连接)。key 改动都在这里。
   - 两个文件都是 LLM 可读可改的普通 JSON——**改完会被 app 实时热加载**(catalog 监听 files-changed、settings 监听 settings-changed),连接页自动刷新,不用重启。告诉用户这一点,他想核对/手改时知道去哪。
2. **填 key** —— `EditModelCatalog` 不写 key。把获取 key 的页面链接告诉用户;若用户已给 key,用通用 **Edit** 工具把它填进 `~/.code-shell/settings.json` 的 `credentials[]`(走 Edit 审批,key 改动可见),别用任何工具自动静默写 key。
3. **去连接页配置** —— 告诉用户:catalog 写完连接页会**实时刷新**(监听 files-changed,不用重启),去 **设置 → 连接页** 点 [+ 添加] 选刚加的模板、填/选凭证、设默认即可用;或者直接让你帮他改上面两个文件也行。

落地的依据**只能是第一步查准的事实**——id、参数字段、取值范围都照报告填,绝不凭记忆补。
