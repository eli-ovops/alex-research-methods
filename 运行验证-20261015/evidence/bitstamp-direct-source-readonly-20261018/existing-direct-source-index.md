# Bitstamp直接历史来源：旧证据索引

结论：旧资料已保存一个官方“历史公共订单事件缺口恢复”入口，不能只因OHLC可读就认定历史盘口也免费完整；也不能说从未找到官方历史订单方法。本轮仅读4份最相关旧记录，无新增联网或行情核验。

## 最值得复用的直接原文

`evidence/Kaggle-BTC-v755-tail-check-20261017/timestamp-primary-search.native.json`保存Bitstamp官方API文档原生工具抽取。实际读到以下章节，不是只读审阅转引：

| 已存章节／入口 | 已证范围 | 未证范围 |
|---|---|---|
| `https://www.bitstamp.net/api/` 的 **OHLC data**；GET `/api/v2/ohlc/{market_symbol}/` | step秒数、Unix start/end、limit 1–1000及排除当前柱参数 | 这不是历史L2或逐订单档案；这4份记录没有直接Bitstamp OHLC接口成功数据回执，Kaggle文件成功不能替代它。 |
| **Public order event data for gap recovery**；POST `https://www.bitstamp.net/api/v2/order_data/` | 官方描述历史公共订单事件用于缺口恢复；market必填；since_id含起点、until_id不含终点，均为hex MarketEventID；不传since_id默认从until_id前24小时起，不传until_id默认now | 尚未实际调用；最大保留期、最早可达时点、免费权利、认证行为、限额、完整快照与重建能力均未核。默认24小时不能写成最大只留24小时，也不是免费多年档案承诺。 |
| **Commercial Use of Bitstamp's Exchange Data** | 保存正文针对companies商业用途及Data License Agreement，并述及数据商业整合／再分发及派生计算 | 未证明本个人离线活动的具体适用，更未取得明确AI／外部模型服务条款；本索引不作泛化许可判断。 |

同一抽取另有`account_order_data`、`open_orders`、`trade_history`和`user_transactions`等账户相关内容。不能只因标题含“history”就当作公共全市场历史；本轮没有调用任何账户或数据方法。文档示例数值不作为实际行情证据。

该原生文件32,490字节，SHA256 `9eedc0b8563617de0436bcbe05e56f28aab7db72c347628f4badc931c2b8feb2`。它是既有工具抽取，不是完整HTTP HTML或本轮最新全规范。

## 其余旧记录避免重复的部分

- `bitstamp-depth-source-readonly-20261018/README.md`已记录Tardis官方Bitstamp元数据路线，标称BTCUSD盘口历史从2019-03-30开始，含L2、quotes和5/25档。入口为 `https://docs.tardis.dev/historical-data-details/bitstamp` 与 `https://api.tardis.dev/v1/exchanges/bitstamp`。本轮只继承该报告，未重读其底层metadata；它不是Bitstamp直接免费档案，也不覆盖2014–2018。
- 同README记载Bitstamp WebSocket说明页此前返回无正文，单位未确认。本轮4份记录不足以判定具体HTTP状态或是否安全挑战，不能写成确定403、必登录或绕过理由；本轮不重试。
- `Kaggle-BTC-v755-file-semantics-20261017/audit.md`已区分CSV生成器取OHLC与官方时间参数，企业商业数据段具体个人适用仍UNKNOWN。Kaggle版本页的工具读取失败属于另一资源，不移植为Bitstamp拒绝。
- `annual-execution-cost-capacity-20261018/decision-readout.md`已有官方当前及2015／2019手续费入口；费率不能证明历史盘口、成交或容量，无需在本任务重查。

## 收口范围

根可把有限公开核验集中在上述公共订单恢复方法的保留／访问范围，以及是否另有官方可下载历史L2／订单档案，不必再把OHLC、既有Tardis覆盖或手续费当成新发现。这里仍未授权任何行情下载或方法调用。

状态`PASS_LIMITED_EXISTING_DIRECT_SOURCE_INDEX`。精确4份输入路径、字节和当前SHA见同目录JSON。检索仅用于文件名和精确关键词定位，未读raw行情，未声称全库证据不存在；原生抽取可能是分段，不把未显示内容当作字段不存在。实际model/effort UNKNOWN；新增联网、下载、模型、回测、账户、付款、交易均0。完成停止。
