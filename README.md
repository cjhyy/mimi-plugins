# mimi-plugins

codeshell 官方插件市场。`.claude-plugin/marketplace.json` 与 Claude Code marketplace 格式兼容,可被 codeshell / Claude Code 直接添加为插件源。

## 插件

| 插件 | 说明 |
|------|------|
| [skill-creator](plugins/skill-creator) | 交互式引导创建和改进 skill(SKILL.md):访谈 → 选位置 → 起草 → 校验 → 触发测试 |
| [media-downloader](plugins/media-downloader) | yt-dlp + ffmpeg 下载视频/音频/字幕/播放列表/剪辑;SKILL.md 路由 + references 排错表与参数速查 |

## 使用

codeshell 桌面端首次启动会自动注册本市场并预装核心 skill;也可手动添加:

- codeshell:设置 → 扩展 → 市场 → 添加 `cjhyy/mimi-plugins`
- Claude Code:`/plugin marketplace add cjhyy/mimi-plugins`

## 目录约定

```
.claude-plugin/marketplace.json   # 市场清单(名称/插件列表/版本)
plugins/<name>/                   # 每个插件一个目录
  .claude-plugin/plugin.json      # 插件清单
  skills/<skill>/SKILL.md         # 插件携带的 skill
```
