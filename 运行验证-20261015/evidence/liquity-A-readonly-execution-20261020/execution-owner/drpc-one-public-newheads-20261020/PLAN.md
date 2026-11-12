# 匿名newHeads：隔离候选，未执行

唯一固定wss://eth.drpc.org/，既有system HTTPS loopback路线只读一次（IP literal/validport、HTTPS开启、PAC关闭），CONNECT/SNI同host。无账号/key/auth、env读取、DIRECT/DNS代理回退、改配置、重连或重试。不导入旧core/collector；原主源只做身份绑定，原A与T0/T1不动。必要codec参考原core HeadStream L396–441（nonce/accept、masked客户端帧、read_exact/帧检查），去除Alchemy HOST/key/计费/副作用耦合；新增严格Upgrade/Connection、重复头检查、限额及有界fragment重组。

Root必须先静态审阅并明确允许执行；本目录probe.once/result/三raw未存在才允许唯一启动。项目.venv/bin/python -B -E -S，stdin DEVNULL、固定安全env。外层整wall45秒，父子累计CPU5秒采样超限终止、RSS128MiB目标采样监视；脚本本身CPU RLIMIT5、SIGALRM45。采样不保证瞬时峰/短命子进程绝不漏记，macOS不把RLIMIT_AS冒充RSS硬帽。执行/封存属本Owner15秒准备+执行CPU预留内，Reviewer3/Root7由Root合计futureguard7240，不双计。所有新文件合计≤256KiB。

连接/TLS/Upgrade合计阶段deadline起始+15秒，各I/O≤5秒；整个进程45秒。Upgrade头≤8KiB，逐字节避免过读，严格HTTP1.1 101+Upgrade websocket+Connection Upgrade+SHA1 accept，禁任何extensions/subprotocol，未请求压缩。拒绝header仅bytes/hash，拒绝body不读/不存且hash UNKNOWN，不为取拒绝体延长或补请求。

一次eth_subscribe id1 params[newHeads]。等待ack+首头共同≤30秒（从subscribe发送完成计），接收I/O timeout可达剩余30秒以覆盖正常出块等待，受整45秒约束；不把每5秒socket超时当自动重连/反复接收。只有一次规范ack且subID为有界hex，第一条通知必须绑定它。

接收总≤128KiB（包括Upgrade头与WS framing），单text重组≤64KiB，收到帧≤16、control≤8。服务器mask/RSV/非规范length/控制帧碎片/不正确continuation/非text均停。fragment支持有界text+continuation，不协商extension；Ping→masked Pong不算RPC。Close即停，最后只本地close，不等待/重连。若unsubscribe期间出现其它消息或错误，不跳过重读。

头完整性：要求number/hash/parentHash/timestamp/baseFee及标准header hashes、gas、difficulty、nonce、bloom、miner、extraData字段规范；允许有限标准fork扩展。未知字段或不匹配停止，不猜未来schema。age按本机application-read UTC减头timestamp，[-2,30]秒为本机通过；不是wire/provider/global时效证明。保存接收UTC/monotonic、number/hash/parent/timestamp和规范公开原消息。订阅ack、头、unsubscribe ack三份原体均先验证再落盘，不存provider错误消息/动态异常文本。

若收到头且剩余≥2秒，最多一次eth_unsubscribe id2同subID，ack等待≤min(5秒,整余量)，不补发。头收到和unsubscribe成功分别记录；unsubscribe失败仍保留已收头事实，不声称释放成功。即使age失败，仍可在剩余时间内尽力unsubscribe一次后结束；绝不启动14日。

方法旧总64，发送前记逻辑attempt，send_started/send_completed单列，最多2→66。dRPC官方文档刻度subscribe20CU、notification20CU单列，实际收费、匿名月额度、unsubscribe成本UNKNOWN；不套Alchemy .04/byte，旧Alchemy32734CU不动。本单无chainId/head HTTP/其它RPC。

检查原件：10项合成codec检查一次exit0，STDERR0，无系统路由读取/无network；这些检查不等实测WSS/newHeads免费资格或稳定性。当前仅PREPARED，等待Root审阅指令。
