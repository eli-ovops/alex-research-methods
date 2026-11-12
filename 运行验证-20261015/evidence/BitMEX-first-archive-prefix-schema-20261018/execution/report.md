# BitMEX首个归档前缀：有限结构检查

Owner已完成，待独立验收。唯一普通匿名Range GET成功206，Content-Range `bytes 0-1048575/99509710`及ETag精确匹配后才读正文，无重定向/重试/认证。取得1,048,576B压缩前缀，SHA256 55e33ef05116f6af256a3369f510554a37c52221056b8eb41010737a2a0dbd44。它不是99,509,710B完整对象SHA，未验证整gzip EOF/CRC。

实际CSV表头：`timestamp,symbol,bidSize,bidPrice,askPrice,askSize`，6列，required唯一字段全在、无额外列。最多1000完整记录已达cap，全部6字段、无宽度不符；只查结构/identifier/时间字符串，未对价格/数量做数值解析或导出。

关键限制：这1000条唯一symbol为`100BONKUSDT`，exact XBTUSD=0、XBT_USDT=0。仅在本段未见目标，不能推出全文件/全日无BTC，也不凭此断言全文件按symbol排序；不更换候选、不扩大前缀找BTC。本单元没有完成BTC原记录绑定。

1000条时间字符串均为日期后D分隔的`YYYY-MM-DDDhh:mm:ss[.fraction]`形态，无zone标记，fraction9位；日期前缀2024-01-01匹配1000、不匹配0。这不是UTC/时间精度、exchange event vs collector receipt或PIT认证；未输出原时间值/数组，没有做时序、价格质量、未来标签或收益检查。

被动zlib逐字节展开合计72,865B，记录上限到即停、不flush；未遇完整gzip成员EOF。没有解码更后记录，没有落地decodedCSV。后续残行是否完整未继续观察，不将截断前缀当CRC损坏。原压缩前缀仅本地保留。

运行2026-10-18T15:26:44.277218Z–15:26:47.419836Z，exec session91185，PID98242/98243，exit0；3.142603625s，100ms采样合并峰RSS52,527,104B，终止时盘1,069,119B（后续小报告另计）。采样不是瞬时硬RSS保证，stderr为空、无活worker。single lock、source/config/scope/gate、HTTP/UTC/hash与输出seal全部保留。局部说明/勾稽保守计10秒，独立验收另计同300秒预算。

官方研究发布说明仅支持本次本地、非分发、有限结构检查，不扩大为完整ML/外部AI/商业复用许可。0来源代码/SDK执行、依赖安装、模型、金融计算、账户、付款或交易。剩余最小内容缺口仍是目标BTC symbol的实际历史记录及产品/单位身份；本轮不继续取数。旧结论不改，整体财富目标未实现。
