# 执行前静态gate

**PASS_STATIC：仅允许本次封存输入的一次footer-only QC执行。** 本审阅未执行helper、未联网、未取得任何目标字节；运行成功、206身份和资源使用仍待执行回执验证，不能把gate当数据QC完成。

已完整读root/scope.json、最终helper/config/seal与已有dependency/session preflight。最终helper SHA256 `384740874e5c315c79175254a1cb6084738af2051bd0be81a383d6726b4f43c6`；config `c09fad09ce2ff552e11dbf460d988b24a08be5ea7d81598a1bab5685050ea72e`；scope `0404632466882d1d7bcd321b9e96c6ea6031c3e5ac78b07ba41041c188ff5711`。gate.json以完整绝对路径→sha256/bytes绑定三项。

- helper:35–65最多3Range：尾8字节、按尾部声明取得≤1MiB footer、头4字节。每次先核206、精确Content-Range/Length、ETag和version；通过后才body read，累计应用body≤1,048,588B。非206/身份不符/异常不重试。
- helper:22–23、34、41–42关闭redirect并显式空ProxyHandler；使用默认严格TLS，不带认证、SDK或凭证查询。只对scope内精确URL发GET/If-Match。
- helper:60–70校验PAR1与长度，构造明确标示的人工metadata-only容器，调用pq.read_metadata；71–81仅schema/types/counts/rowgroups/encoding/offsets及metadata键名，不访问statistics、价格行或数据页。
- helper:88–101核gate/source seal并用exclusive formal-started.lock锁住一次正式尝试；修改输入后gate不再匹配。worker继承隔离解释器路径，PyArrow版本核验与2线程设置保留。
- helper:103–117按100ms采样监督combined RSS512MiB、累计300s、截止与8MiB磁盘；超限终止/必要时kill。**这是采样监督，不是绝对瞬时RSS硬限保证**。执行后须审实际回执；preflight的既有74.8MB峰值不是正式运行峰值。

本轮唯一真实修正已复核：原save直接json.dump可能先写超8MiB，最终9–13改为UTF8预序列化、现存+待写bytes检查再exclusive写入。与保留before-disk-guard源码diff仅此变更。已有preflight实测Python3.12.14/PyArrow26、exit0、0.547623166s；发生于修正前，只作为依赖健康证据，未冒称最终helper整链运行通过。

运行中仍必须验证：真实3Range响应与字节上限、对象身份、footer解析、无数据页读取及输出清单、累计时限/磁盘与采样RSS、worker已退出。任一失败按scope停，不调参重取。输出只能证明footer声明，不能证明实际行连续性、时间值质量、全文件checksum、预测优势、净利或容量。

Owner为/root/reusable_academic_case；独立验收/root/train_forward_review；本gate仅静态责任。规则版本未变，actual route UNKNOWN。0helper执行/公网/市场数据读取/模型/统计/回测/交易。仅preflight-review两交付物，无清理项。
