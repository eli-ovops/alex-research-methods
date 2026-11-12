# 固定2024-01-01完整quote文件：symbol库存与XBTUSD质量

Owner完成，待独立原件验收。唯一完整GET正常200，Content-Length99,509,710及原ETag匹配后才读body。全SHA256为f9deec14f86f00e3b9a9c0fe0f777a2706d5f7d454d7291901a66819d60a619b；首1MiB摘要55e33ef05116f6af256a3369f510554a37c52221056b8eb41010737a2a0dbd44与旧前缀一致，在解码前验证。两个hash都在下载流中算一次；没有重复全hash、请求或更换源。ETag不冒MD5。

本地gzip只完整流式扫描一次至EOF，trailer CRC及decoded EOF通过，实际展开568,859,727B；不保存展开CSV。表头精确timestamp,symbol,bidSize,bidPrice,askPrice,askSize。初始表头后9,242,085个CSV记录，全部6字段；坏宽、空identifier、重复header和空CSV记录均0，末物理行有newline。全124个非空symbol的精确计数保存在inventory-summary.json，未在找到目标时早停。

**实际目标绑定：Exact XBTUSD为535,218行。** 旧前缀1000行只见100BONKUSDT并不表示全日缺席；本次是新scope固定全文件结果，旧前缀原件/结论不变，不改币、不按目标何时出现决定停止。

XBTUSD四字段bidSize/bidPrice/askPrice/askSize各535,218 finitepositive；每字段empty/parseerror/nonfinite/negative/zero均0。正价格对535,218，locked=0、crossed=0（价格判断不由数量过滤），strict valid=535,218、invalid=0，仅计数，不修删或构造交易。

目标timestamp全部为规范固定宽D分隔＋9位fraction、无zone标记；2024-01-01字符串前缀匹配535,218，不匹配0。相邻canonical目标对535,217，equal/backwards=0、forwards=535,217。坏targetclock或未知坏宽/空identifier/repeatedheader会断邻接，正常其它symbol不影响目标物理次序。本次没有此类坏记录。仅词序/字符串格式，不是数值时间间隔、UTC/真实精度、exchange vs receipt或PIT认证；没有任何原timestamp/报价/数量输出或价格统计。

运行2026-10-18T15:40:56.394761Z–15:41:31.301406Z，exec session34501，PID99246/99247，exit0；34.906517666s，100ms采样合并峰RSS57,360,384B，终止时新增99,549,661B，低于128MiB（后续小报告另计）。采样不是瞬时硬RSS保证；stderr为空，无活worker。源码/config/scope、门控、single lock、HTTP/UTC、SHA桥、EOF/CRC、全部计数与seals保留。另保守计10秒局部核对/说明，独立验收耗时计同300秒预算。

边界：仅此固定日、此完整文件的目标存在和指定QC成立，不是2025对象也已核、全档案覆盖、真实深度/可成交性、精确历史产品规格/数量单位、预测、扣费盈利或容量证明。XBTUSD不得冒称BTC现货；具体inverse/perpetual的原件身份与日期版本由产品Owner另作有限绑定。官方第三方研究发布用途仅支持本次个人本地非分发检查，完整ML/commercial/externalAI使用仍PARTIAL。

0新增安装/账号凭证/来源SDK执行/模型/特征/未来标签/成本收益/回测/付款/交易。旧FAILED、scope和原件不改；整体财富目标未完成。交独立验收后停止，不开展下一实验。
