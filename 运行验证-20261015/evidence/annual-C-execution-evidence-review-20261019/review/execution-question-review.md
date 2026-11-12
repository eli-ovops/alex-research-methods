# C成功后的最小执行问题：既有证据静态复核

2026-10-19。Owner：`/root/review_reports_annual`。限定读取既有文本、惰性源码、官方抽取及文件可读性；不联网，不打开/哈希395MB行情，不运行来源/金融代码，不重算账户、模型或交易。以下已核事实与推断分别标注，引用路径均相对`运行验证-20261015/evidence/`。

## 1. 来源与Volume：有发布者正面声明，但不能升格为逐条交易所原件

**已核：**保存的Kaggle发布者JSONLD明确写分钟OHLC、Volume in BTC，致谢又区分最初Bitcoincharts与后来Bitstamp API；作者README称其自动取Bitstamp BTC/USD、合并既存数据再上传。固定生成器使用Bitstamp OHLC、step60，但早期审计明确没有绑定它为v755实际生成版本。实际CSV只有Timestamp/Open/High/Low/Close/Volume六列。

**缺证/判断：**可把Volume按“发布者声明BTC”作条件量比，不能将它当可用对侧深度、自己可成交量或已经逐记录核实的Bitstamp原始量。也不能未经版本/历史生成绑定就把整段2012–2026均称Bitstamp直接原件。场所、币对、单位与生成链必须分开核；没有证据说明已发生错列，但惰性生成器按列位置重命名，不能仅凭代码自述消除源映射未知。

**定位：**`Kaggle-BTC-long-history-license-20261017/dataset-JSONLD.passively-extracted.json:5`（本轮直接读保存的发布者声明）；同目录`creator-repository-README.source.txt:4-9`；`Kaggle-BTC-v755-file-semantics-20261017/audit.md:10-22`；`annual-data-provenance-20261018/local-data-coverage.md`§3。

## 2. Timestamp已证Unix秒与UTC网格；开/闭端及首次可用仍是不同缺口

**已核：**早期实际文件前缀与固定生成器均支持Unix秒/UTC；全扫旧回执支持60秒标签网格。保存的Bitstamp官方抽取说明OHLC step秒数、Unix start/end及`exclude_current_candle`参数；该参数用于排除当前未闭柱。早期生成器没有传此参数，其now−10min仅为缓冲。

**缺证/判断：**本轮已读旧原件没有明示v755每条Timestamp究竟是分钟开端还是收端，也未给Close首次发布、接收延迟及历史修订链。`00:12`加两分钟不是已验证的延迟保证；不能用其关闭时间语义问题。最小需要：同一源版本关于柱标签/边界/发布的明确原文或可绑定生成映射；若用盘口还须绑定交易所时钟与采集时钟。当前官方新证据由Root查，本子任务不把旧UNKNOWN升级为当前外部事实。

**定位：**`Kaggle-BTC-v755-file-semantics-20261017/audit.md:10-22`；`annual-data-provenance-20261018/local-data-coverage.md`§1及§4；`Kaggle-BTC-v755-tail-check-20261017/timestamp-primary-search.native.json`中的“OHLC data”段（本轮直接定向读取已存抽取；32,490B，不是全量HTML）。

## 3. 可把最小问题明确到一个封存事件；公开盘口只能核显示报价支持，不能认证真实成交

**已核：**原执行器只以volume>0放行，按历史Close全量调整并计比例费；没有bid/ask、深度、部分成交、排队、冲击或延迟。现有容量报告已把最小缺证写成“指定数量+固定时窗的可执行价量/成交原件+适用全费”。C成功没有补上这些字段。

**最小问题建议（推断，不执行）：**先选一个已有封存的2020 A/C共同首配事件，固定原方向与精确BTC数量q，明确柱可用之后的时点/执行时限、订单类型与成本预算，再问：**同所BTC/USD当时可执行的对侧价格档与数量，是否为该q提供了在该预算内的显示报价支持？** 可直接取已封存25bp首配：2020-01-01 00:10标签、买入`0.5474803783461116 BTC`，原Close代理7158.79 USD；本轮只读C25账首行，不重算。最小公开原件是该时点可信初始L2快照及必要更新/缺口记录、价格和数量单位/双时钟说明，以及当时适用费率。只有BBO不足以支持超过顶档量的q，逐笔成交也不能替代剩余可用深度；静态书可回答显示盘面条件，不自动证明延迟后实成或队列获得率。若要求证明“本人确实成交”，则需订单/成交回执，这是不同层次，当前无账户/下单授权且不必为本轮另索。

**定位：**`annual-execution-cost-capacity-20261018/existing-capacity-evidence.md:7-11,24-40`；同目录`decision-readout.md:9-25`；`annual-fixedmix-C-execution-20261019/root/结论.md`“验收”“结论、限制与收口”；同单元`artifacts/C-fixedmix2020-25bps-ledger.csv:2`（首配精确q）。

## 4. 旧13事件一小时表能回答量比疑问，直接拿来认证C后执行会答偏

**已核：**外部PDF-B第10–12、18页的13事件锚定2014起点旧A：含2014首配、2015/16次日补成交及2017–2025年度事件和末端。刚验收的C问题窗口是2020–2025，相关共同首配和随后五次年度配置及终端；A/C后续目标、数量和账户路径不同。C根结论明确禁止把固定窗口量表当容量认证。

**判断：**若问题仅为“428/198倍是否主要来自单分钟分母过窄”，旧13事件固定一小时表有描述价值。若问题是“C成功后，这一条A相对C的历史差额是否有可执行条件”，旧13事件会混入另一个起点/规模与早年来源覆盖；更换分母也无法提供可执行对侧深度、费率、延迟和成交。即使将表改为A/C相关事件，也只能补流量/价格敏感性，不能改称执行通过；一次单事件盘口核查也不能验证全部六年终值。

**定位：**`外部AI报告复核-20261019/PDF-B-p11.txt:5-29`（工作区根相对路径）；`annual-fixedmix-C-execution-20261019/root/结论.md`比较对象、六年表及末段；`annual-execution-cost-capacity-20261018/existing-capacity-evidence.md:34-40`。

## 5. 部分公开原件已经可读，缺的是目标价量记录，不能把“本轮未读”说成“文件不存在”

**已核现有材料：**

- Kaggle发布者JSONLD（4,396B）、惰性生成器（9,283B）、Bitstamp API既有原生抽取（32,490B）均可读，本轮已读相关段落。约395MB原CSV也实际通过可读性检查；按本轮边界没有打开内容，不把它列缺件。它已有，但仍只有OHLCV。
- Tardis的Bitstamp元数据原件`bitstamp-depth-source-readonly-20261018/bitstamp-exchange-metadata.json`（134,104B）可读；本轮未逐字复读这个JSON，只读其README及`source-metadata-audit.json`。已存抽取将btcusd/BTCUSD spot、L2/quotes/5及25档、2019-03-30起点绑定到来源；它是目录metadata，不是2020目标时点的盘口。此前报告未下载目标行情，不能把“标称覆盖”当实际日文件完整。
- Bitstamp公共`POST /api/v2/order_data/`缺口恢复文档已存且可读，本轮定向读其since_id/until_id描述；既有报告未调用。默认前24小时不是已证最大保留期，也不是多年免费完整档案承诺。Tardis月首免费规则可能覆盖六个元旦，不覆盖12月31终端，不能改终点。

**实际缺证：**上述已读来源目录/回执未提供能绑定这一预定q/时间窗的历史对侧价量记录、可信初始状态与缺口恢复，以及与其对应的全费。这是本轮限定材料的缺口，不宣称整个工作区不存在相关档案。Root可先核官方保留/下载/使用范围；无需重新泛搜平台，也无需先运行一小时表或收益程序。

**定位：**`bitstamp-direct-source-readonly-20261018/existing-direct-source-index.md:7-17,21-28`；同目录`README.md:7-21`；`bitstamp-depth-source-readonly-20261018/README.md:11-25`及`source-metadata-audit.json`；同目录`existing-tardis-scope.md:17-19`。条款及费率均为10月18已有读取，本子任务没有刷新当前外部状态或作新法律判断。

覆盖回执：完整读取本轮五份指定材料；扩读指定引用的v755语义报告、直接来源索引/说明、盘口metadata审计/说明、发布者JSONLD相关完整声明和惰性生成器命中段，并只读已封存C25首配行。仅写本review目录；无临时清理项。实际model/effort保持UNKNOWN，不影响本轮已核静态范围。
