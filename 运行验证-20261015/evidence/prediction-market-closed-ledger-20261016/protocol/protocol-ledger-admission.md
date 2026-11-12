# 官方账本入口与费用口径审阅

结论：**PASS，仅通过文档规则与会计边界审阅；尚不是某个历史案例净利润通过。** 本轮0新增网络读取，仅被动阅读四份官方Markdown及下载回执。四份原件的实际SHA256/bytes均与回执相符（合计71,080 bytes）；绝对路径、原URL、读取UTC和指纹保存在同名JSON。文档发布日期及首次公开时间均UNKNOWN；实际model/effort均UNKNOWN。沿用PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4。未执行任何源代码、SDK、SQL、EVM、模型、回测或交易。

## 版本必须先于解码

| 市场版本 | 余额账本与ID | Exchange域 | 本次官方文档地址 |
|---|---|---|---|
| Gamma `version="v1"` | CTF，`tokenId` | `"2"` | Conditional Tokens `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` |
| Gamma `version="v2"` | PositionManager，`positionId`；签名订单字段仍叫`tokenId` | `"3"` | PositionManager `0x006F54F7f9A22e0000CC2AB60031000000ae9fEF` |

原文位置：`onchain-position-data.original.md` L9–17、L75–84、L221–230；`contracts.original.md` L9–18、L28–38。**CTF Exchange V2仓库名称不等于市场已使用PositionManager的V2。** 同形订单、字段存在或同一交易出现CTF腿都不足以选择版本。

当前地址表不是旧交易时点的部署/升级快照。`contracts` L42–53表明pUSD/账户钱包支持两套系统且存在CTF抵押物adapter，不足以把每笔历史兑回直接叫USDC或美元现金。L134–137说明迁移须先登记；`onchain-position-data` L268–288的`MigrationConditionRegistered`、`PositionMigrated`、`MigrationResolved`、`LegacyCollateralSettled`用于新旧ID和资产桥接，不自动产生新利润。`blockchain-data` L15–17明确第三方schema可能落后升级。

## 事件与不重复记账

- CTF与PositionManager余额都以实际部署账本发出的`TransferSingle`/`TransferBatch`为标准；zero→holder为铸造，holder→zero为销毁，非零地址间为转移。`ApprovalForAll`是授权，不是收入。原文分别为`onchain-position-data` L43–57、L175–189。
- CTF合并事件名为`PositionsMerge`，兑回为`PayoutRedemption`；V2为`PositionsMerged`/`HorizontalMerge`及`PositionRedeemed`等，模块不同还可能有组合操作。生命周期、Router和AutoRedeemer事件是归因上下文，不能再重复增加相同的ERC1155余额或兑回金额。原文L59–73、L194–219、L86–102、L232–266。
- 两类Exchange均列`OrderFilled`、`OrdersMatched`、`FeeCharged`，但这四份叙述文档没有完整事件ABI、indexed字段、topic或收费字段单位，不能仅凭事件名称完成原始日志解码。必须保留地址/版本；`FeeCharged`与已扣费的实际Transfer不是可机械相加的两次费用（L75–84、L221–230）。
- **一次merge抵押物到账是含回收本金的毛现金流，不是该金额全部为利润。** 应将实际ERC20抵押物流与ERC1155头寸变化分别记账，使用同一笔生命周期事件关联它们；买入/初始库存成本、兑回本金及重复事件只算一次。迁移的新铸造亦不能当外部免费收入。

## 钱包PnL字段不能冒充完整实付净账

`wallet-activity.original.md` L41–53明确：

| 字段 | 可由本次原文确认的含义 |
|---|---|
| `entryCostUsdc` | fee-exclusive入场成本基础 |
| `entryFeesUsdc` | 已归属BUY费用的披露项；不能从上述基础再减去该费用以构造inclusive成本 |
| `totalCostUsdc` | 恒等于`entryCostUsdc + entryFeesUsdc` |
| `unrealizedPnl` | `currentValue - entryCostUsdc` |
| `totalPnl` | `realizedPnl + unrealizedPnl` |
| `realizedPnl` | 已实现表现字段；这四页**未给完整费用/成本分摊公式** |

因此不能把exclusive与inclusive字段同时当独立成本扣两次；实际净转账已包含的收费亦不可再扣一次。也不能反向假定`realizedPnl`已覆盖所有BUY/SELL/合并/兑回费用、gas、失败费、内部付款、返佣和外来持仓成本。其完整定义在本轮仍UNKNOWN。字段示例和文字交替使用USD/USDC标签，不是已证明美元结汇。

L102、L206、L265说明首次取得可来自buy、split、mint、migration或incoming transfer，不能把它一律当现金买入时间。L340–344的closed是`currentSize`约零残量，不是精确链上余额零证明；默认按已实现PnL排序，L507–513再次确认默认降序，取“前十”若不显式改变选择规则会变成收益排序样本。L1071–1096为累计PnL序列，不可逐点相加或以null填零。

活动API示例有`transaction_hash`（L698）但不保证原始收据或完整费用。**L680–682：默认排除deposit/withdrawal，即使type请求也如此，须显式`exclude_deposits_withdrawals=false`。** 分页需跟随cursor并保留过滤/排序参数（L267–268、L328–330、L709–714）；有hash、有closed行或所谓full history均不是独立无漏证明。

## 可以支持及尚不能支持

现有材料足以选择账本/版本、建立去重规则并识别API费用口径缺口。后续固定样本若取得限定账期的初始持仓或明确取得来源、全部相关现金和头寸流、末端余额、实际交易费用及观察到的失败/内部费用，即可研究该**限定历史现金结果**；不要求公开完整私人bot或全实体多年账才承认事实。

本轮尚未读取实际样本，不能声称已闭合盈亏、无失败费、V2覆盖全部旧记录、完整数据再分发许可或未来可复制盈利。缺失项不填零，单API的成功分页只支持该来源的返回范围。上述为会改变金额和归属的必要核账边界，不额外加入未来OOS/零风险门槛。
