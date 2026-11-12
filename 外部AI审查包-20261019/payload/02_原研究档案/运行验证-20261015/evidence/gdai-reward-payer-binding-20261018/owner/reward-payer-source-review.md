# gDAI奖励付款人：直接caller已知，资金性质未明

限定结论：已存933条RewardDistributed的直接sender全部为`0x6c612c804c84e3d20e3109c8efd06cd2d8b28f46`；独立归档只取得该地址的proxy包装源码，不能证明全部奖励来自交易费。按任务停止条件未使用第二GET，不猜logic。

## 原件与字段

本地`gdai-historical-ledger-access-20261018/root/official-arbitrum-fixed-holder-vault-original-logs.raw.json`的response23共933条，topic1均为上述地址，范围为返回记录block49860685–51241624。仅核地址与范围，没有加总奖励或归属某位持有人，也不把它称全平台历史全集。

`gdai-deployment-ledger-entry-20261018/root/GToken.initial.source.txt` L720–730：L722把sender设为_msgSender，L723从sender实际safeTransferFrom资产至金库，L725–729增加奖励状态、更新份额价并发事件。因此按取得的初始实现，sender不是任意传入标签，而是直接caller及被拉款的资产账户；仍不是最终资金来源或交易根EOA。该函数本身无角色限制，不能从Reward名字直接认交易手续费。本轮未逐笔复核933个receipt／资产Transfer或完整升级史。

## 独立Sourcify记录

唯一公开GET：
`https://sourcify.dev/server/v2/contract/42161/0x6c612c804c84e3d20e3109c8efd06cd2d8b28f46?fields=sources%2Ccompilation%2Cmetadata%2Cdeployment%2Cabi%2CcreationBytecode.transformationValues`

2026-10-18T09:13:10.457670Z—09:13:12.038176Z，HTTP200，105,050字节，SHA256 `ccaa024744872542d8f4f44626b1752bfa1923a7acf225cafddf497bac5e658a`。runtime exact_match，编译名TransparentUpgradeableProxy；creationMatch、部署交易／block、constructor transformationValues均缺。verifiedAt2024-08-08T11:10:33Z不是部署日期，也不是2022事前源码公开证明。

包装源`TransparentUpgradeableProxy.sol` L15–23说明admin与普通调用转发，L28–36定义构造；L1 MIT只限取得的包装代码。归档中包含其他编译输入，不代表它们就是此caller运行逻辑。没有构造参数就未绑定初始logic；当前及2023实现、费用分配函数、管理修改权限和任意注资路径均UNKNOWN。不能按地址名或同编译包猜实现。

缺的不是又一次Reward地址统计，而是可可靠绑定该地址在窗口期运行实现的原件，继而核其手续费收取／划拨路径。即使以后找到该路径，仍不能无交易来源证据将每次入款自动全部定性为trading fee。

所有本地输入、原始GET和UTC回执当前SHA／字节见JSON。已用1/2公开读取后停止；未请求proxyResolution、RPC、被拒Arbiscan或任何其他链上数据。无源码／ABI／EVM执行、模型、回测、收益／容量计算、账户、凭证、付款及交易。actual model/effort UNKNOWN；完整盈利案例未获证明。
