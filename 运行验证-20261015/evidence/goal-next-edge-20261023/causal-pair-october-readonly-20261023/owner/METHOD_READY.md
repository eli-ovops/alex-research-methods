# 一日公共数据读取与时钟配对QC（READY，未正式执行）

2026-10-23。仅本owner目录归Data Owner；Root/review及旧资料不修改。actual model / effort UNKNOWN。普通公共数据下载已获任务授权；现在停在READY，等Root/Reviewer快审后的Root放行，不向用户重复索批。

## 固定对象与一次顺读

1. Kraken：唯一匿名完整GET `https://datasets.tardis.dev/v1/kraken/quotes/2026/10/01/BTC-USD.csv.gz`，预期12,646,757B，最多20MiB，失败不重试、不换通道/身份。禁自动接受重定向。成功与失败压缩流均保留在owner下`kraken_BTC-USD_quotes_2026-10-01.csv.gz.part`；是否完整只由终态结果认证，不凭后缀。
2. Bitstamp：仅pointer指定的既有10/1 gzip，预期26,500,836B及SHA256 `22d347447c1b12f422ea2ed16ba84725eb1b8c716a22aa6b53f775f7e2fd2fe0`。不下载、不复制、单遍流式hash/CRC/QC；不进保护Library。
3. 先完成Kraken流式下载、原压缩字节落盘、hash/gzip EOF/CRC/单源CSV检查，再打开Bitstamp顺读。每源仅保留86400点的最近local_timestamp与L1有效flag（array/bytearray，无价格数组），最后合并时钟数组。不交织两条大迭代器，避免HTTP等待；无第二次QC/hash遍历源。
4. 源读取有字节预算、唯一网络段（包括Kraken流内QC）120秒alarm、总CPU120秒及256MiB峰RSS检查，单线程；120秒不新增为整formal墙钟门槛。新增盘上限64MiB，不安装、不付费。压缩读取64KiB缓冲。使用显式NoRedirect handler/opener，在发出重定向第二个GET之前拒绝；不依靠geturl事后检测。所有失败保留部分件/错误，不自动重启。HTTP错误只保存至多64KiB的同次错误响应，非新请求。

## 单源检查

固定身份：bitstamp/BTCUSD/现货book_snapshot_25、kraken/BTC-USD/现货quotes，UTC日期2026-10-01。必须有exchange/symbol/timestamp/local_timestamp及L1四字段；不计算Bitstamp其余24档价格/深度指标。全行重复比较涉及完整CSV行文本，除此仅检查L1。

- 完整读至CSV/gzip及压缩源EOF，CRC错误即停止；Bitstamp SHA/bytes须匹配旧pointer，Kraken bytes须匹配声明并形成新的SHA。
- 保留物理序，不排序修复；local与exchange时钟倒序各计数。仅local接收钟倒序/缺失使该次local-asof配对不准入；exchange源事件跨频道乱序只报告，不单独阻断配对。同µs并列保留，as-of取最后物理行。
- 只计相邻整行重复，不删行；非相邻全局重复UNKNOWN。
- 缺失、非有限、非正或不能解析的L1数值按字段/类别计数；交叉bid>ask及锁价bid=ask分别计数，不修价、不反向寻找较好的旧有效行。保留其记录存在与L1有效flag区别。
- source timestamp晚于local只报告计数，不作个人延迟解释。两钟分别统计首尾及UTC日外行；local日期不符、缺local、身份/结构不符或空源则时钟配对不可准入。source日外/数值异常保留描述，不自动解释feed故障。

## 固定网格及输出

UTC 00:00:00至23:59:59，每秒一点，共86400点。每源只能取local_timestamp≤t的最近物理行，同钟最后一行；不插值、future-fill、取未来最近价或按有利价格选行。不能定位的timestamp只计错误且不用于配对，不能认证配对可用。

输出只有聚合：
- 双源有最近行、仅缺Bitstamp、仅缺Kraken、两边都缺；
- 双源最近行均有有效L1的格点数；
- 双边记录年龄都≤1秒、都≤5秒；以及互斥的最大记录年龄≤1秒、(1,5]秒、>5秒。
- 不输出逐点时钟/价格、不计算价格相关、leadlag、标签、预测、持仓、成交或收益。
- 唯一最小见证例外：每源固定网格索引0/43200/86399，只存tick、所选local、下一条local（若有）、所选/下一条物理数据行号（header不计，从1起）、有效flag及年龄。没有价格，不做全点audit；可核所选local≤tick<下一条local及同戳取最后物理行。

年龄是“距最近保存更新的时长”。报价/快照可随状态变化才记录，因此>1秒或>5秒不直接证明断流、报价已撤销或坏数据；年龄只描述、不删样本、不设置全覆盖硬门槛。高覆盖也不证明feed完整、真实可成交或个人500ms优势。local倒序/缺失时即使仍有机械覆盖计数，也明确标不可作为已准入的因果配对；source时钟倒序仍是描述项。

## 准备证据与正式入口

`pair_data_qc.py`仅标准库；缺显式参数时只打印READY，不打开行情或联网。原`synthetic-checks-v2.json`保留；本次`--revision-selftest`只检查集中修订影响的redirect/local-vs-source倒序/三个固定见证，回执为`synthetic-revision-checks.json`。人工测试不是市场证据，不重新运行原数据QC。

正式入口仅在Root放行后使用：
`python3 pair_data_qc.py --formal-after-root-release`。
脚本先exclusive写FORMAL_STARTED.json防止同目录正式重跑；终态写result.json。READY时上述正式文件均未创建，两个行情源均未打开。

只检查as-of边界、同戳末行、缺失/陈旧计数、倒序、相邻重复及最小hash/CRC语义。未用真实行情试跑、未加载策略/Notebook或模型，不恢复旧停止配置，不扩任何日期/供应商。

