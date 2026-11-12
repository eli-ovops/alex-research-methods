# Carver公开报告：只读原账审阅

审阅日期：2026-10-16。只读已存reports/system与4个必要源文件，未运行代码、模型、回测或交易。结论仅评估证据完整性：当前公开报告有实际生产系统诊断价值，但不是能够独立复核2025-04-06—2026-04-05净盈利的完整年度原账，也没有独立券商审计证明。作者净23.7%及前一年−16.3%仍应明确标为作者自报；本次没有重算或确认这两个数字。

## 原件能证明什么

固定reports commit：`50f5af7cc58af5a690967d00135986d91f1b9930`，仓库 `robcarver17/reports`。固定system commit：`a62269d27707806ba61f516791b71a9cd14cf268`，仓库 `pst-group/pysystemtrade`。

|原件|实际保存范围/字段|审阅判断|
|---|---|---|
|P&L_report|2026-10-14 22:48—10-15 22:48；总P&L−0.745%，分instrument、strategy、asset class；futures−1.550%，residual+0.805%|单日百分比汇总，非年度逐日账户权益/资金流账。分instrument大多只显示一位小数，不足精确闭合年度收益。|
|Trade_report|2026-10-14 22:49—10-15 22:49；六段No trades|只能说明该报告窗口没有显示交易；不能说明全年无交易，更不是全年逐腿成交文件。|
|Reconcile_report|2026-10-15 22:48；DB与broker各22条当前合约持仓，有instrument_code、contract_date、expiry_date、position；Trades in DB及from broker均空表，列含fill_datetime/fill/filled_price|支持当前持仓一致性自检，不能替代逐期持仓、完整fills及独立broker原件。报告称Broker vs Contract无break，但Optimal vs actual仍有三个break。|
|Commission_report|报告日期2024-03-20；configured/broker/diff及货币对照|费率/配置诊断，并非2025—2026全年逐笔佣金receipt，不能将broker列逐行求和当全年佣金。|
|Slippage_report|2026-02-06—10-15；按instrument汇总bid_ask_trades、total_trades、sampled、权重、estimate、Configured及差异，两组单位为price/ticks|滑点估计与配置诊断，混合交易和定期采样，不是每笔quantity×price的成本ledger。日期也未覆盖完整被声称年度。|
|Costs_report|2026-02-07—10-15；percentage_cost/annual volatility/SR_cost，分别列both、commission only、spreads only|预期单笔成本和SR量纲，不是年度已付现金成本。三个面板互有包含关系，不能相加。|
|Strategy_report|2026-10-15生产时点；backtest timestamp20261015_222807；目标/优化/当前仓位及预测诊断|包含大量当前配置与决策信息，但不是过去年度每次决策及实际执行历史。标题中的backtest timestamp不可当作真实券商成交凭证。|

原件入口均为 https://github.com/robcarver17/reports/tree/50f5af7cc58af5a690967d00135986d91f1b9930 。根保存的source-receipts固定相应blob；本次不修改它。

## 净值与费用：重复扣除的具体风险

1. **Costs_report的both面板已经包括spread及commission。** 将其与commission-only、spread-only面板或Commission/Slippage报告再相加，会重复计量；而且这些量大多是预期单笔百分比或SR单位，不能不经数量/币种/时间映射就从年度收益扣减。
2. **真实fill price已包含执行相对报价的滑点/买卖差价效果。** 当前源 `pandl_using_fills.py` 的 `merge_fill_prices_with_prices` 在有成交的时间用fill价格合入价格序列；production/reporting/data/pandl.py按实际fills/持仓/FX/合约点值计算instrument和strategy部分。因此若从按fill计算的P&L再次完整扣Slippage_report估计，存在重复扣滑点的风险。这里只确认源码路径，不证明作者当前运行或年度自报每个环节都采用相同版本。
3. **佣金是否已体现在账户总收益、是否只出现在residual，尚不能独立确认。** production `get_daily_perc_pandl`取accumulated capital的差分并除maximum capital，期间再求和；分instrument/strategy路径调用fills计算器时未显式传佣金成本。代码又把total减strategy/futures解释为residual。当前报告residual很大，但没有明细，不能把它全部解释成佣金、FX、融资或其他任一项。不得据此肯定“所有佣金已扣”或“佣金漏扣”。
4. **已称net的年度自报不能再机械减配置成本。** 必须先取得期初/期末账户权益、每日现金/持仓MTM、全部外部出入金、实际commission/FX/利息等，确认net定义及它与fills口径的关系，再决定还需扣什么。现有公开文字不支持完成这一步。

必要源码：
- https://github.com/pst-group/pysystemtrade/blob/a62269d27707806ba61f516791b71a9cd14cf268/sysproduction/reporting/data/pandl.py
- https://github.com/pst-group/pysystemtrade/blob/a62269d27707806ba61f516791b71a9cd14cf268/systems/accounts/pandl_calculators/pandl_using_fills.py

## 配置、独立性和对照缺口

- 公开软件提供private_config.yaml加载路径及环境目录override，示例需本地broker和MongoDB参数。这说明完整production运行需本地状态与配置；不能据“代码开源”推断作者个人实盘配置、数据库或账户全部公开。没有读取/连接任何真实凭证。
- 已存public `systems/provided/rob_system/config.yaml` 有规则、权重、25%目标波动等大量参数，但与当前Strategy_report有可见差异：公开config风险max正常风险倍数1.75/最大杠杆20，报告风险为2.0/15；公开名义资金500,000，报告使用710,482.06。可能来自override、动态状态或不同生产配置；来源尚未核清。因此不能将该public配置认定为2025—2026账户完全相同配置，也不应凭少量差异断言其不可复制。
- 对于声称年度，未见完整期初/逐日/期末权益及外部现金流、全年度每合约持仓和fills、逐笔费用原件、完整价格/FX/合约乘数/换月历史、逐期版本与参数绑定。当前22仓对账无法补齐这一年度链。
- reports由作者自身系统生成，内含“from broker”字段也不是另一个独立来源：没有原始券商statement、外部审计签署或可核验的第三方连续账户记录。
- 本轮报告未给出同资金、同风险、同费用、同市场窗口的可执行基准，不能把作者账户正收益直接解释为规则alpha；也不能跨年度选择盈利年、忽略−16.3%自报年份。
- 软件LICENSE为GPL3.0；reports仓库metadata license=null且README只有一行标题。软件授权不能自动扩展为reports数据、券商数据或市场行情复用授权；具体个人研究/交易使用的授权结论留根核定。

## 尚不能确认

年度净收益、年度佣金和总滑点实际支付额、出入金处理、精确收益分母、funding/融资与FX影响、已公开规则与年度实际配置的一致性、独立券商证明，以及对比简单可执行基准的净增量价值。当前原件足以保留为更强的研究候选和生产诊断实例，但未满足独立年度净盈利复核。

本次最多4次必要源码GET，4个小文件；新增文件仅在audit-source/及audit-source-receipts.json。本报告未给盈利成立与否作超出证据的判断，也未将当前无交易、当前对账或软件可运行当作年度验收。
