# HftBacktest BTC 示例：一次只读格式/时间QC

**完整读取成功；不等于因果重放、可实时预测或盈利通过。**只一次公开GET、一次gzip/JSON扫描，无重试。

固定对象为新repo tree5f3ec40b2afb764e0fea112f941ed85523ef4e88内 `examples/usdm/btcusdt_20240808.gz`。Git blob `a786c69d99a77be6060af5f7714db7393c9a4f5d` 独立匹配；实际3637062B，SHA256 `0ad7b3a0f5cff220761ea890cfd6e3c15f6899edc7f94637ec915043d7a72251`。GH公开API raw media响应HTTP200，wire含HTTP头3638493B；没有第二请求或Base64回退请求，没有pickle。完整MIT通知原样存MIT-NOTICE.txt，许可层级仍依根已有有限审阅。

gzip实际EOF/CRC通过，解码27757550B，93954行；空行、非整数prefix/缺JSON、JSON解析失败、非对象均0。全部93954个prefix为19位整数，93953相邻比较相等0、倒退0，原序严格递增；未排序或修复。

按官方同名DataPreparation的“首token本地接收纳秒”说明解释：2024-08-08T23:54:15.030314667Z 至23:59:59.833492584Z，跨度344.803177917秒。文件名日期不是整日覆盖，本例只有约5分45秒。这不认证本机时钟同步、内核到达或所有样本均是原始arrival。

| 原stream/event | 条数 |
|---|---:|
| btcusdt@depth@0ms / depthUpdate | 6551 |
| btcusdt@bookTicker / bookTicker | 66089 |
| btcusdt@trade / trade | 21313 |
| 无stream/event/symbol对象 | 1 |

前三流都标BTCUSDT。第55行存在lastUpdateId键，是snapshot线索；前54行已出现普通feed，不能仅此证明起始簿完整或更新序列可重建。本QC只辨识snapshot/reset/clear命名与lastUpdateId，不检查L2序列连续、深度状态、报价数值/盘口一致性；未发现命名reset/clear不证明所有断线不存在。

E/T在所有93954对象均存在且为13位整数；分别按每个stream的原顺序检查，倒退0。bookTicker的E/T相等次数32203/31843；trade为16039/16053；depth为0/0。不同流的时序不能混成一种exchange顺序。本轮未另读E/T单位权威原文，因此不凭13位换算UTC，不减去prefix算延迟，不称正延迟或可用时点已核。详细比较数/字段宽度及首5行键名元数据见QC.json，没有向工具输出大量报价/数量。

标准库适配与config在GET前封存。监督器只查本任务supervisor/worker/活动GH的PID，每0.1秒采样；正式墙时1.901675583秒、采样合计峰RSS84197376B、目录峰7304315B，worker自身高水位31490048B，均在scope上限内。采样并非连续绝对峰值证明。已退出，无活进程。

本轮不运行原collector/converter、不重建L2、无未来价差/涨跌标签/收益/成本空间/模型MSE或账户资金曲线，0模型/回测/安装/账号/付款/交易。actual model/effort UNKNOWN。独立验收由Reviewer负责，Owner仅提交只读QC原件，旧成果不改。

