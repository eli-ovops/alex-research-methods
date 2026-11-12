# dRPC 全集预检：实际原件独立验收

结论：`PASS_CURRENT_BOUNDED_FULL_CENSUS_TECHNICAL_PREFLIGHT_ONLY`，`must_fix=[]`。这一次已发生的有界技术预检有实际原件支持，完成后退出；没有 ARMED、没有正式 A 观察样本，更没有 14 日覆盖、个人全成本优势或容量认定。本单元没有必须再取的缺失字段，不需为同一预检重复取数。

审阅于 2026-10-20 UTC，开始 13:37:32。仅读取冻结静态包、实际结果/执行回执/归档；用 stdlib 解 gzip/JSON，以及冻结 core 的原件还原和 ABI 解码辅助函数读取原始字节，未运行 preflight、Scanner、qualify、forecast、评分、测试或策略。未联网、读秘密/Terminal/私人行情/QC、改 live 原件或停止进程。本次保守 CPU 预算借记 10 秒由 Root 将 future guard 7365→7375，非实际 CPU，旧用量不清零。actual model/effort/route `UNKNOWN`；原三版规则不变。

## 原件实读，而非照抄 PASS

归档 SHA 及 48 个拼接 gzip 成员完整解析，逐个不可变成员范围/哈希可读。20 个 HTTP 响应（chainId1、header5、getCode5、eth_call9）均还原其 body；含 delta 的响应逐级还原并核 body 字节长度/SHA、JSON-RPC id/result、HTTP200/error-null。两条 WS 请求单列，因此方法新增 22、累计 93，而不是将重复保存的 stream before/after 两份证据重复计费。

1. **身份与 runtime。** 原始 chainId=0x1；初始 B=`0x1904d06`，H=`0x86914932df8f89b51ba109e7a8427e5fd26996b1c73949258e3c133136cca745`。五个 getCode 请求均带同一 EIP-1898 `{blockHash:H,requireCanonical:true}`；实际解码 runtime 与冻结、绑定 chain1/address 的源记录逐字相同：TM23779B、registry3326B、SP8198B、feed1629B、MC3 3808B。不是只比结果报告的布尔标记。此层仅覆盖初始 H，不能说后四个扫描 H 都另取了五份 code。
2. **独立提供者背景。** 实读 BlockCypher 两原始 HTTP200 JSON：chainroot `ETH.main` 的 height/hash 与固定 B/H 一致；固定块对象的 chain/height/hash 也一致，Block.time=`2026-10-20T13:32:35Z` 与 dRPC header.timestamp 对应。chainroot.time=`13:32:39.574043221Z` 是 root 更新字段，不冒充建块时间。两个 GET 的本机起止 UTC/monotonic 和不同来源对象保留，只是有限交叉核对，不证明独立后端、canonical 最终性或 14 日持续独立时效。
3. **真实订阅与六个连续头。** 原件有101 Upgrade、正确订阅 ACK、6 个通知和 unsubscribe true ACK，正常结束。通知块高依次 `0x1904d07` 到 `0x1904d0c`，逐一 parentHash 对前一 hash、块高+1、无重复；第三头作 initial，后三头作 measured。8 次 receive 结算为 ACK+6head+unsubscribe，已知帧字节与336B Upgrade合计11505；没有因保存两份 stream 证据二扣。源计数含 Upgrade，不能当纯通知负载。工程接收计量不等 dRPC 实际账单。
4. **四次完整 census。** 四个 H（`17b354…e7e9 / 41af16…5f54 / 15a62e…cce2 / a18b13…e058`）分别机械解请求和响应：initial 一个 count，再169个 base/ID子调用；其余头169个 base/ID子调用。每次 N105/P160，105个唯一 ID 成功，55个 past-count 槽失败，顺序与 compact snapshot ID 逐一相同。每次95个 status1 active、10个 status4 zombie，均在全集内。
5. **债务/抵押/利息与 oracle/SP。** 每次212个 detail 子调用的目标、selector及 ID 参数全部逐一核对：105组 status+LatestTroveData，各最新 tuple 恰10个 uint256，420组 tuple 都保存在可无损还原的 RPC 原件，没有把 compact snapshot 删去 latest 当成源字段遗失。核 base count/shutdown/MCR、registry feed/SP与TM SP地址、mode/lastGood/ethUsdOracle 三字段，与 snapshot 中原量相同；末两项确为 SP deposits 和 fetchPrice，fetchPrice 是最后子调用，四次 mode0、新失败=false、返回协议价正值。它是同 H 非持久 eth_call 的结果，不是市场可成交价，也未在此审阅重做金融资格/收益计算。每次 fence 的请求 B 和返回 number/hash 与该 H 一致；所有原始 response artifact 的范围哈希闭合。

## 时序和资源

四次原件 receive→formed 分别约3.6353、1.4339、1.3418、4.1723秒；包括后续证据处理后的三 measured 处理字段为1.43524、1.34290、4.17478秒，均低于原12秒守卫。formed 时按本机 UTC 对块时间的年龄约5.413、3.335、3.446、8.031秒，符合30秒/未来2秒规则。通知应用层读时刻不能当网卡到达、供应商产生时刻或已赢竞价；本机时钟误差界仍 UNKNOWN。backlog 检查通过由冻结代码成功控制流支持，没有独立 socket/NIC 逐时遥测。

**4.17秒是完整 scan+本地处理间隔，不能与服务文档 backend2秒当成同一度量。** 原件九次 aggregate HTTP 应用起止间隔约0.425–1.694秒，同样包含网络/连接/传输，不是独立后台执行耗时，也不形成SLA或后续稳定性结论。

工程量从旧 shadow32945/方法71 到33850/93；历史 Alchemy32734保持原值，dRPC 实际 CU/月余额仍 UNKNOWN。8次接收 ceil(wire delta/25) 影子结算及20个 HTTP方法+subscribe/unsubscribe的工程借记可由原件核回，无 fallback 触发，不与官方文档每通知20CU混账。

按已冻结 forecast 的工程公式，直接核对原始三cycle字段和结果分项，未调用预测函数或建立新模型：

| 项目 | 本次条件投影（含对应旧量/储备） | 原帽 |
|---|---:|---:|
| 工程等效 CU | 15,186,755（未来15,152,905+当前33,850） | 25,000,000 |
| 方法 | 305,501（未来305,408+当前93） | 400,000 |
| 物理盘口径 | 7,023,411,200 B | 8,588,886,016 B（8GiB−1MiB） |
| CPU保守预算口径 | 13,520.668605 s | 18,000 s |

盘余量1,565,474,816B、CPU余量约4479.331395秒，是此条件投影的余量，不能说未来实耗已知。公式保留100800块/12秒约定、至 T0 等待3131头、每100块日志、1000条detail/192MiB/120CPU秒储备，当前 already_disk=10,862,592B不清零。initial额外count不冒稳态成本；三周期方法均3，CU147/147/145，完整周期从接收前至扫描/证据保存后量。磁盘周期增量65536/65536/0B是物理分配观测最大值，不是理论必需压缩量；0也不等于没有新数据。已用空间、未来观察、T0前等待和审计储备对应不同部分，未见同一费用重复计入或删除等待层。

per-cycle CPU/历史物理分配是程序当时 OS 计量字段，原始 archive 无独立逐次 kernel 轨迹，不能从事后 stat 完全重建每次分配；本审只核其计量位置、已保存字段及公式一致。当前归档实际285210B、stat物理307200B，不能拿当前归档大小替代累计项目盘或未来投影。

外层回执 exit0、outer_stop=null，整命令77.383855125秒，目标内部77.121854875秒；实际单PID/once原件一致。采样峰RSS78,217,216B低于128MiB目标，本单终态目录720896B低于6MiB。wrapper CPU1.111585 + reaped children/monitor2.437162 =3.548747秒，与目标process CPU0.365569、route child0.004313属于不同覆盖层，不能全部相加重复借记。264次采样不保证短命子进程/瞬时RSS绝无漏采；不冒充集体kernel硬帽。Root当前单元预留和7375未来guard另属预算借记，不冒实际 CPU。表内13520.668605是当次以7365为prior的历史投影；后续若承接新7375预算，须保留新增本审10秒（对应13530.668605，仍低于18000），不能改写旧原件或漏掉此借记。

## 验收边界与下一层

终态 gzip 成员与 result 的状态/四snapshot/资源/工程累计逐项相同，必要 terminal 归档已成功，旧MF2未重现。once 保存 PRECHECK_ONLY_NO_ARM，程序已正常退出，ARMED=false、A_observation_started=false；这次并无正式观察样本。

在本次有界技术层可以接受：匿名HTTP/WS数据通道、同H完整状态读取、原全集/时序门及本次资源条件投影通过。没有必须补件阻碍这个有限结论。若接续原A，尚需将同样已验数据接口/工程分层接入唯一正式观察入口并保持既有发布、持续预算、覆盖与退出门；不能把本候选直接叫已运行14日，也不需要为了保证未来无故障重复本次取数。原T0=`2026-10-21T00:00:00Z`、T1=`2026-11-04T00:00:00Z`未变。增长、服务限流/断链、储备耗尽、缺块或时效失败仍按原规则停 UNKNOWN，不能靠漏采/重置/换价保持PASS。

完整个人净利、真实获胜/失败收费、实际劳动成本、容量与财富目标仍未达；这次技术进展不能抹旧正账，也不能替代那些经济证据。

## 精确输入

| 本候选目录相对路径 | 字节 | SHA256 |
|---|---:|---|
| `result.json` | 11694 | `e8c21ac01a5de4bdf48d219ee6047bebf13761cd20c865b1cfcd552be17c32cb` |
| `execution-receipt.json` | 2059 | `735c664aeee454857354863d04fe0adbbff229f325552eab150aef7ffcb20010` |
| `evidence/1792503158152626000-records-1.json.gz` | 285210 | `c0dd6218469f4e3478bdd7cd18bf886b6090dc3fd7d6e1e43d9e03d692f55fff` |
| `preflight.once` | 89 | `0b945a31b235503326eb9434a607301978b355c5af7ccb90c165738fe8e1e3c0` |
| `manifest-v2.json` | 16824 | `1026182372831c2ca748000545813f5105598f281be40de1d2df45869dc7fbff` |
| `preflight.py` | 19154 | `d39dde2562da777e8940e40f7d4ca515ef46a891650a009db1102e353c150f9b` |
| `adapters.py` | 14837 | `406067e55de219a38d8afc156a2ac82a5d754ec8ceb16f59cab765bb3f033385` |
| `config.json` | 2649 | `e12c20417b50dc07118248d49c46a9678e7cbdd34963749cb67bda894c58cdf2` |

辅助输入仅当前 manifest 已绑 frozen core/collector、binding及其指定 source/runtime；它们用于原件反解与语义对照，不是重新通读全部依赖或 runtime 审计。只写本新审阅文件，未修改任何获取结果或旧审阅。
