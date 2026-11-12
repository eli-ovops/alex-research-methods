# 原账准入终稿审阅

**限定PASS，material_errors=[]。** 仅确认本稿的来源对应、数字、版本及金融口径；不代表任何预测市场盈利案例通过。0新增联网，未执行来源代码、模型、回测、SQL、SDK、EVM或交易。实际model/effort UNKNOWN；规则版本保持PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4。

报告SHA256：`1f303e344b43bcf0c1ea25af853d08f765f28d65222efb8093a092848a18ee90`。审阅UTC及30份实际输入的绝对路径/SHA/bytes保存在同名JSON。

- 版本与事件：市场v1/CTF/domain2、市场v2/PositionManager/domain3、CTF Exchange V2及DataAPI v2区分准确。Goldsky原生正文L182明确2026-04-28后旧公开子图不完整/错误，L208明确推荐流程需要账户及CLI；本稿没有借此声称所有V2账本相同、所有旧数据均失效或全网不可得。
- 费用：新增`list-positions` L623–634确有BUY费用披露及“不从PnL重复扣”的警告；L688–707给出的`percent_realized_pnl`兼容公式不是realized/base，已实现PnL仅称累计字段，未给全费分摊公式。L729–736的inclusive成本关系亦支持稿中区分。没有将merge本金回款、字段名或closed约零残量升级为个人全成本净利。
- 查询范围：`list-trades` L73–78、L221–245支持仅user路径使用start/end；global及condition/event并非相同时间窗口。`wallet-activity` L680–682及新activity参考支持默认排除出入金。稿中分页与取样警告恰当，未把默认PnL降序首行当无偏样本。
- 拒绝原件：Routescan正文为400/`NO_BLOCKCHAINS_FOR_PARAMS`，不是成功空数组；DataAPI、dRPC、PolygonScan保存正文均为拒绝，未得到有效钱包/区块/交易。dRPC确为一次batch的两个只读元数据方法，不是0RPC请求；也不是合约执行。原件及事前范围只支持本环境这些请求失败，稿中未外推全球不可用或从未盈利。
- 数量：逐下载回执核得13请求、8成功文档162664 bytes、4个403（含OpenAPI错误记录但未保存正文）、1个400；12GET/1POST与回执一致。逐实际保存正文hash/bytes核得162857 bytes，正确保留未知未保存部分。9个原生web记录与上下文inventory一致，7query/8open/1click及2不可读作为执行记录计数，不冒独立网络流量。子审阅0新增网络。
- 所有2个本地链接实际存在；正文外链与已存官方来源URL对应，没有新增外链访问。编码错误说明与诊断回执一致，仅被动记录，不能独立证明未保存的环境行为；不影响会计结论。
- 下一数据包方向仍未执行，无新增采集/监控或盈利评分。没有把私人机器人未公开变成认可历史现金的额外门槛，没有改动既有正负结果、Kronos FAILED或财富目标状态。

本轮无需修正文案或追加读取，保持“当前未取得可核实际原账”的限定结论。
