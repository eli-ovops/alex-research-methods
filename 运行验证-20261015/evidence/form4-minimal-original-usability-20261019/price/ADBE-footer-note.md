# ADBE同issuer日期边界补证

现存TD日频test文件的ADBE rowgroup footer时间边界包住2025-03-21至2025-04-21。**只证明范围，不证明这两个具体日期有行、逐日连续、价格质量、真实成交或READY。**

2026-10-19T05:01:59.322383Z，先核编码文件SHA256与既存identity一致，再用现有PyArrow只读metadata。用symbol列footer min=max识别ADBE，命中rowgroup index=8，446行，0个未决symbol rowgroup。datetime统计min=`2025-01-02 05:00:00+00:00`、max=`2026-10-13 04:00:00+00:00`、null_count=0；物理INT64、逻辑microseconds/UTC-adjusted。这是footer读出值，不是逐行检验。

文件：`evidence/paper-reuse-20261015/twelvedata-fixed-daily-test.parquet`，5552288B，SHA256 `b09092507ec0aa00cb7cdc87ef5757ff6f5428aa7f9e6e55e632c8bbb74fa2b5`。完整编码SHA只用于身份，未解码任何table/column/data page，未访问价格或量的统计，未读取价格行或计算股票回报。

root报告另有ADBE原始Form4普通股买入原件（0000796343-25-000058，交易2025-03-20、接收2025-03-21 16:34:57）。本note仅使同issuer的价格文件元数据与之可对应，不重核该申报、也不将接收时间无条件换作可成交时刻。原AAPL拒绝和WDAY缓存缺口保持原样，不以ADBE替换其通过。这里没有选择盈利样本、放行收益核算或认证未来可用性。

详细操作和输入指纹见`ADBE-footer-time-metadata.json`；旧evidence/receipts未改。0公网、0来源代码/模型执行、0金融计算。actual model/effort UNKNOWN。
