# 两固定交易：CTF ABI与静态结算准入

**限定PASS：原始字段与公开静态机制对应；不是现金闭合、利润或历史runtime身份通过。** 本轮3次官方源码GET均200、312516 bytes；未取新账数据，未执行源码、Keccak、EVM、SDK、模型、回测、交易或安装。actual model/effort UNKNOWN；PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4沿用。原URL/请求与完成UTC/HTTP/字节/SHA在`read-receipts.json`，12份实际输入绝对路径及指纹在同名JSON。

官方Gnosis仓库HTML嵌入`currentOid=eeefca66eb46c800a9aaab88db2064a99026fde5`，随后取得该固定版本的[ConditionalTokens.sol](https://github.com/gnosis/conditional-tokens-contracts/blob/eeefca66eb46c800a9aaab88db2064a99026fde5/contracts/ConditionalTokens.sol)及[IERC1155.sol](https://github.com/gnosis/conditional-tokens-contracts/blob/eeefca66eb46c800a9aaab88db2064a99026fde5/contracts/ERC1155/IERC1155.sol)。本次未独立比部署字节码、首公开时点或完整许可；它们是原始官方静态定义依据，不能仅凭当前网页给历史源码身份背书。

## ABI与数据顺序

| 事件 | indexed字段（除topic0） | 非indexed data |
|---|---|---|
| `PositionSplit(address,address,bytes32,bytes32,uint256[],uint256)` | stakeholder / parentCollectionId / conditionId | collateralToken / partition动态数组 / amount |
| `PositionsMerge(address,address,bytes32,bytes32,uint256[],uint256)` | stakeholder / parentCollectionId / conditionId | collateralToken / partition动态数组 / amount |
| `TransferSingle(address,address,address,uint256,uint256)` | operator / from / to | id / value |
| `TransferBatch(address,address,address,uint256[],uint256[])` | operator / from / to | ids动态数组 / values动态数组 |

位置：ConditionalTokens L29–45，IERC1155 L10/12。需注意**split/merge的collateralToken不indexed、conditionId是topic3**；不要套用PayoutRedemption的另一种indexed布局。TransferBatch的两个head是offset，不能当token ID或金额。本轮未计算topic哈希；按已有原日志的topic、shape与官方字段布局对应。

对root的raw-word-view共7＋15条日志逐条复读，address/topics/hex words/int words均与前phase SQD原NDJSON一致；不是只信派生标签。

## 实际split及流转

第二笔`0x5248139a…cc8ef86` log1074独立解得：stakeholder为`0xada100874d00e3331d00f2007a9c336a65009718`，parentCollectionId零，conditionId为`0x7880e75cbec05c8e0565ddfb616478536148a0019b4029c0366ab751d75f6496`，collateralToken=`0x2791bca1f2de4661ed88a30c99a7a9449aa84174`，partition=`[1,2]`，amount=`6330000`。

log1073是zero→ada100874的TransferBatch，两观察token ID各6330000；log1075是ada100874→E111同两ID及原量。随后log1076/1078将其中一个ID的330000＋6000000发给5f8d795…，log1082将另一个ID的6330000发给c2beC11…。这是同条件两分区权利在不同地址间分配，不能把两人的互补份额合并成某一人的套利收益；此处也未自行哈希重算ID或查询结果状态。

ConditionalTokens L99–162：需已准备条件、非平凡且互斥partition；完整集合且root parent时从调用者收抵押物，其他路径会销毁相应父/组合持仓，之后每个子持仓铸造同量。L165–215的merge反向销毁各子份额；完整/root路径返还抵押物，否则铸造父/组合持仓。该函数未要求先报告结果，**但返回抵押物含本金，不等于利润**。静态路径须与历史部署、实际付款对应后才能进一步称真实结算全闭合。

## E111成交与费用

复用固定commit`ccc0596074f4dfd62c944fbca4de252893b82b4b`的官方Events/Trading。第一笔`0x4ea2410f…35edcd0`有同一02e489…卖方的两条SELL，均卖5000000 outcome、对应4000000 collateral；两个实际ERC1155转移均到0b52…买方。买方汇总BUY为10000000 outcome/8000000 collateral，fee115200。其OrderFilled汇总及OrdersMatched不是第三、第四笔独立付款，FeeCharged亦不可与已扣净付款重复扣费。

Trading L217–251及L351–382的静态逻辑为SELL从所得扣fee、BUY额外支付fee；fee为数额，builder/metadata为独立bytes32。本次只核原量含义，不替root算现金收益，也不将当前固定源码视作历史运行的独立证明。

## 地址角色与过滤缺口

- 旧官方`contracts.original.md` L48/57明确C011…为当前pUSD CollateralToken proxy；不因此独证它在样本块的实现或历史完整配置。
- 实际ada100874…是观察到的split stakeholder、铸造接收/转出及抵押路由地址。当前官方表的CtfCollateralAdapter是**不同地址**`0xAdA100Db00Ca00073811820692005400218FcE1f`（L52/62），不能移植部署身份。历史正式角色UNKNOWN。
- c417fd8…仅在旧2791日志可观察为转出者/授权owner；精确合约角色、现实主体UNKNOWN，不猜。

原查询仅筛E111、CTF和2791三个日志地址，没有C011的ERC20 Transfer，无法闭合新版collateral付款；更不含所有币、全钱包、全部native或跨持有期记录。新增币种付款需root另行固定范围取原件，不能以缺表填0。持仓创建是抵押物/父权利转换，ERC1155 transfer是余额标准，生命周期事件是上下文，不重复制造收入。

无需完整私人机器人来承认这些历史数量事实；本阶段的实质缺口是限定资产与费用原账，而不是私人动机。完整财富目标仍active未达。
