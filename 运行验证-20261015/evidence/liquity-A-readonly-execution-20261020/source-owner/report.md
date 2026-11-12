# A 依赖接口与 Multicall3 来源准入

本单正常匿名公开GET共 **11次**，全部HTTP200、完整原体，无重定向/认证/重试。初始8次上限用尽后，Root因三依赖缺少runtime字段，在A已授权资源内明确调整为最多12次；仅补了三次runtime投影，未取第12次。每件低于2MiB。未连接Alchemy或其他链节点、未执行来源代码/ABI/EVM、未注册/付费/安装/交易；实时读取由执行Owner统一完成。

## 已可直接交工程的接口

以下文件均在本目录，原响应、请求、安全头、UTC、bytes/SHA逐次见同名前缀receipt：

| 精确链1对象 | ABI/源码 | 服务验证记录及部署身份 |
|---|---|---|
| registry `0x20f7c9ad66983f6523a0881d0f82406541417526` | `registry.abi.json`、`registry.verified.sol` | 01原体211477B；三个match原值均为`match`，不是`exact_match`；verifiedAt2026-08-26T12:17:30Z；AddressesRegistry/solc0.8.24；部署记录block22512007、tx `0x70905cddd847c0f7a87c7d903ed51a3ec02276058bb64382e76bc4800953adde` |
| SP `0x5721cbbd64fc7ae3ef44a0a3f9a790a9264cf9bf` | `stability-pool.abi.json`、`stability-pool.verified.sol` | 02原体263175B；三个`exact_match`；verifiedAt2025-05-21T14:51:33Z；部署记录block22516080、tx `0xffcab6aa659468b2de56fae8ed3dd5a98483ea1a50537b6e081e027a9437275c` |
| feed `0xcc5f8102eb670c89a4a3c567c[REDACTED_PHONE]c24f` | `weth-price-feed.abi.json`、`weth-price-feed.verified.sol`、`mainnet-price-feed-base.verified.sol`、`mainnet-price-feed.interface.sol`、`aggregator-v3.interface.sol` | 03原体300620B；三个`exact_match`；verifiedAt2025-10-15T12:50:38Z；部署记录block22516075、tx `0x51627e2c693865976778d60f2da51bb33d3b7b57f38890172253e960d415c232` |

必要已确认ABI：registry `MCR()/priceFeed()/troveManager()/stabilityPool()/WETH()/collToken()`等均view；SP `getTotalBoldDeposits()`→uint256 view；feed `ethUsdOracle()`→`(address aggregator,uint256 stalenessThreshold,uint8 decimals)`、`priceSource()`→uint8、`lastGoodPrice()`→uint256均view。feed `fetchPrice()`是nonpayable，返回`(uint256,bool)`，不是无状态getter。

三追加原件 `09-registry-runtime.body`、`10-sp-runtime.body`、`11-feed-runtime.body` 现均包含`runtimeBytecode.onchainBytecode`及服务提供的编译/不可变引用元数据，原字符串含0x长度分别6654/16398/3260。其chain/address/match身份与01–03一致，可供执行Owner对同B `eth_getCode`做字节核对。**验证档案内onchainBytecode不等于本单从当前节点读取的代码**；本Owner未做live核对，未解释或提升registry的`match`原标签。

## 构造、immutable与状态关系

本轮复用旧TM完整记录（`liquity-official-deployment-binding-20261020/root/sourcify-record.body`，SHA002c37f8…）的`creationBytecode.transformationValues.constructorArguments`，原文为`0x00000000000000000000000020f7c9ad66983f6523a0881d0f82406541417526`，与精确registry一致。该档案中的构造参数和已核TM constructor(IAddressesRegistry)→`MCR=_addressesRegistry.MCR()`组成来源绑定；仍非本地重编译或当前链状态认证。

新registry验证源为flattened文件：L4331为public immutable MCR，L4366–4388构造校验/赋值；L4391–4430的`setAddresses`为onlyOwner，设置后调用`_renounceOwnership()`。这些说明源码机制，未凭源码推断本次B已初始化/owner状态。SP源L192–198构造从registry取collToken/TM/BOLD，L207–208实际getter返回内部`totalBoldDeposits`，不是以BOLD余额替代存款账。

feed源L10–16及base L42–50构造保存aggregator/staleness、读取decimals并assert8。本轮01–03的`additionalInput`均null；未取得它们实际constructorArguments，不能填写当前aggregator、阈值或MCR数值。参数应由同B已绑定getter取得，不能从旧常量或名称猜测。

## 同B oracle价格可构造的准确范围

`mainnet-price-feed.interface.sol` L8–12给出枚举顺序：primary=0、ETHUSDxCanonical=1、lastGoodPrice=2。WETH具体源L19–44只有primary与lastGood分支；mode1在该WETH实现中会触发assert，不能误当支持LST路径。

- **mode0且实际oracle读取成功、answer>0、updatedAt不晚于B.timestamp、严格陈旧度小于threshold**：base L86–93/L116–123说明以answer按该oracle.decimals缩放到18位，构成B状态下的条件协议价格。必须同B保存raw answer/updatedAt/threshold/decimals和来源；最新trove数据本身不含oracle价。
- **mode2**：WETH源L23–25返回lastGoodPrice。这是协议回退价，不保证市场新鲜/可成交。
- **mode0而oracle读取异常、非正值或陈旧**：源码期望调用BorrowerOperations关停并切到lastGoodPrice，返回newFailure=true；但外部call gas不足可抛`InsufficientGasForExternalCall`（base L96–103），关停调用也需实际上下文。`updatedAt>B.timestamp`还可能在Solidity减法处revert，不能按普通陈旧fallback处理。
- 外部Multicall或直接读取aggregator失败，**不单独证明feed内部读取会失败**，两者caller上下文不同。没有精确aggregator当前实现/访问控制绑定时应保留UNKNOWN，不伪造oracleDown。`aggregator-v3.interface.sol`只证明feed调用`decimals()/latestRoundData()`的接口；不是具体aggregator部署验证原件。

因此A可在所读正常路径构造同B条件价格；异常/上下文未解释的记录不得静默变成可用候选价。未来真实执行仍会重新取价，不能把B末状态变成B内我方可捕获机会。本Owner未调用fetchPrice；工程若坚持仅getter观察，不应把它塞入Multicall，避免只读模拟内的状态写入影响同批后续结果。

## Multicall3已部署身份及使用边界

官方 `https://www.multicall3.com/deployments`（04）正常200但原HTML仅1898B客户端空壳，没有把它当已读部署表。随后官方仓库README实际指向`src/Multicall3.sol`并说明`deployments.json`；06/07正常读取，两个Git blob均用本地Git对象格式独立核同：

- `multicall-deployments.json`：blob `77d092013a01a69a45d25316384234b8cc95b48f`；chainId1/Mainnet明确链接地址`0xcA11bde05977b3631167028862bE2a173976CA11`。
- `Multicall3.official.sol`：blob `7582ea960ca347a151b3ad3af067fa7b09ed3b78`；源L19–35为Call3/Result；L98–123为aggregate3。源码标MIT。

08为精确chain1该地址的Sourcify独立记录，三个`exact_match`、verifiedAt2024-08-08T11:19:59Z、部署block14353601、tx `0x00d9fcb7848f6f6b0aae4fb709c133d69262b902156c85a473ef23faa60760bd`。其中提取的`Multicall3.sourcify.sol`与官方源SHA均`2054218939d3fa0f52f8ce1a33658d570a550671f63197356ee5744f7e188b1e`。ABI见`multicall3.abi.json`/`multicall3.aggregate3.abi.json`，runtime见`multicall3.runtime-record.json`；原签名记录明确`aggregate3((address,bool,bytes)[])`→`0x82ad56cb`，未在本单执行哈希/ABI调用或编译。

aggregate3是payable非view，内部使用CALL（L105），并非STATICCALL。A只能通过节点只读eth_call、无签名/广播、明确value0，且目标/函数严格限既定getter；逐子调用保存success/returnData，失败不能补0。`allowFailure`影响revert传播，不代表失败可忽略。减少HTTP/外层eth_call次数不自动证明CU、gas/返回体限制或观测时效通过；当前节点代码和吞吐仍交执行Owner核验。

## 来源、许可和实际覆盖

registry/SP提取文件首行BUSL-1.1；WETH feed/base/interface及Multicall3所读文件标MIT。不把文件标记扩大成全部源码、数据服务或生产复用许可；本单仅公开记录研究/接口准备。服务metadata验证时间不是首次公开时间，也不认证当前全依赖状态。

语义阅读范围：registry flattened L4303–4432相关声明/构造/设置；SP L188–211；feed46行/base125行/枚举16行/aggregator接口12行；Multicall源L1–40/90–123；README仅读部署/ABI/aggregate3相关段；01–03/08/09–11仅必要身份、ABI及字段投影，未全面审依赖或metadata大包。完全未读取/使用proxyResolution，字段选择也未请求它。

本地首次Git blob核对因自有内联脚本把NUL误写为两个字符而停止；查询LOCAL_BLOCKERS后以`bytes([0])`修正，只重新解析已存06/07原件，未重取/改源，随后两blob一致。该恢复不是来源拒绝或源码错误。actual model/effort/CPU/RSS UNKNOWN。完整获取回执/覆盖与manifest见本目录JSON。
