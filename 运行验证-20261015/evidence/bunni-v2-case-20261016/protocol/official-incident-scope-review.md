# Bunni V2官方事故与版本风险：只读核验

结论：保留为机制研究反例，不能将未修复源码作为可生产复用或已核盈利案例。本轮仅1个官方页面读取；无PoC/gist/交易链接读取，无复现、模型、回测或EVM执行。实际model/effort UNKNOWN；规则版本沿用。

| 官方来源及位置 | 支持结论 | 限制 |
|---|---|---|
| [事后报告](https://blog.bunni.xyz/posts/exploit-post-mortem/) L3、17 | 署期2025-09-04；称9月2日两池合计被盗约840万美元：Unichain weETH/ETH及Ethereum USDC/USDT。 | 官方近似数，非独立净损失账；精确损失、回收及估值时间UNKNOWN。 |
| 同文L26、39 | 约133万USDC加100万USDT属Ethereum示例的归还闪贷后余款。 | 非两链总额；不能与840万美元混算，未核全部费用。 |
| 同文L42、113–122 | 作者称事故非调仓/移位引发；文中只恢复提款，仍探索修复与测试。 | 是署期自述，非2026当前状态或安全审计；不证明调仓逻辑安全。 |
| [冻结README](https://github.com/Bunniapp/bunni-v2/blob/2b303b8c1b9f8afbb169d62ba52da93d6d2171fe/README.md) 首段 | 明示问题“not addressed”，警告“do not use this code in production as is”。 | 仅这个固定repo状态；未断言所有后继版本均未修复。 |

精确受影响部署版本/字节码未在本轮文档中绑定，UNKNOWN。文章给出的拟议修改不等于完整修复已部署；不另做攻击或安全审计，不追逐收益。

原生抽取保存在official-post-mortem-native-response.json，SHA256 288acd748d731e0b6828173e0a9ad3f36326db89be125c5b870bb456260ac486。批次开始UTC2026-10-16 08:27:17；逐页完成UTC、HTTP状态和原网络bytes UNKNOWN，工具抽取不是原HTML。输入hash、精确位置及固定ref来源边界见同名JSON；未改root或旧证据。
