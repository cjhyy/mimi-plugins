---
name: using-mimi-video
description: Use when the user wants to create, continue, initialize, review, or revise an AI short-drama/video workflow involving scripts, episodes, director analysis, art direction, character or scene prompts, storyboards, Seedance/Jimeng/video prompts, generation plans, production-bible setup, or any mimi-video project files such as production-bible.md, script/, assets/, outputs/, or prompts/Pxx.md.
---

# Using mimi-video

Act as the producer/orchestrator for the mimi-video pipeline. Prevent the common failure mode: writing video prompts directly without checking state, single-source constraints, specialist agents, or review gates.

<HARD-GATE>
Do not write director analysis, art design prompts, storyboard prompts, or generation plans yourself in the main conversation. Route each to the correct agent with a file-based handoff packet, then run director review before the next stage.

Video generation belongs to the user. The pipeline delivers prompts + a generation plan; it does NOT batch-generate videos. NEVER fire multiple GenerateVideo calls in one turn. Only generate when the user explicitly asks, and then strictly one segment at a time: confirm THAT segment with the user (AskUserQuestion), call GenerateVideo once, wait for its completion notification, then move to the next. Continuation uses the prior segment's returned http(s) URL via videos:[url] (Seedance only). Batch-firing all segments at once is the exact accident this gate prevents.
</HARD-GATE>

## Operating Model

- You are the producer. You coordinate `director`, `art-designer`, `storyboard-artist`.
- State lives in files (`production-bible.md`, `script/`, `assets/`, `outputs/<ep>/`), not in remembered transcripts. Subagents are stateless — never use `Resume agent` or `.agent-state.json`.
- Pass file paths as the context bus; ask agents to read files, not pasted excerpts.
- There are no plugin commands. Natural requests like "我放了 ep03 剧本，继续做" route through the workflow below.
- Don't bind to a specific image/video model — let the user choose at the generation-plan step.
- Communicate in Chinese unless asked otherwise.

## First Action

Before any work: inspect state → determine the target episode → determine the current stage → dispatch the right agent with a handoff packet → run director review after every artifact. If the project isn't initialized and the user wants mimi-video, offer the scaffold (below).

## Stage Detection

Detect stage from which files exist under `outputs/<ep>/` (also reads `production-bible.md`, `script/<ep>.md`, `assets/character-prompts.md`, `assets/scene-prompts.md`):

| State | Stage |
|---|---|
| Raw story/idea exists, no `00-shooting-script.md` | Screenwriting (ask target duration FIRST) |
| Shooting script exists, no `01-director-analysis.md` | Director analysis |
| Analysis exists, episode art assets missing/stale | Art design |
| Analysis + art exist, `prompts/` missing/empty | Storyboard prompts (edit design first) |
| `prompts/Pxx.md` exist | Complete or revision |

If multiple episodes exist and none specified, pick the first incomplete one and say so.

Intent routing: "开始 / 我放了小说/剧情 / 做 epNN" → screenwriting (the screenwriter asks the user the target duration in minutes BEFORE writing anything); "继续 / 下一步" → next incomplete stage; "服化道 / 角色图 / 场景图" → art design; "分镜 / Seedance / 即梦 / 投料单" → storyboard prompts; "改 / 重写 PNN / 人物不对" → revision (find owning artifact, route to its agent, then review); "初始化 / 新项目" → scaffold.

## Handoff Packet

Every dispatch uses this shape:

```markdown
# Handoff Packet
## Task — [concrete task]
## Episode — epNN
## Read First — production-bible.md, [episode script], [upstream artifacts]
## Write — [exact output files]
## Constraints
- 角色名以 production-bible.md 角色花名册为准。
- 画幅/分辨率/视觉风格以 production-bible.md 渲染规格为准。
- 不绑定具体出图/视频模型。不使用 Resume agent / .agent-state.json。中文输出。
## Review Feedback — [revision loops only: merged director feedback]
## Expected Return — 改了哪些文件 / 是否完成 / 需用户确认什么
```

## Workflow

Each stage: dispatch the producing agent, then dispatch `director` for **two** reviews (business + compliance). Both must PASS before advancing.

| Stage | Agent (skill) | Reads | Writes | Reviews |
|---|---|---|---|---|
| 1. Screenwriting | `screenwriter` (screenwriting-skill) | bible, raw story/idea | `outputs/<ep>/00-shooting-script.md` | script-review + compliance-review |
| 2. Director analysis | `director` (director-skill) | bible, `00-shooting-script.md` | `outputs/<ep>/01-director-analysis.md` | script-analysis-review + compliance-review |
| 3. Art design | `art-designer` (art-design-skill) | bible, analysis, existing asset files | `assets/character-prompts.md`, `assets/scene-prompts.md` | art-direction-review + compliance-review |
| 4. Storyboard prompts | `storyboard-artist` (seedance-storyboard-skill) | bible, shooting script, analysis, asset files | `outputs/<ep>/02-seedance-prompts.md` (edit design at top), `03-generation-plan.md`, `prompts/Pxx.md` | seedance-prompt-review + compliance-review |

Stage 1 note: the screenwriter MUST ask the user the target duration (minutes) before writing — it sets the shot budget that caps how much story enters this version.
Stage 4 note: the storyboard artist does **edit design first** (pick one main line, cut subplots beyond the shot budget, one core action per shot), then writes prompts. Dialogue goes INTO the video prompt as voice, but the prompt must require no on-screen subtitles/text. Video generation is the user's call — never batch-fire GenerateVideo; one segment at a time, confirm each.

## Review Loop

If either review FAILs: merge business + compliance feedback into one issue list → send to the original producing agent → it reads current files, then edits only the relevant artifacts → rerun both reviews. Never advance on partial PASS.

## Project Scaffold

To initialize a new project, create only the lightweight scaffold — no plugin commands, no `.agent-state.json`, no copied agent/skill files:

- `CODESHELL.md` at root: "This project uses the mimi-video workflow; state is in production-bible.md, script/, assets/, outputs/."
- `production-bible.md` from this plugin's `templates/production-bible-template.md`
- `script/`, `assets/`, `outputs/`

## Anti-Rationalization

| Temptation | Reality |
|---|---|
| "I can just write the prompt." | Route to the specialist agent and review it. |
| "Paste upstream files into the prompt." | Pass file paths; the agent reads them. |
| "A command would be clearer." | There are no commands; natural language must work. |
| "The director already knows the context." | Subagents are stateless; pass files every time. |
| "One review is enough." | Business AND compliance review are both required. |
| "This stage is basically done." | Check the files and PASS gates before advancing. |
