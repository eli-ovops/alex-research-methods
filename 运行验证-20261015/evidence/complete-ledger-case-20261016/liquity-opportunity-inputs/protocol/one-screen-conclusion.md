# 一屏结论：公开接口够形成机会输入，未证明时效

**足够。** 在同一确定区块状态下，审计版本abe7cbf…提供枚举全部未关闭仓位、读取完整债务/抵押、状态、价格来源、门槛及稳定池数据的公开路径；不必依赖私人索引才能定义这些输入。本次仅源码静态核验，未发链请求、eth_call或运行策略。

| 最小输入 | 官方公开路线/关键限制 |
|---|---|
| 分支与仓位ID | CollateralRegistry确定token/TM；TM getTroveIdsCount + getTroveFromTroveIdsArray。同区块分页，数组会swap-and-pop重排。 |
| status及全额债务/抵押 | getTroveStatus + getLatestTroveData。需active或zombie；含利息、再分配与批管理费，不能只取raw debt/coll。 |
| 清算门槛与价格 | 对应AddressesRegistry.MCR、协议PriceFeed与getCurrentICR；严格ICR<MCR。price参数不自行验证，真正执行会重新fetchPrice。 |
| SP及执行约束 | getTotalBoldDeposits减保留1BOLD；批内逐次扣减。最后一个仓位不可清算，整批无债务减少会失败。 |

**利率排序≠风险排序。** SortedTroves/MTG按年利率遍历；MTG不返回status/MCR/价格/SP，且排序表可漏zombie。它是批量数据读取工具，不是已验证风险排行。

**官方LiquidateTrove示例是测试价格演示。** 会setPrice制造可清算条件再恢复；不能当主网发现器/公开bot，更不能运行它来声称找到了真实机会。

已确认静态输入的公开可得结构；没有确认RPC可得性/成本、实际刷新速度、抢先执行或盈利。本结论不改变已核七次历史正净账。6/6新增小源码读取，0安装/模型/回测/EVM/策略/账户/交易/凭证读取/外发；actual model/effort UNKNOWN。

原件、逐请求UTC/hash、字段清单与详细执行差异：receipts.json、source-reuse-and-integrity.json、minimal-public-field-map.json、static-source-findings.md。固定GitHub路径均以abe7cbfbd465fba3812282c51773455766a70e96为ref。
