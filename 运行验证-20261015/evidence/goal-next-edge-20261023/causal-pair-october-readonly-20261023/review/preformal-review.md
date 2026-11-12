# 一日双市场只读QC：预正式审阅

初审：NEEDS_FIX（正式尚未开始）。UTC日期2026-10-23，精确起止UNKNOWN；actual model/effort/speed UNKNOWN。完整静态读24382B脚本、METHOD_READY及synthetic-checks-v2，另读已指定pointer小JSON；没有运行合成/下载/QC或读取行情。

确定must_fix R1：urllib.request.urlopen默认自动跟随重定向，事后response.geturl检查不能阻止额外请求，不符合METHOD禁自动接受重定向及固定一次URL。应在GET前配置拒绝redirect的opener；原GET不执行，准备期修正即可。

同轮需要Root明确的原有边界：R2 protocol单次wall≤120秒是否全formal；当前alarm仅覆盖Kraken下载/QC，之后取消，旧源处理没有wall保护。若原意全formal，须保持该alarm到完成；若只下载，明确而不伪造整体帽。R3验收文字要求固定网格见证，当前只有聚合数组输出；可最小固定3点保存clock/物理行/age/有效flag而无价格，或由Root明确以静态asof/聚合为本轮验收层。两点已集中报Root，不自行扩大。

其余主体已完整审：asof只消耗local≤tick到最后物理行，同µs最终行有效flag可覆盖前行；无未来插值或回退到更好旧价。缺local不用于配对且最终拒准入，倒序不排序救结果，最终drain扫描尾部并使倒序来源不准入。固定86400秒网格和年龄互斥/累计数量恒等式清楚，字段异常计数不改价格。两源顺序读取、压缩SHA/长度/CRC/EOF、Bitstamp固定旧hash及公开新对象明确。两源首末钟/结构与价格有效性分开，年龄不冒断流/用户时延；不保存预测价格或金融路径。

Bitstamp硬编码path/SHA/bytes与october-target-pointer小JSON吻合，未stat/hash/open市场体。CPU硬上限/RSS/字节及磁盘边界与独占排他marker已有；正式仅一次，失败保留现场不修后重跑。代码准备通过不代表数据质量或获利。待同轮修订后只审变更和新hash/准备回执。

初审绑定：pair_data_qc.py 52af75b041d0baf581f68f728ec762637b30cb52b88a5675a60292817d9aaed1。其他初始身份见preformal-initial-receipt.json。仅写review，不改Owner/Root/旧源/STOP。

## 同轮局部闭合：PREP_READY

R1已闭合：显式NoRedirect.redirect_request在follow前抛HTTPError，fixed_public_opener用于正式GET，不再以geturl事后判断替代禁止跟随；原geturl防漂移仍留。受影响人工检查实际调用handler并验证拒绝，无真实请求。

Root新增必要修复已核：exchange_timestamp_backwards继续完整计数，但已从admission_issues移除；local倒序/缺失/日外及结构/身份门槛保持。合成源clock倒序而local递增可准入，local异常仍拒，符合固定接收钟目标，无排序或换钟救结果。

R2原口径已消歧：protocol/METHOD明确120秒仅唯一网络段含Kraken流内QC，不冒全formal上限；代码原alarm范围因此不需改。R3固定三见证已补：每源index0/43200/86399，仅tick/selected与next local、物理数据行号、flag/age，无价格；Source返回行号三元组及at消费同步。受影响合成中间点同戳末物理行3的invalid flag保留，selected≤tick<next核合，无新增有利回退。

最终must_fix=[]，PREP_READY，当前fingerprint以preformal-receipt.json为准。原主体结论复用，不重审不相干逻辑、重跑合成或读取行情。正式仍由Root按当前SHA内部放行一次，不由本Reviewer执行。
