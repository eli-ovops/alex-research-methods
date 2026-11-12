# Alchemy Ethereum固定区块与订阅：文档准入，未实测

2026-10-19 UTC。使用agent-reach已验证的web__run路径；不复测Exa旧Unknown，不访问RPC endpoint。**官方文档支持按确定区块标识设计小规模只读验证；尚未认证EIP-1898 canonical对象、多请求快照一致性、订阅无损补历史或运行性能。** 免费额度、key/卡与条款由pricing-owner独占核查，本报告不重复准入它们。

## 已读提供者声明

| 对象与原链接 | 本次可支持的事实 | 精确覆盖/限制 |
|---|---|---|
| [Ethereum eth_call](https://www.alchemy.com/docs/chains/ethereum/ethereum-api-endpoints/eth-call) | Block可选，默认latest；列number、latest/safe/finalized标签和32-byte hash。 | 正文提取L99–107。可读schema为string/enum；没有展示EIP-1898的blockHash/requireCanonical对象，不能从支持hash推成对象及canonical校验已支持。 |
| [newHeads](https://www.alchemy.com/docs/reference/newheads) | 官方搜索正文称新头含重组，新链头可造成同高度多条通知；timestamp为区块时间字段。 | 仅官方页搜索提取，未另开正文；它不是本机接收时间、确认深度或最终性/低延迟认证。 |
| [logs](https://www.alchemy.com/docs/reference/logs) | 新块匹配日志可按address/topics过滤；重组旧链日志可removed:true，新链重发，同一tx可多见。 | 正文L93–115；不能只按txhash去重或把收到一次认作最终确定。没有读到断线补历史保证。 |
| [WebSocket最佳实践](https://www.alchemy.com/docs/reference/best-practices-for-using-websockets-in-web3) | 列newHeads/logs及pending/mined等订阅；提示静默失败，建议普通JSON-RPC用HTTP，订阅范围要窄。 | 正文L119–152、187–214。没有提供此次连接捕获率、重连补漏或延迟SLA实测。示例未运行。 |

另在搜索中见官方[订阅入口](https://www.alchemy.com/docs/reference/subscription-api-endpoints)，只用于确认方法导航；其他链/Solana结果未混作Ethereum支持证据。方法页里的“200 Success”是文档响应示例，不是本轮请求或RPC运行成功。

## 固定最新确定区块：最小方案依据与未验项

以下是**拟议核验逻辑**，不是已开发、已运行或由文档保证的能力：先确定一个目标区块的number/hash及链身份，再对所有只读值显式使用同一固定标识，保存每次请求/结果与错误；不让多个默认latest调用各自跟随移动链头。若只用number，重组可能使同号不再指同一hash，须核前后身份；若采用hash/canonical对象，其确切参数和提供者行为仍需相应原件或未来单次验证。不能用同一WebSocket或batch自行推定多读原子快照。

当前文档列safe/finalized，可作为未来“最新确定”选点的待核接口依据；本轮未读取这些标签的提供者正式定义/保证、eth_getBlockByNumber完整参数或EIP-1898对象支持声明。**不扩成多年archive，也不以archive完整性作为当前小验证前提。**

订阅若以后单独获准，只应作为新事件提示：记录区块标识、parentHash、日志身份/removed以及本地接收时刻；区块timestamp和接收延迟分开。对重组、重复和断线缺口必须有明确检测、回滚/去重与有界历史补漏设计。这里的历史补漏是方案需求，**不是已核Alchemy自动回放承诺**；本轮未调用getLogs或subscribe，也未执行第三方示例JS。

## 本轮不能授予的结论

- `EIP1898_object_requireCanonical_support=UNKNOWN`；官方当前提取未明示，不等于已证不支持。
- `multi_call_fixed_state_consistency / automatic_backfill / no_loss / latency / current_runtime=NOT_TESTED`；不能因WebSocket减少轮询就宣称更快或不漏。
- 无实际RPC、合约状态读取、注册/key访问、模型、金融运算、交易或开发。官方声明只是未来可审方案的依据，不认证清算机会捕获、净利润、容量或财富目标。

## 来源封存层级与预算

共5动作：两条官方限定搜索，三次官方文档URL打开；没有再请求、显式重定向、拒绝对象或工具切换。所有动作时间范围、URL、原工具输出hash及字节见manifest.json/receipt.json。

**保存的是web工具原返回（搜索摘录/网页正文提取），不是服务器HTTP body。** 工具未给实际HTTP状态、HTTP原字节或传输大小，因此这些均UNKNOWN、没有可声称的HTTP raw SHA；文档源码总体大小和传输上限也未独立测量。已保存工具输出均低于单件1MiB、合计3MiB保留上限，但不以此冒充HTTP原体大小合规认证。无公开页正文/标题可读错误发生；预算用尽后停止。实际model/effort/CPU/RSS=UNKNOWN。
