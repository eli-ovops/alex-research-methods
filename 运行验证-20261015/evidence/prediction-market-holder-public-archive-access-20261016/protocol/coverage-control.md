# 已知合并交易：HF过滤覆盖正对照

**唯一可选过滤GET超时，覆盖UNKNOWN；不是空返回或无交易。** 原`archive-access-admission.*`和旧`read-receipts.json`未覆盖，指纹核实不变。本补充仅新增coverage-control文件和独立读取回执；13份实际输入SHA/bytes在同名JSON。actual model/effort UNKNOWN，规则版本保持不变。

## 请求与未取得内容

根于2026-10-16T15:47:03.126321Z另行封存单一正对照：已知tx `0x3ca8e82d43f1f34dd92f7a5de60121005ed7ad4cb1b42f6ed094f8a3a1079bb9`、block86161976。仅实际标量列：

```text
"transaction_hash" = '0x3ca8e82d43f1f34dd92f7a5de60121005ed7ad4cb1b42f6ed094f8a3a1079bb9' AND "block_number" = 86161976
```

使用HF公开/filter、default/train、offset0、length100、cap1MiB；未使用topics数组、LIKE、函数或猜测字段。精确URL及参数保存在`coverage-control-read-receipt.json`。一次本地exception分支的SyntaxError发生于脚本解析阶段，尚未发GET或写来源文件；查LOCAL_BLOCKERS后仅修正常规语法，未更改环境/认证。

唯一实际GET发于15:48:00.591669 UTC，15:48:31.314967 UTC记录`The read operation timed out`后停止，无重试。未取得可保存响应正文或HTTP状态、headers、x-revision、partial，因此这些均UNKNOWN，不能写0行、partial=false、数据不存在或已知10logs不匹配。未读取更早1800块、未做新收益计算。没有下载Parquet或执行SQL/SDK/来源代码/EVM/模型/回测/策略/交易。

## 零网络复核的原始文件入口

旧固定HF metadata（dataset `wzsg/polymarket-raw-chain-logs`、revision `6de5f2a7fc9ff4b42ced990f47c556fa448933c6`）有8323项siblings，每项只有`rfilename`。索引5934实际列：

```text
raw_chain_logs/block_group=043080/part-b086160001-b086162000-1dd5745bbf06.parquet
```

文件名编码86160001—86162000，包含原固定1800块86160176—86161975及已知merge块。**只是名字声明的范围，未取内容、未验证覆盖/完整性。** siblings保存顺序不是链时间或文件行序；没有此分片size、完整内容SHA、row groups或footer字段。可按既有HF resolve路径构造固定文件URL，但本轮未请求它，不冒已可Range读取。

已读清单只有`db-prefix.json`，其范围不含目标块；另11个manifest文件名确在metadata中，但内容未读，不能从前者推整个归档缺目标。既存206/Content-Range/同ETag与commit仅证明**该manifest**支持那一次Range，不证明上述Parquet也支持Range或footer小读。

所以filter超时不扩大为原始归档不可读；原始分片入口真实存在于固定元数据，具体可用性、许可、footer/行组与取得成本仍待限定原件核验。本次不自行下载、补读或扩范围，财富目标未达。
