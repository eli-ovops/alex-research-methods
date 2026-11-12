# 唯一新候选：Crypto Lake

结论：**NOT_YET_ADMITTED，未取得具体可准入的多日BTC/ETH原始消息免费样本。** 官方元数据有价值：区分高频快照与增量产品、给出服务器接收处理时间及一般使用条款。但免费样本的具体日期/文件/版本、是否含增量及适用许可绑定仍未知；不据此宣布来源不可用或有盈利优势。

候选官方入口：[免费数据](https://crypto-lake.com/free-data/)、[数据与schema](https://crypto-lake.com/data/)、[条款](https://crypto-lake.com/terms-of-service/)，官方API仓库链接为 `https://github.com/crypto-lake/lake-api`。仅研究这一新来源，未继续第二候选。

| 准入项 | 已核官方正文 | 未核/判断 |
|---|---|---|
| 免费与多期 | 免费页声明L2等免费试用，四类数据合计约一年 | 未取得免费BTC/ETH逐日清单、精确文件大小或固定版本；不能把全服务历史覆盖当免费样本覆盖 |
| 原始程度 | Data:7–17区分book（约100ms级20档快照）与book_delta_v2（增量更新、需重建book） | 免费环境是否包含delta、初始snapshot与连续多日文件UNKNOWN；不能把book快照称原始每消息流 |
| 时钟 | Data:31、77–88、173–178定义origin_time为交易所事件、received_time为其服务器接收并处理时间，nanosecond epoch；另有sequence_number | 同页明确订单簿origin_time往往为空/0/−1。不能承诺完整双clock，更不是未经处理的网卡接收时刻；实际时钟校准/转换代码/字段分布未核 |
| 研究使用 | Terms:4–6授予客户受限制的数据使用许可、禁止未经同意向第三方再分发raw或可重构主要原数据的派生数据；未列NC或额外ML禁止词 | 个人内部统计/模型研究可作为一般使用的条件性解释，不要求额外“ML”字样。匿名免费sample是否明确适用customers授权、以及任务实际工作流仍须绑定；不升级为开放再发布许可 |
| 实际可读性 | 三官方文本页本次正常原生抽取；schema列按日/交易所/币种分区的API/S3访问路径 | 未请求任何行情文件、目录清单或API。native工具未提供HTTP状态/原始响应bytes，不冒称HTTP200或payload可得 |

第6次读取沿免费页真实链接到 `https://raw.githubusercontent.com/crypto-lake/analysis-sharing/main/available-sample-data.png`，返回只有链接标识，无可读图像正文，未做OCR、重取或从URL猜日期。条款正文标最后更新 **2022-11-14**；免费页、schema及覆盖图发布时间均UNKNOWN。

公开动作预算已尽：2条公开检索query＋免费页/schema两次open＋terms/coverage图两次click＝6；工具批处理3调用不替代动作计数。UTC总窗口2026-10-18T13:29:08Z—13:30:28Z，未记录单动作精确时刻，不补造。原生返回原样保存并hash；它们是工具文本证据，不是原始HTML/HTTP回执。

最小下一原件：免费环境官方小型文件清单/manifest，需同时列明BTC或ETH至少两个日期的delta及起点snapshot文件、固定版本/字节数，并明确该free sample适用条款。这是具体缺口，不要求额外特定ML许可词；本轮不追加读取、不下载payload。

已先查LOCAL_BLOCKERS并避开列明旧源；Exa已知未配置，不修工具。规则沿scope，actual route UNKNOWN。0市场payload下载/读取、collector/来源执行、模型、统计/回测、账号凭证/注册付费或交易。仅publisher目录原生文本与报告保留，无清理项。
