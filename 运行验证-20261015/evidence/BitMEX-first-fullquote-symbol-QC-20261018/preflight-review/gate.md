# Full quote symbol QC 静态 gate

PASS_STATIC_ONLY。允许唯一执行Owner按封存scope进行一次完整对象GET与流式结构/QC扫描；不是已下载、已通过数据QC或盈利结论。静态审阅者0公网、0行情文件读取、0helper执行；只读小源码/配置/封存身份并使用AST解析。

核对输入：helper最终12445B/SHA256 `1e384f17e496f4fbe7645127d23281d933cec166ef6df2bb4a63fe02334fcf00`；config与scope均4609B/SHA256 `1a1a0bfd3488b6843bd6aab5f672e97c05483f55f20c1769cb0384e03eb2fc92`；旧prefix验收1394B/SHA256 `9ce696b81c1357abce6916357417256a6725bbb97bd71d4702b3de42ac3918c9`。seal为1143B/SHA256 `a66ae239b96a8680a16f91894b3acd6c6e720f80ccbd4c4acefd0d2a7cf7bf64`；全部4项本地逐字节核对匹配。精确path字典见gate.json。

## 静态支持的边界

- helper L43–69：唯一固定普通GET，匿名/noCookie/no代理身份、默认TLS、禁止重定向；If-Match与identity编码；status200、Content-Length99509710、ETag、编码在body前验证；限长流式写入且只额外1字节探测oversize，不重试。全文件SHA与既有首1MiB哈希在下载流中计算；首段匹配后才将文件交gzip解码。全SHA为新取得对象指纹，不冒称已有独立expected全SHA。
- L21–32、72–85、114–117：gzip.readline分块读取，logical CSV record累计8192B、64列、4GiB展开上限；不把整个文件逐字节扫描，不落展开CSV。完整迭代到decoded EOF，依赖Python标准gzip在读取尾部验证trailer/CRC；CRC/EOF异常将失败，不发布完整成功摘要。解码前后stat身份比较。是否实际正常EOF/CRC仍待执行回执。
- L79–120：扫描全文件，不在找到XBTUSD时提前结束。全symbol inventory上限4096、symbol长128；repeatedheader/坏宽度/空标识保留计数。总record、宽度、symbol、target、各字段分类、时钟分组有守恒检查。
- L91–113：仅固定XBTUSD作数值QC；empty/parseerror/nonfinite/negative/zero/finitepositive互斥计数。locked/crossed只要求两价格finitepositive，不与数量资格混用；strictvalid要求4字段positive且ask>bid。仅导出计数，无真实price/qty/time值或统计分布。实现使用Python float分类与比较，不能据此认证任意精度十进制相等性或经济单位。
- L107–113：canonical D9时间字符串按物理target顺序作相邻equal/backward/forward计数；坏targetclock、未知宽度、空identifier、重复header重置前值，不跨这些坏行暗连。其他有效symbol不重置target前值。无排序、补值、时钟修正、间隔收益、事件/接收赋时或UTC精度认证。
- L131–163：exact seal/gate绑定、exclusive formal lock和输出创建，截止与0.1s采样的256MiB combinedRSS/300s/128MiB盘监督；stdlib单worker与supervisor、线程环境2，无SDK/安装/账户/模型。失败或超限STOP，不重跑。资源为采样监督，不冒称OS硬限或零瞬时超量；总QC与验收300s仍须以最终实际回执判定。

## 唯一实现修正

初版监督路径缺少异常清理，ps或run.live保存异常可能留下child。Owner仅增补L139–161 try/except/finally：监督Exception转sanitized STOP，并确保仍活的child terminate→wait3s→kill/wait。已核与before-cleanup快照的完整文本diff，仅此生命周期改动；GET/QC/科学规则未变。修正后AST解析通过，尚无formal lock。未运行合成测试或来源代码。

gate只对封存版本支持一次执行；实际HTTP身份、全对象hash、完整gzip EOF/CRC、计数、资源和无活动worker由执行Owner与最终review核验。用户既有常规研究授权覆盖本步骤，无需新增逐步许可。actual assistant model/route UNKNOWN。
