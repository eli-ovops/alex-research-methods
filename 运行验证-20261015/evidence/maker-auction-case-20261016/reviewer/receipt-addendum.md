# 新历史receipt补充：当笔原始DAI字节缺口已关闭

结论：**PASS_THIS_RECEIPT_AND_OBSERVED_FLOW_LAYER**。新receipt的四条DAI Transfer原量与旧代币索引逐笔一致，WETH/USDC及Withdrawal亦对齐；当笔原始DAI字节缺口已关闭。观察ETH净增仍为**0.097465192271862691 ETH**。这不等于完整策略/期间费用或运营身份通过。

本补充不覆盖旧review.md/json，旧“当时未取得完整DAI原量”结论保留为历史读取状态；旧坏getLogs原件也未改或回填。所有新检查、字段原量、输入hash和复核UTC见`receipt-addendum.json`。

## 新原件实际通过层

本地复读`target-transaction-receipt.original.json`：21857B，SHA256 `c23cdf8011df60e66fa0e95cea3270cde005ec63cd7a4d2f9b290ea0c46da1f9`，与新回执一致。JSON-RPC result status0x1、目标tx/blockHash/区块/自调用from=to与先前normal原件一致。25条日志各带同tx/blockHash/区块/transactionIndex，logIndex从0x119至0x131连续且无重复，无removed=true。没有据此宣称节点或共识独立验证。

四条DAI日志现在各有完整32bytes data和blockHash：

| logIndex | 方向 | 原量DAI单位（18位显示） |
|---|---|---:|
| 0x121 | 兑换池→callee | 31105.204277208570603330 |
| 0x125 | callee→零地址（Join对应索引流） | 30887.306726180869414834 |
| 0x127 | callee→caller | 217.897551027701188496 |
| 0x12e | caller→后续兑换池 | 217.897551027701188496 |

销售减偿还等于余款，caller DAI收付净0。该等式从本次receipt原字节重算，不再仅靠旧token-index金额；所有相关索引行均唯一匹配同方向、同币、同原量的receipt Transfer。仍是同一Routescan提供者的不同接口/格式，不是独立第二来源。

三条WETH Transfer、两条USDC Transfer与先前完整getLogs逐字段集合一致。WETH callee入/出各15724131581065069254原量相抵；caller收到109938735732142791原量，随后唯一Withdrawal同量、同src，与原ABI和已记录native入款一致。两条USDC为同笔中间路径流，不给caller额外计收入。合计9条上述币种Transfer，不能把中间资产往返叠加为多份利润。

receipt实际gasUsed=536332、effectiveGasPrice=2643941791wei，乘积1418030588650612wei，与旧normal所载gas字段一致。仍按已记录native流量计算：

`109938735732142791 − 11055512871629488 − 1418030588650612 = 97465192271862691 wei`。

1019wei自转未计本金；外付地址角色仍UNKNOWN，未叫builder；WETH ERC20入款与解包ETH不双计。receipt本身不含完整native内转清单，这两笔native流仍由先前internal索引及Withdrawal交叉对应支持；未新增状态余额证明。

## 仍未通过/UNKNOWN的层

- 旧raw getLogs四条DAI仍缺data/blockHash，与receipt只在地址/topics/logIndex对应；其质量问题没被修复或抹去。不能把新receipt说成旧API原件已完整。
- 同一提供者完整receipt改善本笔可复核性，但Etherscan403原件仍不存在；没有独立服务、独立节点或归档完整性证明。
- 只有这笔成功交易的receipt与观察流量，没有预定完整账期、其他失败尝试/全部费用、关联授权/部署/运营成本、未来复制收益或容量证明。
- 私有外层完整语义、实际运营者、所用Sidestream bot/参数与历史版本绑定仍UNKNOWN；公开callee、minProfit=1及早于交易的release线索不自动完成这种绑定。没有新编译或部署字节码验证。

## 读取行为的准确记录

本审阅新增联网0次，只读本地保存JSON。父任务新原件的实际来源为已发生交易的`module=proxy&action=eth_getTransactionReceipt`公开只读HTTP GET；回执已明确记录**1次RPC格式历史receipt读取**。这不是eth_call、estimateGas、模拟、trace执行、签名、广播或交易。不能把整个研究追溯改称“0 RPC格式读取”；也不改变此前本审阅确实仅本地静态、0联网/执行的历史记录。

实际model/effort UNKNOWN；沿用PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4。无模型、回测、策略/程序执行、安装、账户、付款或外发；只新增本Owner两份补充，未改protocol/root、旧报告或任何源。
