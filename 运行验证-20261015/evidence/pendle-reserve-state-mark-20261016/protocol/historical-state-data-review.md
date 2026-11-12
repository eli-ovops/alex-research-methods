# 实际Sync历史与持久储备状态：独立原件审阅

**限定PASS：已存提供商返回376/0条实际Sync，结合已审声明源码，可条件性支持固定端点的stored reserves。** 本审阅未算价格、标值或profit，不升级freshquote/实际出售/独立全链完备性。0网络、无模型/回测/策略/EVM或下载代码执行。

两GET回执HTTP200、源status1/OK、page1=376、page2=[]，hash/bytes全符，合219999rawbytes；查询pool/topic/start16857476/end16940286/page1/2与事前scope一致，未改端点/选有利事件。376条均地址/topic正确、data两word各uint112范围、tx/blockhash32bytes、block/log/time有效，重复0，原返回block/globalLog严格有序，同块hash/time相符。与parent全部parsed字段逐行相同；未盲信布尔结论。

12个transactionIndex原样`0x`，未回填、不用于排序。removed字段未返回不等于独立canonical/finality证明。分页成功结束只说明此索引器返回完结，不证明节点独立无漏。

首条seed与旧入场receipt block16857476/log186的address/topics/data/txhash/blockhash/block/log完全一致，provider timeStamp也等于receipt blockTimestamp；已复用旧收据作阳性对照，非不同节点证明。

最后状态block16940032/log94，2023-03-30T12:22:35+00:00，raw储备0=76885776430031180710、储备1=998791937182814351981576。端点16940286距末次更新254blocks，实际兑回距其3084秒。末次事件不在旧100块16940187..16940286，原窗口成功空与新返回一致，**没有变成有freshquote**。

若实际部署runtime符合所读source、token身份条件与返回完整性成立，最后Sync能支持端点stored reserve0/1；余额/donation/rebase/externaltoken状态不一定等于stored reserves。ratio后续只能另行作为历史储备状态标值，不是成交价/可执行规模或已经清算的ETH/USD利润。Pair源版本/初始化、单提供商历史覆盖原边界保留，不添加零不确定性门槛也不隐藏它们。

全部输入hash及逐12警告见JSON。审阅UTC：2026-10-16T10:25:25.555848+00:00；实际model/effort UNKNOWN，未改root/历史产物。

JSON SHA256：`f8670f1bbf3c1b4c2c8da3b2442da6f661f5af9f89345b529102645be1696bdb`。
