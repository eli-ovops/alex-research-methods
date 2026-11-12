# Basis固定Notebook：独立静态时序与经济边界审阅

UTC日期2026-10-23，精确起止UNKNOWN。actual model/effort/speed UNKNOWN；继承路由，Followup没有setter。已读现行PERMISSIONS-2026-10-14-v1主规则及AGENTS.details §2/3对应HANDOFF-2026-10-10-v2、ROUTING-2026-10-13-v4。本次仅指定文件只读与本review写入，无网络/Notebook/模型/策略运行、数据或金融重算。

固定对象：Git blob870724a0af3cfcd4ec15d698842941b51a6aaf4c；本地Notebook SHA256 472d315152bb7c2aa1b9a657f65462c09d21f02a84eefe2f3ab7b6d998ca7d8a。实读导出全部19代码cell，并以惰性JSON源文本核19cell均对应导出；未执行代码或加载输出收益数组。另读首段educational/返佣Note及获取receipt。下列行号指root/sources/basis-code-static.txt。

## 1. 左端时间戳提前可见的疑点有明确代码链

L68–86两腿group_by_dynamic(index=local_timestamp,every=sampling_interval).agg(mid_price.last())，未显式label/closed/period、未保留桶内实际last时刻。L88–100按桶时间join，rolling_mean包含当前行差值，输出原桶时间。L107–112固定100ms桶/3000行均线；L173–179跳过timestamp≤current_timestamp，取最后一行，L181直接fair=spot+basis，再L183–187生成报价。

因此**只要该运行Polars默认将100ms左闭桶标在左边界**，该行值使用的是桶内last、可见时间却只核左边界，静态设计即存在提前引用桶内未来数据的路径。比较符号是>才停，等于桶左端也能消费该行；rolling_mean平滑不是延后一桶。订单决策也100ms、或之后订单有传输延迟，不会自动让决策输入恢复因果。

教学时间例（不是运行结果）：若桶[12:00:00.000,.100)最后观测在.090，预计算行时间为.000，而回放在.020消费该行，则使用了决策之后的.090信息。实例仅说明条件逻辑，不给实际发生次数、利润改善或确切提前长度。

本独审随后已读Root保存的官方语义读取记录（非本人重新联网）：Polars0.20与当前stable默认closed=left、label=left、period=every，故在这些已核默认下，源码提前可得链成立，属于具体设计层因果缺口。Notebook当时Polars版本、原market/precompute数组或hbt起始相位未核，不能升级成已测得每次均泄漏、提前恰100ms或全部收益来自泄漏，也不能据execution_count推当前版本可复现。官方定位见下文补核。

## 2. 这是什么报价与库存机制

现货mid及期货mid差的滚动均值给fair锚（L94–100、181），没有学得预测权重、预测期限或样本外精度检验。position/order_qty进入normalized_position/skew（L165–170），买卖fair偏移受best bid/ask限位及tick取整（L183–187），随后双侧GTX网格撤旧发新（L192–233）。这是跨市场价格参考驱动的条件做市机制，不是已披露XTX模型。

L138 asset_no=0，L271只建[asset]一个linear资产回放。spot仅用于参考价输入，代码未创建/交易现货对冲腿，不能称现金现货—期货无风险套利或两腿利润账。库存容许正负及skew/名义上限并不证明尾部/强平风险已实证控制。半价差参数或库存限额不等于获利因果贡献。

## 3. 成交、费用和净利证据边界

L256–280显式插值order_latency文件、power_prob_queue_model(3)、no_partial_fill_exchange、trading_value_fee_model(-.00005,.0007)、5万美元订单和100万美元名义库存上限。只证明这些回放配置，不证明本人时延、真实队列fill、可得maker返佣/资格或容量。开头Note明确educational，并称基于Binance Futures最高0.005% maker返佣；不是零售普适条件。

L302–308以LinearAssetRecord/resample5m/stats(book_size=1m)计算输出，具体PnL含费/库存估值口径由Root另核stats源码，本独审不据summary数值推完整个人净利。Notebook未显式展示现货对冲账、资金费/融资、运营/税费、真实本人执行账或最终库存实际清算；这些未取得不能记0。亦不能把图中收益反推价格预测alpha或把其单额缩成5000本金等比例可复制。

两版本CELL13/21使用同样撮合/费率/库存/interval配置，仅参考现货BTCUSDT换为BTCFDUSD（CELL17–20）；并不是两次独立、控制全相同的个人净利润证明。未检验FDUSD/USDT现金兑换等条件。

## 行动判断

应先将这个固定公开示例保留为方法候选，并把信号时间戳因果性列为会改变收益证据接受的具体缺口。若Root官方语义支持默认左标，本版本的公开收益不能直接当已经通过因果时序验收的可复制净利证据；这不是对作者实际运行数据或整个HftBacktest引擎的全部否定。本次不修源码、不新实验、不移动或改写旧已验收结论。


## 官方语义与固定统计源码补核（本轮闭合）

只读Root保存的《官方语义读取记录.md》及三份同固定tree Git-blob源码文本；没有联网/运行Polars或引擎。默认语义不是由Root结论替代源码：Notebook的构造/消费链已由本Reviewer独立实读；官方默认参数由Root已取得记录支持。Polars0.20页签名/窗口/period/label定位分别为原文L1378–1402、1422–1425、1445–1454：
https://docs.pola.rs/api/python/version/0.20/reference/dataframe/api/polars.DataFrame.group_by_dynamic.html
读取日2026-10-23，发布日UNKNOWN；Notebook实际Polars版本UNKNOWN。因此接受的是“按已核官方默认此固定写法存在lookahead路径”，不替原运行鉴定实际污染幅度。

metrics-a1d916f.py L42–44：Ret使用equity_wo_fee−fee的末首差；L164–167 ReturnOverTrade=Ret/TradingValue；L278–282 TradingValue为保存trading_value_合计。stats-608433a.py L419–438：linear equity_wo_fee由balance+position*price*contract_size记账；若有累计trading_value则差分，缺字段分支仅用位置差估算且源码警告记录间信息会丢失。没有原raw stats字段，不能认证此Notebook当次实际走哪个分支或其精确成交名义。

nopartialfillexchange-ae8daa4.rs L318–348和379–405：GTX订单到所时已穿对手价则Expired，存活进maker队列；L125/132/149/157和259/268/295/304的被动成交调用maker=true，fill L178–190按maker状态和执行价更新账。这支持固定全GTX LIMIT路径的maker费率解释，不认证真实本人获单/返佣资格。

现已静态核Notebook cell14/22的原text/html完整表头及对应列：ReturnOverTrade分别显示0.000032（显示四舍五入值，约0.32bp）与0.000031；cell14 Return显示0.05166。此前text/plain中表头折行成ReturnOve/rTrade、其他列有省略，不把该层说成完整表头来源。未运行统计，亦未把截图/显示值冒精确账。若同一计价区间、原TradingValue分母正确且全部成交确按maker −0.00005，则含返佣单位成交回报=无返佣记账项+0.5bp。因此第一显示值对应同路径去返佣项约0.32−0.5=−0.18bp。此为带前提、用四舍五入展示数的标量恒等式，不是零返佣策略回放，更非已证明原真实run或实盘亏损；未改变订单行为/库存/分母，不能据此提供个人策略收益。

独立view_image完整读Root从Notebook cell15原嵌入输出提取的PNG（未重画）：橙线明确标Equity w/o fee，末端低于零；另一蓝色曲线末端为正。stats L192–213绘图公式将前者与equity_wo_fee−fee并列，故发布者自己的图支持“该展示的正含费结果依赖负费率返佣”的条件解释，不需要从小图估精确金额。图是作者发布回放输出，不是独立验证或实盘原账；且前述时序缺口仍存在，返佣不能修复它。

新增源码固定blob：metrics a1d916f29ab8fe325e7c23abed0c60e27be5d615；stats 608433afb86f36864f3a8c896bd2a9b483f7191b；exchange ae8daa41cb054dc22ac2439270c0448895531287。公开入口为各本地receipt的api.github.com/repos/nkaz001/hftbacktest/git/blobs/对应ID，Root GET200日期2026-10-23；本Reviewer核文本SHA和Git blob身份，不运行。官方stats文档来源：https://hftbacktest.readthedocs.io/en/py-v2.4.2/_modules/hftbacktest/stats/metrics.html 。Notebook实际执行依赖是否正是这些版本UNKNOWN。

最终判断：PASS_WITH_LIMITS（只读审阅完成），无额外必须调研。存在两条会改变个人复制决定的具体问题：按已核默认的信号可得时间前置；发布输出的条件返佣依赖。当前不能将这个固定Notebook作为已核因果、普通个人费用后赚钱的现成证据。它保留为公开机制参考，不能据此宣判作者真实交易、整个引擎或所有跨市场预测无效；不改旧已验收结果，不启动修复/新回放。
