# 一次公开无密钥phase probe实际结果

状态：STOPPED_PUBLIC_HEAD，唯一执行exit2，无重试/回退。发布核查11:30:10.329530Z，早于有效期11:32:42.339490Z；执行前本目录once/result均不存在，现保留独立once和结果。

固定系统路线阶段到达SOCKET_CONNECT→PROXY_CONNECT_SEND→PROXY_CONNECT_HEADER→TLS_HANDSHAKE。TLS_HANDSHAKE发生TimeoutError，约5.048786167秒；TLS_completed=false，HTTPstatus=null，未到HTTP_REQUEST_SEND，所以实际HEAD请求未发出、API/RPC0。public_transport_HEAD_attempts=1指本公开HEAD诊断逻辑尝试一次，不是成功发送一次HEAD。已验源码只有CONNECT状态200才会进入TLS阶段，因此前置TCP/CONNECT通过；不保存原响应头或路由值。

安全异常：TimeoutError/NONE、errno/verify_code null、timeouttrue、TLS类型分类false、certverificationfalse、固定Stopcode null。TLSfalse只描述异常类；明确phase把本次超时定位到TLS握手，不能据此前02粗OPEN记录追认同根因，也不能推密钥错误/失效、付费或供应商永久不可用。显式body读0，不意味着网络传输0字节。

真实wrapper整子进程wall 5.160184542秒（monotonic在subprocess.run前后，非工具等待），外层20秒未触发，stdin DEVNULL。子CPUdelta 0.076895秒；内部processCPU 0.063368、child 0.004966秒，范围不重复相加。stdout20B/stderr0。计算包含原本共享30预留，不新增借记；未来guard6970、旧32734CU/63RPCmethods保留，逻辑公开transport尝试另记1，实际发送HEAD0、RPC0。

result.json SHA `c3ca96b211558a9f43ab92e8636e7ba8ea68629a7515c981f88e57cae3589d86`；execution-receipt.json SHA `d555d3e408425500a6d84739d947d41c9300b4fa5dda235a5c363e5c60a18e05`。实际stdout SHA `2796704abfff0d09b09f4b80521ee5721d43757e97b0dd230c43f2007c1b6496`、stderrSHA `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`，全部在 `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/public-no-key-phase-probe`。无原header/body/异常文本/URL/key落盘，主采集器/候选未改。

本次失败结束，未启动A、未输入、未重试。唯一新增事实为‘当次既有路线CONNECT之后的严格TLS握手超时’，不是02根因或修复结论。后续如有必要仅由Root依据此证据界定；本Owner已停止。
