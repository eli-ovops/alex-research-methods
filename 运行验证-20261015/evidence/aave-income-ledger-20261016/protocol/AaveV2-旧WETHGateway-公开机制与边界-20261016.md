# Aave V2 ETH/WETH 供给机制与旧网关身份

结论：旧地址 `0xcc9a0b7c43dc2a5f023bb9b738e45b0ef6b06e04` 的既存 Etherscan Exact Match 源码可以与官方历史 V2 源文本逐字节对应。协议机制是公开的借贷收入分配，不是预测或交易优势；本分支不证明任何真实账户扣费盈利。现行推荐网关、历史旧网关和池实现升级须分开。

本轮仅公开GET、源码/HTML/JSON静态解析与哈希，无编译、EVM、模型、回测、下载程序执行、安装或交易。实际model/effort UNKNOWN；沿用 PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4。

## 版本、许可与时间

固定官方仓库版本：[aave/protocol-v2 682a7d13fec9ee9f3e50412d68d7b00664a3b252](https://github.com/aave/protocol-v2/tree/682a7d13fec9ee9f3e50412d68d7b00664a3b252)，API返回提交时间2021-02-26T18:18:38Z。本次保存README、LICENSE及网关、AToken、ReserveLogic、LendingPool、默认利率策略、MathUtils、ValidationLogic九份关键文本，未称下载完整可编译包。

根LICENSE为 GNU Affero GPL version3或以后版本；主要协议/网关源码 SPDX `agpl-3.0`。允许个人阅读、使用与按许可条件修改/复制，并非MIT；分发、网络服务及依赖组件各自许可义务须保留，不能声称零条件商用。未复核所有依赖许可。

[官方社区V2上线帖](https://governance.aave.com/t/aave-v2-is-live-megathread/1621)标2020-12-03，表述V2已上线；官方历史仓库README明确供应流动性赚取passive income，并链当时V2文档、白皮书及2020年审计。它们共同支持机制在2025-09账户供给之前已公开存在；精确首次公开时间、当时网页可见性的独立归档时间仍UNKNOWN。Git时间本身不能单独证明当日首次公开。今日的[官方V2专页](https://www.aave.com/docs/resources/legacy-versions/v2)仅作版本与机制交叉核验，不把V3/V4导航或新机制套给旧实例。

## 地址身份与适用边界

从根已存 [旧网关源码页](https://etherscan.io/address/0xcc9a0b7c43dc2a5f023bb9b738e45b0ef6b06e04#code) 的 `editor_contractJsonData` 按字符串转义规则和JSON数据解析，未eval或执行网页脚本，得到18源标准编译输入。页面标Exact Match，编译器0.6.12，构造参数WETH为 `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`。抽出 WETHGateway.sol 与上述固定官方文件逐字节相同，双方SHA256：`3896daa06a7fd62134349ad7c50d9c92993b096bce2d335d0eac42d07cb0d89f`。是精确字节比较，无须规范化才相同。

该网关构造函数仅固定WETH；每次 `depositETH/withdrawETH` 另传 lendingPool，不能仅凭网关地址断言池版本。根已存2026-06-04提现原件传入 `0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9`；[官方地址簿固定版本707fb57089f3aac8bb99f7fce7defe1d1d2d7494](https://github.com/aave/aave-address-book/blob/707fb57089f3aac8bb99f7fce7defe1d1d2d7494/src/AaveV2Ethereum.sol)（2022-12-22T12:09:36Z）将此地址列为 AaveV2Ethereum POOL，addresses provider为 `0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5`。固定2021协议README也给同一主网池地址。

2022地址簿 WETH_GATEWAY 已为 `0xEFFC18fC3b7eb8E676dac549E0c693ad50D1Ce31`，因此不得称cc9a为2022或当前推荐网关。未查cc9a部署时间、撤换完整历史；也未编译独立验证字节码或核2025/2026池/aToken代理全部实现升级。公开源码与explorer提供强身份对应，但这些未知必须保留。

## 供给、提取与收入公式

| 环节 | 固定历史代码行为 |
|---|---|
| ETH供给 | WETHGateway.depositETH将msg.value包装为WETH，调用指定池deposit，aTokens铸给onBehalfOf。普通入口无白名单；目标池需获网关owner的WETH allowance授权，池仍可暂停/限制reserve。 |
| 直接WETH供给 | 用户批准WETH allowance后调LendingPool.deposit；池更新储备状态与利率，转入aToken合约并按当前index铸缩放余额。 |
| ETH取回 | 用户先批准aWETH给网关；withdrawETH按amount或uint256.max读取全部aWETH余额，transferFrom至网关，再经池销毁aToken领WETH、解包ETH并发给to。approval、deposit、withdraw及失败交易均可能耗gas。 |
| aToken利息 | mint缩放单位约 amount/index；AToken.balanceOf = scaledBalance × getReserveNormalizedIncome（ray精度1e27，含舍入）。没有余额变化不代表没计息，利息可由余额view计算。 |
| 指数更新 | getNormalizedIncome约 I_last × [1+r_L×Δt/SECONDS_PER_YEAR]，更新状态后分段累计；不是把屏幕APY固定套整个持有期。 |
| 供给利率 | 默认策略 U=(D_stable+D_variable)/(availableLiquidity+D_stable+D_variable)；r_L=[D_variable×r_variable+D_stable×平均稳定借率]/总债务 × U × (1-reserveFactor)。零债务时借贷供给rate为0。 |
| 协议储备 | ReserveLogic._mintToTreasury按新增债务利息×reserveFactor为treasury铸aToken；供给端rate已扣储备因子，不能在净收益里重复扣同一项目。 |
| 额外收入 | 此历史LendingPool.flashLoan的无债务偿还路径把premium经cumulateToLiquidityIndex分配到该reserve指数；不能笼统说全部收入只来自普通借款利息。 |

以上是固定历史算法，**不是2025/2026实际WETH reserveFactor、利率曲线、费用率或实现版本核验**。实际参数、暂停/冻结与升级事件要按账户每段持有区间核；本轮未读取链上状态或部署参数。没有从后来的余额反推未核参数。

## 费用与亏损风险

收入支付者主要是借款人，历史闪贷溢价另由闪贷使用者支付。Gateway和普通deposit/withdraw历史函数未另收固定存取手续费；ETH↔WETH在该路径按同数量包装/解包，无DEX换汇，不应凭空加滑点。gas和approval成本真实存在；若用户额外换币、桥接或领取奖励，应按实际交易另算，未发生者不假设收费。

账户净收入至少应按已实现提取＋期末可兑现残余资产－净投入本金－所有关联gas/approval/失败费核算，不能仅比较存取名义数额。aWETH余额与Transfer事件不是可直接逐条相加的独立利息发放；还须排除转账、重复计利和借款/清算。

源码允许供应/提款受暂停、reserve状态和抵押健康检查影响；高利用率时底层流动性不足可能使提款失败。借款人违约与清算不足可能造成坏账/偿付风险，合约/网关/预言机和治理升级也有风险；这些是机制风险，未在本轮量化发生概率。只供给且未借款，不应称其因ETH价格下跌本身触发借款清算；若以该供给作抵押借款则另有清算风险。ETH计价本金增长也不保证法币本金增长。历史不收存取费不保证任意未来版本或第三方前端免费。

## 原件与读取覆盖

逐GH请求URL/读取UTC/字节数/响应SHA256在receipts.json；固定源码文本与API原响应一并保存。公开网页保存为官方web工具渲染响应 `official-web-tool-response.json`，明确不是原HTML。root两份原HTML与读取收据的输入哈希，以及精确源码比较，见gateway-static-source-comparison.json。

工具边界：原生web读取该explorer曾返回403，停止该路线；由根正常取得的既存原HTML继续静态核验，没有绕过限制。全地址/片段公开搜索及GH代码搜索未命中不能证明地址不属于Aave；已以原源码和实际池参数修正。一次对不存在deployed-contracts.json的GH请求404原响应保留；未重试猜文件。早期搜索结果/失败web响应未完整落盘，响应哈希UNKNOWN，不能冒充已归档原件；不影响已保存源码与explorer比对。
