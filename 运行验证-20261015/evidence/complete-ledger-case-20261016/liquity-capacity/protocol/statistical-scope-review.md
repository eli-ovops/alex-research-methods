# DefiLlama Liquity V2费用归属：固定适配器静态核验

结论：网站Gas Compensation旨在统计清算者的**毛补偿**，不是净利润；但本次固定源码把固定WETH补偿误归到BOLD币种，故不能直接采用其美元值作为本例完整报酬的全市场规模或可靠上界。总Fees、Revenue或SupplySideRevenue也都不能替代清算者毛收入。没有运行适配器、请求RPC或独立复算网站聚合结果。

固定DefiLlama/dimension-adapters当前HEAD：`b803360579fdea8be3ae7771ee02599f1481607c`，GitHub返回提交者日期2026-10-15T20:20:11Z。本地记录2026-10-16（UTC详见receipt）。实际model/effort UNKNOWN，继承不覆盖；PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4。5次公开GET已用完，另1次代码搜索；其中错误目录路径404，随后仅用公开tree定位正确文件，无绕过限制。未读凭证、env/config，gh认证静默检查；未执行下载代码、模型、回测、EVM/RPC、策略或交易。

## 实际调用和覆盖

- [协议入口fees/liquity-v2.ts](https://github.com/DefiLlama/dimension-adapters/blob/b803360579fdea8be3ae7771ee02599f1481607c/fees/liquity-v2.ts)并非直接调用`liquityV2Exports`，而是调用同文件helper的`getLiquityV2LogAdapter`并汇总两部署结果；本地保存为`index.ts`。初次代码搜索只命中helper，不足以定位该入口，已由固定tree确认。
- Ethereum，适配器开始日2025-01-24；每次包含旧registry`0xd99dE73b95236F69A559117ECD6F519Af780F3f7`。当查询起始时间≥1747526400（2025-05-18T00:00:00Z）再包含`0xf949982b91c8c61e952b3ba942cbbfaef5386684`（入口16—25、34—35行）。这些是适配器取数起始/分支条件，不冒充部署或首次公开时间。它同时覆盖两轮部署，不是仅已核2026目标分支。
- [helpers/liquity.ts](https://github.com/DefiLlama/dimension-adapters/blob/b803360579fdea8be3ae7771ee02599f1481607c/helpers/liquity.ts)31—43行从registry的`totalCollaterals/getTroveManager`动态枚举各TM，再取activePool、collToken、stabilityPool和interestRouter；后者必要时从addressesRegistry读取。没有固定TM/分支地址数组。本次不执行查询，实际枚举返回值、分支数、历史区块读取口径及完整覆盖UNKNOWN；不能声称已独立核到所有市场。

## 钱归谁

| 源码项目 | 收入归属及入账 | 与清算者的关系 |
|---|---|---|
| Borrow Interest | helper45—54行汇总发往稳定池/interestRouter的稳定币铸造流；全部入dailyFees，75%入dailySupplySideRevenue，25%入dailyRevenue（入口8—9行） | 稳定池存款者利息及协议流动性激励，不是清算者报酬。比例为适配器配置，未独立读链确认各时期真实分配。 |
| Redemption Fees | TM的RedemptionFeePaidToTrove事件，抵押币金额入dailyFees和dailySupplySideRevenue | 留给借款仓位的赎回补偿，不是清算执行者收入。 |
| Gas Compensation | Liquidation的第3/4个金额入dailyFees及dailySupplySideRevenue；不入dailyRevenue | 定义上对应清算者毛补偿；无失败交易gas、成功gas、RPC/运营成本扣除，也无个人分配。两个总计是同一流的分类，不能加总为双份收入。 |
| SP liquidation gains | V2 helper没有把_collSentToSP与_debtOffsetBySP做损益相减入账 | 没有计入V2的Gas Compensation，也不能把SP抵押物到账当清算者报酬。helper后半段V1另有ETHGainWithdrawn的抵押收益减稳定币损失、仅正值入Liquidation Profit；不能搬到V2。默认V2方法说明的liquidation profit字样不替代实际实现。 |

## 完整事件与关键币种错配

helper64行事件ABI（10个非indexed uint256）：

```solidity
event Liquidation(uint256 _debtOffsetBySP, uint256 _debtRedistributed, uint256 _boldGasCompensation, uint256 _collGasCompensation, uint256 _collSentToSP, uint256 _collRedistributed, uint256 _collSurplus, uint256 _L_ETH, uint256 _L_boldDebt, uint256 _price)
```

57—60行另读`event RedemptionFeePaidToTrove(uint256 indexed _troveId, uint256 _ETHFee)`。上述Liquidation签名与已存verified标准JSON内`src/Interfaces/ITroveEvents.sol`一致；协议接口本身也遗留`_boldGasCompensation`字段名。因此**不是事件签名或解码不兼容**，问题是金额实际支付币种与适配器记账币种不同。

复用已核官方审计版`abe7cbfbd465fba3812282c51773455766a70e96`、与目标已验证源码逐字节相同的TroveManager/Constants：

- TM461—475行emit第三实参`totals.ETHGasCompensation`、第四实参`totals.collGasCompensation`，随后付款给msg.sender。
- TM524行每个被清算仓位累加固定ETH_GAS_COMPENSATION，Constants13行=0.0375 ether；TM537—545行固定部分从gasPool以**WETH**转清算者，可变部分由activePool以该分支collToken支付。可变金额按collSPPortion/200并受2个抵押币单位上限约束，不能一概写0.5%全部仓位抵押物。
- DefiLlama helper81—84行将第四字段按collateralToken入账，却把第三字段按stableCoin（默认从registry的boldToken读取）入账。它没有为固定WETH部分单独选择WETH资产。
- 对已核一笔实际0.0475 WETH毛到账，协议两部分为固定0.0375 WETH与可变0.01 WETH。该代码表达的记账将是0.0375 BOLD加0.01 WETH，而非0.0475 WETH；不能认为美元汇总已覆盖两部分真实经济价值。这是静态对齐，不宣称本轮运行得到上述网站输出，也不外推旧部署/所有fork都完全相同。

## 美元化、规模与未核项

V2路径只向`createBalances()`交付代币原始数量和分类，没有使用事件`_price`给补偿定价。USD估值发生于下游框架；本预算内未读取Balances类型/实现、价格来源、取价时点、缺价处理、回填/缓存/重跑逻辑及网站当前构建版本，均为UNKNOWN。V1局部`getUSDValue`不能证明V2网站的具体取价口径。

分层判断：

1. **可核定义**：Gas Compensation的目标类别确为清算者毛报酬，两类事件金额都被纳入；SP所得、借款利息和赎回费应另列。
2. **不能直接采用当前美元总量**：固定WETH被归BOLD，当前代码与网站实际部署/历史计算对应亦未核。它既不能视作完整毛收入，也不能保证是上界（漏计/错价方向与覆盖都未闭合）。
3. **理论毛收入规模边界**：若按正确币种、明确区间、实际registry/TM完整事件清单与独立价格口径重核，补偿总和可以界定该范围所有清算者可分得的历史毛报酬池；它不是额外资金、个人可获收入或净利润，不证明未来机会规模。本轮没有完成这项聚合核验。
4. **总Fees最多是宽泛类别包，不可作利润上界背书**：有其他受益者、币种问题和覆盖未知；不把所有协议Fees或SP收益划给执行者，也不将网站数字与已核单笔净增混算。

本次不推断复制成本或未来盈利。若要改变结论，最小新增原件是：固定适配器相应币种纠正/网站实际构建版本说明，并给出目标区间按正确资产的完整清算事件及下游估值规则；无需索取全运营者跨账户或私人bot才承认已有历史限定账期结果。
