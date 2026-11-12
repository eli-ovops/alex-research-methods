# Phase74公开schema准入

**来源版本已固定；目标请求字段准入UNKNOWN。** 预算3次GET均200、保存正文407893 bytes；未取历史数据、未运行源码/SQL/SDK/EVM、模型、回测、策略或交易，未安装、登录或改认证。actual model/effort UNKNOWN；规则PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4不变。URL、精确请求/完成UTC、状态和字节/SHA在`source-read-receipts.json`；同名JSON绑定5份实际输入。

## 已取得的身份

1. [官方仓库公开页](https://github.com/subsquid/sqd-portal)嵌入currentOid=`cdbb6271c2deac22b87c251c515afba3085368bc`。
2. 通过已存在且未改变的gh状态，只读[该ref的递归tree](https://api.github.com/repos/subsquid/sqd-portal/git/trees/cdbb6271c2deac22b87c251c515afba3085368bc?recursive=1)，truncated=false，定位实际路径和blob身份；没有读取或输出凭证值，没有使用此前受限的匿名API重试。
3. [固定resources/schemas.json](https://github.com/subsquid/sqd-portal/blob/cdbb6271c2deac22b87c251c515afba3085368bc/resources/schemas.json)，26458 bytes。树中blob SHA=`c1c5acf04a32bbc167b9460686fa606ebbae02b6`，被动按Git blob对象规则计算其SHA1完全相符。此为文本身份，不是历史Portal runtime或首次公开证明。

## 实际内容与不能推导的字段

文件是各链**存储/SQL表结构**，不是Portal POST请求模型。未执行SQL。EVM段从L159开始；transactions列含gas_used/effective_gas_price/status；logs表L408起有transaction_hash、transaction_index、log_index、address、data和topic0—topic3。L457/L462的topic2/topic3明确是varchar列。

因此只可确认底层表中存在相应坐标与topic列。**不能从列定义推出**`topic2:[...]`、`topic3:[...]`数组过滤、`transaction:true`、`transactionLogs:true`请求flag，也不能确认是否返回关联交易的全部日志。选中文件没有`transactionLogs`字符串；字段是不存在于本文件，不是证明整个Portal无此能力。

root当前可沿用的最小JSON仍只有前阶段已获原文支持的地址logs过滤与字段选择；本轮没有新增可准入的holder indexed-topic payload。精确过滤类型不足保持UNKNOWN，不猜查询，也不额外要求必须所有关联字段都存在才承认最小logs读取能力。费用/整笔记录不足时净利照常UNKNOWN。

## 明确但尚未读的下一入口

实际tree还列`generated/portal-client/src/lib.rs`，54083 bytes，blob SHA=`a1b279b79e94d37277a7a6630739f280fdd8fb19`。它仅是一个可能的请求类型入口，**本阶段尚未读取**，不能声称其中已有所需字段或已准入；不自动超预算续读。根可在另行固定的只读步骤核该单文件，不重取本次存储schema或受拒文档，仍沿同holder、两token、1800块范围和原历史读取上限。

本阶段在3次源读取上限收口，未请求历史、未更换钱包/窗口/赢家；来源文件选错层次不等于API不可用或盈利失败。完整目标未达。
