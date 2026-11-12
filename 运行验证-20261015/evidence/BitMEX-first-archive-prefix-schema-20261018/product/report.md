# XBTUSD：历史产品身份与单位边界

结论：官方搜索缓存支持预固定候选 XBTUSD 为逆向永续合约，不能把它直接当 BTC 现货。其经济乘数为每张 1 USD，报价币 USD，保证金及损益币 XBT。但实际有限前缀未见 XBTUSD，候选尚未与已取得记录绑定；本轮亦未取得 2024-01-01 当日固定版本的完整规格或历史 quote size 定义。结果为 PARTIAL，不是 BTC 数据准入通过。

## 原件与定位

1. 01-official-search.native.txt：2026-10-18 15:22:42–15:22:49 UTC 官方域精准搜索 `site:bitmex.com XBTUSD inverse perpetual contract specification 2024 USD contract bitcoin settlement`。这是搜索抽取/缓存，不是本次官方站点原始HTTP字节。
2. [Perpetual Contracts Guide](https://www.bitmex.com/app/perpetualContractsGuide)：缓存称约一月前抓取、无固定修订。上述原件L27列 XBTUSD / Inverse Perpetual / 1 USD，L61–68列 USD 报价、XBT 保证金及损益；L80解释固定美元面值、以反向币值表示。列出的2016上市日是当前缓存的历史自述，不是2024原版快照。实际 open 在15:22:58–15:23:03 UTC转认证域，工具报告500/non-retryable，未访问账户或继续认证。02-03-product-opens.native-redacted.txt保留错误和host/path，认证URL query未保存。
3. [2024 Tick Size 公告](https://www.bitmex.com/blog/site-announcement/now-live-changes-to-minimum-price-increments-for-xbtusd-and-ethusd)：缓存L126–133载明30 July 2024，并称XBTUSD是perpetual swap、USD tick于2024-07-31变动。这是2024产品名称/计价的旁证，同时说明不能把后来的价格网格倒推至1月。实际同批open报告404，不以缓存冒充当前正文，也不以404推断产品从未存在。
4. [Dust on Crust](https://www.bitmex.com/blog/dust-on-crust)：缓存L145–152称XBTUSD inverse perpetual、1美元面值、以Bitcoin支付；发布日期工具仅给相对3.6年前，不据此填写精确2023日期。实际15:23:09–15:23:12 UTC open报告404，见04-historical-blog-open.native.txt。

搜索也返回其他产品和testnet文章，本轮未继续打开或以它们认证2024合约。已查询LOCAL_BLOCKERS；4/4公开读用完，没有重试404/认证入口、已知quote文档重定向路径或此前403的ToS。

## 可用判断与不能跨越的边界

|项|证据支持的限定判断|2024归档仍待核|
|---|---|---|
|产品身份|官方缓存将XBTUSD列为inverse perpetual；2024公告缓存独立称其perpetual|无2024-01-01完整固定spec；不能认证期间所有规则未变|
|报价|USD为quote currency；报价约定为每Bitcoin的美元价格|历史CSV数值缩放/小数编码未由本Owner读取或认证|
|经济乘数|每张合约固定1USD面值|这不是已读取API instrument原始整数multiplier字段，也不是BTC币量|
|size|官方指南以contracts计持仓，支持合约张数语境|未取得archive字段规范证明bidSize/askSize确以张记录、非lot数/缩放量；不得直接当BTC数量或假定最小交易单位=1张|
|结算/损益|缓存支持Bitcoin/XBT支付及XBT margin/P&L语境|永续无通常到期日；不将其误写为某日现货交割，实际2024账务精度/规则未核|
|timestamp|本轮未取得额外定义|上轮Quote time字面不足以认证交易所事件赋时、接收时钟或即时可得；不复开该已封存研究|

因此不能把现货的本金、库存和现金买卖公式原样用于该候选；本轮只识别产品差异，没有推导或运行衍生品收益、资金费或交易模型。官方当前/缓存说明和2024公告旁证可以缩小产品误认风险，不能替代实际历史合同及档案字段规范。

## 实际档案绑定

执行Owner报告：1000条完整记录仅见100BONKUSDT，exact XBTUSD 与 XBT_USDT count 均为0。这只说明已检查前缀未见，不能推断全日/归档没有BTC产品。具体回执身份见report.json。本Owner只读取非价格的identifier摘要，不读取gzip、CSV行或quote值。

因此上述XBTUSD规格审阅保持候选层，不套用于100BONKUSDT，不新增该产品研究，不扩大前缀寻找BTC。六字段表头相同不证明不同symbol具有相同经济单位。

## 最小剩余证据与停止

最小剩余原件为覆盖2024-01-01的官方XBTUSD规格版本及archive quote size字段定义；无需新模型或运行提案。本轮0市场payload读取、0金融计算、0代码执行、0账户/交易；实际assistant model/route UNKNOWN。原件、scope与最终报告的SHA256及读取时刻见report.json。
