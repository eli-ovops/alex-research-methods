# LP事前费用/风险研究查重：LVR已读，事前预测验证尚未定位

仅项目内既有Markdown定向检索和一份已封原论文HTML的局部实读；零网络、零金额运算。**旧LVR不是一个新的未读论文候选。最有决策价值的补充是原文明确区分事前与事后波动率：事前潜在LP分析应使用隐含波动率；已做实证使用事后实现波动率。这不等于已验证能事前挑出费用覆盖风险的机会。**

## 已做原始材料及边界

1. **Milionis、Moallemi、Roughgarden、Zhang，Automated Market Making and Loss-Versus-Rebalancing，arXiv2208.06046v6。** 旧报告`运行验证-20261015/公开做市为什么还不等于定价优势-20261016.md`已明确读取第3/7/8节及附录C。实际已封原文：`evidence/inventory-edge-mechanism-20261016/root/LVR-v6.original.html`，815039字节，SHA256 `e3c0eab1ae9f236d09d36b47608b30dfa0b42ecc[REDACTED_PHONE]ac78cc451a286`；相邻`normal-primary-read-receipts.json`记载2026-10-16实际HTTP200来源为`https://arxiv.org/html/2208.06046v6`。本轮已核此单文件hash并直接读模型假设、实证/数据口径、事前输入脚注及书目；不是只凭导航自述，也不是全论文新审或运行论文查询。
   - §3脚注6：事前潜在LP分析选隐含波动率；事后表现分析选历史/实现波动率。
   - §3.1：流动性与费用过程作为输入，不在文中建立能预测它们的完整均衡/信号模型；理论简化包括无限深CEX、忽略gas、套利者免CEX/DEX交易费及离散区块摩擦。
   - §7及附录C：样本2021-08-01至2022-07-31、Uniswap V2 WETH-USDC，Binance价格和Dune链上记录。LVR测量使用当日实现波动率；这属于事后风险分解及度量验证，不是交易前冻结信号、后续独立测试与个人全成本实盘验证。
   - fees−LVR相对动态再平衡基准，不等于hold差；数学上的predictable过程也不等于有可交易的样本外预测准确率。不能追改既有历史正账，不能在实际净额上再扣一次LVR。

2. **动态费实现已有覆盖，不能当动态费论文或盈利验证。** `BunniV2-链上触发与未修复风险核验-20261016.md`已审固定commit `2b303b8c1b9f8afbb169d62ba52da93d6d2171fe` 的动态费/hooklet/am-AMM管理者费用分支、权限及外部履约。它不是“事前预测费用相对库存风险”的实证论文。该版本因维护者未修复事故警告已关闭原样生产复用；本轮只读旧报告，不重审源码、重开收益或恢复候选。

3. 上轮`evidence/v2-real-positive-case-mechanism-reassessment-20261020/candidate-owner/reassessment.md`区分已核正数量、固定日毛费用/份额权重与尚无持续优势/容量证据。**本轮不重新立项799天分解、1379Swap或个人份额计算，也不把私人择时缺失升级成一切会计/收费机制研究的门槛。**

## 未做但已定位的原件：目前仅书目线索

以下均来自上述已封LVR原论文References；针对其ID/标题的既有Markdown检索未定位正文实读报告。本轮未获取或读取其正文，不能声称免费完整可得、事前验证通过或盈利。

| 确定原件身份 | 已定位程度与尚不能判断的内容 |
|---|---|
| Milionis/Moallemi/Roughgarden，Automated Market Making and Arbitrage Profits in the Presence of Fees，2023，arXiv2305.14604 | 有确定arXiv ID；旧LVR明确将费用摩擦进一步分析留给此文。尚未读其假设、数据/验证或个人执行成本边界。 |
| Adams/Moallemi/Reynolds/Robinson，am-AMM: An Auction-Managed Automated Market Maker，2024，arXiv2403.03367 | 有确定arXiv ID；LVR§10将其关联到套利权拍卖及向LP重分配。未读论文，不能等同已验证动态费预测/可部署或净赚钱。 |
| Cartea/Drissi/Monga，Decentralised Finance and Automated Market Making: Predictable Loss and Optimal Liquidity Provision，2022，SSRN4273989 | 有确定SSRN ID；其最优流动性/预测损失设定、信号可得性与证据类型未知。 |
| 同作者，Predictable Losses of Liquidity Provision in Constant Function Markets and Concentrated Liquidity Markets，Applied Mathematical Finance30(2):69–93，2023 | 有完整作者/刊物/卷期页；未定位既有实读正文或免费正文入口，不杜撰DOI或性能结论。 |

参考文献另有Cata Labs动态费博客及动态曲线论文；博客不冒充学术原论文，动态曲线不自动等于动态手续费。既有Bunni分支也不能替代上述论文实读。此处不自行决定新取数优先级、不联网。

## 重开风险与本轮收口

- 将旧LVR重新当新发现，或把事后实现波动率/统计分解叫作事前可用预测，都会高估进展。相反，旧文脚注提供了尚需检验的事前输入方向，并未证明它可免费获取、足够准确或能覆盖全部成本。
- 只有新原论文能实质回答公开信息时序、预测对象、费用/库存/套利风险、验证类型与摩擦，才可能改变下一步；仅书目、理论最优或回顾性正残差不足以放行模型/回测/交易。
- 本轮未定位一份**已经实读并完成事前信号及后续全成本验证**的LP费用/库存风险预测或动态费论文记录。结论限本次定向归档覆盖，不声称全球不存在或所有历史文件都没有。

Root要求后已停止扩展查重。实际读取/检索边界见`coverage.json`；执行回执见`receipt.json`。无新金额、源码执行、模型、实验、账户或交易，既有正账/FAILED和KMLM拒绝保持原状。
