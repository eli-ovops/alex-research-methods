# Maker callee单笔交易现金流：独立原件审阅

结论：**PASS_OBSERVED_SINGLE_TX_WITH_QUALITY_LIMITS**。保存原件支持同一地址在该笔交易的**已观察ETH流量扣网络费后正增0.097465192271862691 ETH**；不是完整策略账期、账户年度收益、全经营利润或美元ROI。根派生JSON已经明确这些边界，未发现把它升级为上述结论的实质错误。

交易`0x8c06abcb3a94762501ce7064e08616c1541e63b98f185b217403762f8c88cca4`，提供者所载block24392025、2026-02-05T17:09:23Z，caller `0xfa0253943c3ff0e43898cba5a7a0da9d17c27995`。本审阅仅读取既存API原件/回执、提取源码、派生JSON及已有历史标签报告；全部指纹、数字、条件解码和检查见`review.json`。0联网，0下载代码/模型/回测/适配器/策略/RPC/EVM执行或交易。实际model/effort UNKNOWN；规则PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4沿用，未改其他文件。

## 通过层：实际保存数据与整数算术

相关normal/internal/source、三币raw logs、WETH all-events/ABI、caller token-index及callee recent10原件的bytes/SHA256均与保存收据吻合，API均status1/messageOK，收据记载HTTP200。这是本地原件与收据一致，不是重新联网或独立链节点证明。

normal索引仅1笔目标，isError0、txreceipt_status1，from=to=上述caller，value1019wei为自转，不能当外部本金或再扣一次成本。地址性质与完整外层执行器代码未核，不能因from字段就称它普通EOA或Sidestream运营者。

| 该地址本交易已观察ETH项目 | 精确数量 |
|---|---:|
| WETH合约记录的解包ETH入款 | +0.109938735732142791 |
| 付其他地址的ETH，角色UNKNOWN，整笔扣除 | −0.011055512871629488 |
| 网络费536332×2643941791wei | −0.001418030588650612 |
| 观察净增 | **+0.097465192271862691** |

外付接收者为`0x4838b106fce9647bdf1e7877bf73ce8b0bad5f97`，没有证据将其称builder/coinbase/特定服务商；扣除金额不依赖这种归因。internal回复仅两行，均成功、区块与时间相同；它们本身无txhash/blockHash，交易绑定来自保存的`txlistinternal&txhash=…`请求URL及同块/时间，不能冒充完整canonical trace。

## 避免代币、解包与出售重复计收入

caller token-index同笔共3行：DAI收217.897551027701188496、DAI付217.897551027701188496、WETH收0.109938735732142791。DAI净0；不能再把收到的217.89755…DAI加到之后换得的ETH上。

原WETH Transfer日志找到唯一该地址入款，原量109938735732142791，与token-index一致；独立事件类型Withdrawal ABI是indexed address src＋nonindexed uint256 wad。all-events原件中唯一目标Withdrawal的src为caller、原量同上、blockHash/区块/时间/tx一致，也与记录的native入款一致。这里的“独立事件类型”不是独立提供者：三种数据仍来自同一Routescan服务。WETH入款随后解包，只计最终ETH一次；不是两笔额外收益。

callee recent10索引返回10行，其中5行属于目标交易。此目标子集里：

`31105.204277208570603330 DAI销售收入 − 30887.306726180869414834 DAI偿还/Join对应索引流 = 217.897551027701188496 DAI付caller余款`。

仅作为提供者indexed金额，此等式及WETH转入/转出相等通过；recent10限制不证明该交易绝无其他日志，也不提供整个经营历史。无需把已实现兑换流程里的同一笔支出和余款再重复扣/加。

## 数据质量与未通过层

目标四条DAI raw getLogs的logIndex为0x121/0x125/0x127/0x12e，均确实缺data和blockHash。没有对空data做uint解码，没有从token-index回填原件，也不能说DAI金额获得raw日志第二次独立验证。根对此已明确披露。USDC及其他记录存在于保存集合，不等于本次已对整条swap的每跳金额与费用完整审计。

Etherscan目标原网页读取收据明确HTTP403且停止，未取得原HTML；本次没有第二浏览器/来源佐证或独立档案完整性证明。此前Routescan其他块的缺字段问题亦不能因此消失。

## 公开源码与内层参数：可核但不等于私人bot身份

SourceCode API为双括号包装的标准编译JSON，安全JSON解析后其中`UniswapV3Callee.sol`与保存的提取文件逐字节一致。其SPDX为AGPL-3.0-or-later；`minProfit`注释单位是DAI wad，兑换最低输出为`ceil(owe/RAY)+minProfit`，随后join偿还并把剩余DAI转to。此保护不含caller的ETH gas或用户链下最低净利阈值。

API声明ContractName UniswapV3Callee、Proxy0等只作为提供者元数据。未编译、核部署字节码或独立确认代理状态，不称部署源码身份完全验证。

在opaque自调用input里只出现一次已知take selector`0x81a794cb`。条件按该内层ABI被动解析，得到auction106、callee上述db9c…、收款人caller、minProfit原量1、bytes288及路径66bytes（fee codes500/100），与根派生一致。按已读callee语义，1是10^-18 DAI的最低回调余量，不是1 DAI或扣ETH费后利润保证。此为**假设该嵌入位置按已知ABI解释**的局部解码；没有执行，也没有证明完整私有外层语义及实际所有调用。

历史tag报告提供发布元数据早于交易、当前tag下相关四模块规则可读的证据；它没有把caller、外层程序、私有筛选/发送参数或真实运行软件绑定到Sidestream。公共callee调用者不必是Sidestream运营者，参数近似公开示例也不能证明使用其bot。

尚未闭合：独立完整receipt/state账户余额、指定账期全部成功与失败及费用、关联授权/部署/RPC等成本、实际运行版本/阈值/择单、未来复制收益/容量。它们限制可声称的层次；不要求全经营实体跨账户或证明未来永远赚钱，才承认本次单笔观察数量正增。

因此本轮接受限定的正ETH观察结果，保留原DAI缺项、同源覆盖和私有执行身份未知，不将其升级为已验证的完整公开事前策略长期盈利案例。
