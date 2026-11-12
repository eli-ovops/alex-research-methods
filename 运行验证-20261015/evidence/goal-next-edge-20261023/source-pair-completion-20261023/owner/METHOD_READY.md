# METHOD_READY：最小资料适配副本

2026-10-23；Owner：external_packet_research_catalog。仅本新单元 owner/ 写入；旧代码、部分件、结果和封存不变。协议唯一入口为 ../protocol.md，正式执行等待 Root 按代码及协议指纹放行；准备阶段网络请求 0、市场源读取 0。

基线为 ../../causal-pair-october-readonly-20261023/owner/pair_data_qc.py（已审 SHA256 c7b5115fc7482060e3e639451e70c24e51fc307fada287e7e509120ef7b72252）。helper-minimal-change.diff 保存精确 unified diff。

改动仅为：Kraken 正文期望改为 kraken/BTC/USD，下载 URL 仍使用 BTC-USD；唯一网络段（含流内 QC）墙钟改为 900 秒；新增实际身份有限见证与计数；新单元正式启动前机械核对 root-release.json 中 code_sha256、protocol_sha256，并把 Root 放行文件指纹绑定到启动与结果回执。

实际身份精确比较不作别名放宽。最多保存 8 组身份，每字段最多 128 字符并明确截断性，计数保留；身份不符先记录实际值及不符计数，再立即停止，故不能将已读计数外推未读全文件。正式异常分支保留已读 source stats。

其余已审方法保持：显式拒绝重定向；一次普通匿名完整 GET，无 HEAD/Range/续传/重试；Kraken 完整后才打开旧 Bitstamp。各源单遍流式压缩保存/hash/字节数/EOF/CRC及CSV检查；Bitstamp绑定旧SHA和字节数。只保留时钟与有效标志数组，固定 UTC 日内86400个1秒点，local_timestamp<=t 最近物理行，同戳末行，不排序、去重、插值或未来填补。固定索引0/43200/86399保存无价格时钟见证。local缺失/倒序阻断配对，exchange倒序只计数。记录年龄只表示距最近保存更新的时长，不证明断流、报价撤销、个人延迟或feed完整。

资源保持 CPU累计120秒、RSS256MiB、1线程、下载20MiB、本单新增磁盘64MiB、主动研究30分钟；网络段900秒，不新增整个formal墙钟门槛。异常/到帽即停并保留部分件，不再取数。无价格关联、未来标签、模型、策略、收益、账户或交易。

仅运行 --preparation-selftest 的少量合成检查：正文BTC/USD精确匹配、URL不变、实际身份计数、错误身份先见证后停止、900秒常量；通过回执见 preparation-checks.json。没有重跑旧as-of/CRC/数字完整fixtures；人工合成不是市场证据。READY只代表准备可审，未GET、未打开旧源、未完成正式资料QC。

规则：PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4 / HANDOFF-2026-10-10-v2；实际model/effort UNKNOWN。
