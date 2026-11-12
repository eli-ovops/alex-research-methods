# 奖励caller逻辑补证：交易平仓费用分配

新证据支持明确的“平仓费用→vault奖励”源码路径，仍不证明窗口933条奖励全部已逐笔归因。旧proxy源审原样保留。本补证只用剩余1次Sourcify GET，未触已停的RPC或Arbiscan。

## 实现身份及时间

实际观察地址`0xae31db60aa9a82502d5d63dab3e4cd5f8bd06121`的Sourcify既有记录HTTP200、88,955字节，SHA256 `9d9e03718d6c7ab71e7d270a6f8602549cd5cfe441c1e1dadb9e4c926449ed5c`，creation/runtime均exact_match。编译单元`project:/contracts/v6.3/GNSTradingCallbacksV6_3.sol:GNSTradingCallbacksV6_3`，solc0.8.17；部署block49275550，早于根UI所见caller proxy部署49275558及已核奖励最早block49860685。

GET时间2026-10-18T09:17:32.952920Z—09:17:35.541539Z。完整URI、原件及回执见JSON。verifiedAt2024-08-08T10:38:19Z不等于事前源码公开。取得源L1为MIT，仅限该文件／相关许可范围。

根从独立Blockscout UI看到creator tx `0x0c45dda801a83896aa524ce34a7681eba2b3dc6aae74ff62016937d6c7d1d604`首个Upgraded指向AE31，并见caller→gDAI的DAI Approval。这个绑定来自根实际UI观察，本Owner未重新打开该页；原始creator receipt及完整升级窗口尚缺。UI当前Implementation也是AE31不能证明中间从未改变。

## 源码钱流（行号对应惰性source.txt）

- **入口权限**：L155–166限定onlyGov＝storageT.gov、onlyPriceAggregator＝storageT.priceAggregator；主要交易回调有onlyPriceAggregator及notDone。`unregisterTrade`为private，不是任意人单独调用的公开奖励函数。
- **费用基数**：市场平仓L298–343由仓位及杠杆求名义额，再用交易对close fee参数形成closingFeeDai。L750–760把closingFeeDai＋nftFeeDai传入pairInfos.getTradeValue作交易者净结算；本轮未独立核pairInfos内部公式或实际历史参数。
- **vault分成**：L772–780在trade.positionSizeDai>0分支，以`closingFeeDai * daiVaultFeeP / 100`算reward2；先`storageT.transferDai(storageT,this,reward2)`，再`storageT.vault().distributeReward(reward2)`并发DaiVaultFeeCharged。直接资金从storageT的DAI经callback进入vault，不等同自然人直接支付。此文件仅L778一处直接调用vault.distributeReward。
- **PnL另计**：L782–805及L902–905处理其余费用及交易者剩余抵押物；盈利不足额从vault.sendAssets取，剩余则receiveAssets入库。此类PnL入出不能重复称奖励手续费。
- **比例可改**：L123–153初始化三项费分成且sum100，授予staking／vaultToApprove DAI allowance；L170–182允许onlyGov改三比例，L185–195可暂停／停用。L27注释“eg.40”不是已核历史值；实际初始化参数、后续修改及storageT.vault()历史目标仍未绑定。

这906行是交易／预言机回调、费用分配及结算机制，不是披露的价格预测模型。不能推广为平台上游绝无模型，亦不能由机制公开推个人有预测优势。

## 保留边界

相比旧报告，现在有特定实现源码及正面的交易费分配机制。仍缺全升级史、每笔reward对应的DaiVaultFeeCharged和storage/callback/vault实转、实际费比例与交易参数；所以不能把所有933记录自动全部定性为已核tradingfee，更不能据毛奖励认个人净利。金库PnL、借款、抵押机会成本及全费用另有范围。

来源原件、惰性文本、旧源审指纹及逐点定位见补充JSON。累计2/2GET已结束，源码未导入／编译／执行，没有ABI／EVM调用、链查询、模型、回测、收益／容量计算、账户、付款或交易。actual model/effort UNKNOWN。完成停止。
