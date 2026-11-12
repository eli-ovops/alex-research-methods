# 已知footer读取：限定成功

状态：PASS_METADATA_ONLY，Owner完成、待独立验收。旧单元上限停止结论保持；本新单元在旧tail及停止验收绑定、新静态gate通过后，只运行一次。

同一公开对象的footer Range 251260648–267304091及first4 Range 0–3均206；Content-Range总长267304100、ETag、version-id和长度先验全部一致后才读正文。新正文总16,043,448B，未重取tail8。footer原件留本地，SHA见output-seal.json/completion.json；不是完整源文件hash。

现有PyArrow26的read_metadata仅解析内存中“first4＋真实footer＋旧tail8”人工容器，未另落重复16MBwrapper，没有原始data pages，绝不是完整Parquet文件。声明：863,465行、83列、1,728行组；created_by为parquet-cpp-arrow9.0.0，格式2.6。

字段包含timestamp、receipt_timestamp、sequence_number（INT64，无logical时间单位），bid/ask两侧0–19档price/size（DOUBLE）。所需顶档字段均存在；max_definition_level=1表示可空声明，不是已检查实际缺失。只保存首末各2组非价元数据：组0有1行、组1有500行、组1726有500行、组1727有464行。完整schema与选定chunk offsets/encoding/size见metadata-summary.json，不输出价格min/max。

metadata键名包含exchange、event_type、symbol、ARROW:schema、contains_gaps、date；没有读取/报告其值，不能由键名断言无缺口、具体日期或单位。尚未知实际行时钟范围、时间/数量单位、事件与接收时钟可用性、顺序/缺失/连续性、成交能力、预测或净盈利。

正式2026-10-18T14:00:36.722092Z–14:00:55.740694Z，PID91824/91825、exec session76489，exit0且无活worker。实际正式19.018525833s；100ms采样合并峰RSS258,523,136B，新盘16,209,801B（终止时，后续小报告另计），预算内。采样不等于瞬时硬RSS保证。没有新依赖、vendor SDK、模型、统计、收益/账户账、回测或交易；0付款。

下一缺口仅是这些已声明时钟及book字段的有界实际记录QC，不是模型或策略授权。本轮不继续请求/解码，交验收后停止。
