# 固定commit调用层因果核验

结论：调用层确认它是完整小时加邻近资料的后验重建，并实际剔除后验识别的ephemeral订单；仍未证明各事件当时可得、恢复时序唯一正确或初态完整。具体预测泄漏UNKNOWN，未读预测样本及其决策截点，不能宣称所有用途泄漏。

固定commit `5c1ee3488c9780b98e42f6077dd4d0434d52ce2a`，沿用完整tree `71243ff443342494911999043ed7e0b7c74b1bfe`。4指定文件全部HTTP200、SHA256及Git blob核验通过，29,508B；UTC为2026-10-18T10:43:38.855754Z—10:43:40.755080Z。逐请求原URL/UTC/状态/hash见source-receipts.json。

| 问题 | 已读代码给出的结论与限制 |
|---|---|
| first opens/cancels | stage4:34–55、89–98从前/当前/后一小时statuses窗口按oid取min(ts)，不是已证全生命周期first。CANCEL_LIST成员的orderstatus.py未读 |
| trades与seq | stage4:58–84读取邻小时触及日期的整日trades，合并两方oid-ts、unique排序。seq从derived/diffs直接输入；README:43仅说stage1保留file order，seq生成器未读，具体生成UNKNOWN |
| 后续anchors实际可达 | stage4:75–102对整coin-hour一次recover并写ts/src/ephemeral，未传decision_at/available_at截止。上轮已核next_anc backward-fill、forward trade匹配、backfill与cummax均在此路径可达 |
| ephemeral实际删除 | stage5:46–60排序小时文件，创建一次BookState；每文件filter(~ephemeral)后sort seq再重放，跨小时继续。该标记来自整hour与订单后续remove，不是已证实时可知 |
| gated处理 | stage5写出gated但不滤；A1:85–125直接用全bb表统计/找prior block，没有gated筛选。fills只看mid_pre非null。README:89–94称gated fills markouts=null，06_build_fills/markouts/clean_mask未读，落实情况UNKNOWN。诊断统计保留gated本身不证明预测泄漏 |
| 质量结果 | stage4/5打印语句与A1输出t1表都是将运行才生成的代码；本轮无实测表/日志。README:80明确结果表不随repo；22M fills、三小时精确复核及性能为作者自述。README:163–172也明确单元测试用手工synthetic输入 |
| 到达时间/初态 | 指定调用层无arrival/available_at或因果缓冲策略；time.time只计任务耗时。stage5仅空BookState，无snapshot/初态认证。前轮已核gap>5s清空、120s gated，暖机不认证真实初态 |

能成立的是“已有可复用的后验重建代码路径”。不能由此证明“恢复ts就是原始接收时间”“每条diff唯一映射”或“预测决策时已拥有后续资料”。离线描述/标签重建与预测特征可用性要按具体截点分别评估。

明确未读：diff seq生成器、orderstatus常量定义、build_fills、markouts、fills.clean_mask、toxicity及后续分析、DATABASE/DESIGN_NOTES、LICENSE正文、实际行情与结果输出。README MIT仅作者说明；publisher CC BY层按已有通过结论保留，不重开。若继续，最小缺口是一份已存在且带输入身份/原日志的时序初态质量审计与可用性说明；本轮4GET已尽，不执行重建求证。

路由目标gpt-6.1-sol/medium，actual model/effort/速度UNKNOWN。规则版本未变沿用已读版本。0来源执行、模型/训练/回测/收益计算、行情包、安装、账户/认证/凭证、外发或交易。所有产物仅caller目录，原文与回执为交付证据保留，无清理项。
