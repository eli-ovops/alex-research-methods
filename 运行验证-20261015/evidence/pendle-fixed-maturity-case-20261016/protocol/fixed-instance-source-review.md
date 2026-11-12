# 固定LOOKS实例源码：静态独立审阅

限定PASS：三份provider source声明及构造参数支持固定到期和机械赎回路径；不升级为独立编译、事前公开时点或盈利通过。0联网/执行，仅本地JSON/ABI/hex/源码静态读取。

## 身份与到期

- PT `0x293811f161fbfea8f417e222b226bb821548ba63`、YT `0xc20dc81e8844f8ff154a67003849cea8e951dedc` 构造SY都为`0x35c16314d6ee4753289e5cc15a5c5e1dd4ead345`，YT构造PT相符。PT反向YT字段经factory-only initialize填，未读初始化原账，反向关系仍UNKNOWN。未独立读market合同，不把元数据关系升级链状态。
- PT/YT immutable expiry同为`1680134400`，即 **2023-03-30T00:00:00+00:00**；MiniHelpers判`expiry<=block.timestamp`。不是私人keeper决定是否到期。
- provider三者Proxy=0，编译器v0.8.17+commit.8df45f5f；PT/SY optimizer90000，YT24500；PT/YT London，SY顶层EVMVersion空且输入未设，不能擅填同London。源码主文件GPL-3.0-or-later；OpenZeppelin导入MIT，factory接口GPLSPDX/MIT正文张力保留，不一概称MIT/全部商业许可已核。

## 真实赎回规则与文档概括差异

YT redeemPY外部无白名单，但需先将PT（到期前还需YT）转入合约；到期前取min两币余额，到期后仅PT余额。burnPT经onlyYT，YT只在到期前burn。返回SY而非直接美元/LOOKS。函数有nonReentrant/updateData，外部SY调用成功等前提不能省略。

**重要更正：此固定实例用户到期后仍按当前index计算SY**：YT行374 `syToUser=assetToSy(indexCurrent,amountPY)`；375—377另以firstPYIndex算总可分配SY，与用户差额计Treasury。并非用户一直直接按firstPYIndex拿SY。firstPYIndex用于快照和YT利息截止。此前source-rule-review按当前文档概括“期后用快照”的文字，仅是文档层，此处按实例实代码收紧。

SYUtils为floor(PY*1e18/index)；当前index=max(SY.exchangeRate,stored)，cache参数构造为true。底层计价汇率持续下降时名义PT不保证足额LOOKS，不计算本例收益。postExpiry首次交互初始化一次（或显式调用），不是到期自动现金到账；期后利息归factory Treasury，不属于PT额外收益。

## LOOKS底层与权限/费用依赖

SY构造LOOKS=`0xf4d2888d29d722226fafa5d9b24f9164c092421e`，staking=`0x3ab16af1315dc6c95f83cbf522fecf98d00fd9ba`，feeSharing=`0xbcd7254a1d759efa08ec7c3291b2e85c5dcc12ce`。getTokensIn/Out与isValid都只准LOOKS，assetInfo也是LOOKS；计价/直接out不是1美元。数值decimals源码读取外部LOOKS，本轮未独核数值。

wrapper无本地等待期：_redeem调用staking.withdraw(shares)，取LOOKS余额实际增加量发receiver。exchangeRate来自staking.totalShares与feeSharing.calculateSharesValueInLOOKS(stakingContract)。**外部两实现未核**，不能断言没有锁/外部fee/管理员/资金可得性问题。SYBase owner可pause/unpause，beforeTokenTransfer的whenNotPaused会阻断burn等，故能阻断赎回；当前owner/paused及历史未核。未知权限状态不是认定实际已暂停。

所读PT->SY->LOOKS路径无显式PT本金费扣项；但不证明外部staking免费。YT利息feeRate从factory动态读，不填历史数值。Gas/买入PTswap/审批/底层退出条件仍需实际原账，当前2026文档费率不能回填2023。

## 后续原账所需事件字段

YT Burn caller/receiver indexed，amountPYToRedeem/amountSyOut data；Mint caller/receiverPT/receiverYT indexed，amountSyToMint/amountPYOut data。SY Redeem caller/receiver/tokenOut indexed，amountSyToRedeem/amountTokenOut data；Deposit同理。ERC20Transfer from/to indexed，value data。完整ABI字段/索引及全部sourceunit SHA/逐行证据见JSON。事件不能代替receipt状态/gas/实际Transfer/第三方资金来源与所有限定费用。

公开机械路径本身无需私人预测/调仓/keeper择时；投资者仍选资产/买价/本金/是否到期持有。不得要求私人动机全公开来否认机械环节，也不得因此宣称历史利润/完整投资政策/未来容量已证。版本首次公开、provider声明相对部署字节码、外部两合约与实际配置仍UNKNOWN。

审阅UTC：2026-10-16T10:02:46.735219+00:00。实际model/effort UNKNOWN，继承未改。

JSON SHA256：`971052a87c91cfc1b158f18a61d8879d07223766f6f9862b4b69da2efaaace82`。
