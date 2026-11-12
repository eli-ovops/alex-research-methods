# 拍卖106历史计算器、参数与启动批次：新证据补充

**PASS_HISTORICAL_EVENT_AND_PARAMETER_PRICE_CORRESPONDENCE**。所读历史File、Kick和Take事件与已存计算器源码精确相容：top2150.287944695经552秒、60秒一档、cut0.99，9档后的价格恰为实际Take价。旧source-price-rules报告及其当时UNKNOWN未覆盖；本文件只追加新证据。

本轮0联网，只读保存JSON/源码、被动hex解码与整数/Decimal算术，未运行下载源码、策略、模型、回测、EVM或交易，未产生反事实收益曲线。实际UTC、输入hash、回执状态、原量与逐项检查见`historical-calculator-and-params-review.json`。actualmodel/effort UNKNOWN，规则PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4沿用；仅新增本Owner两文件。

## 计算器与时序

在提供者返回的Clipper全部263条日志中，按区块及全局logIndex排序，目标Kick前最新`File(calc,address)`绑定：`0x19e26067c4a69b9534adf97ed8f986c49179de18`，block12381609，2021-05-06T15:45:10Z。

该地址source API声明StairstepExponentialDecrease；安全解析标准编译JSON后，与保存的StairstepExponentialDecrease.verified-source.sol逐字节相同。其价格为：

`rmul(top, rpow(cut, floor(dur/step), RAY))`，RAY=10^27。

rpow含中间半向上舍入，最后rmul向下取整。源码注释中“cut^dur”的简写不替代实际`dur/step`实现。本次0.99的第9次乘方在RAY精度恰可精确表示，算术核对未执行该源码或复制其运行流程。

| 参数 | Kick前最新原量 | 含义/显示 | 对应File时点 |
|---|---:|---|---|
| calc | 地址如上 | 外部价格计算器 | 2021-05-06，block12381609 |
| cut | 990000000000000000000000000 | 0.99 ray | 2021-05-06，block12381609 |
| step | 60 | 秒；此前先有90，后改60 | 2021-06-21，block12678048 |
| buf | 1100000000000000000000000000 | 1.1 ray | 2022-10-16，block15761894 |
| tail | 4800 | 秒 | 同上 |
| cusp | 450000000000000000000000000 | 0.45 ray | 同上 |
| tip | 250000000000000000000000000000000000000000000000 | 250内部DAI，rad | 同上 |
| chip | 1000000000000000 | 0.001 wad，即0.1% | 2021-05-06，block12381609 |

Clipper File还显示buf从1.3→1.2→1.1、tail8400→4800、cusp0.4→0.45、tip0→300→250；不能以constructor默认值或早期90秒step解释本次。所读集合内Kick至Take间没有这些相关参数更新。

计算器先读6条page1，随后根新保存page2空数组亦已核hash/状态；Clipper263条page1/page2空、id106两条page1/page2空均匹配回执。它们支持本提供者返回范围的最新参数选择，不是独立节点历史storage/源码升级证明。API的verified-source/Proxy0声明未经独立编译或部署字节码验证，源码与历史部署身份前提仍保留。

## 实际价格与max对应

本合约id106的所读事件：Kick在2026-02-05T17:00:11Z（block24391979），Take在17:09:23Z（block24392025），事件所载timestamp差**552秒**。tic取Kick时区块时间，所读范围无该id的Redo；并未新增独立Kick块header读取。

- Kick.top原量2150287944695000000000000000000 ray，即**2150.287944695 DAI/抵押单位**。
- 档数floor(552/60)=9；cut^9因子为913517247483640899000000000 ray。
- top×因子/RAY精确得到**1964.325124535031849346152080805**，与Take.price原量1964325124535031849346152080805完全相等。
- 数值第8档为**1984.1667924596281306526788695**，与Take.max一致。这仅是相邻档的数值对应，不能推断程序在上一档发现、签名或广播，不能推发生过60秒/12秒等待，也不能证明实际使用公开bot。
- 552<4800且price/top=0.913517247483640899≥0.45，故按该配置done=false，与成功Take无需重置一致。

top到Take价格下降**8.6482752516359101%**，这是拍卖定价变化，不是对实际市场价的折价或净回报。**552秒起拍到成交也不是552秒可套利窗口**：尚缺每一时点可执行市场退出报价、费用和竞争事实，不生成它们的假想收益路径。

## Kick106信用及多场启动交易

按源码`coin=tip+floor(tab×chip/WAD)`，Kick106的coin原量为：

`280887306726180869414833925266508363764551865793 rad`，即**280.887306726180869414833925266508363764551865793内部DAI**。

这是`vat.suck(vow,kpr,coin)`内部信用，kpr=`0xb1650649cc244311e65c4e9e4f20055834c293e3`，不是拍卖买方`0xfa025…`。启动实际交易`0xb29c41fd0b34872acb33791b1ef184aaac03ed66e3525c34293c12c061aeac8c`的from=`0x08f97dee6d864282c67b1f1822cd39bd3ea79918`、to为b165；不能把kpr与外层发起者、最终买方或现实运营实体混同。

该receipt实际含**5条Kick、无Take**：emitter c679…的id930/931，当前71eb…的id105/106，以及c2b…的id289。这里只对另两emitter的同签名事件解码，不声称已核各自部署源码。整笔gas1522193×2551739086wei=**0.003884239374535598 ETH**；不能全归106，或无依据除5。

根随后补到的同笔native3流也已本地独核，作为**整批**观察而非单场分摊：

- receipt中DAI mint到b165原量1412301774814089536788，同量DAI卖出；5个coin的rad总和向下转wad恰同此数。此算术对应不证明期初内部余额为零。
- 该笔换得并Withdrawal的WETH及已记录ETH入b165均为**0.707747839571627240**；三种形态是同一流，不与1412.301774814089536788 DAI重复算收入。
- b165付未知角色地址`0xdadb0d80178819f2319190d340ce9a924f783711` **0.311409049411515985 ETH**，再付08f97… **0.396338790160111255 ETH**，两笔恰耗尽这笔可见native入款。
- 08f97…收到后扣**整笔**实际gas，观察当笔数量净增为**0.392454550785575657 ETH**。未知角色外付已经在helper分流中扣除，不能向EOA净额再次重复扣。

这不是Kick106单场提现利润，不与后续另一买方的0.097465…ETH净增合并。仅为此批提供者记录的可见流量，没有跨tx全部费用、全资产/内部负债、实体身份或持续盈利证明。保存的helper source API返回SourceCode空、ABI未验证，不能叫公开完整bot。

## 历史范围与原件质量

同一emitter返回263条中，Kick106条（id1—106各一次）、Take133条、Redo/Yank0条、其他24条。Kick时间范围为2021-05-17T05:01:45Z至2026-02-05T17:00:11Z；仅描述这个合约截止目标块的返回密度，不是全协议/未来容量。对id106，全emitter集合与indexed集合的Kick/Take相同，另按非indexed Yank的data筛选无106取消；不能据此认定独立归档无漏或唯一买家。

新签名辅助索引的四个text signature与现有ABI逐一匹配，才用于区分Kick/Redo；没有猜hash、用SHA3替代Keccak或安装依赖。辅助索引不是部署身份来源。

质量限制：indexed Kick106的transactionIndex原件为`0x`；全emitter集合共有62条此类空hex写法，原件未改。启动receipt/transaction给出0x0；历史参数排序使用区块及全局logIndex，不悄悄把原字段修成有效hex。事件地址/topics/data/hash/time和相应receipt的对应可核，但不是独立第三方完整性担保。

新证据关闭的是**所读源码、参数事件、Kick/Take价格和启动批次可见流量的对应层**，不是公开私人执行策略、全经营利润、独立全链完备或个人未来获利层。

## 补充：普通参与者入口与拍卖债务含义

本地补读UTC：2026-10-16T06:31:01.611619+00:00。新增Dog源码API原件及提取文本的hash见同名JSON。API声明`ContractName=Dog`、`Proxy=0`；标准编译JSON安全解析得到的Dog.sol与保存文本逐字节一致。Clipper构造参数第三个地址确为`0x135954d155898d42c90d2a57824c690e0c7bef1b`。这是提供者源码/构造输入对应，未独立编译或核当前状态；Clipper授权`file("dog",address)`可改此字段，不能仅凭构造参数认定它永远不变。

**直接`Clipper.kick`受`auth lock isStopped(1)`约束**（Clipper源码229—234行），普通EOA不能因此被说成可无授权直接启动。所读Dog的`bark(bytes32 ilk,address urn,address kpr)`是不带auth的external入口（170行）；源码未设调用者身份白名单。普通EOA或合约可在状态与依赖条件满足时经Dog触发清算，不等于任意时刻能成功。

条件包括Dog `live==1`、价格有效且仓位不安全`spot>0 && ink*spot<art*rate`、全局与该抵押品剩余清算容量`Hole>Dirt`及`milk.hole>milk.dirt`。可清债务份额由room、rate、chop限制；部分清算后残余低于dust时会改为全仓清算，并可能有限超过容量，否则部分拍卖债务本身须不低于dust；另有非零抵押量及整数溢出保护（171—213行）。配置的`milk.clip`、必要授权、外部依赖及Clipper停止/重入锁也须允许调用。本补充未读取当时或当前状态来证明现时资格或机会。

Dog `due=dart*rate`（219行）是**被清算份额的累积债务rad**，含rate累积因素；`tab=floor(due*chop/WAD)`（224行）是**含清算惩罚乘数的拍卖目标债务rad**，不是原贷款本金，也不是将chop原量直接加到due。实际chop参数本补充未核，不能从tab倒称已知本金、利息、罚金各项。

`bark`调用者提供`kpr`，Dog原样传给配置Clipper；`usr=urn`为被清算仓位及余抵接收者（228—233行）。kpr可以不同于交易from，不能据此认定现实运营身份。机制源码也不单凭Kick事件证明实际私有外层走了何种入口或使用哪一公开bot。
