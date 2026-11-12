# Aave V3供给利息：官方文档与核账边界

结论：可保留作公开利息现金流基准，尚无真实收益通过结论；不替代预测alpha、XTX策略或财富目标。只读3/3官方页面，无账户、APY或收益选择，无源码/模型/回测/EVM/交易执行。实际model/effort UNKNOWN，规则版本沿用。实际UTC与输入hash见同名JSON。

| 官方页/精确位置 | 可核事实与范围 |
|---|---|
| [Liquidity Pool](https://aave.com/docs/aave-v3/concepts/liquidity-pool) L170–181 | 供给者提供可借资金并赚利息；借款者抵押借款。供给率随利用率、治理参数及操作变化。提款含本金和利息，但受未借出流动性及有债账户抵押要求约束。不是固定回报或无条件即时赎回。 |
| [Pool](https://aave.com/docs/aave-v3/smart-contracts/pool?language=en) L188、207–262 | Pool为市场proxy入口；supply转底层币并铸aToken给onBehalfOf，需底层授权；withdraw燃烧aToken返底层币，max可请求全部余额；不能使health factor低于1。amount是底层币最小单位，不能将USDC数值套18位ETH。 |
| [Tokenization](https://aave.com/docs/aave-v3/smart-contracts/tokenization) L174–179、201–249、356 | 普通aToken可转让，balanceOf含本金及累计收益；mint/burn关联liquidity index。burn时也可能发Mint事件，另有Treasury铸币、清算转移；不能将每次Mint或余额增长直接归个人存款/利息。 |

## 真正需要原账补齐什么

- 提款包括本金，不是全额收入。需先固定账户、市场及账期，核底层资金进出、aToken转入/转出/清算、残余头寸；不能仅用两次余额相减而遗漏第三方转入。Pool文档的onBehalfOf说明不是原受益人永久独占权，aToken可流转，核当前持有人链条。
- 三页已返回文本未给完整reserve-factor分配公式和实际历史值。谁从借款利息中扣何比例，待root冻结rate源码/参数核验；不把借款人利息全部归供给者，也不把当前页面当2026Q3参数快照。
- 实际授权、供给、提款、失败gas及换币成本须另读原账。展示供给率/APY不是已收到金额，更不是扣费净收益。文档中的100USDC是示意，不是真实盈利案例。
- 本轮只支持流动性限制、动态利率及借款抵押/清算边界；未完成合约、预言机、USDC脱锚/发行人或系统风险审计，不宣称低风险。普通AToken不能混用同页RwaAToken权限或StataToken包装器规则。

## 来源限制

批次起始UTC2026-10-16 08:36:01（前两页）、08:36:11（tokenization）；页面发表/更新日期、首次公开时间、逐页完成UTC、HTTP及原网络bytes UNKNOWN。保存的是官方网页原生工具抽取，不冒充原HTTP HTML或独立链上状态。两份原生响应及SHA256记录在同名JSON。本阶段不查询具体部署、盈利账户或收益榜；下一步由root按事前范围核具体版本和真实账。
