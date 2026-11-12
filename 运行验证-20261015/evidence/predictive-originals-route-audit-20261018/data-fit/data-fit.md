# 既有 BTC 输入与逐事件 queue 论文的数据适配

**不能直接复现。**已核的实际输入是分钟聚合/快照 CSV，不是逐事件最优报价与真实队列变化档案；数据不匹配不否定论文方法。

本轮仅读三份正文，未读原始大 CSV、未计算新指标或运行模型：

1. `BTCUSD-fixed-forecast-protocol-20261017/protocol/proposal.json`：这是未执行的 Kraken/Tardis 方案，假设以 collector local_timestamp 的 BBO/size 预测未来 60 秒 midprice log-return（bp），六特征、XGBoost/Ridge/zero、时间分割。它不是后来实际分钟 LSTM 实验，不能把其逐报价、到达时钟和 60 秒标签语义移植过去。
2. `BTC1min-public-access-and-clock-20261017/protocol/data-audit/data-quality-review.md`：实际 Kaggle 版本1 `BTC_1min.csv`，SHA256 `1a4bf5d19f0f9b41f93a7fadacb44f015f8f7eb3212995b77bd70182d99afa93`，33161767B；17113行、156列（空索引列、system_time、154数值列）。2021-04-07T11:33:41.122161Z 至 2021-04-19T09:54:00.386544Z。17041个间隔恰60秒、71个大于60秒。midpoint/spread 及两侧 level0 notional 的内部一致性已核，但没有独立逐档价格列；notional 不是本轮已证的逐事件原生 queue size。system_time 的 UTC 标签也不证明真实事件到达时刻或2021采集器配置。
3. `BTC1min-fixed-evaluation-run-20261017/artifacts/run-settings.json`：正式运行确实绑定同一 CSV，以及冻结 TRAIN/TEST 时间索引；列出 LSTM_price、LSTM_state、Ridge_price、Ridge_state 四版本与先封存预测后评分记录。其权威目标定义只引用另一 readiness 目录的 `fixed-once-evaluation-proposal.json`（SHA969ac08e…5d983），未在本正文展开。受三正文上限，本轮不冒充独立核实该目标公式、输入维数/窗口或完整切分；这些精确项为本次读取范围的 UNKNOWN，不是旧实验不存在记录。

| 论文问题所需（由根已读论文提供，非本轮独立论文核验） | 现有输入适配 |
|---|---|
| 逐事件 best bid/ask 及两侧真实 queue | 未取得此粒度；现有分钟字段不能补回分钟内顺序 |
| 下一次 mid-price 变动的时间/方向 | 未保存的中间变动不能从分钟 midpoint 唯一重建；一次或多次变动/反转会混同 |
| 原生数量/价格及事件时点可解释 | level0 notional 与价格代数一致不足以证明原生 queue、历史生成版本或事件年龄 |
| 同一目标与评估设计 | 早期60秒方案不是 next-change 标签；实际分钟目标完整公式本轮未展开，不应声称 exact replication |

现封存输入只能支持其原有分钟层级研究边界，不能把论文的股票逐事件结果迁移成 BTC 一分钟预测已获支持。也不能把旧 LSTM 失败解释为 queue imbalance 方法无效。论文的随机80/20与其目标由根核验，本产物没有重读或独立确认论文内容。

唯一最小缺口：若要精确陈述“旧分钟实验目标是什么”，只需既有冻结 `fixed-once-evaluation-proposal.json` 的目标字段；本轮不再读第四正文。直接复现论文则仍缺逐事件盘口原件，本轮不建议获取或申请运行。

网络、行情读取、代码执行、训练、预测、回测、收益核算、交易均0。actual model/effort UNKNOWN；旧判定及所有原件不改。

