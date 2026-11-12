# 历史实现身份与合约机制独立审阅

**限定PASS：所返回升级事件＋最后升级收据与Sourcify验证源构成有条件的历史实现链；不等于独立节点/静默存储写完备证明，也未证2023源码已公开或完整策略盈利。** 实际18项输入绝对路径/SHA256/bytes及审阅UTC见同名JSON。actual model/effort UNKNOWN，0新网络/来源代码/模型/回测/SDK/SQL/EVM/交易执行。

## 历史身份

两个getLogs原页均成功，查询明确目标0x41eeba…、Upgraded topic及0..16862554；page1两事件，page2成功空。按block/log排序为16741125、16827963，后者topic1为`0x2fde9e0ce83769e88eaa9fb7be27cb26c385d1b2`。独立核该后者receipt成功，同tx/block/hash/logIndex/emitter/topic1相符。首索引事件data原文为空字符串，后者为0x，未抹平；后者收据为0x。

Sourcify原件950220B指纹匹配回执，chain1/实现地址相符，creationMatch/runtimeMatch都是原文`match`，不是本地独立编译/精确字节码验证。平台deployment16827953 < 升级16827963 < 目标16862554。资料商原源为空只证明该处未验证返回，不能否定已经取得的独立Sourcify源。

这比today latest实现或constructor初值更接近目标历史；限定为该提供商返回的标准升级事件链及收据，不推所有潜在存储写路径必发事件、索引全链无漏或完整共识证明。也不因仍有这些边界否定有限历史身份进展。

原始Sourcify的signatures给出execute规范签名及0x73e7b48d，与旧交易input前4字节相符；ArbitrageExecuted完整signatureHash32与receipt末日志topic0相符。ABI/源码布局一致，区别于后来flashloanAndArbV2。本审阅没有自行计算Keccak、调用ABI或执行合约。3个已提取源与原sources[].content逐字节相同。

## 已读源码真实约束

- execute（L246–264）无onlyAdmin，有nonReentrant、1..10路由、sourceAmount>0及最后目标必须BNT；外部调用者无需该函数中的管理员门槛。回调（L270起）要求msg.sender为BancorV3、caller为自身，保护回调来源，不是execute用户白名单。
- BNT flashloan后逐路由把目标币实际余额增量作为下一输入，最后返还amount+feeAmount。minTargetAmount/deadline等转给各交易所方法，是路由成交保护，**未见caller gas后必须正收益的检查**；外部贷款/交易协议其他约束未全读，不扩称全系统风险消除。
- `_allocateRewards`（L437起）按还款后合约**全部BNT余额**乘比例并封顶，再分给caller、将其余转给BNT token地址。它不严格隔离本次delta，因此存在既有余额/其他入款时，不能仅据该函数名把全余额都叫本次新套利收益。具体已核交易的Transfer仍保留，不追改原金额。
- 初始化默认100000ppm、100×1e18只是默认；setRewards受onlyAdmin及参数校验约束，不能据源码默认推历史state。另需保留原文细节：L218的prevPercentagePPM取newRewards.percentagePPM，而prevMaxAmount取旧state；不能按“prev”名字/注释直接解释事件旧比例或单独改比例的效果。本次仅指出静态语义，不运行测试、PoC或推实盘曾改值。

许可标记SEE LICENSE IN LICENSE，未取得该原LICENSE，不能继承后bot MIT。verifiedAt=2025-06-21T17:01:26Z是平台验证记录，晚于2023交易；部署早于交易、机制当时存在，不等源码在交易前公众可得。此前治理帖的开放参与/报酬规格也不自动绑定具体源版本或完整机会发现/发单规则。

## 收口

material_errors=[]；重要已知未知已列。根后续可用这份历史源解释原calldata/事件，但不能把历史实现定位升级成预注册、已实现跨币净盈利、完整私人运行策略或未来个人容量。无需全部私人bot/秘密才能承认旧收据报酬与gas事实。本任务到此结束，不新增请求或扩范围。
