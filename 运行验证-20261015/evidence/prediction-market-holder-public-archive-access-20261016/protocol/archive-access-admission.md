# 独立HF原日志归档：精确holder过滤准入

**匿名viewer元数据实际可读；固定holder＋两token的精确过滤仍UNKNOWN，未取历史行。** 3次官方文档/元数据GET均200，124450 bytes；条件未满足，0次可选filter请求。无Parquet、大包、SDK/SQL、源码/EVM、模型回测策略执行、安装、账户凭证、付款交易或外发。actual model/effort UNKNOWN；沿用PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4。

## 来源与版本

复用原件确认独立归档为`wzsg/polymarket-raw-chain-logs`，固定revision=`6de5f2a7fc9ff4b42ced990f47c556fa448933c6`，非私有、ungated。它不是被拒SQD数据请求的代理，未重试SQD或切host/认证。

本轮原始读取：

1. [HF官方filter文档](https://huggingface.co/docs/dataset-viewer/filter)，123317 bytes。
2. [该归档splits元数据](https://datasets-server.huggingface.co/splits?dataset=wzsg%2Fpolymarket-raw-chain-logs)，117 bytes，实际提供default/train。
3. [该config的info元数据](https://datasets-server.huggingface.co/info?dataset=wzsg%2Fpolymarket-raw-chain-logs&config=default)，1016 bytes。

后两响应`x-revision`均精确等于上述固定revision，状态200、未截断，无key/账户/付款。每次UTC、原URL、原响应headers、bytes和SHA在`read-receipts.json`；同名JSON绑定9份实际输入。文档精确发布日期/首次公开时间UNKNOWN。

## 为什么不发送猜测的where

官方文档只明确`/filter`参数dataset/config/split/where/orderby/offset/length（最多100）；where由双引号列名、比较运算`= <> > >= < <=`及AND/OR/NOT组合。未取得数组下标、成员判断或LIKE/contains语法依据，不能自行构造来试。

实际12字段schema中`topics`是string数组，`data`是原始ABI字符串；没有独立topic2/topic3或token_id列。因此已读文档无法准确表达固定holder在topics中的参与关系，再同时限定两ID（ID还可能位于动态Batch data）。这不是证明服务永不支持数组过滤，只是本轮精确请求准入不足。标量block/contract比较语法虽有依据，也不能用它替代授权的holder/token筛选而读取整个窗口市场。

官方另说明大于5GB的数据集过滤可能只索引最初5GB，返回partial=true时不能视为全量。当前info声明5407974405条、dataset_size=2669484374490 bytes、download_size=132478910129 bytes及partial=false；这些只是元数据，不是本轮下载、独立事件数/无漏核验，也不能将info的partial=false当作filter覆盖整个包。索引前缀是否含目标1800块亦UNKNOWN。

## 对取得成本的结论

同holder `02fe2a4c…fa6f3`、同两个ID、86160176—86161975范围未变；没有读取任何相关取得记录，也不计算收益。整包精确覆盖、viewer精确过滤、历史成本和净利润均UNKNOWN，不填0或假设期初零。

数据卡未给明确许可，当前dataset_info.license也是空字符串；公开元数据可读不等于后续交易实施或再分发已获许可，不能继承SII的MIT。即使未来能取得精确原日志，raw logs仍缺完整receipt gas/status/native，尚需对应资产/费用证据，而非私人bot全部公开。

按预算与条件停止，不再试宽过滤、不扩钱包/窗口、不取大分片。已有历史原账和正负结果保留，完整财富目标active未达。
