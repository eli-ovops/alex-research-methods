# 目标柱完成证据准入补丁

仅修补未来评分准入；模型、预测、目标、公式和原188窗不变。
原脚本字节保存在 `score_endpoint_observation.before.py`。

未来调用：

```sh
python score_endpoint_observation.py --data NEW_LOCAL_PARQUET --receipt LOCAL_RECEIPT.json --completion-evidence REVIEWED_COMPLETION.json
```

成熟前仍直接返回 `NOT_MATURED`，不读新数据；成熟后材料缺失、版本/文件/目标不一致、源事件过早、日期无时区等返回 `AWAIT_COMPLETED_TARGET_EVIDENCE`，不生成分数。

completion JSON 的字段（这里只给结构，不提供可冒充真实完成证明的样例文件）：

- `dataset_id`, `dataset_revision`, `relative_file`, `data_sha256`, `symbol`, `timeframe`, `target_bar_start`, `target_bar_end`：精确绑定输入收据和封存目标。
- `file_publication`：`event_at_utc`, `source_url`, `artifact_path`, `artifact_sha256`；来源内容须支持这个具体文件版本的发布时间，不能只用整个仓库lastModified。
- `completion`：`type` 为 `post_end_source_fetch`、`post_end_generation` 或 `official_completed_bar`；另含 `event_at_utc`, `source_url`, `artifact_path`, `artifact_sha256`。独立审阅须确认原件实质支持目标结束后的抓取/生成或官方完成标记，且关联选定文件。下载时间、后继柱及人工true声明本身不够。
- `independent_review`：`reviewer`, `reviewed_at_utc`, `decision`（accepted）、`source_content_finding`（实质核查依据），以及 `reviewed_payload_sha256`。后者为去掉整个`independent_review`字段后JSON对象的原评分器`digest`，用于防止审阅后替换证据包。

时间均须带时区；目标结束 ≤ 完成事件 ≤ 文件发布 ≤ 本机取得 ≤ 本次检查，独立审阅不得早于文件发布或晚于检查。来源路径可绝对，也可相对completion包所在目录；必须存在且哈希匹配。

**机器只做一致性、防误用检查。** 它无法认证审阅者身份或从任意JSON自动证明来源解释正确。真正材料到来后仍须独立核实原件内容，再记录审阅。不能只补写字段或true强行放行；也不要求未来永不修订。

`test_guard.py`只测试拒绝路径和纯函数约束。构造的事件/审阅字段明确为软件测试，不是行情或完成证明；不启动模型、不执行真实评分，也不改时钟。真实未来正向评分尚未验证。
