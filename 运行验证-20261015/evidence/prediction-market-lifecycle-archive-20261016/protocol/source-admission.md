# SQD历史数据来源准入

**找到官方声明的具体匿名HTTP路径；实际免费数据能否返回、完整schema与净账能力仍UNKNOWN。** 不称原账准入通过。本轮1普通GET＋1搜索调用（2query）＋4官方页open，共6读取动作/7个细分GET-query-open；没有数据请求、RPC、SQL、SDK、源码、模型、回测、EVM或交易执行。实际model/effort UNKNOWN；PERMISSIONS-2026-10-14-v1与ROUTING-2026-10-13-v4不变。

指定营销页`https://sqd.dev/solutions/prediction-markets/`仅GET一次403即停，没有换身份/工具重读。异常正文未保留，实际bytes/hash及精确请求UTC为UNKNOWN；拒绝后记录UTC为2026-10-16T14:41:53.956671Z。查LOCAL_BLOCKERS后仅搜索独立官方文档，未绕该资源。其后工具读取在14:41:53.956671—14:42:47 UTC内；各请求精确UTC/HTTP传输字节未由工具返回，不伪称原HTTP原件。两份原生工具全文快照及回执SHA/保存字节在同名JSON，抽取字节不是网络字节。

## 四个官方页面及能证明什么

1. [Portal EVM Introduction](https://docs.sqd.dev/en/api/evm/introduction)：已取得L0–216。L157–179给HTTP POST/NDJSON示例：`type="evm"`、`fromBlock/toBlock`、`fields.block.number`、`fields.log.data`、`logs:[{address:[...]}]`。L181–183明确省略不匹配中间块、流可能在toBlock前结束，须从最后header.number+1续读；不能把一次200当整个区间完成。L188–192解释`parentBlockHash`、409回滚和finalized-head头的语义；`/finalized-stream`有官方链接。本轮只读文档，没有执行示例或独立验证最终性。
2. [Portal pricing](https://docs.sqd.dev/en/portal/pricing)：已取得L0–163。L51、L137将Public共享门户与需要key的Testing/付费区分；Public例子无认证。但L34明确计费尚未上线、当前公共限制仍适用，所以L42–50表内约0.1MB/s、约50MB/月、traces included、无SLA是发布计划/声明，不能冒当前实测额度。L139又规定与`sqd.dev/pricing`冲突时以后者为准，该优先页未在预算内读取。
3. [Polygon官方链页](https://sqd.dev/chains/polygon/)：已取得正文至L220。L80/122明确Polygon137及`polygon-mainnet`，L112–140声称genesis到当前的archive/realtime；L154–170列blocks、transactions、logs、traces。L179–212给精确普通HTTP路径`POST https://portal.sqd.dev/datasets/polygon-mainnet/stream`；body有`type:evm, fromBlock, toBlock, fields.block.{number,timestamp}, fields.transaction.{hash,from,to,value}, transactions:[{}]`。这是具体文档路径，尚未取一笔数据验证其匿名可用性。页面的“验证入库”是提供方保证，不是本轮独立全链证明；SDK开源标签不是数据许可。
4. [Accounting官方说明](https://sqd.dev/solutions/accounting/)：open工具只返回标题/原URL/总353行的头部，**未取得正文**。同轮官方搜索索引展示`gasUsed/effectiveGasPrice/status`及trace的`action.value`、`error`与父transaction关联线索；它们可指导下一步精读schema，但本轮不能把索引摘要当完整字段规范或成功数据回执。

## 金额核账所需字段目前到哪层

| 事项 | 此轮证据层 |
|---|---|
| Polygon137、历史logs/transactions/traces路径 | 官方正文有明确声明及HTTP例子；未实读数据 |
| log.data与地址过滤、block号/时间、tx hash/from/to/value | 已读官方例子支持 |
| receipt gasUsed/effectiveGasPrice/status | 仅官方搜索索引线索；完整字段类型/选择器/历史覆盖UNKNOWN |
| 失败交易 | 链页称all transactions；尚未读详细status筛选/失败覆盖，不能从logs补失败费或填0 |
| native/internal flows | 官方称traces；action.value/error仅索引线索，成功父调用/祖先回滚/自毁等完整语义UNKNOWN |
| topics/logIndex/blockHash/完整receipt映射 | 未取得全schema，不能保证字段全部齐备 |
| 版本、区间完整性、最终性 | 需metadata/实际响应绑定；当前网页声明非不可变dataset版本；截流续读与重组规则已明确 |

因此可以提出“先实质精读官方Stream schema，再另行固定小范围正常历史HTTP正对照”的最小问题，但本子任务未执行。此前完整目标、真实利润与全部成本不因此通过。

## 免费、研究与未来交易许可

pricing L48/L56明确Public和Testing不用于商业用途、商业须付费；L51称Public供探索/原型，L56称开发/评估。**没有逐字规定个人只读研究属于禁止商业用途，不能把本次读文档或被动研究硬判不可行；也没有据此确认未来自营交易/交易系统可以免费实施。** 未来用途分类和数据再分发许可均UNKNOWN。不能拿SDK开源或营销“free”替代数据许可/成功读取。

本轮不注册、改认证、付款或取原账，也不要求私人bot作为历史现金准入门槛。预算已收口，无自动追加读取；证据仅支持一个有文档依据但待实际核验的来源路径，不支持“SQD完整账已免费取得”或“SQD全网不可用”。
