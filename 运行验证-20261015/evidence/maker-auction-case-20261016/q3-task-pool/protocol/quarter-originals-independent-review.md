# Q3原件独立审阅：限定返回范围PASS

审阅UTC：2026-10-16T06:51:21.827115+00:00；实际model/effort UNKNOWN。规则PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4。0联网，仅被动JSON/ABI/hex/整数/hash核对；无RPC、EVM、模型、回测、策略或交易执行。全部实际输入hash见同名JSON，根文件未改。

**与根quarter-derived.json的主要计数、状态与边界一致，无实质错误。通过的是同提供商、固定三地址Q3返回集合与同registry三键历史重放，不是独立全链无漏、全Maker/Sky覆盖或个人净利。**

## 账期与请求范围

固定scope为Ethereum主网三个指定ETH-A/B/C Clipper，UTC账期为2026-07-01T00:00:00Z（含）至2026-10-01T00:00:00Z（不含）。原月份定位请求均closest=before；原回应及对应块头相符：

| 边界前块 | 高度 | 块头UTC |
|---|---:|---|
| 起点前 | 25433938 | 2026-06-30T23:59:59Z |
| 终点前 | 26093737 | 2026-09-30T23:59:59Z |

实际三地址查询为25433937—26093738，向外各扩一块，按原记录的closest-before解释足以包住季度；精确时间过滤为[1782864000,1790812800)。未另读相邻块头独立证明服务定位最邻近性；不冒称独立节点证明。Chainlog的截止26093737与季度末前块一致。

全部读取回执逐文件核HTTP200、bytes及SHA256，实际JSON亦无API错误。块头number/hash/timestamp与月份定位及根派生值对应。

## 三地址空结果与阳性对照

每地址page1/page2均status=1、message=OK、result=[]，offset1000；实际URL地址、起讫高度、页码正确，无topic过滤，不是拒绝、错误或误筛某个事件。因返回全部事件均空，所读范围内Kick=0、Redo=0，二者内部coin原量毛额均为0 rad。

| 分支 | Q3两页行数 | 块24391979阳性对照Kick id |
|---|---|---|
| ETH-A | 0/0 | 930、931 |
| ETH-B | 0/0 | 105、106 |
| ETH-C | 0/0 | 289 |

阳性五条逐项核地址、Kick topic、四topics形状、四个data word、区块/交易hash、UTC与logIndex；与既存启动批次receipt对应日志逐字段一致。阳性证明这些历史地址/事件查询路径能返回已知记录，不能证明任意季度完全无漏，更不能证明合约已停止。

## Chainlog有序重放

UpdateAddress page1为686条、RemoveAddress为113条，均小于offset1000，各page2成功空。实际请求是官方Chainlog地址、fromBlock0至26093737及此前核准topic0。依据ABI，两事件非anonymous且参数全部NONindexed；从data首word解三键而非topic1。Update正好两个word，地址高12字节零；Remove正好一个word。

逐条核emitter/topic、data长度、有效tx/block hash、区块及时间范围，按blockNumber与全局logIndex排序。去重后仍799条，重复0；同高度hash/时间一致，时间随高度不倒退，全局日志索引不冲突，删除键均有前序登记。Q3时间筛选与高度筛选一致。

三键期初均已有有效目标地址，其最后前置Update同在区块12381609、2021-05-06T15:45:10Z、交易`0x42e122bb5c4addef1bd8c74402178ac982ef813d72c7f846743efd6f8b3cd092`：

| 键 | logIndex | 期初及期末登记值 |
|---|---:|---|
| MCD_CLIP_ETH_A | 93 | 0xc67963a226eddd77b91ad8c421630a1b0adff270 |
| MCD_CLIP_ETH_B | 120 | 0x71eb894330e8a4b96b8d6056962e7f116f50e06f |
| MCD_CLIP_ETH_C | 147 | 0xc2b12567523e3f3cbd9931492b91fe65b240bc47 |

全registry在Q3有18次Update、3次Remove，三目标键均无变化；CHANGELOG键在Q3也无变化。最早所见CHANGELOG登记在区块11023567，指向同一官方地址。

因此不再只靠旧1.14.2静态清单推Q3：**在该registry的所读返回历史内，已补齐三键期初与季度变更衔接，没有观察到三键替换/移除。**旧报告当时UNKNOWN结论保留，本审阅记录新增证据。未据此排除未登记部署、更名键、平行registry或提供商遗漏。

## 质量及经济结论

Chainlog799条中13条transactionIndex为`0x`，五条阳性对照也全部为`0x`；均保留原样，排序不使用该字段、不回填。其他核对字段有效，不意味着同源结果等于独立链上完备证明。

可表述：这三个已官方命名、且在该registry历史中季度未换指的Clipper，Q3指定范围返回事件为零，观察到的启动/重置内部DAI毛补偿为零。不可升级为全部Maker/Sky或所有清算市场零任务；也不能说个人净利为零、未来没有机会，或抹去二月两笔另行核实的历史正现金结果。未增加全实体多年经营账等额外门槛。
