# 固定八次请求：官方demo、schema与CU的本地证据准备

**本轮最关键更正：账号不是所有官方示范取数的必需前提。** 已存Alchemy官方正文有意邀请开发者试用公开WS demo；HTTP eth_call页也有单独的docs-demo默认/样例。二者不能混作同一凭证，更不能从示例推当前可用、八种步骤均支持或免费限额已核。没有发请求或订阅，不改上一轮来源报告。

**八次是原检查设计的正确请求计数，不是已证明的数学最少次数；当前仍非完整可发包。** 动态取得B/H不等于未固定规则：第2次成功返回的finalized区块身份固定后，后续均按同一B及H比对，无结果择样、换块或重试。欠缺的是若干官方方法schema正文，不是需要先运行策略才能知道的价格/收益。

## 1. 官方有意公开demo的原始依据

原件为父目录`methods-owner/02-three-pages.tool-return.json`，31299B，SHA256 `6806b9dbff32bb70230f54f1741951fee032cf28404a846f3eb9b6a8257cc608`。这是已存web工具返回，不是原始HTTP HTML；HTTP状态及源HTML hash未暴露，不能伪补。

- [WS Best Practices](https://www.alchemy.com/docs/reference/best-practices-for-using-websockets-in-web3)原源L102–110：标题问如何建立连接，正文邀请尝试下面命令，给出`wss://eth-mainnet.g.alchemy.com/v2/demo`，随后说明需要更高限额可注册免费账号、换自己的key。**有明确开发者试用语境，强于猜测一个key字符串。** 同句过时的300M免费额度不采用；本轮只用它证明demo意图。
- 同页L187–189建议普通Ethereum JSON-RPC用HTTP，**并没有说可将上述WS demo字符串原样换成HTTPS调用全部方法**。
- [eth_call方法页](https://www.alchemy.com/docs/chains/ethereum/ethereum-api-endpoints/eth-call)L84–88将apiKey列为required、默认`docs-demo`，建议更高吞吐创建自己的key；L118的官方curl样例使用HTTPS `/v2/docs-demo`。它证明**另一个HTTP文档样例存在**，不证明本机匿名调用已成功或chainId/取块也获同样支持。

以上完整带原源行标签的片段保存在`demo-intent-excerpts.txt`，SHA256 `28bcd523cb2c4c0bec8ccdca8d21687510bfe60268b12424dea48400ccc7a8f2`；没有执行片段中的wscat/curl或任何外部指令。当前用户账户问题无需作为所有研究的阻断；选择专用Free key路径与核公共demo适用范围是不同条件。

## 2. 三个方法逐项证据

| 方法 | 已保存的官方schema证据 | 精确CU证据 | 仍缺原件/字段 |
|---|---|---|---|
| eth_chainId | eth_call页L39/65导航出现名称；**未取得该方法正文**。不能用导航补params=[]、响应编码或正式错误schema。 | 旧指定目录的Alchemy *Compute Unit Costs*正文L110–113：CU=0、Throughput CU=5。不是零资源开销或无限制。 | eth_chainId正式请求/响应定义正文。Ethereum链1是原计划的验收目标，不等于方法schema已核。 |
| eth_getBlockByNumber | eth_call页L39/65导航出现名称；**未取得正文**。`(finalized,false)`来自Root原方案，不能借eth_call支持finalized就推该方法的参数也已核。 | 同一官方成本表L144：CU=20；Throughput CU列空。 | 正式第1/2参数、finalized支持、false含义、数值区块编码、number/hash返回字段和空值/错误定义；空TCU列含义未核，不填零。 |
| eth_call | 原方法页L72–123：POST；Transaction为必填object；Block为可选string或enum，默认latest，文字明确number/tag/hash及safe/finalized；结果为十六进制字符串。JSON-RPC envelope和params顺序有官方样例。 | 方法页L78直接列CUs26；官方成本表L173同为26；Throughput CU列空。 | “Show15properties”未展开，正式data/input、gas/from/value属性与可省略约定不在已存返回。样例含to/value，但不能把value=0x1复制给只读getter；空返回0x样例也不能作uint256零值。 |

CU原件精确路径：`/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/complete-ledger-case-20261016/liquity-opportunity-inputs/root/official-data-pricing-plans.web-tool.txt`，23501B，SHA256 `cf332ebe9edc7f43a04b2da0888ed78a43455d7638edeb5498d4c082aa9ac11a`。它实际包含Alchemy官方[Compute Unit Costs](https://www.alchemy.com/docs/reference/compute-unit-costs)正文，不是其它提供者价格或搜索摘要；相关原源行完整保存在`exact-CU-primary-excerpts.txt`。仅绑定该已存快照，不声称本轮刷新实时计费；不作费用或CU总量乘加。

## 3. 原八次设计的可固定与未固定

| 次序 | 固定规则草稿 | 证据状态 |
|---|---|---|
| 1 | eth_chainId，验收目标链1 | 方法名/目标可固定；wire params及响应schema待原文。 |
| 2 | eth_getBlockByNumber，候选参数finalized/false；取其B/H | 选择规则固定；提供者正式参数与B/H字段schema未齐，不能发送。 |
| 3 | 同方法候选参数B/false，核与H对应 | B为第2步返回的占位，不预选当前价格/有利区块；编码/输出schema同上缺件。 |
| 4–5 | Registry.MCR()重复两次，显式同B | eth_call形状、26CU已核；地址/ABI/calldata由ABI Owner绑定，data/input/gas/value的wire约定仍未齐。 |
| 6–7 | TM.getTroveIdsCount()重复两次，显式同B | 同上；不以估计仓位数或价格填参数。 |
| 8 | 再取B的区块头，核仍为H | 后置比对规则固定；不能把三次同hash升级为原子快照/永久不重组保证。 |

故“八次”仍是预定**1次链身份、3次区块头、4次getter**的上限计数。没有补请求、批量扫描、订阅或重试；schema缺件不能通过先发一笔试错来绕开。B/H动态占位本身不是缺少设计；合约地址、ABI和calldata准备不由本Owner猜测，亦不将“ABI已知”替代提供者wire schema。

## 4. 具体缺件与收口

尚需的原件已经能精确命名：Alchemy eth_chainId正文、eth_getBlockByNumber正文及eth_call调用对象15属性的正式定义。当前已存方法页提供导航锚，但工具原返回未保留这些锚的实际href，不能猜URL再称已定位完整原件；本轮0新公开动作，不补查。CU缺件则已从旧同服务官方正文补齐，不能继续一概写为UNKNOWN；Throughput CU空列含义仍未补齐。

`field-evidence.json`保存逐字段来源等级、已知/未知和非可执行请求序列。没有创建适配器、组装可发送请求、读key或访问demo/RPC。Pricing中的月额度、相对更新日期、搜索摘要与其它服务的价格都未被拿来补方法schema。

本轮只读当前协议、两份已存方法工具返回、Root已准备方案、必要Pricing/billing文本及指定旧root两份价格定位文件。源清单和实际选读字节见coverage/receipt，低于8MiB；没有读私有行情/QC、账号邮件、凭证或旧交易raw。0网络、0新金融运算、0模型/回测/交易/源码执行/安装/外发。实际model/effort/CPU/RSS UNKNOWN，只写schema-owner。
