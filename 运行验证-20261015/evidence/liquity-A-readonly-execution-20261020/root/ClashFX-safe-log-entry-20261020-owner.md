# ClashFX 当前日志机制与安全入口（仅静态/元数据）

结论：已定位当前ClashFX应用日志目录 `/Users/USER/Library/Logs/ClashFX/`，有一份元数据上可能覆盖11:30:10–15Z的日志；**没有读取正文，尚不能确认目标连接记录是否存在**。独立mihomo core日志仅定位到静态文件名`.mihomo_core.log`，实际完整路径/是否写入/保留范围UNKNOWN。不凭文件名或mtime认定网络根因，也未证明此应用监听系统代理端口。

读取UTC：2026-10-20T11:43:11.849634+00:00。Root已有PID/libproc身份，本Owner另定点读取Info.plist及bundle一层文件名/大小：CFBundleIdentifier=com.clashfx.app，CFBundleShortVersionString=1.1.11，CFBundleExecutable=ClashFX；Info.plist SHA256 `ffabdec5ae26dc0391aa03dd4d96308497e472072f1fad47ebb8aa19de5e81a6`。未读取任何yaml、订阅、配置、env/argv、凭证、剪贴板或Terminal。

## 已有静态机制证据

- `/Applications/ClashFX.app/Contents/Resources/CocoaLumberjackPrivacy.bundle`存在。应用Mach-O `/Applications/ClashFX.app/Contents/MacOS/ClashFX`（75819264B）以内存映射只筛固定日志关键词字串，未执行：`DDFileLogger`、`DDLogFileManagerDefault`、`defaultLogsDirectory`、`logsDirectory`、`ClashFXLogFileManager`、`.mihomo_core.log`。没有输出或保存任意相邻字串/URL，也没有读取core执行文件或运行它。
- 这些可支持“bundle包含CocoaLumberjack文件日志机制/自定义file manager及core日志名”这一有限结论；不能从符号证明具体日志级别、应用日志是否含core网络消息、字段格式、轮转时限/持久化保证。
- 未执行`log show`/`log stream`，未读取OSLog store。是否还有额外OSLog数据UNKNOWN；当前已存在文件入口优先，不泛查系统日志。

## 仅目录元数据实读

只对由应用名及默认文件日志机制指向的两个精确目录做exists/stat：

| 位置 | 读取到的元数据 |
|---|---|
| `/Users/USER/Library/Logs/ClashFX/com.clashfx.app 2026-10-20--19-12-31-899-+0800.log` | regular file，528473B，mtime UTC2026-10-20T11:42:03.076746+00:00 |
| `/Users/USER/Library/Logs/ClashFX/com.clashfx.app 2026-10-20--17-20-06-379-+0800.log` | regular file，1048598B，mtime UTC2026-10-20T11:12:31.654781+00:00 |
| `/Users/USER/Library/Logs/ClashFX/com.clashfx.app 2026-10-20--16-22-33-342-+0800.log` | regular file，1048635B，mtime UTC2026-10-20T09:20:01.024906+00:00 |
| `/Users/USER/Library/Logs/com.clashfx.app` | 不存在 |

文件正在变化的可能性保留，mtime/大小是本次metadata快照，非封存hash；未读/哈希日志内容。最新文件名有+0800，但该名字不保证**消息正文**使用相同时区，不能未经识别强行换算消息。仅元数据不能确认11:30或公开目标在内容中，不能据无旧文件mtime覆盖就判缺失。未枚举其他应用/全盘/配置目录。

## 下一次如需消息内容：先限定格式与最小提取，不在本任务执行

实际行格式/字段目前UNKNOWN。CocoaLumberjack允许自定义formatter，不能把其常见格式冒充当前原文。建议Root若确定有必要，限定**仅上表最新一个精确文件**、先重新stat、总读取≤1MiB/单行≤16KiB、单次本机内存过滤，不拷贝/打印/落盘原文，也不跨文件补扫：

1. 内存中只识别确定的时间语法/显式时区；仅输出格式枚举及“能否无歧义转UTC”布尔，不输出样本消息。没有足够时间字段或明确时区就UNKNOWN停止，不能以filename offset代正文时区。
2. 只接受UTC[2026-10-20T11:30:10,2026-10-20T11:30:16)且包含精确公开host `eth-mainnet.g.alchemy.com` 的行；若host仅在另一行、关联ID缺失或时间无法解析，不自动串联。输出匹配计数/覆盖布尔、UTC、固定阶段枚举（upstream-connect/TLS/UNKNOWN）、固定错误类型/整数错误码；任何无法白名单解析的消息仅UNKNOWN，不输出原异常文本。
3. 禁止输出代理节点/地址/端口、订阅、用户URL/path/query、HTTP头、密钥、账户或任意行片段；不因匹配0就推出没有该连接，需注明app/core日志范围未知及轮转/级别可能缺失。若没有与目标同时间的可归属记录，即没有足够证据，不新连网/改代理或要求新输入。

这只是可审读取方案，尚未实现解析器或读取任何消息。Root可据实际格式前提决定是否存在安全的下一窄读；`.mihomo_core.log`完整位置仍未定位，不猜用户配置目录去找。

资源与停止：本轮保守CPU10秒（非全命令实测）、主动≤15分钟、新文档<64KiB，旧累计不清零，0网络/付款/连接/源码或配置变更。只写本文件，不改旧原件/其他Owner。当前Owner停止。
