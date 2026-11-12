# run06固定范围经济证据审查

**结论：即使14日完整结束，采集器最强也只能支持“指定范围的数据/时序覆盖、按冻结规则形成的episode与日簇、事后完成交易原件，以及奖励减假设gas的乐观情景”。个人实际获奖、捕获率和全成本净利仍不能由它通过。** 原方案已明确这些边界，无须修改基准、收益定义或正在运行的观察。

| 项目 | 源码实际处理及精确位置 | 未覆盖/不能推出 |
|---|---|---|
| 候选奖励 | `readonly_collector.py:61–76`：full-SP等条件后按固定项＋有上限抵押补偿计算`minimum_reward_wei` | 协议状态下的情景补偿，不是实际Transfer或个人收入 |
| 假设执行支出 | 同L71–76：只有方法审查accepted且USD anchor存在才给fee资格；冻结gas/tip，按B的basefee构造最高费率/支出帽并减去；标`scenario_only_not_actual_fee_or_fill` | 不是已发送费率、实际gas或成交；不能替代完整经济成本 |
| 情景选择/累计 | `readonly_core.py:495–519`按episode首次参与、每日一次、冻结排序选择；collector L548–554固定anchor后累计`minimum_reward_minus_ceiling` | 不累计他人成功为我方胜利；情景未自动扣劳动/基础设施 |
| 已完成事件 | collector `completed_event_audit` L215–233按Liquidation日志取唯一tx及receipt，核hash/block/status，保存完整对象和完成块本机接收UTC；明确posthoc/not-signal | 只覆盖这些成功事件关联交易，不覆盖没有事件的失败尝试。**未解出奖励Transfer收款者，未验证其与tx.from相同，也未构造实体归属账** |
| 实际网络费 | 完整receipt若含gasUsed/effectiveGasPrice，可留作后审原件；上述函数没有做两者乘积 | 没有把该乘积称全成本，也没有自动扣成功/失败费用；不能从成功receipt推整段尝试账 |
| 顶层/内部/额外支付 | 原transaction对象可保留供应商返回的value/input/from/to；该函数不单列核value，不请求内部ETH流或分解奖励拆包/转付 | builder/fee-recipient、relay、融资及链下支付未采或未归类，不能假设必有，也不能填0；tx.to不是奖励最终收款者证明 |
| 一次性/持续成本 | `execution-owner/operating-costs.json`：setup/maintenance hours和infra实际值均null、entries为空，资本成本UNKNOWN；collector L562明确等待实际劳动/设施账和独审 | 没有自动经营成本账。时薪20美元是假设；CPU/AI等待不是用户实际工时，历史研究沉没成本也不重扣 |
| 时间/结果边界 | core L316、362–373保存RPC起止UTC/monotonic；L457–469记录应用层通知到达；collector L88、137记录snapshot开始/形成、B/hash及模拟oracle标志；L231保存完成块接收UTC | 不是NIC/供应商时间，不证明入块竞争可赢。模拟新增关停不是B已发生值；L562不自动宣布A通过 |

**唯一具体后续核对点：**若以后解释`completed_event_audit`中的实际收入，须先对其既存receipt机械核WETH奖励`token/from/to/raw`，与tx.sender/调用目标分列；当前留存并未完成此角色归属。它不阻碍按原A采集，也不要求私人H、钱包全史或新增交易；只是防止把“某合约收到奖励＋另一地址付gas”误称同一个人的净入账。其他费用缺口原方案L47–62、85–101已充分说明，不新增门槛；乐观情景仍暂将失败/竞争支出归零，且并非严格收益上界。必要实际固定成本未补齐时，原A经济门仍不可判定，不能用累计字段直接过门。

实读仅指定函数/相关片段、成本JSON及方案相关段；未读活归档、未触进程、未import/执行项目代码，0新网络/RPC/模型/回测/交易。输入SHA256：collector `4dd5774bf4d5fea066bb55714907615c208009065582db70e80f824f843a6e74`；core `a2f7d56b1f90c2ee535679d3d48c461a30f2ec2e92001227887312c5b3508436`；costs `c00f16e531c14103e1f615ba68569fa15179c67e89ce94375b16699de6f25d57`；方案 `2300f2a3c4c761061c61224a374be6bfde1bdac544d0cf17085288d5e5f4f9d8`。actual model/effort UNKNOWN。
