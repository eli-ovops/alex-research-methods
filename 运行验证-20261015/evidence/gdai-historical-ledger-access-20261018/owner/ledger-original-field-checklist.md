# gDAI完整存赎周期：原件字段清单

已备好字段清单，未选钱包、未取日志、未建账或计算收益。仅依据上一阶段两份独立Sourcify原件内的初始GToken及proxy源码／ABI；它们不代表当前实现。绝对路径、字节和SHA256及完整事件ABI见JSON。

## 每条事件先保留共同定位

chainId、emitter地址、blockNumber/hash、transactionHash/index、logIndex、原始topics/data、removed或规范链状态，以及另从块／详情取得的timestamp。按block→tx index→log index排序，不只按日期或txhash；保留查询范围、分页和provider限制。

| 事件 | ABI字段（i＝indexed） | 需联核及误计边界 |
|---|---|---|
| Deposit | sender i、owner i、assets、shares | 同笔asset转入proxy、proxy份额mint；sender不必是owner。事件及Transfer只计一份投入。 |
| Withdraw | sender i、receiver i、owner i、assets、shares | 同笔份额burn及asset转至receiver；caller／owner／receiver不可混。要有成功receipt，不能仅凭事件名推本人到账。 |
| Transfer | from i、to i、value | proxy发出表示份额；asset合约发出才是资产。零地址区分mint/burn；普通份额转移不等于按报价实际卖出或DAI赎回。 |
| WithdrawRequested／Canceled | sender i、owner i、shares、currEpoch、unlockEpoch i | 请求／取消本身没有资产到账；按owner与epoch跟踪，不重复计本金。 |
| RewardDistributed | sender i、assets | distributeReward无角色限制；联同asset实转及调用来源才能归交易费，公众注资不能自动认平台费用。 |
| AssetsSent | sender i、receiver i、assets | pnlHandler限制的PnL出款，不是普通存款者Withdraw。须联实际asset转出及版本身份。 |
| AssetsReceived | sender i、user i、assets、assetsLessDeplete | 拉取caller资产；user为传入标签，净会计数assetsLessDeplete不是第二次转账，也不能只凭标签叫交易者损失。 |
| Upgraded | implementation i | 由选定proxy发出，新实现按时序生效；不是收益／资金事件。初始构造绑定不能替代后续升级史。 |

GToken定位：WithdrawRequested／Canceled L587–612；奖励L721–730；AssetsSent L733–759；AssetsReceived L761–786；份额转移限制L437–456。ERC4626Upgradeable `_deposit` L230–250、`_withdraw` L252–272提供实际拉入／转出与mint/burn。proxy原件ERC1967Upgrade L31、L53–65定义／发出Upgraded。

锁仓路径若落入固定样本，还须保留DepositLocked／Unlocked的depositId、owner/receiver及结构体shares、assetsDeposited、assetsDiscount、atTimestamp、lockDuration；跟踪NFT／锁定权利转移。其释放不是资产赎回，钱包份额0不能单独证明完整退出。epoch和份额价事件只解释权利／价格状态，不新增现金收入。

## 费用、状态和权利另有原件

交易详情须有from/to/input/value及币种；receipt须有status、gasUsed、实际gas价／链特定费字段、完整logs及真实付款人。Arbitrum L1相关费用按来源定义核，不默认额外全加或省略，不把provider总费与分项重扣；缺项UNKNOWN。失败调用可能无保留event，若声称相关尝试全费须覆盖固定范围内成功／失败根交易，不要求无关全钱包终身账。

各金额保留原整数、emitter和已绑定token decimals；份额与资产即使都18位也不能混。DAI原量不是独立美元到账证明，native gas不按虚构汇率换算。期末分别列钱包份额、待提请求、锁仓／NFT权利；有残余或转出对价未知就报告有限现金段及未知权益，不擅自按0算完整利润。

未来最小原件包是固定非盈利筛选的持有人／期间、完整相关proxy/share/asset日志与升级版本、成功失败receipt及费用、实际期初资金来源和期末权利。这只是准备清单，不自动授权取数或核账。

状态`READY_FIELD_CHECKLIST_ONLY_NO_HOLDER_SELECTED_OR_LEDGER_BUILT`。实际model/effort UNKNOWN；新网络、链／ABI／EVM调用、源码执行、账户选择、收益计算、模型、回测、付款和交易均0。完成停止。
