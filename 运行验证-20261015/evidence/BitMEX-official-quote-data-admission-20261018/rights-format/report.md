# BitMEX 官方 quote：许可与格式有限核验

结论：PARTIAL。有官方“向第三方发布去标识市场记录以供监测和研究”的正面依据，可支持将个人内部、非分发研究视为合理的条件研究用途；本轮没有核完适用总条款，不能称无条件数据许可证通过。API 搜索缓存支持 BBO 字段框架，尚不能认证历史归档的实际表头、产品单位或接收时钟。没有读取行情文件、价格行、模型或计算收益。

## 已读原件及层次

- 复用 data/02-native-read.json：官方 [Privacy Notice 2025](https://static.bitmex.com/documents/Bitmex_Privacy_Notice_2025.pdf)，2026-10-18 15:08:46 UTC。原生全文 256 行、8 页；PDF 页4（零基P3）L123–124为第三方监测/研究发布说明；页8 L251载明 April 2025 更新。此文件是发布目的的直接证据，不是完整数据许可合同。本审阅只关注上述定位，未将个人信息处理条款误当市场数据使用授权。
- official-search.native.txt L225–338：官方 [Get Quotes](https://docs.bitmex.com/api-explorer/get-quote) 搜索抽取，工具称约3个月前抓取，非本次实际页面全文。说明为按 symbol 的最佳买卖报价序列；bidPrice/askPrice 为 double，bidSize/askSize 为 int64，symbol 为 instrument，timestamp 为 date-time/Quote time；另有 pool。搜索结果中的自动示例不是行情证据。
- docs-and-terms.native.txt：上述 docs URL 实际 open 重定向到 https://www.bitmex.com/，页面自称 exchange 已结束服务。只证明本次重定向与所见声明，不独立认证关闭事实；也不说明历史档案不存在。原生输出只覆盖首页前部，不能当全文。
- official-search.native.txt L358–378：[production June 2025 Terms](https://static.bitmex.com/documents/Terms_of_Service__June_2025.pdf) 的 Annex D 1–3 搜索抽取。原文涵盖历史数据等 publications，并将其使用纳入总条款/附录；公开无账户访问不等于开放许可。日期来自题名，生效日和当前适用版本 UNKNOWN。另有 testnet March2026 搜索命中，本轮未打开/未将其替代 production 当前合同。
- terms-end-annex.native.txt：同PDF原生元数据声明64页/1956行，但实际取得主要P52–63软件、跟单等附录，不是完整64页条款。该软件的MPL及许可不能转用于历史行情。
- 最后同PDF普通公开GET返回 HTTP403，未保留错误响应体/HTTP头，未形成PDF原件。已查 LOCAL_BLOCKERS，停止该资源且不换身份/渠道补取。

## 字段、时点与经济意义

|问题|本轮支持|仍未知或边界|
|---|---|---|
|内容粒度|官方缓存称 best bid/offer time series|不是完整深度/逐订单事件流，归档是否同API schema未由真实表头认证|
|timestamp|仅有 Quote time/date-time|交易所事件、生成、发布或采集接收的精确定义 UNKNOWN；没有 local_receive/available_at 证据|
|排序/同时间戳|API缓存有 reverse 参数|API查询排序不认证历史CSV物理顺序、同戳先后或完整性|
|bucket时间|另一个 bucketed 端点缓存明确为期末/写盘标签|不得套给非bucketed quote 或历史归档 timestamp|
|价格和size|字段名/类型是报价价格和报价数量|具体计价币、合约乘数、币数/张数、缩放、最小单位及历史变更 UNKNOWN；int64不等于BTC币量|
|产品|symbol 表示 instrument，缓存也提及季度/永续查询|本轮未取得具体XBTUSD或现货产品规格，不能将全球daily quote对象当BTC现货或把inverse/perpetual现金式直接搬入spot协议|

没有接收钟不自动禁止条件研究：在明确采用“交易所报价时点代理可用时点”等可检验假设且不宣称实时可交易的情况下，仍有有限研究价值。但当前仅 Quote time 的字面定义不足以把该假设升级为已核事实；即时可用、真实延迟和NTP精度均 UNKNOWN，不以精确NTP证明作为所有研究的前提。

## 用途边界

官方研究发布说明提供的是正面用途依据，而不是“公开即任意使用”。Annex D 搜索抽取说明总条款仍需适用。本轮没有核完数据知识产权、复制/再分发、商业使用、自动抓取、ML/内部分析、外部AI服务上传或未来交易相关条款；这些不得写作“无此限制”，也不能反向断言“明确禁止”。无需凭空增加专门ML许可或作者回复作为个人条件研究的自动前提。

当前有限判断：个人本地内部研究有合理官方目的依据；完整合同兼容性尚未通过，不认证外部AI上传、原始数据分发或商业交易权。用户所在地只作公开数据研究范围记录，不涉及开户或实盘资格。本轮没有引入新的运行方案。

## 预算、停止与最小缺口

共5次公开读取：1搜索、2次独立URL open（同批）、1 PDF定位open、1普通PDF GET403。没有请求API行情端点、日期目录、gzCSV或市场payload。所存原生抽取共约86KiB，HTTP403正文未读取；原生工具不提供原始wire bytes，不能冒称PDF原字节已取或完整SHA。所有本地原件指纹见 report.json，actual assistant model/route UNKNOWN。

最小剩余原件：取得适用于 public.bitmex.com 历史数据的当前 production 总条款及 Annex D 全文（明确可读官方版本/现存可靠原件即可），核其数据使用边界。格式准入仍需官方归档schema/具体symbol历史产品规格；本轮无行情下载授权，未为补字段读取CSV。403资源本轮不重试；预算到限已停止。
