# 2号短周期USDC现金流独立核验

**限定PASS：两笔真实收据的USDC收支和ETH gas可复算，返回历史层已取得成功空末页。** 这是另立成本问题，仍不符合原500–20000USDC/7–180天门槛，不改变原0 eligible。实际UTC及完整输入hash见同名JSON；实际model/effort UNKNOWN，0联网/外来代码/模型/回测/EVM/交易，不改root。

| 项目 | 原账复核 |
|---|---|
| 本人入金 | 2026-08-31 22:57:35UTC，nonce14，Pool顶层**supplyWithPermit(0x02c205f0)**；真实USDC Transfer本人→aToken60750000raw=60.75USDC。不是简单supply调用。 |
| 本人提款 | 2026-09-01 01:07:35UTC，nonce17，withdraw MaxUint；真实USDC Transfer aToken→本人60750796raw=60.750796USDC。 |
| 数量余量 | 7800秒内实际USDC数量正增796raw=**0.000796USDC**，不是提款全额收入。 |
| 入金gas | 243377 × 2048401026 = 498533696504802wei。 |
| 提款gas | 183654 × 2141134359 = 393227889567786wei。 |
| 两笔直接gas合计 | **891761586072588wei = 0.000891761586072588ETH**。此文件先与USDC余量分列。 |

两receipt均status1、本人from/Pool to，hash/blockHash/height及gas与正常交易索引相符；真实底层币Transfer各唯一，并与Supply/Withdraw语义相符。permit Approval在同一存款receipt内，费用已包含，不另造一笔批准gas。

aToken首Mint/Transfer显示60749999raw，较实付少1最小单位。首index1183951228550571059193220496、末index1183966756038341943897004155，按源码floor换算得scaled mint51311235；起始显示60749999，末兑付60750796。成功MaxUint路径burn全部scaled，支持该笔全scaled关闭；未独立读历史存储映射。Burn的balanceIncrease为797raw，**不是现金利息796raw**；少1来自初始取整显示差异，不能另算一份收益或费用。

返回Pool owner topic2/3只见本次Supply/Withdraw及抵押开关；aToken Transfer只见Null→本人mint及本人→Null burn，未观察第三方转入或借款路径。复用old candidate02 pool初页，新Pool topic2末页及本轮其余4个terminal页均status1/OK空。只能确认同一提供商的返回范围，不证明全链或实体外部债务为0。

owner normal共23行，18个本人发起，nonce0–17连续，全部成功；5外来普通交易不是本人的gas。只有nonce14/17直调用该Pool。nonce15的USDC approve授权给router881d…，不是Pool批准；router活动nonce0、16没有与本次Aave本金直接绑定的证据，不能把全钱包费用都扣本存款，也不能据排除就声称资产取得/退出等成本为0。未核这些router的完整经济业务。

外部资金取得、现金退出、融资、税费及运营成本未证。未在此文件直接相减USDC与ETH，也不称真实USD或全钱包亏损；后续固定历史spot的成本标价见另份quote-and-cost-review，仍不是实际结汇。复用价格池身份另在该审阅对照原mint输入/receipt内容。
