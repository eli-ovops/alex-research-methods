# 官方Liquity V2 subgraph能否提供完整清算原账

结论：本轮没有取得现成Liquidation原始事件数据包。已读官方subgraph是MIT许可的仓位状态索引实现；其schema没有完整Liquidation事件实体，不能据此称已经持有逐条补偿账。README只说明本地部署，不提供完整原账下载或公开查询入口。本轮未发送GraphQL、RPC或其他数据采集请求。

## 固定来源和读取范围

复用已有官方`liquity/bold`递归tree（未截断，root tree SHA `d262669ef3c4d37bf0544df3bb2624c07b8a5ee0`）定位路径。旧manifest记录的`cc2a420067e47cafc1b1b1309045b341f9ced1b1`仅为历史标签，不能证明本次tree/blob属于该commit。本轮没有独立绑定commit，故四份内容的所属commit为UNKNOWN。权威标识仅为以下本次真实GET的不可变Git blob API URL与blob SHA；结论仅适用于这些已读内容，不代表当前生产subgraph或其覆盖：

- [subgraph/schema.graphql](https://api.github.com/repos/liquity/bold/git/blobs/048b20ff3af8748e1ee4e6def46b85bc83802766)：blob `048b20ff3af8748e1ee4e6def46b85bc83802766`，3137B。
- [subgraph/src/TroveManager.mapping.ts](https://api.github.com/repos/liquity/bold/git/blobs/4bb2ba2f87a27e94e14ce89b7d1fc22e69f622e6)：blob `4bb2ba2f87a27e94e14ce89b7d1fc22e69f622e6`，11339B。
- [subgraph/LICENSE](https://api.github.com/repos/liquity/bold/git/blobs/8e0b7f2ba064f4c4401c67344df28d6bd9a3e350)：blob `8e0b7f2ba064f4c4401c67344df28d6bd9a3e350`，1067B，MIT，2025 Liquity AG。
- [subgraph/README.md](https://api.github.com/repos/liquity/bold/git/blobs/617db9d8d26a98f368fed259a1dcd22332acbd54)：blob `617db9d8d26a98f368fed259a1dcd22332acbd54`，882B；作为本轮唯一官方说明页。

上面真实GET的Git blob API URL及blob SHA用于标识已读内容；每次读取UTC、SHA256和历史标签均保存在`source-receipts.json`。旧回执中的`fixed_commit_url`与`commit_ref_scope`保留为原历史表述，由新增`provenance_clarification`明确降级，不作为已验证关联。新增3份源码/许可GET和1份说明页GET；未扩大检索到其他仓库或部署页面。

## 字段事实表

| 所需字段 | 已读schema/映射是否持久保存 | 精确边界 |
|---|---|---|
| 清算目标Trove ID/分支 | 有状态关联 | schema38—61行，id为collIndex:troveId；collateral关联含token/TM等地址字段（9—19行）。这不是逐事件唯一键。 |
| 清算状态、抵押与债务变化 | 有 | mapping211—217行将状态设liquidated，并存liquidatedColl、liquidatedDebt、collSurplus、priceAtLiquidation；字段来自TroveOperation及同交易其他日志，不是完整Liquidation原量清单。 |
| 清算时间 | 有区块timestamp写入closedAt | mapping179—190行；不是发现/发送时间。Trove为mutable entity，保存状态不是全操作版本账。 |
| txhash、logIndex、blockNumber | schema没有这些原账字段 | mapping处理Graph事件/receipt时可接触部分交易和日志元数据（如BatchUpdated辅助构造），但未将这些值持久存成可导出的清算事件记录。 |
| 固定0.0375 WETH补偿原量 | 无 | 没有对应schema字段；mapping不保存Liquidation第3字段。协议可产生该原量，不等于此subgraph保存它。 |
| 可变抵押币补偿原量 | 无 | mapping不保存Liquidation第4字段；liquidatedColl不等于collGasCompensation。 |
| 清算者/收款人 | 无 | Trove.borrower是借款人，不能当清算者。 |
| gasUsed、effectiveGasPrice、失败费 | 无 | schema没有这些字段，不能核执行者费用、失败尝试或净利。 |
| Liquidation原事件完整保存 | 无 | schema全文没有Liquidation事件entity；mapping79—103行仅在TroveOperation receipt中寻找后续Liquidation topic，解码data的第9索引取价格。 |

mapping31—34行给出的原事件topic为`0x7243af9a1cff94d3429b2ee00b78c1c10589259f20dc167cb67704f38f9e824e`，注释对应10个uint256的Liquidation签名。该topic可辨认事件类别，不能据此声称本轮已取到任何事件清单或证明查询结果完整。

## 数据包、访问、许可与完整性

- README只有本地anvil、合约部署、graph node和subgraph部署说明，以及生成地址的说明。文中没有公开数据包、CSV/Parquet、现成Liquidation账或匿名生产读取URL；本轮没有执行其中命令，也没有读取网络/config文件或寻找私有端点。
- 已存未截断tree里没有`.csv/.parquet/.jsonl/.zip/.tar.gz`路径。这只是固定tree内按这些扩展名的有限检查，不涵盖GitHub Releases、外部托管、无扩展名文件或未来版本，不能断言官方任何地方都不存在数据包。
- MIT许可明确适用于该subgraph软件及随附文档，可在保留声明等条件下个人研究复制。没有取得已发布数据包，故其单独数据许可、数据再分发条件为UNKNOWN；不将MIT自动扩展成所有外部服务条款许可。
- 生产索引部署地址、无需key可读性、开始区块、覆盖哪轮部署/哪些TM、同步截止块、索引错误与重组处理、导出行数和完整性均UNKNOWN。源码能实现某些索引，不等于已运行、已同步或已取数。

本轮最小结果是定位了一个**不保存所需完整原账字段**的官方状态subgraph。要补齐原始补偿账，仍需一个公开已发布的逐日志导出或索引实体，明确网络/部署/TM覆盖、区块范围、txhash+logIndex、区块时间、两个补偿原量及抵押币身份；若要净利润，还需真实收款、成功/失败交易费用。当前不以写采集器或执行查询替代现成原件，也不重复根的Dune分支。

实际model/effort UNKNOWN，继承路由未覆盖；规则PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4。仅公开GET和静态阅读，无模型、回测、EVM/RPC、策略、交易、安装、账户、付款或外发；没有修改其他Owner目录。

## 来源澄清（本地追加，0联网）

原稿将旧manifest的commit标签连接到本次tree里的四个blob，这一关联未独立证实，已更正。当前只证明实际GET到指定blob内容及其完整性；不证明它们属于上述历史commit、不提供首次公开时点，也不证明当前生产部署采用同版本。字段分析对已读schema/mapping成立；生产版本、起止区块及覆盖继续UNKNOWN。源文件、API原件、UTC与hash不变。
