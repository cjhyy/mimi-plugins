---
name: media-downloader
description: 当用户想下载视频或音频时使用——下载 YouTube/Bilibili/B站/抖音/Twitter 视频、视频转 mp3、提取音频、只下字幕、下载播放列表、剪辑视频片段、查看视频清晰度。基于 yt-dlp + ffmpeg;工具缺失会先引导安装。触发词:下载视频、download video、yt-dlp、转 mp3、下字幕、剪视频。
---

# Media Downloader — yt-dlp + ffmpeg

yt-dlp 支持上千个站点。本 skill 是「自检 → 路由到配方 → 排错」三段式;**报错时不要盲试参数**,先读 `references/troubleshooting.md` 对表。参数细节速查在 `references/flags.md`。

## 第 0 步:环境自检(每次下载前先做,别等报错)

查"装没装"**和"够不够新"**——yt-dlp 版本号是日期 `YYYY.MM.DD`,站点反爬月月变,**版本太旧是下载失败的头号原因**,所以下载前就该拦,不要等 403/SABR 报错才想起升级。

```bash
command -v yt-dlp >/dev/null && yt-dlp --version; command -v ffmpeg >/dev/null && ffmpeg -version | head -1
```

判断版本是否过旧(把版本号当日期比):**超过 ~30 天就先升级再下载**。一条命令直接判龄(无 python 时改用 `date` 手算):

```bash
yt-dlp --version | python3 -c "import sys,datetime; v=sys.stdin.read().strip()[:10].replace('.','-'); d=(datetime.date.today()-datetime.date.fromisoformat(v)).days; print(f'yt-dlp {v} 距今 {d} 天'); print('⚠️ 偏旧，先升级' if d>30 else '✓ 够新')"
```

- **缺了 → 安装**(征得用户同意):macOS `brew install yt-dlp ffmpeg`;Windows `winget install yt-dlp.yt-dlp Gyan.FFmpeg`;Linux `sudo apt install ffmpeg` + `pipx install yt-dlp`(apt 的 yt-dlp 太旧)。兜底:`python3 -m pip install -U yt-dlp --break-system-packages`。
- **太旧 → 升级**(同样先问):`brew upgrade yt-dlp` / `pipx upgrade yt-dlp` / `pip install -U yt-dlp` / `yt-dlp -U`(standalone 二进制自更新)。升级后再继续下载。
- **优先包管理器,别下 standalone 单文件二进制**——PyInstaller 打包的首次运行要解压内嵌 Python,冷启动可达 ~24s,容易被误判挂死。

## 任务路由

先问清存哪(没说就 `~/Downloads`);输出模板统一 `-o "~/Downloads/%(title)s.%(ext)s"`。

| 用户要什么 | 配方 |
|---|---|
| 看有哪些清晰度/格式 | `yt-dlp -F "<URL>"` — 拿不准格式时**先列再选**,别猜 |
| 下视频(默认最高清) | `yt-dlp -f "bestvideo+bestaudio/best" --merge-output-format mp4 --no-overwrites -o "…" "<URL>"` |
| 指定清晰度(如 1080p) | `-f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" --merge-output-format mp4` |
| 只要音频 mp3 | `yt-dlp -x --audio-format mp3 --audio-quality 0 -o "…" "<URL>"` |
| **只下字幕**(不下视频) | `yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "zh.*,en" --sub-format vtt --convert-subs srt "<URL>"` |
| 视频+内嵌字幕 | 默认视频配方 + `--write-subs --write-auto-subs --sub-langs "zh.*,en" --embed-subs --ignore-errors` |
| 播放列表 | 先 `yt-dlp --flat-playlist --print "%(playlist_index)s %(title)s" "<URL>"` 列给用户确认,再加 `--playlist-items 1-5,8` 下载 |
| 剪片段(已有文件) | `ffmpeg -ss 00:01:30 -to 00:02:45 -i in.mp4 -c copy out.mp4`(无损秒剪,切点在关键帧;要精确到帧去掉 `-c copy`) |
| 只下载某片段 | 默认视频配方 + `--download-sections "*00:01:30-00:02:45"` |
| 查视频信息 | `yt-dlp --dump-json --no-playlist "<URL>"` |
| 封面/元数据 | `--write-thumbnail` / `--embed-metadata` |

## 全局防御约定(每条命令默认遵守)

- **`--ignore-config`**:忽略用户机器上的全局 yt-dlp 配置,保证行为可预期(全局配置常埋着代理/格式偏好,会让同一条命令在不同机器表现不同)。
- **URL 永远加引号**:YouTube 链接带 `&`,不引会被 shell 截断。
- **单视频链接带 `list=` 参数时加 `--no-playlist`**,否则会意外下整单。
- **字幕参数后必带 `--ignore-errors`**:字幕接口常 429 限流,不能连坐整个视频任务失败。
- 默认带 `--no-overwrites`;网络差时加 `--retries 5 --retry-sleep 3`。

## 交互契约

- 长下载(>1 分钟的视频)放**后台执行**,期间可汇报进度;完成后 `ls -lh` 报文件路径和大小。
- 播放列表必先列单确认再下,可能非常大。
- 403/登录类问题需要用户配合(cookie),按 troubleshooting 表引导,别替用户决定读哪个浏览器。
- 下载前确认用户对内容有合法使用权;DRM 内容拒绝(yt-dlp 也不支持)。
