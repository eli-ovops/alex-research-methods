# 首日顶档报价与配对时钟 QC

Owner完成，待独立验收。0网络，唯一一次本地全SHA-before-decode匹配旧源a41f0c3a3769a1e198dade55f05cdefaf82b955a5acccd5fc19c8d6dd97e1319，267304100B；不复制原文件，扫描后size/mtime/inode未变。

只按原序project六列：timestamp、receipt_timestamp、bid_0_price/size、ask_0_price/size；863,465行、18批，batch上限50,000、use_threads=False。四报价字段各有863,465有限正值，null/nonfinite/negative/zero均0。正价格对locked=0、crossed=0；严格valid_state=863,465、invalid=0。这只是预定描述域，未删行、修复、排序或择优；没有输出实际价格/数量，没有计算spread/imbalance序列。

同一行两时钟均正的配对863,465，invalid/negative/zero差均0，positive差863,465。exact integer receipt_timestamp−timestamp：最小1,676,288，最大629,390,336，原生单位不变；按来源ns口径约1.676–629.390ms。

| 正差幅度桶（ns条件解释） | 计数 |
|---|---:|
| (0,1ms] | 0 |
| (1,10ms] | 861,952 |
| (10,100ms] | 1,498 |
| (100,250ms] | 10 |
| (250ms,1s] | 5 |
| >1s | 0 |

同边界的负差幅度桶全0。24个source UTC标签小时的rows/validBBO/配对符号均保留在summary；无出日标签或非正/空timestamp。每类最多first5问题索引规则保留，本次为空。字段、符号、桶及小时计数勾稽通过。

解释边界：这是不同clock同一记录的读数差，不是已测网络延迟；正差不证明同步精度、数据生成次序、实时可见或PIT。顶档数值有效不证明真实报价可成交、深度单位/容量、未来预测或净盈利。旧contains_gaps='Yes'声明及未明定义保持；本轮不把有效顶档或正时钟差当无缺失证明。

正式2026-10-18T14:24:59.849796Z–14:25:01.664625Z，exec session40335、PID94210/94211，exit0，1.814817625s，100ms采样合并峰RSS283,230,208B，终止时新增23,855B（后续小报告另计）。采样不是瞬时硬RSS保证。stderr为空，无活worker；source/config/scope/gate、single lock与输出seal保留。检查之外保守计10秒小型本地整理仍低于300秒。

模型、未来标签、价格表现/收益、信号、回测、账户和交易均0，无下载/安装/付款。下一仍需明确源时钟生成/缺口语义及更广日期有效性；本轮不自行扩展或执行金融实验，交验收后停止。
