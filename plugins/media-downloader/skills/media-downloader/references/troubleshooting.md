# 排错表:stderr 特征 → 诊断 → 动作

先跑 `yt-dlp -v "<URL>"` 拿完整日志,再对表。**总则:升级 yt-dlp 永远是第一排错步骤**——站点反爬月月变,旧版本是最常见死因(`brew upgrade yt-dlp` / `pipx upgrade yt-dlp` / `pip install -U yt-dlp`)。

| stderr 特征 | 诊断 | 动作(按序尝试) |
|---|---|---|
| `HTTP Error 403` / `403 Forbidden` / `Sign in to confirm` | 被风控或需要登录 | ① 升级 yt-dlp ② 带 cookie(见下) ③ 用代理的换节点,或关代理重试 |
| `SABR` + `missing a url` | YouTube 实验性接口(部分格式缺 url) | 升级 yt-dlp + 带 cookie;必要时换网络/代理节点 |
| `LockingUnsupportedError` / `No such file or directory` + `.part-Frag` | **下载目录在同步盘(iCloud/OneDrive/坚果云)或桌面**,分片临时文件被同步进程动了 | 换成本地普通目录;降低并发;关杀毒/同步后重试 |
| 字幕请求 `429` | 字幕接口限流 | 确认字幕参数带了 `--ignore-errors`(视频不受影响);字幕过几分钟用 `--skip-download` 单独补 |
| `HTTP Error 404` | 视频已删除/链接错误 | 核对链接;不要重试 |
| `HTTP Error 416` / 文件已存在被跳过 | `--no-overwrites` 在生效 | 想重下就删旧文件,或去掉该参数 |
| 下载极慢/超时 | 网络/被限速 | 代理环境加 `--proxy http://127.0.0.1:<port>`(端口问用户);防封限速 `--limit-rate 5M` |
| `ffmpeg not found` / 合并失败 | yt-dlp 找不到 ffmpeg | 回到环境自检;非标准路径加 `--ffmpeg-location <path>` |
| 年龄限制 / 会员视频 / 地区限制 | 需要登录态 | 带 cookie(见下) |

## Cookie 两种带法

**方式一(优先):直接读浏览器**

```bash
yt-dlp --cookies-from-browser chrome "<URL>"   # 也支持 safari/firefox/edge/brave
yt-dlp --cookies-from-browser "chrome:Profile 1" "<URL>"   # 指定 profile
```

坑:macOS 读 Chrome 会弹一次钥匙串授权;**Chrome 正在运行时 cookie 库被锁可能读不到**——让用户关掉 Chrome 重试,或改用 safari,或走方式二。用用户**实际登录过该站**的那个浏览器。

**方式二(兜底/无头环境):Netscape cookie 文件**

让用户用浏览器扩展(如 "Get cookies.txt LOCALLY")导出该站 cookie,然后:

```bash
yt-dlp --cookies ~/cookies.txt "<URL>"
```

坑:必须是 **Netscape 格式**(首行 `# Netscape HTTP Cookie File`);JSON 格式的 cookie 不行,yt-dlp 会报格式错——先 `head -1` 校验再用。
