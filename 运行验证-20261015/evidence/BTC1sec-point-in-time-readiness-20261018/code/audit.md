# 固定crypto-rl的point-in-time代码审查

结论：**固定工具不能单凭导出system_time证明该行在标签时刻已经可用于预测。** 本轮补齐具体book、TradeTracker和配置，代码链可明确区分事件字段、采集处理时钟与导出网格标签；历史2021生成绑定由publisher Owner独立核，当前仍不以此工具版本认证真实文件或宣称实际泄漏。

固定commit `078081e5715cadeae9c798a3d759c9d59d2041bc`。新3份原文普通GET均200，8,083B，UTC 2026-10-18T12:25:34.001299Z—12:25:55.497962Z。复用此前保存完整tree `75f6caa20ec4de14fabd30b29cc4e7a47a4e6ec9`，3份源码本地Git blob均与其条目相符；没有访问旧受拒tree。原URL、UTC、SHA256、既存原文身份及精确引用见audit.json/source-receipts.json。

简称：D=既有Database，S=Simulator，B=Book，C=CoinbaseOrderBook，O=OrderBook，P=PriceLevel；CB/TT/CFG是本轮CoinbaseBook/TradeTracker/configurations.py。

| 代码逻辑已证 | 时点含义/限制 |
|---|---|
| CFG:28–35默认RECORD_DATA=False、BATCH_SIZE=100000、TIMEZONE=tz.utc、快照间隔1000000微秒 | UTC与1秒是该固定默认配置；默认不采集。不能把默认值当历史实际运行配置 |
| D:55–63仅recording=True时以本地dt.now覆写index/system_time，先入缓冲，满批再write | local处理时间，非市场事件时间/精确写盘时间；数据库与导出实际可访问时间可晚于它 |
| C:146–148调用db.new_tick之后设置last_tick_time=msg.time；默认replay的Database不改写历史system_time | msg.time与system_time是不同来源字段。其历史准确含义和同步误差未由代码认证 |
| S:210–229读取tick.system_time作输入时间；首次应用tick后把last_snapshot_time设为last_tick_time | 起始网格使用事件字段，后续推进用system_time比较。两钟差异可影响首批标签；网格未直接对齐UTC整秒边界 |
| S:234–261在跨界tick到来后，先render当前状态一次，把同向量复制到所有跨过网格标签，再处理该tick | 触发tick未进入这些快照，但这些标签的生成要等它到来；不是在每个标签时刻定时输出，也非mean/min聚合 |
| B:191–193、210–228、250–272提取流tracker并clear；O:87–95提取buys/sells并clear；TT:14–24、35–54存累计交易notional、读属性无额外变换 | render是读取并清流统计的边界；跨多个标签复制同一flow向量，不能视为各秒独立新增流后逐行相加 |
| CB:19–39插入size或remaining_size后同时add_limit/add_quantity；41–69以maker_order_id扣match.size并add_market；75–92按old_size−new_size减库存；103–115仅reason=canceled时计remaining_size的cancel | 明确是已经处理的过去消息统计，change未记为cancel；不能叫未见/未来订单流。preload同走insert，初期flow可能含初始化记录，实际清理配置需另证 |

O:80–81的midpoint为绝对中价、spread为绝对价差；P按quantity×price累加notional；B:175距离为price/midpoint−1。上述公式只补足固定实现解释，不认证实际CSV单位或历史变换。本轮不再扩大数量/收益问题。

**教学时间轴，完全是假设例子，不是真实行情或2021证据：** 假设第一条可处理消息的msg.time为00:00:00.000，system_time为00:00:02.100，程序先应用该消息，再将网格起点置为事件时间00:00:00.000。下一条tick在local/system_time 00:00:02.200进入，程序可能把既有状态写为00:00:01与00:00:02两行。该状态已含local 02.100才处理的消息，且两行都到02.200才由这条触发tick生成。因此不能把两个标签直接当当时已可见；是否真实发生这种钟差未知。

**另一教学例子：** 已有网格标签t，下一条tick直到t+3秒才来，render一次得到flow向量F，复制到t+1、t+2、t+3。F是已有tracker历史量，不是三份互不重叠的新流。它不表示触发tick被提前看见，也不证明真实文件确有这段空隙。

最小正确时序要求（只提出，不实施）：

1. 绑定实际发布v1的生成commit/config与后处理，明确system_time、msg.time、时区、重置和起始网格规则。
2. 对特征区分event_time、local_received/processed_time、生成/提交/发布available_at。预测决策只能使用依赖均已到齐且available_at不晚于决策截点的记录；标签时间不能替代available_at。
3. 证明初始化/重连快照完成与钟差处理，并标识复制网格和flow累计区间；避免把preload与复制flow当真实逐秒到达。
4. 若只有CSV标签而无可用时间，不能凭“整体滞后1秒”或任意经验lag保证因果；需原日志/可用性上界或按已证规则保守排除。不能由当前源码直接恢复真实2021逐行available_at。

分层判断：代码链核验完成；条件性不可即时可得风险有具体依据。一般的晚触发生成和前值保持可以完全因果，不能单凭晚生成判泄漏；需区分真实可用时间延迟与混合时钟条件下把已含较晚local消息的状态赋给早标签。**真实2021是否存在标签后生成/未来依赖、误差规模及具体预测泄漏仍UNKNOWN**。未运行计算，未检查市场数据或预测样本。

剩余最小原件是实际v1生成身份与可用性/时钟记录，由publisher Owner负责；本代码Owner不另建数据Owner、不泛搜。所读版本PERMISSIONS-2026-10-14-v1/ROUTING-2026-10-13-v4/HANDOFF-2026-10-10-v2；actual model/effort/速度UNKNOWN。0来源执行、模型/训练/回测、市场文件/CSVZIP解析、标签/成本计算、凭证/交易/付费安装或外发。只保留code目录原文、回执与两报告，无清理项。
