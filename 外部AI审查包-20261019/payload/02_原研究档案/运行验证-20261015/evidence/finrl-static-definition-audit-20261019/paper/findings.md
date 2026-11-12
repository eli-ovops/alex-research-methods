# FinRL-X v1论文—固定代码版本绑定审计

结论：可核同一官方项目与对应机制，**尚不能核为论文观察期内同一个可复现部署**。+19.76%是作者报告的两策略ensemble之Alpaca纸面跟踪，不是Adaptive Rotation单腿实盘扣费收益。公开代码和README可用于静态机制研究，不替代当时checkpoint、配置、信号/持仓/成交/费用原件。没有指控论文作假，也不把未取得原件写成全部公开资料不存在。

## 论文定义：几个口径不得混用

原文为[arXiv2603.21330v1](https://arxiv.org/html/2603.21330v1)，原生L40标22 Mar 2026；实际HTML与原生行回执均保存。以下定位见paper-v1.native-lines.txt对应L行及HTML节号：

|定位|已读作者定义|不能推出|
|---|---|---|
|§4.1 L153–155|历史期2018-01-07至2025-10-24，每边10bps；另列2025-10-26至2026-03-12纸面期；称滚动样本外与仅用当时可知信息|未给具体训练/验证/测试切点、调参候选与选择记录、训练完成时间或模型hash，不能独立认证无选择偏差/泄漏|
|§4.2 L165–166|DRL用rolling OOS作模型选择|仅原则说明，不是明确冻结的选择算法/实际训练日志|
|§4.4 L213–218|Rolling Selection是NASDAQ100候选、季度财报后选top25%+DRL配置；Adaptive Rotation另以相对QQQ的IR选组、组内残差动量、最多两组、每周轮动|两者不是同一策略；DRL滚动选股组合的绩效不能归给规则轮动单腿|
|§4.5 L219–240|每日调仓的两者ensemble，在Alpaca paper环境，作者报告+19.76%；作者明说短样本不确立统计显著alpha|不是实际资金；§4.5未明确该数字扣了哪些全部费用，不可把历史10bps自动认作纸面实收费用，也不能反断言完全未扣费|

论文的系统级“一致接口”、risk overlay和paper部署声明，不等于逐笔原账已独立勾稽。§4.5的订单拒绝、跟踪误差等只给低水平定性描述（L235），没有本轮可审的完整数值账/模型版本对应；作者汇总与独立核账严格分层。

## 固定README与Git元数据

实际读取固定[README](https://github.com/AI4Finance-Foundation/FinRL-Trading/blob/4409abe925c904e570be78ebfb5e77ac3491dff8/README.md)，API返回的Git blob `c624724b88486a063396d4121e4de2505cd21446`与本地解码原文一致。fixed-README.inert.md：L115起区分Rolling+DRL，L119–130为每周轮动+每日监测；L160–180明确ensemble纸面表；L236–246示例指定AdaptiveRotationConf_v1.2.1.yaml。只是README源码文本，任何部署/安装/账户指令均未执行。

实际[固定commit元数据](https://github.com/AI4Finance-Foundation/FinRL-Trading/commit/4409abe925c904e570be78ebfb5e77ac3491dff8)的author/committer时间都是2026-09-18T01:13:20Z；message是合并修正MLStockSelectionStrategy缺少apply_risk_limits的PR。该时间晚于纸面截止和v1登记日期，且是这一个Git提交的时间，不是repo最早公开日期、release发布日期或全体代码最早产生时间

README指向论文、重列其结果，却没有给观察期内实验commit、checkpoint、ensemble组合权重/运行manifest、账本hash或早期release原件。因而只足以建立“作者将此项目呈现为官方实现”的关系；不能从晚版README倒推早期运行版本。也不能仅凭晚commit证明所有历史代码都不同。初次4读至此未查历史；之后root补充一个最小路径历史核查，所得独立证据如下，原始原件全部保留。

## 补充：观察期截止前已有历史候选（不是当时部署证明）

限定固定commit4409abe925c904e570be78ebfb5e77ac3491dff8为history根，分别只查README实际列出的 `src/strategies/AdaptiveRotationConf_v1.2.1.yaml` 和 `src/strategies/run_adaptive_rotation_strategy.py`，until=2026-03-12T23:59:59Z、per_page=30。两个GitHub公开metadata请求均HTTP200，各只返回同一提交：

`d70c43420a4e73534da753f72b238a6785c61220`，author/committer均为2026-02-05T14:52:54Z；message为Add Adaptive Multi-Asset Rotation Strategy。原JSON4712B/SHA256 `f255118155b6d0fcbd47af6c1ce4600970df57951a33e1af91abcacbd2aa0ca0`，两路径各保留独立URL/HTTP/UTC回执。未取得旧源码、模型或release，也未执行任何代码。

因此，已找到元数据早于观察期结束的2/5候选提交，但未取得实验当时运行绑定。不能只凭最新9月提交便放弃历史机制/代码的可复用性。反面限制同样明确：Git author/committer时间不是独立事前公开日期、release时间或实际执行时间；该候选晚于2025-10-26纸面期起点；未绑定Rolling Selection+Adaptive Rotation ensemble、完整模型/配置或券商记录。论文对应早期运行版本仍UNKNOWN，不是“所有早期代码不存在”。metadata阶段止于这两个限定路径；之后按root追加的最后两读只比较旧文本如下，不追全repo、旧模型或第四案例。

### 2/5候选源码与9月固定源码的最小静态比较

旧commit d70c…的两个已指定文件实际GET200：old-runner.inert.py.txt21898B/SHA256 `e1e7d826c52a0d31733be927aebedd178d302926e7a5b8f3d6555e59bdd195ea`；old-engine.inert.py.txt24524B/SHA256 `727dfc857dd47db88a2d56aa0a903928db93475170e2f6187e77a1fa88b02973`。只读惰性文本，不import/执行或取旧模型；Git blob为计算指纹，无expected tree独立核对。

|局部问题|旧2/5候选与当前9月源码比较|限定意义|
|---|---|---|
|独立收益报告/费用入口|旧runner L335–406只汇总仓位、保存summary/weights/audit后return；该文件没有当前L408调用、L417起的_generate_performance_report，也未见独立收益/费用参数入口|当前新增报告段不能倒套为旧runner已计算的回报。不能从旧runner缺入口断言别的组件无费用|
|close与持仓状态|旧L158–160取as-of数据的close；L243–250用末close建PositionState|这是状态/价格基准，不是实际成交/严格可得性凭证；只读范围不足以独立认证每个bar可得时刻|
|fast-risk-off|旧L271–291明确只log并更新tracking，不append权重结果|该局限已见于2/5候选，不能单独归因为9月改动；也不证明paper ensemble使用此路径|
|ranking lookback接线|旧engine L149–151与当前L149–151均将ranking.top_n_per_group传给lookback_weeks；两engine全文去换行差异后相同，原始bytes/hash不同|该接线不是9月新引入；未取旧config内容或模型，不据此认证旧实际数值/实验使用关系|

为定位比较，当前runner的独立报告L443–456用权重行及其日期close至下个权重日期close计算portfolio value，所见循环无显式成本；这不是另一个通用BacktestEngine，也不是论文纸面ensemble原账。本轮只是验证旧/新文本差异，未重新核算任何收益。以上不能推出论文用错代码、作假或根本不可复现；精确实验绑定仍缺原件。

因此，固定版本中专用rotation显示报告、通用回测组件、论文ensemble纸面曲线必须各自标识。当前专用组件能跑或输出一张表，不等于已重现论文+19.76%账。具体成交/费用代码和信号时序由其他Owner核，本审计不重复执行或扩大其结论。

## 可复用与证据等级

- 已证：原论文节号与作者实验描述；固定README/blob与commit身份；已有config/license身份回执可复用。
- 作者报告：滚动OOS、信息截至t、paper性能与运行稳定性。它们不是本轮独立复现或券商资金对账。
- UNKNOWN：观察期实际部署hash、完整训练/选择时序与参数、原始ensemble权重、完整纸面费用口径、实际成交/持仓/费用账绑定、真实资金收益。
- 现有archive schema只列price_data/raw_payloads等数据表，没有本轮已核的独立纸面绩效表；仅复用旧目录检查原件，不读取DB行。不能据此断言所有地方都没有日志。

原代码许可和供应商数据权利独立；本审计没有新增任何数据许可通过结论。最小改变判断的原件是：论文对应的当时固定版本/配置/checkpoint和paper运行manifest，明确连接该ensemble与原始记录。无需完美NTP或作者回复作为先验通用门槛，但也不能用现代README替代这个身份关系。

## 读取与限制

8/8公开小读取：论文原生一次、同URL正常GET留完整hash一次、固定commit元数据一次、固定README API一次、限定路径历史metadata两次、2/5候选两源码文本，均无拒绝。读取UTC集中2026-10-19 02:14–02:18，完整HTTP与各原件SHA见source-receipts.json。HTML HTTP Last-Modified为2026-08-24，仅记录为服务端文件元数据，不把它自动解释为v1科学内容在该日修改；v1标注与该头分开。

0源码执行/import、0模型/训练/回测/金融核算、0DB内容/行情数组读取、0账号/凭证/安装/交易/外发；唯一写paper/，旧结论与其他Owner文件不改。actual assistant model/effort UNKNOWN。到本结论停止，不扩大第四案例。
