# 已有 BTC_1sec 元数据定位

结论：已保存原发布者 BTC_1sec 的字段、展示体积、CC0 与采集工具定位证据，可复用。它与 BTC_1min 分别列名；旧一分钟失败不自动否定一秒产品，一秒聚合快照也不能冒充每事件流。

证据根目录：`运行验证-20261015/evidence/open-license-crypto-book-source-20261017/`。

- `root/Kaggle-BTC1s-metadata.AX-excerpt.txt`：选中 BTC_1sec 的原页 AX，展示 **1.76 GB、156列**。原观察 UTC 为 2026-10-17T02:32:23.576Z。
- `root/Kaggle-BTC1s-column-selector.full-AX.txt`：字段选择器原文，包括 system_time、midpoint、spread、buys/sells，以及两侧0..14档 distance、notional、limit/cancel/market_notional。派生 `published-columns-and-evidence-precedence.json` 实际仅155个具名字段；第156列与实际CSV字节表头 UNKNOWN，不补猜。
- `protocol/publisher-dataset-landing.original.html:100` 与 `publisher-dataset-metadata.passive.json`：JSON-LD直接绑定 martinsn、dataset1567989/version1、CC0 与 zero/1.0 链接。可复用现有发布者许可证据，无需再搜。
- 同一 JSON-LD 致谢 `https://github.com/sadighian/crypto-rl`；`protocol/schema/tool-book.read-receipt.json`、`tool-simulator.read-receipt.json` 定位固定 commit `078081e5715cadeae9c798a3d759c9d59d2041bc` 的本地源码。此工具版本与2021数据生成配置绑定 UNKNOWN。发布者 starter notebook 实际链接也保存在 BTC1s AX:82。

尚未知：BTC_1sec精确原始/压缩字节数及payload hash、受支持的匿名免费有界小样本取得能力、实际CSV表头/第156列、时区/分箱截止/可用时间、经济单位及历史生成身份。整数据集 ZIP 广告大小1,041,602,262 bytes不是BTC_1sec大小，1.76GB也是展示值而非实测。

最小下一问题可收敛为：BTC_1sec是否支持免费有界小样本获取，以及如何固定精确版本/byte身份。本任务不尝试获取。

逐项绝对路径、大小和本次SHA256见同目录JSON。0联网、下载、行情CSV/zip/parquet读取、模型、回测、收益计算或来源执行；actual runtime UNKNOWN。仅本目录两报告，无清理项。初次命中文件夹内通配rg误匹配既有protected-state快照，未据其作结论，未继续扩查。中文heredoc遇Non-UTF-8解析错误，按LOCAL_BLOCKERS既有替代改用apply_patch/ASCII脚本，未改环境。
