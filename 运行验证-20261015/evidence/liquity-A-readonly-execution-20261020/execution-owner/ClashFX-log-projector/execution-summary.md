# 一次固定日志安全投影实际结果

状态：INCONCLUSIVE_FORMAT_OR_TIME_COVERAGE，唯一执行exit2。发布核查11:49:49.238468Z仍有效至11:54:01.511226Z；once/result此前不存在。格式未知按计划结束，未改规则或重新读取。

取得UTC11:49:49.354741–11:49:49.358317Z，初始size/读取前缀均721966B，prefix SHA d79a568f3c20d996aa3754243768e4afbde77f24d7f55a2e0d98f038abeb256d。inode/path identity检查稳定，本次fd后检未发现追加；不是atomic读快照，也不是可变日志全档不可变认证。无原文/原异常文本/片段保存或输出。

显式时区前缀两类各识别0行；未知时间4411行，过长0、尾截断0。因此目标日期/窗口/host/phase/error计数0均是‘没有可归属时间的统计’，**不能解释为该连接不存在或日志未报错**。不展示sample、不借文件名时区解释正文、不扩大文件/窗口，不换解析规则再试。

真实wrapper monotonic整wall 0.136398792s，子CPU user0.017419+system0.017035s。子RLIMIT_CPU soft/hard5秒，未触发；外层20秒未触发。wait4子进程peakRSS 21282816 bytes（macOS单位，含整个子生命周期）；8次pid-only ps采样max19087360B，采样不是瞬时硬内存帽，退出后peak亦<128MiB。工作数据≤16MiB是设计上界，实际独立working-set未测UNKNOWN，不将RSS冒充原字节缓冲大小。stdin DEVNULL，无网络/输入/采集器。

stdout37B SHA 093b8f83c9f31a32bfc3c37a3cd8308033dde564a252f3454719311aa0fc098d，stderr0B SHA e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855；仅数/hash，无stdout/stderr原文落盘。result.json SHA 4559d60dfd7b6be05035c3ed7d03b53f5064d4556dea0bb15f6876b72dedbd22；execution-receipt.json SHA 7abe61f0741be598bd3db8429b1377862f3da0e5906571ef9cb49a39f9f7d9b6；script SHA 3a586d3715fa8af281e9b737e738490c2403b1c0de87b2659200c83bf7380bce。全部固定安全字段可供独审。

资源计入既定新共享40/累计7040，不另追加本次Root执行子项，旧32734CU/63RPCmethods及所有原件保留。当前结论只是本受限投影无法识别时间格式，不支持代理上游或TLS根因判断。本Owner停止，未继续读取、联网、重试或改动主源/配置/旧02。
