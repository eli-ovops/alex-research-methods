# 单次匿名Ethereum chainId诊断：未执行

唯一业务目标为 https://eth.drpc.org/ 的一次POST，固定eth_chainId、params=[]、id=1。脚本不导入旧core/collector，主源码身份在manifest中只读绑定，原A/once/证据不变。

Root静态审阅并发明确执行指令后，才能由独立外层wrapper用项目既有.venv/bin/python -B -E -S启动；stdin=DEVNULL。执行前核精确源hash、once/result/raw均不存在。外层monotonic整wall20秒到即终止，监控本进程及scutil子进程累计CPU5秒并超即终止；脚本另设进程RLIMIT_CPU=5和SIGALRM20。后者不是父子合计CPU硬帽的替代。wrapper需保存实际整wall、CPU、exit、stdout/stderr字节数/hash，不保存任意stderr原文。

内存目标128MiB，由外层监视RSS并超限终止；macOS采样监视不能证明两次采样间绝无瞬时超限，不冒称RLIMIT_AS等价RSS硬帽。目录总新增上限128KiB，成功raw最多64KiB；外层亦须核总文件量。scutil输出只在内存，固定安全env不是读取现有env。只解析HTTPS启用、HTTPSProxy/Port和PAC开关；必须为IP literal loopback、有效port、无PAC。配置缺失、名称代理或无效值均停止。现有路由仅一次读取，不认证、无DIRECT或DNS回退、不改系统。

CONNECT只含eth.drpc.org:443，响应头8KiB、逐字节读避免过读TLS，非200立即停止且不落代理响应。TLS使用默认CA与hostname/CERT_REQUIRED，固定SNI eth.drpc.org；成功前不发送POST。各I/O剩余超时最多5秒，请求累计15秒；外层20秒涵盖整个进程。

一次锁在配置/网络之前独占建立。发送前后分rpc_attempted/send_started/send_completed；中途失败不冒称服务收到。尝试1方法则共享方法数63→64，即使无有效响应；未走到业务发送则0新增方法尝试。dRPC CU为UNKNOWN，不与旧Alchemy32734CU混算。

HTTP非200、拒绝、重定向、JSONRPC error或schema/chain身份失败都结束，不重试、不跟随。只在HTTP200且精确jsonrpc/id/result三字段、规范hex结果0x1时保存公开原体和完整JSON。其余响应只保留已读字节/hash、整数HTTP状态和固定错误类别；没有异常str/repr/traceback、动态类名、raw header/body输出。错误体被截断或读取失败时已收大小未必可确知，不能冒称完整响应。任何阶段失败均本单结束，不能据成功推newHeads、FULL_A、时效或经济有效。

已完成检查仅源码AST/compile，无导入、无客户端/网络执行。Owner准备CPU保守预留15秒属于本新共享预算，非实测且不得再次叠加；Root10秒另由Root登记，未来guard7215。0付费/安装/账户/密钥/钱包/模型/交易。待Root审阅，不创建实际执行回执或假once。
