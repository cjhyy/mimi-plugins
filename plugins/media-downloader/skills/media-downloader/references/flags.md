# 参数速查

## 格式选择器(`-f`)语法

- `bestvideo+bestaudio/best`:最高清视频+最高质音频,合并;斜杠后是单流兜底。
- 过滤条件写在方括号:`bestvideo[height<=720]+bestaudio/best[height<=720]`。
- 常用过滤:`height<=N`(清晰度)、`ext=mp4`(容器)、`vcodec^=avc1`(强制 H.264,排除 AV1,设备兼容性最好)、`fps<=30`。
- `-F` 列出的格式号可直接用:`-f 137+140`(调试用;正式配方别写死格式号,各视频不同)。
- 质量档位映射(人话 → 选择器):best→`bestvideo+bestaudio/best`;1080p/720p/480p→`height<=N`;worst→`worstvideo+worstaudio/worst`。

## 输出模板(`-o`)常用变量

`%(title)s` 标题 · `%(ext)s` 扩展名 · `%(id)s` 视频 ID · `%(uploader)s` 频道名 · `%(upload_date)s` 日期(YYYYMMDD) · `%(playlist)s` / `%(playlist_index)s` 列表名/序号。

播放列表建议:`-o "~/Downloads/%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s"`(每单一目录、序号排序)。

## 字幕参数矩阵

| 需求 | 参数 |
|---|---|
| 人工字幕 | `--write-subs` |
| 自动生成字幕(没人工时) | `--write-auto-subs` |
| 语言 | `--sub-langs "zh.*,en"`(`zh.*` 同时命中 zh-Hans/zh-CN 等变体) |
| 统一转 srt | `--sub-format vtt --convert-subs srt`(srt 对后续处理/学习场景最通用) |
| 烧进视频文件 | `--embed-subs`(需 ffmpeg) |
| 列出可用字幕 | `--list-subs` |
| 只要字幕不要视频 | `--skip-download` |

## 播放列表/批量

- `--flat-playlist --print "%(playlist_index)s %(title)s"`:只列单不下载(快)。
- `--playlist-items 1-5,8,10`:范围+离散选集。
- `--playlist-end 10`:只取前 10。
- 批量 URL:写进文件用 `-a urls.txt`。

## 网络与重试

- `--proxy http://127.0.0.1:7890` · `--limit-rate 5M` · `--socket-timeout 30`
- `--retries 5 --fragment-retries 5 --retry-sleep 3`(或指数退避 `--retry-sleep exp=3:30`)
- `--concurrent-fragments 4`:分片并发提速(同步盘目录别开,见排错表)。

## 其他常用

- `--download-sections "*00:01:30-00:02:45"`:只下时间段(需 ffmpeg)。
- `--write-thumbnail` / `--convert-thumbnails png`:封面。
- `--embed-metadata --embed-chapters`:元数据/章节写入文件。
- `--dump-json --no-playlist`:机器可读的完整元数据(时长/清晰度/格式列表)。
- `--ignore-config`:忽略全局配置(本 skill 默认带,保证确定性)。
