# 历史Swap与直接成本标值独立审阅

**限定PASS，无金额或取价方法实质错误。** 是实际历史spot的费用标值，不是执行换币、美元结算或全钱包净亏。实际UTC/全部输入hash见同名JSON，实际model/effort UNKNOWN。0联网、模型/回测/策略/EVM/交易，不改root。

先核价格池内容身份，而非只看hash：复读旧NFT1307592的原multicall→mint输入，token0=USDC、token1=WETH、fee500；原receipt同一NFT由Null铸出，实际PoolMint emitter88e6…及两个币实投量与NPM记账匹配。原receipt、交易索引和旧独审输入hash未变。USDC6位来自固定官方地址簿，WETH18位来自已保存WETH9源。支持此历史池身份，不声称独立编译或当前链状态验证。

quote-rule SHA256 2d16128b4b7a7f048a3fd24076dfb18f297662c775a0b32eb40e48047195bdfb，保存早于两批报价首次GET。独立核每个[b−99,b]区间、emitter/topic、5word数据、去重、成功空末页；排自hash并选严格早于receipt首globalLog的最大(block,log)。不是从多报价选有利结果。

| 成本时点 | 返回页数/实际最近Swap | sqrtPriceX96 | 费用USDC标值 |
|---|---|---|---:|
| Supply | 49/0；25878392/log330 | 1594444648590323642124790225081244 | 1.230934066658864… |
| Withdraw | 114/0；25879037/log334 | 1592843757380827581066506932759235 | 0.972875181243543… |

从原始第3个data word取sqrtPrice，独立Decimal算术：USDC/ETH标价=2^192×10^12/S²；因token0 USDC6、token1 WETH18，需取倒数方向。两个历史spot约2469.109059806567与2474.074721182346。ETH费用按1ETH=1WETH仅作机会成本标价，没有wrap、出售、费用币兑换或滑点实测。

两笔实付gas标值合计 **2.20380924790240675…USDC**；实际USDC数量盈余0.000796，差 **−2.20301324790240675…USDC标值**，与root独立派生一致。只扣这两笔直接gas，permit成本已在内；无绑定的router与其授权没有一并扣。没有把不同业务或全钱包gas充作这笔费用，也没有将其余外部取得/退出/融资/税费/运营成本断言为0。

原Swap中3/13条transactionIndex='0x'保留，仅用区块及globalLog排序。末页为空只支持提供商返回范围，非独立全链无漏证明。

原10候选0 eligible及2号金额/期限不合格结论不变；负标值不等于真实全换USDC/USD亏损、账户整体净亏、所有Aave用户亏损或未来必亏。未年化、回测、扩大报价窗口或换候选，不证明个人净利、容量或预测优势。
