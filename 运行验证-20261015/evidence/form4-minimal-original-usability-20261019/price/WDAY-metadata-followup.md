# WDAY既存元数据补读

0公网、0行情payload读取，旧evidence/receipts原件不覆盖。

现存`bars_1day/test.parquet`的已保存symbol footer元数据共有51个标的、0个未决rowgroup，未列WDAY。该结论依赖既有footer元数据真实性；本轮没有重新打开Parquet或解码列。因此现有缓存的行情覆盖不支持把Workday申报标成价格READY。

已保存发布者README L121–129只称51个大盘股，并链接另一个`config/symbols.yaml`，没有在本文枚举完整宇宙。本轮不联网追该链接，整个release其他文件是否含WDAY仍UNKNOWN；也未取得WDAY专属价格文件身份、覆盖日期或schema原件。现存通用OHLC/close_adj schema不能证明WDAY存在。未列不扩大成Tiingo/Twelve Data全服务不存在该股票。

实际Form4发行人WDAY不能与AAPL行情拼接。若当前仅核Workday申报结构，行情缺口不妨碍结构事实；若后来研究其价格响应，应先取得同一发行人明确的价格覆盖证据，本note不启动该步骤。

输入精确SHA256与元数据路径见`WDAY-metadata-followup.json`。actual model/effort UNKNOWN。
