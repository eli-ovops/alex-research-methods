# BitMEX前缀结构与产品限定验收

**PASS_LIMITED_PREFIX_STRUCTURE_QC_TARGET_BTC_BINDING_PARTIAL，无必须修正项。**静态gate/冻结源码/配置/官方绑定/单次lock/HTTP与输出seal及product小原件hash一致。实际一次206，Range0–1048575/99509710及ETag先验匹配后取1MiB；未重试或扩量。Reviewer未读取/重解压压缩前缀，原prefixSHA由Owner真实receipt与seal绑定。

1,000完整记录达到冻结上限，展开72,865B；精确表头timestamp,symbol,bidSize,bidPrice,askPrice,askSize，required唯一、全部6列。计数/时间格式/fraction/date前缀总量一致，没有数值parse报价。唯一identifier100BONKUSDT共1000，XBTUSD/XBT_USDT0只属前缀缺席，不是全日无BTC或全文件按symbol排序证明。未换产品或扩大前缀。

时间均D分隔、无zone标记、9位fraction并匹配2024-01-01前缀；不证UTC/精度/交换所或接收钟/PIT。gzip仅前缀，不flush、未到完整EOF/CRC，不冒99MB完整文件hash。结构成功不等数值质量/覆盖成功。

官方缓存支持候选XBTUSD是inverseperpetual、USDquote、每张1USD经济面值、XBTmargin/PnL；2024July公告缓存仅为当时perpetual身份旁证，不是2024Jan固定规格。实际文件片段未绑定XBTUSD，这些规格不能套100BONKUSDT，更不能直接用spot现金/成本。实际guide转认证未继续，公告404未重试；原文为缓存层，不冒当前官方全文。archiveSize单位/缩放、固定历史规格、目标BTC实际行与clock仍UNKNOWN。

官方研究发布用途依据继续，完整用途条款仍partial，不作任意再分发/AI上传/商业交易授权，也不要求新增ML专门许可。下一层只是这些具体缺件，不从局部未见判整个源不可用。本轮没有预测/费用/收益/账户/回测/交易。

Owner3.142603625s、采样RSS52,527,104B、exit0无活worker；Owner说明与本两次review分列计同300s，采样非瞬时硬峰。Reviewer0新增网络、行情解析或helper执行，无自己后台进程，actual route UNKNOWN。输入fingerprints和资源在audit.json，旧FAILED/原件不改。
