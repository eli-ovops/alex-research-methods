# gDAI历史原账入口：独立限定验收

**PASS_LIMITED_RAW_CASHFLOW_STRUCTURE_REVIEW，无材料错误。**

九组原始JSON与对应receipt bytes/SHA匹配，RPC请求/响应id及交易hash/receipt/from/to/块标识对应；部署初始10000块返回4条与部署receipt正控一致。12M请求原件只有明确10M上限RPC错误、无候选；此后重新冻结10M与最早事件规则，先于返回及候选选定，无按金额/利润择优重选。仅是固定窗口/provider返回的最早Withdraw，不能冒全局最早或交易前选例。

该owner nonce36–44逐一找到原tx与成功receipt，连续无缺。最新id101是nonce40/0x28，hash`0xa29c55c90603f4b804fc1a91e579b0ac36c4a61820044124f4103172db1ee123`，对应id100 status0x1；不是缺失或失败交易。存入、请求、赎回与share mint/burn结构相连，不代表全经济账户关闭。

资金原件id62确有同asset从pool体系地址转入owner原量850000000000000000000；id104反向同asset原量850110166431858826003。这支持资金/偿还线索，不证明自有本金、完整借款/抵押负债、利息或全账户净利；未核具体ABI，不相减或换算。nonce40其他协议关联和费用分摊仍未知。

费用仅核gasUsed/effectiveGasPrice/gasUsedForL1存在，未相乘或求和，不把L1 component再加一遍。NFT零返回仅限两请求的合约/主题/区块窗口，非无全部NFT权益。全部结论只允许“实际存赎现金流结构已对应，nonce gap已补齐，净利/全费/容量未确认”。

完整输入hash、九笔nonce映射、查询范围及实质缺口见review.json。仅本地只读验原件，没有RPC/联网/源或模型执行/收益核算/钱包/交易，旧结果与原件不改。actual model/effort UNKNOWN。完成停止。

审阅器初始方法白名单漏列部署批id1的eth_chainId；实读请求确认为普通只读链标识，已纠正本审阅分类，未改原件或重发。
