# 本地BBO/同row双clock QC静态gate

**PASS_STATIC_ONLY，允许封存helper的一次本地全SHA与六列扫描。** 本审阅未读取市场文件、未执行Owner helper、未联网；不代表BBO质量、paired-clock分布或时点可用性已通过。

最终helper SHA256 `f40af9a61945dc9677a377b21d4bd43f35563912e5f6ec408b3e516261ba5174`；config/scope均 `542fb821997638a1bc0084e51b762a4ab8167a6daac5ff1b19fe1b2119cb6fbe`。gate.json绑定seal全部3项，config与scope逐项一致。

- helper:21–30先只读本地原文件，1MiB流式完整SHA及size匹配后保存identity回执，之后才import PyArrow/ParquetFile。没有复制源文件或网络路径；不重复依赖preflight。
- helper:35–38按scope核两时间INT64、四BBO DOUBLE；54–56唯一iter_batches精确六列、50000行/use_threads=False，所有物理行保留，无sort/fill/drop/未来shift或第二次数据扫描。
- helper:59–73逐字段null/nonfinite/negative/zero/finite-positive互斥计数。locked/crossed仅在两价格有限且正时比较，不被size条件过滤；strict-valid另外要求四值有限正且ask>bid，仅计数，不删行、不建spread/imbalance/信号。
- helper:80–97只对当前同row两个正整数时间计算Python exactint `R−T`，正/零/负分开，负数用magnitude分固定桶；min/max仅clock差非price。ns解释注明来自源文档条件，不叫实测网络延迟或服务器availability证明。
- helper:41–50固定对称正负桶；45预建源日24小时域，timestamp非正/null或越界另计，不产生任意时间key。first5 issue只输出原物理row index/reason，不输出实际价量或quote统计值。
- helper:99–106检查源stat、行声明、字段/paired/bucket/hour计数不变量；112–128核gate+seal和新exclusive lock，沿既有venv运行，CPU/IO设2、512MiB combined RSS每100ms采样、300s、8MiB预写容量与14:36:31Z截止，失败终止不修复重跑。

本轮无实质修正项。正式runtime仍需独立核一次fullSHA-beforedecode、真实projection与输出定义、source stat不变、计数恒等式、资源及worker退出；采样RSS不是绝对瞬时硬限。原始价量与时间数组只留本地，外部摘要仅质量计数与有界问题指针。

不推断获利、label/策略/交易或当时instant availability。actual route UNKNOWN；规则版本沿scope未变。0本review网络、市场文件读取、Owner helper执行、模型/统计/回测/交易。仅preflight-review两个交付物保留，无清理项。
