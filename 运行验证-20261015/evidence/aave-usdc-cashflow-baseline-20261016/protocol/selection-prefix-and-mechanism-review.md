# 候选前缀与利息机制独立审阅

**限定PASS，必须保留同提供商覆盖边界。** root前缀派生在返回数据内可复现，无候选顺序错误；不是独立证明全链最早十个。实际审阅UTC、全部输入hash及前十hash见同名JSON。实际model/effort UNKNOWN，0联网、模型/回测/策略/EVM/交易，未解码候选本金、利息或盈亏，未改root。

## 返回群组及前十顺序

独立核7页Withdraw原件/回执hash、200/status1/OK、地址/USDC topic、字段长度与时间：page1–5各1000，page6为166，page7成功空，共5166；全部处于[2026-09-01,2026-09-08)UTC。事件标识去重为0；self-receiver为2220。29条transactionIndex='0x'原样保留，只按block/globalLogIndex排列，不修补字段。

normal query明确page1/offset1000/sortasc，从固定下界查询。1000条按(block,decimal transactionIndex)升序，hash无重复；首条2026-09-01 00:00:23UTC、block25878706，末条10:47:59、block25881930。**它不是完整周normal记录，没有末页，也不能仅由满1000条证明提供商绝无遗漏。** 可以按正常接口分页语义视为提供商声明的时间前缀。

独立检查成功标志、顶层to=Pool、精确withdraw选择器及3word参数、asset=USDC、amount=MaxUint、to=from，再与Withdraw(user=to=from)的txhash/blockHash/height/time对应，得到17个直接本人成功MaxUint候选。重新按事件block/globalLogIndex取前十，逐项event与normal完全等于root派生。第十block25880684，严格早于normal末块25881930；因此前十不受本页末块可能截断的影响。17只是前缀候选数，不是整周全部候选。

精确4byte文本匹配withdraw(address,uint256,address)给0x69328dec，同时用当周Pool ABI核参数类型；不是独立重算Keccak，更未使用SHA3替代。

**可说：在这个提供商返回的固定Withdraw集合及其normal升序前缀内，最早十个符合顶层结构的候选顺序已核。不可无条件说：已独立证明全链无漏或全周normal完备。** 全Withdraw分页成功空与normal单页都是同源，不是彼此独立的节点证明；隐藏漏项仍UNKNOWN。这一限制不要求为了接受前十而追索全经营实体或多年费用，也不需要仅为本前缀结果重新展开整周normal搜索。

## 收入来源与核账意义

已读官方文档Liquidity Pool L170–181与当周ReserveLogic L130–203支持：供给人让出池内资产使用权，借款人承担债息；借款利率/利用率与池现金流参与供给率形成，Treasury按reserveFactor分配部分新增债息，供给人的aToken指数收益与协议Treasury累计不同。Treasury累计不是已经提现，也不能全算个人收入。完整利率模型与实际RF、APY本轮均未取得，不填数字。

提款返回本金加累计收益，实际USDC出入差额仍需排除第三方aToken/债务等来源，再另列ETH gas及相关批准/失败。aToken记账增长不是预测优势；此任务是现金流基准，不是模型回测、alpha、XTX复刻或财富目标完成。

可用流动性与借款抵押健康限制提款；合约/升级、USDC资产与发行人/脱锚及gas成本也不能由展示APY消除。本阶段没有进行完整风险或安全审计，不宣称低风险、必能赎回、USDC=美元或已实现净利润。事前范围、首结构合格正负皆停和不按收益换候选仍应保持。
