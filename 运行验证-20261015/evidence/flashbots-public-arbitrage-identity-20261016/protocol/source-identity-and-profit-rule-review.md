# 固定源码身份、费用规则独立审阅

**限定PASS：公开文本的发现—报价—保护—提交流程可核；盈利部署身份、实际盈利原账和整套个人实施许可未证。** 先独立读源，未读root后续结论。0网络、0源码/策略/模型/SDK/EVM执行。actual model/effort均UNKNOWN；规则版本沿用PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4。

实际读取UTC、19份实质输入SHA及原请求URL见同名JSON。14份直接来源原件的SHA/bytes/HTTP200与三份读取回执一致。固定仓库是flashbots/simple-arbitrage，commit为03cf1058b5bd8079561e2505efc85f77e357b829；页面currentOid与固定树一致。authored/committed元数据均2021-06-21T18:24:00-04:00，不独立证明首次公开。不可与旧simple-blind-arbitrage的73c6…版本、测试或MIT材料混用。

| 核验层 | 原件定位与结论 |
|---|---|
| 许可 | package第15行声明ISC；BundleExecutor与UniswapFlashQuery第1行均UNLICENSED。已存根树未列独立LICENSE。不能称整套MIT，不能将读取研究等同已获整套个人实施授权。 |
| 机会输入 | UniswappyV2EthPair第48—119行枚举配置的factory/WETH池、按同一token分组并筛储备；index第55—64行按block更新。比较已有跨池价格，不是预测模型。 |
| 数量/价差 | Pair第138—160行含997/1000整数公式；Arbitrage第18—66行有限试量与中点启发式，第117行预测盈余须大于0.001 WETH。这不是全局最优证明；跨候选共享best并可覆盖，也不能描述为严格最优求解。 |
| 合约保护 | BundleExecutor第55—72行：仅executor、顺序call、WETH后余额严格大于前余额加coinbase支付额。coinbase支付先用已有ETH，不够再unwrap。保护合约局部WETH，不是EOA全成本净利；owner另有受限任意call。 |
| 费用和提交 | Arbitrage第137—179行确有估gas和bundle模拟/错误跳过，显式gasPrice=0；gasLimit先100万、估值过140万跳过、通过后设为估值两倍。默认80%是预测盈余的配置分配，非实际分润或ROI；提交下一/下二块不等于已包含成交。 |
| 时代条件 | 已存EIP1559第217—218及246—254行要求legacy gasPrice归一后的maxFee覆盖baseFee。未被改写的gasPrice0不满足正baseFee；依赖库是否改写、当前能否运行均UNKNOWN。当时若实际gasPrice确为0，交易gas费用为0而coinbase另付，不能再扣假想gas形成重复成本。 |
| 身份 | README第17—28行要求自行部署、传入地址；index地址默认空。5EF…在addresses与Query中是查询helper引用，factory/WETH也是依赖，不是已核盈利executor。未有实际盈利执行器/运营者/交易绑定；不是证明从未有人盈利。 |

README第3行明确警告此脚本极不可能盈利，原因是公开竞争与机会已广为人知；这是作者说明，不是实测亏损结果。读取范围也未证明全部依赖和历史执行配置。FAQ既有不可读不重试，不扩查部署/钱包，不把私人bot完整公开作为承认已存在现金事实的额外门槛。

本轮可保留公开跨池报价及合约局部保护作为研究材料；尚不足认定一个真实扣费盈利案例，也不构成当前运行或部署建议。material_errors为空；需保留上述许可、版本、成本与身份UNKNOWN。
