# Bunni V2触发与外部执行：冻结源码独立审阅

**限定PASS。** root八项事实与停止决定未发现实质错误；只是静态规则/权限层通过，不是部署、安全或盈利通过。固定commit 2b303b8c1b9f8afbb169d62ba52da93d6d2171fe。6个冻结文件及commit网页逐项hash/bytes与7份200回执吻合；输入、源URL/读取UTC及本次实际UTC见同名JSON。实际model/effort UNKNOWN，0新增联网；不执行源码、模型、回测、EVM、安装或交易，不读PoC/gist/收益榜，不改root。

| 事项 | 独立支持及限度 |
|---|---|
| 触发 | BunniHookLogic.beforeSwap L546–579：rebalanceThreshold非0，且shouldSurge或此前非零deadline严格过期时尝试；surge清除旧订单状态。不是每个swap必调仓，更不是无交易时自动发单。 |
| 订单生成 | RebalanceLogic L34–57、121–169：按idle balance、liquidity及LDF密度比较；TWAP推导数量并应用配置滑点。条件不足可直接返回；不证明任何特定部署配置或成交。 |
| 外部fill | RebalanceLogic L213–233：订单带zone/expiry、记录hash后etchOrder。BunniHook L567–588验FloodPlain来者及预期hash；公开建单与回调不是已经成交、无外部依赖或必然可获利。Flood/solver完整实现与实单未核。 |
| 权限 | BunniZone L35–59：白名单或当前topBid.manager可获准，owner能改白名单。这只是所读zone；实际pool/时点是否使用该zone、个人是否获准UNKNOWN，不推出个人不可能参与或私有定价。 |
| 费用角色 | HookLogic L348–500和Hook L525–559：amAMM manager费、hook费、curator费有分支及分账；无amAMM时部分交换费留LP资产中，amAMM分支给manager累计相应费。不能把粗略总fee都归LP，更不是个人净利；未审全租金分配或真实到账。 |
| 提现/owner | Hook L378–420、504–506：owner可换zone、按约束设hookFeeModifier、手动解锁。canWithdraw实际为block.timestamp > deadline **或** override；到期或手动解锁均可true，不能按注释说永远锁。是否还有其他暂停/部署限制未核。 |
| 许可 | 根MIT及四个已读Solidity MIT相符；需保留版权/许可。README另明示部分文件AGPL-3.0，未推广为所有依赖MIT或安全认证。 |
| 研究决定 | 固定README明示相关问题未修及不要原样生产使用；支持停止本候选生产复制/盈利追逐，保留架构研究反例。不是宣称所有后继版本、自动LP或其他协议均不可行。 |

commit网页作者与提交元数据均2025-10-22T17:42:59-07，晚于官方事故报告；只说明此冻结ref元数据，不独立证明完整策略首次公开或当时实际部署。没有借此回填事故前版本。

本轮没有取具体部署状态、订单、持仓、成交、收益及费用历史；这些继续UNKNOWN。也不因未知而断言私人主观择时、永远不修或个人不可复制。源码自动触发比纯外部keeper示例更具体，但不能越过本仓明确未修风险警告。
