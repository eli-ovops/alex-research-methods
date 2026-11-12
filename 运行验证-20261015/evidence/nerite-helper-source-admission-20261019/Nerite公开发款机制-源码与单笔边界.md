# Nerite公开发款机制：从原始付款推进到已验证规则

读取及核验日期：2026-10-19 UTC。**本轮把指定交易与已验证清算事件、公共业务入口及向调用者发款的源码连起来。可以解释服务报酬从哪里来，尚未证明个人能稳定抢到任务、扣除完整成本后赚钱或放大资金。** 无模型、策略核算、回测、合约/EVM执行或交易。

## 1. 新增了什么原件

官方部署身份及原始付款已有[前一单元报告](../nerite-single-tx-primary-admission-20261019/Nerite单笔原件-部署付款与费用核验.md)，指定交易为 `0xa943b8224459e00164d2ea2df1918363bff8d855e3683fb23485aca2d904871c`，2026-06-25成功；WETH从官方tBTC GasPool到helper，再等额转给sender。同一补偿只计一次。该单元本次仅补完来源验收回执，没有重取交易或新增金融账户。

本轮对官方manager `0x285b3d3813d7a132d3f1ab48bb5a585e1363cdeb` 的[Sourcify既有验证档案](https://sourcify.dev/server/v2/contract/42161/0x285b3d3813d7a132d3f1ab48bb5a585e1363cdeb?fields=sources%2Ccompilation%2Cmetadata%2Cdeployment%2Cabi%2CcreationBytecode.transformationValues)仅一次GET，HTTP200、535942B。档案给出：

- `src/TroveManager.sol:TroveManager`，creation/runtime均为`exact_match`；solc0.8.24。
- `verifiedAt=2025-09-11T15:10:46Z`，早于本次2026-06-25交易；部署block356662416。这是验证服务记录，不冒称独立重编译、全部历史变更审计或精确首次公开日期。
- 原件SHA256 `92acb9b53c7576ae18f2981ac4dbc53d6e3b8376d7576ed8c0f7b566ea973c55`。ABI、提取源码、UTC/HTTP及Owner审阅均在manager-review目录。

Root用自有纯数学Keccak，经空串及Transfer两个已知向量检查，将ABI中十个uint256的Liquidation签名精确绑定原收据log0x7e的topic；发出地址、十个非indexed数据字及长度一致。该核验是来源身份及字段解码，不是运行来源代码、EVM或新收益实验。[签名与原字段勾稽](root/event-signature-identity.json)

## 2. 谁做什么、谁支付

已核源码的入口是 `batchLiquidateTroves(uint256[])`：调用者提交抵押债仓的编号列表，协议在执行时取自身价格、检查状态和抵押率，只处理低于规则阈值的有效债仓。指定入口本身没有调用者白名单修饰器；不等于全部运行条件、当地参与资格或所有关联合约均已审计。

源码L419–477处理债务和抵押物：稳定池能抵消的部分走offset，余下部分按协议规则再分配；没有有效债务减少则`NothingToLiquidate`回退。该入口没有要求调用者在入口中交出全笔债务本金；不能因此称无资本、无风险或保证成功。

源码L463–477先发Liquidation事件，再把固定项与抵押物项传给 `_sendGasCompensation(..., msg.sender, ...)`；L539–547中，固定项经 `WETH.transferFrom(gasPoolAddress, liquidator, ...)`，抵押物项另从ActivePool支付。

因此可定位的流程是：

> 发现符合条件的债仓 → 提交编号 → 协议检查并执行清算 → GasPool向调用者支付固定WETH补偿；有适用抵押项时另行支付。

**经济解释（推断）：**协议用报酬吸引外部执行者及时完成风险处置。当前直接付款方已核为协议GasPool；这些储备最终如何由借款人等参与者筹集，本轮没有追溯全部资金来源，不补猜。

本笔事件第三原值为`1000000000000000`，与已核WETH付款原值相符；第四抵押补偿原值为0。注意ABI第三字段仍叫`_boldGasCompensation`，源码实际传入的是`ETHGasCompensation`；第八字段名也保留`_L_ETH`而实参是`L_coll`。不能按旧变量名把它误认成稳定币收入或擅改资产单位。原始整数保留，未赋美元价、相减算净利或统计全期策略收益。

## 3. 个人能复制的环节与真正卡点

可学习的公开环节是：理解资格条件、读取公开债仓状态、按执行时可能得到的真实补偿约束费用，并对成功和失败尝试完整记账。公共入口及发款规则已有源码依据；**私人helper源码不是理解这个经济机制的必需前提，也不能因未知helper就断言没有可复制部分。**

精确复制该交易的上层程序仍未做到：helper `0x85e65e2aa4a04e1e0a6b709b4d70c65903b1ccb6` 的Sourcify记录HTTP404、match字段null；Arbiscan原生读取无HTTP状态，随后一次普通HTTPS GET明确403。两资源均停止，不换身份/代理/镜像重取，不把未取得档案写成没有源码或永久不可行。manager是独立对象的正常已验证档案，不替代helper的选单/路由/发送实现。

源码公开也没有回答优势为什么没被竞争者吃掉。目前没有证据表明我们能比现有执行者更早发现和成交，或有更低的全部成本。资格在自己提交后失效、别人先完成、价格/状态变化、节点/网络/程序故障，都可能使一次尝试无报酬而发生费用；这项机制不要求先有更准的价格预测，也不提供持久竞争优势保证。

资金扩大时，报酬取决于任务供给、捕获份额与竞争成本，不随本金同比增长。这是机制推断，尚未取得完整任务量或容量测量；不能从一笔0.001WETH的转账年化，也不能以这笔成功推算5000美元能赚多少或何时达到Gerko财富1%。

本次源码为BUSL-1.1标记。公开可读、调用协议函数、复制部署协议业务源码和复用某个执行程序，是不同问题；本轮没有授予全部代码任意复用许可或参与法律资格判断。

## 4. 研究判断及下一步

**保留为“公开服务付费机制”的研究样本，暂不进入开发或资金试验。** 比先找一个公开模型更具体的正事实是：服务被执行、协议有明确发款函数、资产确实到达本笔发送者。但当前仍只有选定成功交易，不能认证完整成本后净优势。

唯一下一只读任务：核指定发送者的公开历史索引能否完整覆盖一个事前固定的研究期间，并找到该范围内所有相关成功/失败尝试、费用及付款原件的入口。先核索引覆盖及交易分类，不只收成功、不归并成新策略账、不计算新净收益；找不到完整入口就保留UNKNOWN。它不需要等待Hypedexer回复，也不启动年度2026核算。

## 5. 本轮范围、预算及原件

本轮4个公开来源动作：helper Sourcify GET404、Arbiscan原生not-accessible（原HTTP UNKNOWN）、同址普通HTTPS GET403、独立manager Sourcify GET200。没有第二次manager请求，没有RPC/eth_call/trace/估gas/编译，没有安装、注册、付款、钱包或交易。公开拒绝均保留并停止；没有把拒绝当成零收益。

并行Owner只拥有manager-review；Root负责helper和原收据元数据/签名复核。Owner终态报告已回读，Root实读入口L419–481、筛选/累计L488–530及发款L535–549；没有声称全源码审计。所有来源及验收文件保留，无清理。

上一目标轮重复已完成的年度计划，对整体财富目标记为NO_PROGRESS；本轮新验证ABI/发款源码改变后续核查对象，记为PROGRESS_NERITE_VERIFIED_EVENT_AND_PUBLIC_SERVICE_PATH。整体目标NOT_ACHIEVED，无已确认live进程等待，无真正连续阻断。旧FAILED/NOT_SUPPORTED及旧Liquity正净数量事实不改。

用户在本轮另明确授权Hypedexer已审邮件发送一次。Gmail接口项目配额失败后未重试该发送接口，正常已登录网页一次发送，随后SENT唯一对象及完整批准正文回读一致；独立发信回执在[Hypedexer发送验收](../hlp-public-profit-mechanism-admission-20261019/cashflow-boundary/outreach-send-20261019/send-verification-receipt.json)。这只完成资料定义求证的外发，不等于取得回复、盈利或资金容量证明，不授权追信或监控自动化。
