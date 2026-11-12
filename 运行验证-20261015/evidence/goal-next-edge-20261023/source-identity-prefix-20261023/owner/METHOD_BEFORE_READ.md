# 独立来源身份前缀核验：读取前固定边界

2026-10-23。仅新source-identity-prefix单元；旧一日QC已结束，不恢复、不重试网络、不改其code/result/manifest/seal/.part。规则PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4；actual model / effort UNKNOWN。

唯一输入是已保存压缩部分件：
`/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/goal-next-edge-20261023/causal-pair-october-readonly-20261023/owner/kraken_BTC-USD_quotes_2026-10-01.csv.gz.part`。

固定只读一次打开、分块8KiB、最多64KiB压缩字节；zlib gzip前缀解码最多256KiB，单线程CPU≤10秒。遇到完整header及第一条CSV记录即停止，不再前进。只核gzip魔数/压缩法等固定头，不请求EOF/CRC、不hash源、不全扫、不试修复。

CSV仅保留原始header文本和解析字段名，第一条记录只提取exchange/symbol文本，与冻结期望kraken/BTC-USD分别比较。其他列不作数值解析、不保存、不输出，不产生价格/量/标签/信号。任何异常仅记类型/固定错误码，避免错误信息带出原行情。

输出限小receipt/note及必要的小提取脚本/运行回执：记录方法与脚本hash、源绝对路径、实际压缩/展开读取字节、是否前缀截断、第一行身份和实际exit/PID/CPU。不声称第一行代表全部498272行，不认证完整来源、全日、EOF/CRC或双源配对。零联网/新下载/安装/付费/账户/模型/策略；不读旧Bitstamp或保护Library。正式仅实施这一次前缀单元。

