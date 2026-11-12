# gDAI初始实现：构造绑定与钱流静态审阅

限定通过：两份Sourcify原件连起所选proxy及其初始GToken，并提供真实源码机制；没有证明当前实现、2022事前公源码或个人盈利。本轮仅本地读两份JSON，原件完整SHA／字节见同名审阅JSON。

## 初始绑定

- proxy `0xd85E038593d7A098614721EaE955EC2022B9B91B`，Arbitrum42161，部署block49275523；记录creation/runtime均exact_match，verifiedAt2024-08-08T11:46:49Z。
- `creationBytecode.transformationValues.constructorArguments`首个32字节word是初始logic `0x38827724dd5abac83828151a6636f250ede58093`，精确匹配第二原件地址；第二word为proxy admin，不能混作GToken自身manager/admin。只是静态切片读构造参数，不执行ABI／EVM。
- `TransparentUpgradeableProxy.sol` L28–36把_logic和_data传入父构造；`ERC1967Proxy.sol` L14–24设初始实现，并可delegate初始化_data。不是当前storage或升级历史证明。
- 初始logic部署block49275518，creation/runtime均exact_match，verifiedAt2024-08-08T10:35:36Z；编译单元`project:/contracts/v6.3/GToken.sol:GToken`，solc0.8.17。该文件L1有MIT SPDX，只限取得的初始源；2024验证日期不是2022事前公开时间。

下列GToken行号均指第二JSON中`sources["project:/contracts/v6.3/GToken.sol"].content`，从1开始计。

## 钱流与权限

| 函数／定位 | 实际机制及限制 |
|---|---|
| `distributeReward` L721–730 | external且无角色限制，拉取msg.sender的asset，再按供给增加累积奖励、更新份额价并发RewardDistributed。调用者仍需余额／授权和成功执行条件；任何符合条件的人可注资，不能把全部Reward事件自动叫平台交易费。 |
| `sendAssets` L733–759 | L735限定pnlHandler；增加当前PnL并检查偿付和每日上限，更新负债／closed PnL、尝试feed／epoch辅助后将asset转给receiver。是PnL出款，不是普通份额赎回。 |
| `receiveAssets` L761–786 | 同样无角色限制，拉取调用者asset。可能分出depletion金额，以assetsLessDeplete减PnL／负债，再发事件。user只是参数，不证明真实付款人角色。 |
| `updateShareToAssetsPrice` L423–431，辅助L340–342 | private：价格＝1e18＋累积奖励－正的accPnlPerTokenUsed，负值按0处理。使用已采样PnL而非实时accPnlPerToken。 |
| `updateAccPnlPerTokenUsed` L844–882 | 仅openTradesPnlFeed；限制delta、更新并快照PnL、重定价和开启新epoch。send/receive没有直接重定价调用，但其辅助函数可能经feed回调影响状态。 |

## 提现不是随时、无条件提款

请求L587–600要求`nextEpochValuesRequestCount()==0`，仅owner或足额授权方，余额须覆盖待提份额；分配到`currentEpoch + withdrawEpochsTimelock()`。初始锁数组L229为[3,2,1]，选择函数L364–373按超额抵押率和可调门槛、严格`>`比较决定。

maxRedeem L492–502也要求request count为0，只认**当前epoch对应桶**，且不超过`totalSupply()-1`；并非把所有已过期请求自动合并。L531–560先检查上限和正值、扣请求及缩放变量，再继承赎回。第二原件内`ERC4626Upgradeable.sol` L252–272对非owner调用花费allowance、烧owner份额、向receiver实际safeTransfer并发Withdraw；L437–456还限制转走待提份额。

“前两天可提”是介绍文章概述；本源码实际门是feed请求计数，未读feed完整时序，不能用概述代替所有历史／当前窗口。亦未读取实际参数storage。

还缺实际持有人的存入、转移、申请、赎回及全部费用；Reward来源也需交易调用链和asset转账分类。本轮没有新建这些账、算收益或认定完整案例。网络、链调用、编译／源码执行、模型／回测、账户／付款／交易均0；actual model/effort UNKNOWN。完成停止。
