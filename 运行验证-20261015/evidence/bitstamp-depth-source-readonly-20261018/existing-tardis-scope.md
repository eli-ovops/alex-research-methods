# Tardis既有条款与Bitstamp盘口范围

结论：既有条款审阅支持有条件的个人本机专用统计／量化研究；免费每月首日不等于完整连续历史。本轮4份材料未证明Bitstamp/BTCUSD的具体覆盖、单位或可用盘口类型，不能从Kraken或Deribit移植这些结论。

本轮直接读的是既有审阅及补证，不是重新获取官方条款。原审阅记录条款最后修改日2026-09-13、读取日2026-10-17 UTC；当前法律和服务状态没有刷新。4份实际输入的绝对路径、当前字节及SHA256见同目录JSON。

## 已经核过，不必重复检索的部分

- §9.5的内部专用量化／统计例外有正面依据，覆盖研究、策略开发等列明用途。将专用XGBoost归入该类别是解释，不是供应商点名认可；仍须并列看§9.2及适用上游条件。不能自行添加“所有内部研究一律仅准非生产”或“所有算法执行都须另行书面许可”的泛化限制，也不能据此启动本轮未授权的实验或交易。
- 基础模型／通用AI训练与评估的旧禁用路线保持关闭。向外部服务提供方披露Data、Manipulated／DerivedData的书面约束及Supplier执行权条件尚未证明满足；只发误差等汇总不能自动放行Codex／通用LLM审阅。
- §23中的Coinbase专门条件不能直接套到Bitstamp。供应商一般上游保留句也不自动生成“一律先取得额外授权信”的要求；Bitstamp具体适用仍UNKNOWN。

定位：既有`protocol/source-review.json`的decisions、terms_limits；§1.1 L87、§9.1–9.5 L159–183、§23 L290–304。较早个人用途审阅只覆盖条款抽取L0–236；后续专用模型审阅已有尾部补读，不能把较早范围当后续仍未读尾部。

## 免费和连续性不是一件事

既有根补证明确：HTTP和标准化CSV均有每月第一天免key说明，不代表整月免费、每个品种／日期必有文件，或已验证实际下载成功。日导出时间不证明完整性。

CSV按collector `local_timestamp`分日，不含disconnect事件；raw HTTP文档以空行标记断线。CSV双时戳是UTC微秒，exchange timestamp可能回填local timestamp。`quotes`来自L2重建，`book_ticker`是原生BBO来源；L2 amount为更新后绝对量而非增量，价格和数量单位仍须按来源绑定。长时间没有新报价行本身不等于断线，空分钟也不证明市场无事件。

已有官方入口：

- https://docs.tardis.dev/api/http-api-reference.md —— HTTP访问与断线标记。
- https://docs.tardis.dev/downloadable-csv-files/data-types.md —— 通用CSV字段及重建语义。

它们是既有审阅引用入口，本轮未新访问；4文件未复述完整terms URL，不猜写入口。CSV首日免费、分日和断线缺失由`root/CSV-free-access-and-continuity-primary-supplement.json`补足。

## 唯一仍需的来源特定证据

本轮材料对Bitstamp/BTCUSD的原生标识、Tardis标识映射、历史起点、quotes／L2类型、数量单位、指定免费日覆盖及原始断线入口均不足。只需根正在查的官方Bitstamp专属元数据／说明来绑定这些字段；不重开通用条款调查，不自行请求行情。即便元数据覆盖通过，也仍不是实际文件连续性、预测优势、成交容量或盈利证明。

状态：`PASS_LIMITED_EXISTING_TARDIS_SCOPE_NOT_BITSTAMP_ADMISSION`。仅完成范围归类，非Bitstamp全准入。实际model/effort UNKNOWN；本轮4份既有文件，新网络、下载、行情读取、模型、回测、账户、付款、交易均0。完成停止。
