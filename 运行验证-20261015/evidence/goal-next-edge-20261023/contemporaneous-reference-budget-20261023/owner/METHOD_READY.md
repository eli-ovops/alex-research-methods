# METHOD_READY：同时点报价距离描述

Owner external_packet_research_catalog，2026-10-23。唯一协议 ../protocol.md（含结果前新增 S_B>2c 必要条件计数）。正式代码 reference_distance.py；准备阶段网络0、市场源读取0。等 Root 对 code/protocol 精确指纹放行后，显式 --formal-after-root-release 才打开两源。默认入口不读源；一次性 FORMAL_STARTED.json 防止同目录重复执行。

复用上单已审 Source/HashingReader/open_csv 的小副本，而非导入旧实验或策略包。精确整文件 unified diff 见 helper-change.diff。保留物理顺序、local-asof 同戳末行、CSV/gzip顺读与流内hash；Source所选行元组只追加当前bid/ask供计算，pending未来行不参与统计。新增必要字段/local时序/交叉异常即停；源事件钟倒序仍按上单作描述，不能冒充接收钟倒序。CSV可解析完整行但只解析L1四个数字，不开展25层深度QC。两源按网格交织各顺读一次，最后各drain至EOF/CRC，校验固定字节/SHA；全通过前不公布距离统计。

固定86400个UTC秒点，仅双方L1有效点进入统计。全部有效层与三互斥年龄层全部保存；未知计数保留。必须复核86398/76512/9608/278及首两点双缺，否则STOP且无统计解释。年龄只表示距最近保存更新时长。固定0/43200/86399各源时钟见证无价格；极值只存首次并列的网格索引。

公式与协议逐项相同：mid_B=(b+a)/2，mid_K=(kb+ka)/2；S_B=10000(a-b)/mid_B，D=10000(mid_K-mid_B)/mid_B，absD=abs(D)，U=10000(mid_K-b)/b，V=10000(a-mid_K)/a。每量min/median/p95/p99/max；排序后最近秩ceil(p*n)-1，空层UNKNOWN。Decimal算式后只在临时binary64数组保存指标供分位排序，不输出逐点值或价格；浮点显示不宣称无限精度。U/V及S_B严格阈值在除法前用Decimal交叉乘积判断，避免先转float再比边界。c固定0/1/5/10/30/40；每层保存U>c、V>c、同时>c、S_B>2c计数，并断言同时>c蕴含宽度必要条件。

Kraken只是输入，不称公平价、未来目标、可获价差、收益、markout或预测上界。30/40bp是公开费用量级的条件比较，不是账户实际或10月1日历史费率；不核算退出/双边获单/排队/滑点/库存/税费，不创建第二交易腿。秒点不视为独立交易，不累加bp，不训练模型、不生成未来标签、不运行策略或账户交易。

少量人工检查已通过（preparation-checks-final.json）：公式分母及正负号、严格阈值相等、S_B=2c边界、最近秩偶数中位数、空层UNKNOWN、1/5秒年龄边界、追加报价元组后的同戳末行和未来pending隔离。初次新增前的 preparation-checks.json 保留；最终回执覆盖协议新增项。没有重跑旧完整QC fixtures；合成不作为市场证据。

标准库/1线程，CPU累计120秒、RSS256MiB、新磁盘8MiB、主动研究45分钟；无联网/下载/安装/付款。异常即停、保留小结果、不重读或调参重跑。Rootrelease须含顶层code_sha256/protocol_sha256，正式回执绑定release自身SHA。旧代码、数据、标签、结果、封存和金融STOP不改。实际model/effort UNKNOWN，规则沿协议三版本。
