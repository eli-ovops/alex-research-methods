# 研究家族目录：供外部 AI 独立审查

编制：2026-10-19。工作区相对路径为唯一定位方式。这里只综合既有人类报告与文件名索引，没有新金融研究、联网、模型、回测或交易。数字是旧报告转录，未重算。当前模型/effort/route 为 UNKNOWN。

本目录定位到 evidence 下 **204 个一级单元**，并索引运行验证根层 **131 份 Markdown 报告**、**44 份 root/结论.md**、早期预测资料 **10 份中文报告**。204 是目录计数，不是204个独立实验、204项成功或204次完整阅读。家族划分只帮助导航；例如数据许可与执行问题会跨家族。实读层级见 receipt.json：两份最新主报告及两份去重/分流文档完整读取；若干代表性报告仅读开头节选；其余仅索引。没有重验底层原账或原论文全文，也没有把第三方README当自写报告装包。

阅读顺序：先看最新目标综合和HMM补核，再看本目录的正证据与局限；最后用索引回查，不能把旧“下一步/尚未运行”直接当当前待办。外部 AI 可以不同意现有停止判断；challenges.md 专门要求审查我们的门槛、归因及资源选择。

## 1．XTX 原始机制、财务与财富目标

研究内容：Gerko/XTX如何取得交易收入，AI在估价、报价和风险承接中的作用，英国公司/LLP财报与个人财富的关系；追查“640亿元”和Gerko财富1%的口径。
正证据：既有报告核得自有资金交易、向客户和交易所提供流动性、部分外汇算法执行收费；公司正利润与财报原件保留。
未确认：生产权重、特征、分策略利润排名及个人到账未公开；关联服务收入不可重复合并；新闻财富估值变动不是当年交易利润；2026原榜与当前目标仍未核。2025的87.45亿英镑只是有年份的估值，既有1%算术为8745万英镑。
当前去向：保留机制与财报研究，不把某个公开模型称为XTX核心；财富目标未达成。企业权益、资本、税费与容量不能用一次回测复利替代。
入口：`Alex-Gerko-XTX公开研究报告-2026-10-14.md`；`运行验证-20261015/XTX到个人财富目标-赚钱机制与证据收敛判断-20261016.md`；`运行验证-20261015/evidence/goal-evidence-synthesis-20261019/root/决策报告.md`。

## 2．公开模型、数据与许可

研究内容：XTX Global Forecasting Challenge、第三方入门/参赛材料、Qlib/Alpha158/LightGBM、Kronos公开实现和数据；Bitstamp、Twelve Data、Binance、Kaggle、Kraken、CoinMetrics、CHRIS、Tardis、LOBSTER、Crypto Lake、HftBacktest、BitMEX；后期Tiingo与Alpaca的22资产数据路径。
正证据：确有公开代码、模型及某些可读数据文件；部分许可有明确私人研究依据。数据质量、字段、时间、费率和使用许可分别核验。
失败/未确认：公开可见≠可商用/可永久封存；目录覆盖≠实际API逐日覆盖；价格代理≠可成交价。Tiingo免费留存与本方案不匹配；Alpaca只有部分技术/产品证据，适用数据权限和许可未闭合。不能把一家供应商不合格外推为策略不可行。
当前去向：停止为自定22资产探针逐家追供应商，保留数据审阅。不复制论文、网页正文、陌生源码或权重进此人类报告包；需要核原件时沿原报告来源定位。
入口：`公开预测资料-20261014/公开预测材料核验报告.md`；Tiingo/Alpaca各自root结论；BTC数据、时钟、免费数据与许可系列报告。

## 3．Kronos：AAPL、50股、输入与盈利转换

研究内容：输入协议、OHLCV与时间语义、论文盈利案例复用、低成本数据、首轮AAPL、50股迁移、同步窗口归因、费用/容量与封存终点预测。
正证据：本机实际推理、封存及独立产物核验完成；50股×188同步窗=9400条预测。AAPL首轮MSE比基准高约4.18%，统计区间跨零；50股固定设置比不变价基准差4.074%，原预测门槛FAILED。
未确认：失败不能唯一归因模型能力、领域迁移或输入适配；9400条不是独立9400次检验。预测误差不直接等于交易效用；论文策略/市场/成本不能直接继承。旧未来封存与成熟评分另有记录，不用本目录替代其验收。
当前去向：保留原FAILED和结果，不追加调参。能运行公开模型已经证明；能盈利与放大尚未证明。
入口：首轮真实评估报告、Kronos-small-188窗口归因与加速验证判断、transfer50的50股真实评估报告；经济探索、终点观察与score-maturity-guard均列入索引。

## 4．BTC 价格预测：分钟LSTM、日频及误差诊断

研究内容：公开BTC预测示例的独立适配，分钟价格/挂单压力LSTM与岭回归、训练前向诊断，日频固定样本外与经济对照。
正证据：分钟固定运行真实完成；加压力MSE比价格版改善0.9143%，但未达预设1%，仍约为不变价基准34.95倍；训练内MSE亦约8倍以上，不能单归咎测试泛化。日频2023–2025在单边25bp假设下5000→8157.53美元，虚拟正收益保留。
失败/未确认：分钟35倍是MSE比，不是亏损倍数；岭回归存在数值警告，旧“对照可靠”需降级。日频综合门槛NOT_SUPPORTED，两个主对照更高，但风险/暴露不同，不能仅终值排序识别预测作用。旧TEST被反复查看，不是新独立检验。
当前去向：固定用法不推进交易系统；原预测、权重、FAILED/NOT_SUPPORTED均保留。诊断与重跑必须区分。
入口：BTC订单簿预测首次固定离线检验、35倍误差诊断、训练集前向诊断、BTC日频单次离线结果。

## 5．风险比例与年度配置

研究内容：每日风险缩放、每年一次配置后持有、同初配静态持有、风险身份、数据来源、执行与容量，2020新资金再入场。
正证据：2014–2025年度A相对同初配静态B，25bp下虚拟终值约148.85万/11.72万美元，风险比约0.988，描述性门槛通过。2020新5000美元/零BTC入场，A55144.15/B49274.54美元，风险比约0.8075合格且回撤较低。
未通过：2020 Sharpe增量0.146719低于事前0.20；不是风险资格失败，也不能抹成规则完全无效。每日调仓相对年度规则未过优势门槛。历史样本与规则形成、基准身份、收盘代理及末端大额退出限制独立保留。
当前去向：目前最强历史管理正证据之一，但未转成可执行财富。参考分钟量198倍不是实际参与率，也不是绝对无法成交证明。
入口：按风险比例持有一次历史诊断、annual-vs-static与annual-restart2020系列、人类经济综合报告。

## 6．挂单压力、成本空间与BitMEX技术停止

研究内容：最优档失衡I0是否有增量；一秒先知报价空间和固定60秒报价空间；双时钟、因果可见性、原生反向合约盈亏、费用/返佣与五日固定实验。
正证据：一秒1,030,656合格对，先知最优方向下每边1bp仅3.758771%正空间、5bp仅0.027167%；60秒单日1438窗，每边1bp正312窗、5bp正14窗，10/25bp零正窗。是历史报价诊断，不是策略收益。Albers论文报告真实资金复杂做市系统，价差−4.4749bp加双边5bp返佣后余量+0.5251bp。
失败/未确认：成本比例不是胜率；重叠窗口不能加总复利；论文未隔离I0单因子和完整原账，返佣条件不能移植当前普通用户。BitMEX五日因TARGET_CLOCK_FORMAT停止，0拟合0预测、未评分，科学状态TECHNICAL_DATA_UNDETERMINED_NO_MODEL_RESULT。
当前去向：保留数据/成本/原生盈亏核查，停止追加该简化模型实验属于资源决定；技术错误不能称模型无优势，也不能因0拟合自动继承旧一次运行许可。
入口：BTC1sec与Crypto Lake60s成本诊断root结论、BitMEX-five-date-once结论、order-imbalance-economic-attribution与current-fee-admission结论。

## 7．公开预测案例、竞赛与可审计记录

研究内容及有限正证据：
- Jansen ETF：保存holdout模拟账扣包内佣金/滑点后+18.1409%，账目闭合；随后发现同测试期换配置重评、匹配基准与风险/成本并不一致，不能称全新独立优势。
- RSI、Funding Harvester、配对/宏观carry/横截面动量、FOREX/astra/dsa等：存在公开代码或作者结果；多数仅索引，本目录不独立认定净利或失败。Carver、Trendrider、Scrooge、AAII及TradingStrategy：已有事前/实盘/公开状态核验支线，保留其原报告限定。
- MomentumTransformer、DeepMomentum：已研究可复用环节与成本；后期机构真实成交成本论文提供成本实施经验，不等于个人周频纯多头轮动的完整原账。
- FinRL2023：提交后模拟评价是正面流程证据，但选定队伍收益、时间/夏普错报、版本和费用限制保留。FinRL-X：有历史扣费模拟、纸面组合+19.76%及Apache2代码；两策略ensemble不能归为单腿轮动，后期实现不能倒授历史版本。
- G-Research：截止后用新行情评价且前三树模型，是比事后回测强的预测流程；相关性、排名、奖金不是交易净利。
- FinAgent：MIT公开实现/架构、历史汇总可读；未来字段存在不等于已证测试泄漏，精确run和完整账未绑定。FinMem：论文明确测试期择最优风险设置且收益公式非完整现金账，实际测试输出未取得。StockBench：明确零成本历史模拟，按见到的同日open成交未证明可执行。
- FreqAI：可复用软件与维护者实时试验陈述，不是完整盈利策略。Numerai：官方公共身份已得，公开回报/评分未绑定固定示例模型及逐轮结算；空查询不是不存在证明。Alpha Arena：429安全检查后停止，UNKNOWN，不是策略失败。
- 新闻：固定成本后历史正结果保留，独立作者新增五周观察也保留；正负组差不是账户收益，首次可得时钟与可成交时刻关键。Form4：原论文/免费SEC入口有正证据，原分类身份键/代码与现代独立净账未核齐，教程不是原复现。
- KMLM：真实基金官方NAV净披露比回测强；基金层费用已扣不等于个人全成本，完整事前规则和归因仍缺。
- QuantConnect：分享机制/记录字段存在，没有取得具体公开run完整账；不能由搜索空结果断言平台不存在案例。
- HMM/sidr20：早期只见189行状态/权重；10/19后续真正补读报告，累计299.04%、年化9.6%、回撤−21.53%，保留低风险表现；报告与README不一致，全期宏观标准化/优化参数进入早期配置的代码路径确证。不能称严格样本外，也不能推出修正后必亏。
- Vanta：模拟交易评价及ALPHA/TAO激励来源不同于市场交易净利，具体策略、逐轮原账和现实成本未闭合。
当前去向：这些是不同证据等级的机制/流程/账目样本；当前综合不建议独立立项任何已核固定候选。外部AI应审查这个资源决定是否过强，而不是被要求服从。

## 8．链上手续费、LP、借贷与库存收入

研究内容：Uniswap V2/V3、Charm/Bunni、rETH、Pendle、Aave、Sturdy、dYdX MegaVault、gDAI，把协议总费用、个人份额、资产返还、利息、资金借还、风险赔付和净数量拆开。
正证据：V2同一小额LP完整退出扣四笔直接gas，相对保留初始两币多9.361165 USDC及0.003166085877958365 ETH；V3十一仓位/其他episode正负结果均保留；rETH真实ETH闭环已核。Aave有真实大小额正负收息/链费对照。gDAI固定存赎与资金借还出现+1.737369382150704725 DAI限定流；一笔手续费支付与RewardDistributed实际转账绑定。
未确认：正资产向量不是已兑现美元收益；协议公式不是个人事前选池/进退规则；不同地址/成功集合不能拼全系统利润。Pendle到期兑回/储备标值、Sturdy分配/历史回应、MegaVault分成与账户余额更新各有未闭合归因；gDAI奖励包括手续费与风险缓冲，不是所有客户亏损直接归持有人。
当前去向：保留真实现金/库存与失败费，不因复制层没过删除正事实；尚无持续优势与容量证明。以上部分只有家族报告开头或文件名覆盖，需循索引读原报告。

## 9．清算、拍卖、公开套利与运营绑定

研究内容：Liquity/V2七次尝试、六月成功集合/Q3需求与竞争时序，Maker买方/启动者拍卖106，Flashbots/Nantucket/New Bedford/FastLane、CoW baseline及ProtoRev。
正证据：Liquity同地址1成6败，七次gas全计后ETH/WETH净+0.039100539874301130；六月九笔成功条件留存有账，另有异资产向量。Maker有实际拍卖/启动收入。ProtoRev存在事前机制与真实套利正盈余；CoW算法/GPL与Nantucket真实执行器线索保留。
未确认：六月全13一笔rETH费用仍缺，不能写全13净利；Q3空返回不等于没需求。公开bot不等于绑定历史运行；协议层执行位置、特殊权限与分成不能靠复制源码获得。一个公开套利调用者同笔报酬低于网络费，官方假设利润不能当实得。
当前去向：学习服务报酬、竞争与净留存；不是继续证明“世界上有没有人赚过钱”。完整机会/发送规则及历史执行绑定与未来个人捕获率分别处理。

## 10．预测市场套利、期权与渠道

预测市场研究了完整组合低价买入/提前merge、4000万美元论文数字、公共成交档案、固定持仓来源、两笔资金流/六笔取得成本。正证据是实际merge/回款及部分取得记录；本金返还、持仓归属和取得成本/费用不全时不能称净利；六笔成本补到后候选降级，旧“待追成本”不能重复作新发现。许可、旧子图失效及条件事件分开。
Ribbon备兑期权研究了首12轮/后12轮、41人cohort、直接20ETH本金、费基异常、波动率输入和实际回款；20ETH新本金界定期扣五笔相关链费后真实多0.286308964405035226 ETH，必须直接承认。后续赔付、美元财富风险与独立策略复刻仍缺，不能年化一段正现金。XYLD有真实基金披露和持仓，完整成交链仍未得。
个人渠道研究了香港盈立、内地上交所资格、Deribit反向ETH、OKX线性/逆向期权单位、保证金/强平、公开历史bid/ask与到期原件、5000美元最小单位/费率。渠道/报价数据可读不等于用户有权限、适用地区已核或完整收费齐全；盈立费用页冲突等缺口保留。没有开户、接券商、下单或付款。
当前去向：保留真实正现金与真实成本/资格缺口；未通过个人当下可执行全成本盈利准入，不把机构/协议利润算用户可复制容量。

## 11．覆盖边界与外部审查任务

主综合报告的“无值得立即运行的任务”是截至对应封存状态的资源建议，不能改写成数学不可能或不存在任何可读余项。HMM从“报告未读”到实读后发现具体问题，就是此前停止措辞需要被校准的例子。
本目录不是原始证据审计。外部 AI 如提出继续研究，应指出具体缺口、既有哪份资料可回答、何种最小新增证据足以改变决定；也可认为现有证据已足以支持更窄的教学/小额研究目标。包内旧许可、费率、条款不声称当前重新核验。

## 附录A．204个 evidence 一级单元的完整导航

以下均位于 `运行验证-20261015/evidence/`。此附录只保证目录名被定位，不保证每个单元内容已读；实读范围见receipt。不同单元可属同一研究，不能当独立试验累计。

### 目标、XTX与研究治理（9）

- `case-decision-synthesis-20261016/`
- `full-goal-evidence-synthesis-20261016/`
- `goal-alignment-readonly-20261018/`
- `goal-evidence-synthesis-20261019/`
- `goal-next-source-audit-20261019/`
- `personal-prediction-route-convergence-20261018/`
- `profit-case-priority-20261017/`
- `public-edge-next-case-20261018/`
- `wealth-target-readonly-20261018/`

### 公开模型、竞赛、公开盈利候选（36）

- `DeepMomentum-original-evidence-20261017/`
- `MomentumTransformer-source-audit-20261017/`
- `aaii-shadow-stock-original-ledger-admission-20261017/`
- `alpha-arena-predictive-case-admission-20261018/`
- `finagent-artifact-admission-20261019/`
- `finmem-record-admission-20261019/`
- `finrl-contest-predictive-case-admission-20261018/`
- `finrl-static-definition-audit-20261019/`
- `forecast-three-case-screen-20261019/`
- `form4-A1-fixed-definition-20261019/`
- `form4-minimal-original-usability-20261019/`
- `form4-opportunistic-buy-signal-admission-20261019/`
- `form4-original-implementation-key-20261019/`
- `forward-case-screen-20261016/`
- `freqai-record-admission-20261019/`
- `gresearch-blind-prediction-admission-20261019/`
- `headline-signal-record-admission-20261019/`
- `kmlm-record-chain-20261019/`
- `momentum-economic-increment-20261019/`
- `new-case-prepublication-admission-20261017/`
- `news-drift-independent-evidence-20261019/`
- `numerai-public-record-chain-20261018/`
- `oos-case-20261015/`
- `preannounced-case-20261016/`
- `predictive-ledger-discovery-20261019/`
- `predictive-originals-route-audit-20261018/`
- `public-case-20261015/`
- `public-profit-case-admission-20261017/`
- `quantconnect-first-public-instance-search-20261019/`
- `quantconnect-public-live-record-gate-20261019/`
- `relative-strength-minimal-definition-20261019/`
- `reusable-case-20261015/`
- `stockbench-record-admission-20261019/`
- `tradingstrategy-live-admission-20261017/`
- `tradingstrategy-state-archive-20261017/`
- `tradingstrategy-target-state-reference-20261017/`

### Kronos、AAPL、评分与复用（7）

- `aapl-once-20261016/`
- `endpoint-recheck-20261015T0456Z/`
- `input-consistency-20261015/`
- `paper-reuse-20261015/`
- `prospective-readiness-20261015/`
- `reuse-readiness-20261015/`
- `score-maturity-guard-20261015/`

### BTC预测、成本与输入（26）

- `BTC-daily-fixed-execution-20261017/`
- `BTC-daily-fixed-protocol-20261017/`
- `BTC1min-failure-diagnosis-20261017/`
- `BTC1min-fixed-evaluation-readiness-20261017/`
- `BTC1min-fixed-evaluation-run-20261017/`
- `BTC1min-public-access-and-clock-20261017/`
- `BTC1min-train-forward-diagnosis-20261017/`
- `BTC1min-training-design-static-audit-20261017/`
- `BTC1sec-access-and-field-semantics-20261018/`
- `BTC1sec-bounded-record-quality-20261018/`
- `BTC1sec-once-cost-diagnostic-20261018/`
- `BTC1sec-point-in-time-readiness-20261018/`
- `BTC60s-independent-data-readiness-20261018/`
- `BTCUSD-fixed-forecast-protocol-20261017/`
- `Binance-public-data-rights-20261017/`
- `CHRIS-current-data-rights-20261017/`
- `CoinMetrics-community-data-audit-20261017/`
- `Kaggle-BTC-long-history-license-20261017/`
- `Kaggle-BTC-v755-file-semantics-20261017/`
- `Kaggle-BTC-v755-full-static-audit-20261017/`
- `Kaggle-BTC-v755-tail-check-20261017/`
- `crypto-book-input-causality-20261017/`
- `kraken-BTCUSD-predictive-data-identity-terms-20261017/`
- `open-license-crypto-book-source-20261017/`
- `original-creator-crypto-forecast-starter-20261017/`
- `priced-in-public-archive-admission-20261018/`

### 风险比例、年度配置、历史重入（9）

- `annual-data-provenance-20261018/`
- `annual-execution-cost-capacity-20261018/`
- `annual-restart2020-execution-20261018/`
- `annual-restart2020-readiness-20261018/`
- `annual-rule-generalization-audit-20261018/`
- `annual-vs-static-execution-20261018/`
- `annual-vs-static-readiness-20261018/`
- `risk-scaled-vs-annual-execution-20261017/`
- `按风险比例持有-最小验证方案-20261017/`

### 挂单压力、订单簿、双时钟与费用（27）

- `BitMEX-first-archive-prefix-schema-20261018/`
- `BitMEX-first-fullquote-symbol-QC-20261018/`
- `BitMEX-five-date-once-20261019/`
- `BitMEX-inverse-payoff-quote-space-bridge-20261019/`
- `BitMEX-native-fee-basis-20261019/`
- `BitMEX-official-quote-data-admission-20261018/`
- `BitMEX-quote-clock-semantics-20261018/`
- `HftBacktest-BTC-example-readonly-QC-20261018/`
- `HftBacktest-continuous-history-source-20261018/`
- `HftBacktest-dual-clock-data-admission-20261018/`
- `HftBacktest-own-sample-permission-20261018/`
- `bitstamp-depth-source-readonly-20261018/`
- `bitstamp-direct-source-readonly-20261018/`
- `causal-raw-LOB-alternative-discovery-20261018/`
- `causal-small-book-source-admission-20261018/`
- `crypto-lake-60s-once-cost-diagnostic-20261018/`
- `crypto-lake-code-manifest-20261018/`
- `crypto-lake-first-BBO-clockpair-QC-20261018/`
- `crypto-lake-first-clock-sequence-QC-20261018/`
- `crypto-lake-first-footer-QC-20261018/`
- `crypto-lake-known-footer-read-20261018/`
- `lobster-free-event-data-admission-20261018/`
- `open-event-data-next-source-20261018/`
- `openbook-causal-caller-audit-20261018/`
- `order-imbalance-current-fee-admission-20261019/`
- `order-imbalance-economic-attribution-20261019/`
- `order-imbalance-isolated-evidence-20261019/`

### 链上借贷、收费、流动性与部署（33）

- `aave-income-ledger-20261016/`
- `aave-source-provenance-20261016/`
- `aave-usdc-cashflow-baseline-20261016/`
- `aave-usdc-large-cycle-cost-20261016/`
- `aave-usdc-small-cycle-cost-20261016/`
- `amm-lp-case-20261016/`
- `amm-v2-actual-LP-share-bounds-20261016/`
- `amm-v2-demand-20261016/`
- `amm-v2-first-Mint-ledger-20261016/`
- `amm-v2-fixed-day-fee-budget-20261016/`
- `amm-v2-prior-inventory-exit-20261016/`
- `amm-v2-second-fixed-exit-20261016/`
- `automated-rule-weth-case-20261017/`
- `bunni-v2-case-20261016/`
- `charm-alphavault-case-20261016/`
- `complete-ledger-case-20261016/`
- `direct-protocol-case-20261016/`
- `dydx-megavault-rule-admission-20261017/`
- `gdai-deployment-ledger-entry-20261018/`
- `gdai-first-fee-cashflow-binding-20261018/`
- `gdai-fixed-case-cost-attribution-20261018/`
- `gdai-historical-ledger-access-20261018/`
- `gdai-original-record-admission-20261018/`
- `gdai-reward-payer-binding-20261018/`
- `inventory-edge-mechanism-20261016/`
- `megavault-btc-ledger-identity-20261017/`
- `megavault-main-feeshare-20261017/`
- `megavault-sweep-indexing-20261017/`
- `pendle-fixed-maturity-case-20261016/`
- `pendle-reserve-state-mark-20261016/`
- `sturdy-historical-allocation-record-20261017/`
- `sturdy-response-origin-final-check-20261017/`
- `sturdy-target-generator-20261017/`

### 清算、拍卖、套利与运营绑定（9）

- `bot-operator-binding-20261016/`
- `cow-baseline-operator-binding-20261017/`
- `fastlane-historical-implementation-20261017/`
- `flashbots-public-arbitrage-identity-20261016/`
- `liquity-Q3-task-demand-20261016/`
- `liquity-june-success-retention-20261016/`
- `liquity-reproducibility-20261016/`
- `maker-auction-case-20261016/`
- `official-liquidator-source-20261016/`

### 预测市场套利与持仓追溯（17）

- `permissionless-case-20261016/`
- `prediction-market-arbitrage-originals-20261016/`
- `prediction-market-closed-ledger-20261016/`
- `prediction-market-first-merge-20261016/`
- `prediction-market-fixed-holder-acquisition-history-20261016/`
- `prediction-market-fixed-shard-footer-20261016/`
- `prediction-market-fixed-shard-holdings-20261016/`
- `prediction-market-holder-history-schema-20261016/`
- `prediction-market-holder-public-archive-access-20261016/`
- `prediction-market-lifecycle-archive-20261016/`
- `prediction-market-merge-acquisition-20261016/`
- `prediction-market-public-archive-20261016/`
- `prediction-market-six-acquisitions-column-location-20261017/`
- `prediction-market-six-acquisitions-fill-footer-20261017/`
- `prediction-market-six-acquisitions-fill-rows-20261017/`
- `prediction-market-two-tx-flows-20261016/`
- `prediction-paper-artifact-followup-20261016/`

### 备兑期权、基金及个人渠道（27）

- `covered-call-personal-channel-feasibility-20261017/`
- `covered-call-risk-premia-original-paper-20261017/`
- `deribit-ETH-inverse-option-current-delivery-cashflow-spec-20261017/`
- `deribit-ETH-option-history-settlement-evidence-admission-20261017/`
- `deribit-ETH-option-public-quote-input-admission-20261017/`
- `okx-historical-option-symbol-units-20261017/`
- `okx-linear-covered-call-margin-admission-20261017/`
- `okx-linear-small-option-fee-structure-20261017/`
- `okx-official-ETH-option-historical-bidask-admission-20261017/`
- `ribbon-completed-option-round-mechanism-20261017/`
- `ribbon-covered-call-source-gate-20261017/`
- `ribbon-direct20-cash-source-attribution-20261017/`
- `ribbon-direct20-user-criteria-scope-audit-20261017/`
- `ribbon-fixed12-live-ledger-20261017/`
- `ribbon-fixed12-persistent-edge-evidence-review-20261017/`
- `ribbon-next-fixed12-original-availability-20261017/`
- `ribbon-nov08-fee-basis-20261017/`
- `ribbon-preopen-cohort-cashflow-20261017/`
- `ribbon-remaining-seven-cashflow-20261017/`
- `ribbon-selected-holder-cashflow-20261017/`
- `ribbon-volatility-input-chain-20261017/`
- `sse-mainland-covered-call-eligibility-20261017/`
- `tardis-free-ETH-option-historical-bidask-admission-20261017/`
- `usmart-contract-assignment-complete-cost-20261017/`
- `usmart-final-public-rule-gap-20261017/`
- `xyld-exante-rule-live-record-20261017/`
- `xyld-full-ledger-public-route-final-20261017/`

### 跨分支数据许可与供应商（3）

- `alpaca-fixed22-data-admission-20261019/`
- `tardis-dedicated-xgboost-terms-schema-20261017/`
- `tiingo-fixed22-data-admission-20261019/`

### 其他被索引单元（1）

- `etf-followup-20261016/`

## 附录B．运行验证根层131份人类报告文件导航

旧稿和before副本只作为历史版本索引；selection.json默认选当前人类报告。

- `运行验证-20261015/AAII微盘价值组合准入-真实资金自述与交易原账访问缺口-20261017.md`
- `运行验证-20261015/AAPL封存预测-一次到期核对-20261016.md`
- `运行验证-20261015/Aave公开利息案例-首十笔筛查与证据边界-20261016.md`
- `运行验证-20261015/Aave大额收息原账-链上成本与复制边界-20261016.md`
- `运行验证-20261015/Aave小额收息原账-实际利息与链上成本-20261016.md`
- `运行验证-20261015/Aave源码公开时间与版本核验-20261016.md`
- `运行验证-20261015/BTC一分钟原件-实际数据质量与时钟核验-20261017.md`
- `运行验证-20261015/BTC免费数据-全文件核验与研究决策-20261017.md`
- `运行验证-20261015/BTC年度配置-2020新入场一次诊断方案-20261018.md`
- `运行验证-20261015/BTC数据-实际文件与最小样本核验-20261017.md`
- `运行验证-20261015/BTC日频-一次样本外扣费验证提案-20261017.md`
- `运行验证-20261015/BTC日频-单次离线验证结果-20261017.md`
- `运行验证-20261015/BTC订单簿预测-一次离线检验方案-20261017.md`
- `运行验证-20261015/BTC订单簿预测-首次固定离线检验结果-20261017.md`
- `运行验证-20261015/BTC训练集前向诊断-跟价能力与预测优势-20261017.md`
- `运行验证-20261015/BTC预测失败诊断-35倍误差从哪里来-20261017.md`
- `运行验证-20261015/BTC预测模型-固定检验方案与执行条件-20261017.md`
- `运行验证-20261015/Binance与Kaggle-数据许可与下一步-20261017.md`
- `运行验证-20261015/BunniV2-链上触发与未修复风险核验-20261016.md`
- `运行验证-20261015/Charm公开策略-区间公式与完整调度缺口-20261016.md`
- `运行验证-20261015/CoW公开代码与运营原账-候选收口-20261017.md`
- `运行验证-20261015/Deribit免费ETH期权报价输入核验-能拿到什么与尚不能证明什么-20261017.md`
- `运行验证-20261015/ETF案例继续核验-基准与测试期重评-20261016.md`
- `运行验证-20261015/ETH期权免费数据证据链-历史盘口与到期原件核验-20261017.md`
- `运行验证-20261015/ETH逆向期权当前规则-权利金支付义务与双币核算-20261017.md`
- `运行验证-20261015/FastLane历史实现与真实调用-源码及成本边界核验-20261017.md`
- `运行验证-20261015/Flashbots公开套利样本-价差逻辑与实盘证据缺口-20261016.md`
- `运行验证-20261015/Kraken-BTCUSD-数据身份与模型研究适用性-20261017.md`
- `运行验证-20261015/Kronos-small-188窗口归因与加速验证判断-20261015.md`
- `运行验证-20261015/Kronos-small-输入一致性补核-20261015.md`
- `运行验证-20261015/Kronos论文盈利案例-复用条件核验-20261015.before-qlib-timing.md`
- `运行验证-20261015/Kronos论文盈利案例-复用条件核验-20261015.md`
- `运行验证-20261015/LiquityV2竞争成本-已清算仓位与实际净收入-20261016.md`
- `运行验证-20261015/Liquity个人复制环节-公开输入与免费数据边界-20261016.md`
- `运行验证-20261015/Liquity六月原始奖励-免费来源核账与规模边界-20261016.md`
- `运行验证-20261015/Liquity六月成功任务-实际费用、分配与规模边界-20261016.md`
- `运行验证-20261015/Liquity失败时序-首次可见与上链等待的证据边界-20261016.md`
- `运行验证-20261015/Liquity收入规模-补偿计价错配与容量证据缺口-20261016.md`
- `运行验证-20261015/Liquity旧部署六月覆盖-原事件空返回与历史正对照-20261016.md`
- `运行验证-20261015/Liquity第三季度任务需求-六地址空返回与路线取舍-20261016.md`
- `运行验证-20261015/Maker启动服务-2026Q3任务池与复制判断-20261016.md`
- `运行验证-20261015/Maker地址整日核账-余额增加与库存变现的区别-20261016.md`
- `运行验证-20261015/Maker拍卖106-公开降价规则与两类真实收入-20261016.md`
- `运行验证-20261015/Maker拍卖套利-真实单笔收支与公开规则边界-20261016.md`
- `运行验证-20261015/Maker近期任务池-四分支与同事件筛查-20261016.md`
- `运行验证-20261015/MegaVault-BTC固定窗口原账核验-20261017.md`
- `运行验证-20261015/MegaVault公开报价与真实账本-首轮核验-20261017.md`
- `运行验证-20261015/MegaVault协议分成与账户增量-原件核验-20261017.md`
- `运行验证-20261015/MegaVault归集事件与转账索引-候选收口-20261017.md`
- `运行验证-20261015/MomentumTransformer-可复制环节与成本缺口-20261017.md`
- `运行验证-20261015/OKX免费历史ETH期权报价-实际原件与质量核验-20261017.md`
- `运行验证-20261015/OKX历史期权-原生合约身份与单位核验-20261017.md`
- `运行验证-20261015/OKX备兑与保证金-5000美元条件及强平边界-20261017.md`
- `运行验证-20261015/OKX线性期权小额成本-公开费率与未确认项-20261017.md`
- `运行验证-20261015/Pendle储备状态估值-成本后负差与复制边界-20261016.md`
- `运行验证-20261015/Pendle到期兑回-真实原账与未确认净收益-20261016.md`
- `运行验证-20261015/Ribbon12轮能否证明持续赚钱-证据判断与下一缺口-20261017.md`
- `运行验证-20261015/Ribbon20ETH原始要求复审-已证明的赚钱事实与独立复刻缺口-20261017.md`
- `运行验证-20261015/Ribbon20ETH正现金来源-权利金费用与份额记账-20261017.md`
- `运行验证-20261015/Ribbon九笔原账汇总-20ETH新本金扣费正现金案例-20261017.md`
- `运行验证-20261015/Ribbon后续12轮真实现金-赔付分支与美元财富缺口-20261017.md`
- `运行验证-20261015/Ribbon固定41名存款者-两笔真实现金差额与成本边界-20261017.md`
- `运行验证-20261015/Ribbon备兑期权-事前规则与首12期原账入口核验-20261017.md`
- `运行验证-20261015/Ribbon实际存款者核账-剩余权益与燃料费上界-20261017.md`
- `运行验证-20261015/Ribbon实际波动率输入-公开可取得性与复制边界-20261017.md`
- `运行验证-20261015/Ribbon异常收费-旧提款准备金与实际费用基数-20261017.md`
- `运行验证-20261015/Ribbon首12期实际交易-权利金费用与可复制性-20261017.md`
- `运行验证-20261015/Ribbon首轮真实交易-权利金抵押返还与费用-20261017.md`
- `运行验证-20261015/Sturdy公开分配算法-历史版本与盈利证据边界-20261017.md`
- `运行验证-20261015/Sturdy最后公开求证-历史回应缺口与候选收口-20261017.md`
- `运行验证-20261015/Sturdy真实分配原账-请求来源与净利边界-20261017.md`
- `运行验证-20261015/Tardis免费历史盘口-访问条件与AI使用许可核验-20261017.md`
- `运行验证-20261015/TradingStrategy事前规则与实盘原件-准入核验-20261017.md`
- `运行验证-20261015/TradingStrategy公开状态归档-身份与完整性核验-20261017.md`
- `运行验证-20261015/TradingStrategy目标原账引用-最终准入判断-20261017.md`
- `运行验证-20261015/UniswapV2公开报价-真实交换需求与盈利缺口-20261016.md`
- `运行验证-20261015/V2两笔固定持仓对照-真实费用与个人复制边界-20261016.md`
- `运行验证-20261015/V2两笔实际持仓份额-从全池费用到个人权重-20261016.md`
- `运行验证-20261015/V2实际收费预算-1379次交换的钱从哪里来-20261016.md`
- `运行验证-20261015/V2小额持仓闭环-两币扣费后净增与复制边界-20261016.md`
- `运行验证-20261015/V2首笔新增流动性原账-代币分配与费用后数量差额-20261016.md`
- `运行验证-20261015/XTX到个人财富目标-赚钱机制与证据收敛判断-20261016.md`
- `运行验证-20261015/XYLD公开原账路线收口-完整持仓不等于完整成交-20261017.md`
- `运行验证-20261015/XYLD真实基金盈利核验-股票增值期权损益与原账缺口-20261017.md`
- `运行验证-20261015/rETH真实闭环-ETH净增与事前策略边界-20261017.md`
- `运行验证-20261015/专用预测模型-免费订单簿数据与验证边界-20261017.md`
- `运行验证-20261015/两笔真实交易资金流-成交收入与利润的区别-20261016.md`
- `运行验证-20261015/个人备兑期权渠道-5000美元规格费用与资格核验-20261017.md`
- `运行验证-20261015/事前规则案例-Carver实盘与费用边界-20261016.md`
- `运行验证-20261015/价格预测模型-公开方法复刻与盈利证据边界-20261017.md`
- `运行验证-20261015/免费链上原账通道-两笔成交与实际Gas核验-20261016.md`
- `运行验证-20261015/公开交易案例-原件与赚钱机制核验-20261015.md`
- `运行验证-20261015/公开借贷收入案例-Aave真实正负原账与复制边界-20261016.md`
- `运行验证-20261015/公开做市为什么还不等于定价优势-20261016.md`
- `运行验证-20261015/公开做市案例-利润口径与事前规则准入-20261017.md`
- `运行验证-20261015/公开套利实账-收入分配和扣费门槛-20261017.md`
- `运行验证-20261015/公开样本外案例-完整账目核验-20261015.md`
- `运行验证-20261015/公开清算补偿案例-LiquityV2完整普通交易与费用-20261016.md`
- `运行验证-20261015/公开程序与运营原账绑定-候选排除与筛选收敛-20261016.md`
- `运行验证-20261015/公开赚钱环节-五类证据与唯一后续核验-20261016.md`
- `运行验证-20261015/公开预测市场成交档案-免费可读但尚不证明净利润-20261016.md`
- `运行验证-20261015/前向公开案例筛选-账户净值与成本核验-20261016.md`
- `运行验证-20261015/可复用案例-ETF留出正收益与证据缺口-20261015.md`
- `运行验证-20261015/固定六笔成交核验-成本已取得与盈利候选降级-20261017.md`
- `运行验证-20261015/固定合并持仓来源-免费原件追溯边界-20261016.md`
- `运行验证-20261015/固定合并持仓追溯-事实链与盈利缺口-20261017.md`
- `运行验证-20261015/固定合并持仓追溯-已找到取得记录但价格费用待核-20261017.md`
- `运行验证-20261015/备兑收益的原始论文核验-风险补偿执行差异与盈利证据边界-20261017.md`
- `运行验证-20261015/官方公开轮子与真实执行器-源码许可和静态参数核验-20261016.md`
- `运行验证-20261015/年度配置对直接持有BTC-最小验证方案-20261017.md`
- `运行验证-20261015/开放许可订单簿数据-CC0候选与真实字段-20261017.md`
- `运行验证-20261015/按风险比例持有-一次历史诊断结果-20261017.md`
- `运行验证-20261015/按风险比例持有-最小验证方案-20261017.md`
- `运行验证-20261015/日频数据准入-CHRIS与CoinMetrics-20261017.md`
- `运行验证-20261015/普通权限清算案例-真实成交与扣费增量核验-20261016.md`
- `运行验证-20261015/比特币公开预测示例-源码与优势证据核验-20261017.md`
- `运行验证-20261015/流动性提供案例-完整撤资原账与收益边界-20261016.md`
- `运行验证-20261015/流动性案例-同钱包11仓位全量核账与复制判断-20261016.md`
- `运行验证-20261015/盈立公开规则短补收口-最小单位末日处理与费用待核-20261017.md`
- `运行验证-20261015/真实套利原账-ProtoRev机制与个人复制边界-20261016.md`
- `运行验证-20261015/真实赚钱案例-Liquity七次尝试与个人复制缺口-20261016.md`
- `运行验证-20261015/研究推进-从预测误差到扣费证据-20261017.md`
- `运行验证-20261015/美股备兑交割与退出-标准单位费用缺口及复制边界-20261017.md`
- `运行验证-20261015/自动做市案例-Uniswap公开规则与真实原账缺口-20261016.md`
- `运行验证-20261015/自动金库决策边界-Sturdy实账与费用份额-20261017.md`
- `运行验证-20261015/订单簿买卖压力-字段含义与预测检验方案-20261017.md`
- `运行验证-20261015/预测市场原账准入-旧子图失效与费用口径-20261016.md`
- `运行验证-20261015/预测市场套利原始核验-4000万美元与实际净利润的区别-20261016.md`
- `运行验证-20261015/预测市场套利复制条件-完整组合可提前合并与现行费用-20261016.md`
- `运行验证-20261015/首笔固定合并交易-回款与盈利边界-20261016.md`
- `运行验证-20261015/首轮真实评估报告-20261015.md`

