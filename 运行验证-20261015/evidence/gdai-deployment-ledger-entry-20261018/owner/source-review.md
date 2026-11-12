# gDAI事前介绍与事件入口

限定取得上线前机制介绍和固定Git树的事件ABI；没有证明部署实现、许可证或个人净盈利。4/4公开动作已用完，停止联网，未重复读取根的Arbiscan资源。

## 原介绍文章

[Gains Network原文](https://medium.com/gains-network/introducing-gtoken-vaults-ea98f10a49d5)标题和日期在L46–54，显示2022-12-07。L68称Arbitrum上线仍在未来，L220–222估计Polygon约一周、Arbitrum约两周后推出。因此支持“上线前公布机制”，不能写成该日已部署。它是当前取得的带历史日期正文，没有独立2022网页快照或精确首次公开UTC。

L110–142说明ERC4626份额、费用累积及交易者PnL影响兑换价；L172–183说明提款申请与epoch延迟。本文没有把特定链上地址与代码版本连起，也不能将2022参数作为当前值。

## 公开Git入口和边界

[GainsNetwork-org/gtoken-subgraph](https://github.com/GainsNetwork-org/gtoken-subgraph)的公开tree GET成功，固定tree SHA为`18ad6359dc210d2a6836f50743f288fdaf2c4ba5`。这是Git树身份，不是已取得的历史commit或发布时间；官方组织身份依据当前检索显示的自述／gains.trade关联，未另开官网反向链接核验。

从该tree明确路径`abis/GToken.json`取得blob `d56b07f62f31d62cdfc0a2582c6f6f4ecc794ce2`，55,817字节，独立Git blob哈希匹配。仅Base64解码为惰性JSON，不调用ABI。它包含：

- `Deposit(sender, owner, assets, shares)`；sender、owner indexed。
- `Withdraw(sender, receiver, owner, assets, shares)`；前三地址indexed。
- `RewardDistributed(sender, assets)`；sender indexed。
- `WithdrawRequested/WithdrawCanceled(sender, owner, shares, currEpoch, unlockEpoch)`；sender、owner及unlockEpoch indexed。

全部34个event定义原样保存在JSON。事件是当前仓库schema，不是已发生交易／转账，也未证明该schema对应所选历史gDAI部署。tree可见arbitrum/polygon配置文件，但预算内未读其内容，不声称已绑定地址。

该tree未定位LICENSE/COPYING；ABI无Solidity SPDX，未取得GToken历史实现。其他SDK的MIT许可不能移植到本实现。历史源码、许可证、升级／版本日期及部署一致性均UNKNOWN。

检索返回的该repo README另明确：AccountVault存入／退出累计也计入按汇率估值的gDAI转移，且可能只是转移、估值近似。此为搜索抽取层，不冒完整README页面读取；不能拿这些累计字段当真实DAI赎回、实收盈利或全费账。

原生返回、两个公开gh GET原件及UTC回执、惰性ABI、每文件SHA／字节见`source-review.json`。新增读取1文章＋1检索＋2源码metadata/ABI GET；链上调用、源码运行、模型、回测、收益核算、账户、付款及交易均0，actual model/effort UNKNOWN。根已报告Explorer明确403，本Owner不重取、不换身份。这里只保存真正可用入口，不自动重建链上账。
