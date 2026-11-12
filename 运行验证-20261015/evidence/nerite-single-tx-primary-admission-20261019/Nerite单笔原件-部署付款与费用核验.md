# Nerite单笔原件：部署、付款与费用核验

读取日期：2026-10-19 UTC。**从第三方笔记推进到官方部署页和官方RPC原件，确认指定交易成功，官方tBTC分支GasPool的WETH经中转合约到达发送者。** 本轮准入的是单笔身份与付款/费用证据，不是完整策略净利、未来优势、可执行复制或容量。

## 1. 核了什么，来源是什么

指定交易：`0xa943b8224459e00164d2ea2df1918363bff8d855e3683fb23485aca2d904871c`。

- 官方部署页实际读取：[Nerite Protocol Contracts](https://docs.nerite.org/docs/technical-documentation/contracts)。页面列出tBTC分支TroveManager、GasPool和Arbitrum WETH；未在返回正文看到发布日期。只认证读取时文档所列身份，不冒称历史完整升级/部署谱系。
- 官方技术页实际读取并指向 `NeriteOrg/nerite` 为核心仓库：[Technical Docs & Code](https://docs.nerite.org/docs/technical-documentation/technical-docs-and-code-repository)。
- 官方RPC `https://arb1.arbitrum.io/rpc`仅对给定hash读取 `eth_getTransactionReceipt` 和 `eth_getTransactionByHash`，各一次HTTP200，无JSONRPC error，原对象非空；hash、blockHash、blockNumber、from、to、index及type一致。未调用eth_call、trace、estimateGas或发送交易。
- 固定仓库ref `2076006c133eae54a8e1f681e1cec7fd76e81d95`读取Constants.sol和ITroveManager.sol，blob独立核对。这个ref先由外部笔记提供、官方文档核了仓库归属；本轮未将此ref编译字节码与历史部署逐字匹配，也未认证提交首次公开时间。Constants L13明确固定项0.001 ether、L66抵押项除数800，头部BUSL-1.1；不能沿用以太坊Liquity的0.0375参数，也不泛化为全代码MIT/可任意复制。
- Arbitrum官方费用说明实际读取：[Inside Arbitrum Nitro](https://docs.arbitrum.io/how-arbitrum-works/inside-arbitrum-nitro)，L365–390说明L2执行和L1数据费用。当前排序/优先费规则不倒推本交易历史配置；实际费用优先依据该历史收据有效价格。

本单元8个来源动作：4个原生网页/搜索读取动作、2个历史RPC对象、2个固定源码GET。RPC与源码四个请求均HTTP200；原生工具未返回原HTTP状态/字节，按工具返回内容保存，不称原始HTTP页面归档。

## 2. 原始交易及支付路径

|项目|已核原值或身份|
|---|---|
|链/区块|chainId42161；block477214808；hash与receipt相同|
|时间|交易对象blockTimestamp给出2026-06-25T13:58:14Z；未额外读区块|
|执行状态|receipt.status=0x1|
|发送者|`0x49b34d0c593b877d426276258a0301f24402d4ec`|
|顶层目标|`0x85e65e2aa4a04e1e0a6b709b4d70c65903b1ccb6`；是中转目标，具体ABI/所有者/源码未核|
|顶层方法标识/value|0x6571cc0a；value=0；不是直接以batchLiquidateTroves selector调用官方manager|
|官方tBTC manager|`0x285b3d3813d7a132d3f1ab48bb5a585e1363cdeb`|
|官方tBTC GasPool|`0xafaa4a10d7878c13e802e11fcbdb75f25f278ce6`|
|官方Arbitrum WETH|`0x82af49447d8a07e3bd95bd0d56f35241523fbab1`|

收据含上述manager的事件，log0x7e的topic0为已识别的Liquidation型谱 `0x7243af9a1cff94d3429b2ee00b78c1c10589259f20dc167cb67704f38f9e824e`。本轮保留原data，不宣称Nerite部署ABI/全部字段已逐字认证或完成全路径验证。

同一收据内，WETH标准Transfer日志给出：

`官方tBTC GasPool → 顶层调用目标 → 交易发送者`

- log0x7f：GasPool到中转目标，raw `1000000000000000`。
- log0x81：中转目标到sender，raw同值；这是等额转发，同一笔款只计一次。
- 以WETH常规18位精度展示为0.001WETH；精确验收保留raw整数，本轮没有额外调用decimals getter。它与本次固定源码中的固定补偿量相容，但不能因此认证整个部署与该ref完全相同。

其他token的Transfer也已保存，未任意赋美元价格或合并为收入。receipt成功本身不代替付款证据；当前付款证据来自实际WETH日志与官方身份绑定。历史主网V2、该Nerite交易以及前述cranker程序三者没有被串成同一个执行系统。

## 3. 费用字段与最小勾稽

|收据字段|值|
|---|---:|
|gasUsed|790494|
|effectiveGasPrice|26754000 wei|
|gasUsedForL1|748|
|transaction.gasPrice|200000000 wei；与收据有效价不同，不用它替换实收据字段|

只做原件字段的静态算术勾稽：`790494 × 26754000 = 21148876476000 wei = 0.000021148876476 ETH`。这是该收据的gas字段乘积，与外部笔记所列该笔网络费一致；**不是新策略账户、回测或净利润计算**。不把gasUsedForL1再作为独立金额重复加费。

没有将0.001WETH减去ETH费用报告为实际单币/美元利润；没有认证内部原生币额外付款、链外订阅/排序安排、RPC/机器费用、此前失败、资金来源、全部资产余额或税。本轮未发起trace或余额/其他交易查询。因此，这里证明实际付款及公开网络费字段，不能宣称完整扣费盈利。

## 4. 对第一性原理目标的帮助与边界

可确认的收入通道是协议GasPool向执行路径付款；这为“完成协议服务获得报酬”提供一笔原始资产移动证据。它不证明收到款的人已经获得全部成本后的经济利润，也不需要推断其用模型预测价格。

个人可以学习的最小环节仍是：用协议真实条件发现任务，事前限制成本，事后按实际付款和所有尝试费用核账。当前缺口已经具体到顶层中转合约的规则与资金边界、完整尝试集及总成本；公开固定模型、更多本金或同一成功交易的多次转账都不能替代这些证据。任务供给、可捕获份额与扩大资金后的净额仍未测。

本轮不认证0.001WETH为长期单次平均收入，不年化、不算ROI，不把单次成功当稳定优势、容量或Gerko财富1%路径。也不把换链当作BTC模型策略的独立样本。

## 5. 原件及下一步

transaction-owner保存两个完整请求/原响应、HTTP头、UTC、SHA256、字段解码及原始协议/支付日志。Root已实质读取原始字段派生件和选中原日志，并核官方地址；来源验收按两个原响应SHA复核，不依赖成功状态自述。

- receipt读取2026-10-19T14:16:50Z至14:16:51Z，15639B，SHA256 `4e28b7538435ceebbec8721ddb9587ace51bee5068a7a96144d6327b1eb63925`。
- transaction读取14:17:07Z至14:17:08Z，723B，SHA256 `b5b6b5fc7e4ecd44a8c53de50ad2003f949a70132bebd59dd629c8564236842e`。
- 网页材料为root下native captures，只对工具返回内容计算哈希，不冒称源站HTTP原字节哈希。

唯一下一只读核查：找顶层目标 `0x85e65e2aa4a04e1e0a6b709b4d70c65903b1ccb6` 的已验证公开源码/ABI和历史身份，判断它如何选定/执行协议操作、是否还有其他资金投入或付款；找不到就保留UNKNOWN，不猜方法名、不反编译私有资料、不运行合约。不先扩成新模型/策略试验。得到资金边界后，才考虑固定完整尝试集的后续资料核验，不能只收成功。

上一目标轮作者有日期无交易叙述及候选收口为PROGRESS。本轮新增官方部署绑定、真实补偿路径及收据费用字段，记为 `PROGRESS_NERITE_PRIMARY_PAYMENT_AND_FEE_FIELDS_BOUND`；**没有新增完整独立净绩效证据，整体财富目标未达成。**

没有运行模型、第三方源码、回测、EVM或新账户核算，没有安装、付款、登录、凭证访问、交易、外发或自动化。年度2026方案未执行，旧FAILED/NOT_SUPPORTED、旧V2正净事实及AAPL/Issue85安排不变，Hypedexer邮件未发送。新原件全部保留，无清理。
