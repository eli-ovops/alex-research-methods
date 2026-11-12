# 已存传输成功/失败路径静态因果核查

结论：没有找到能据现有源码/原件认定为本次TLS握手超时根因的实现缺陷。停止盲改超时、TLS、代理或连接复用，也不继续含key试跑。公开probe只把其当次失败缩小到CONNECT200之后、严格TLS握手中；02原粗OPEN仍不能追认同一子层。当前基线及所有旧失败保持不变。

核查UTC：2026-10-20T11:36:45.351421+00:00。0网络、0采集器/测试/模型/输入/系统配置读取或修改。仅已知源码、已存小型安全回执和实际已安装Python3.12标准库定义。用既有项目Python -B -I -S/inspect只显示stdlib构造/包装定义，没有建立SSLContext/连接或运行客户端。

| 核查点 | 源码位置与实际差异 | 可支持的结论与边界 |
|---|---|---|
| 有效5/15秒 | readonly_core.py:260–280：remaining=min(5,min(15,timeout)-elapsed)，TLS前settimeout；RPC:308–330以15秒剩余额调用；collector:491–495准备传10秒并外层10秒alarm；public probe:46–56传15秒剩余额，另20秒外层。 | 三者初期TLS I/O都最多5秒；10/15并不使TLS握手获10/15秒。确有‘总窗口与单次I/O不同’这一实现事实，没有证据5秒过短就是根因，更不能据此放宽。RPC后置settimeout剩余15与public后置min5发生在TLS返回后，不可能导致此前TLS超时。|
| CONNECT解析 | core:270–279固定CONNECT，recv(1)逐字节，遇首CRLFCRLF止，8192字节帽，状态必须200；candidate仅加固定phase回调。 | 没有读过分隔符并吞掉TLS字节的代码证据；到TLSphase意味着解析已过200。200只证明代理接受隧道，不保证目标端TLS往返正常。|
| SNI/CA/context | core:261严格check_hostname+CERT_REQUIRED；280 wrap_socket(server_hostname=HOST)；readiness493和RPC302/public44均create_default_context；RouteHTTPSConnection292传显式同context。实际stdlib http/client.py HTTPSConnection.__init__收到context只保存，不替换为另一个默认context；ssl.py wrap_socket默认do_handshake_on_connect=True。 | 未发现错SNI、关闭CA/hostname、HTTP wrapper重设context等证据。不同时间CA内容/真实网络出口是否完全相同没有封存身份，仍UNKNOWN；不读取/改CA或私有配置来猜。|
| socket timeout传播与生命周期 | ssl.py:983保存sock.gettimeout；1040恢复该timeout，1053在wrap时握手；1054–1060异常close；1325–1333握手保持timeout。core:281–288失败清理；RPC303–307/373失败关闭并锁会话。 | timeout确实传至TLS对象，未见丢失timeout或泄漏旧socket导致本案的证据。公开probe是新connection，未到HTTP，故持久HTTP reuse不是该次触发因素；02原始也connection_reused=false。|
| 成功准备为何不保证后续成功 | 10:30:31和11:03:57准备同open_tls成功TLSv1.3，然后立即close，无HTTP业务。11:08:04首次RPC粗OPEN超时；11:30:10公开probe经同helper+纯phase候选在TLS握手超时，HTTP尚未发送。 | 成功/失败发生于不同时间和新连接；‘同一固定系统路线策略’不等于已证同一上游出口/解析/代理状态/服务端状态。密钥/HTTP路径尚未参与公开失败，不能把本次失败归密钥；也不能据此认证旧key或RPC可用。|

补充限制：15秒总elapsed守卫是在阶段/I/O边界检查，HTTP内部连续响应头读取与底层行为没有跨所有内部步骤的精确15秒强制抢占；public外层20秒是本轮硬wall帽。这是已知控制口径，不是本次约5秒TLS TimeoutError的根因证据，当前不扩重构。前述解析、默认context和cleanup静态正确不证明网络长期稳定或没有所有潜在Bug。

**当前代理应用/日志入口：UNKNOWN。** 现有项目源码仅以`scutil --proxy`读取获准的系统字段并要求loopback literal/PACfalse；此前已读LOCAL_BLOCKERS相关条目也只记系统路线，不给应用身份或日志位置。不能由端口/loopback猜测具体代理软件或日志目录。本轮未搜索应用数据、未读取日志/配置值/凭证/环境/进程命令行；Root需先有独立安全入口才能考虑下一窄读。

**唯一最有信息量的下一证据**：若本机既有代理软件已留存11:30:10.477–11:30:15.479Z这条固定公开目标连接的上游建立/握手失败记录，取得其仅UTC、阶段、是否上游连接建立、固定错误类型/整数错误码的脱敏原件。禁止带API路径、密钥、代理配置值、凭证、原异常文本或全量日志。它可帮助区分代理隧道接受后未真正建立上游/出口无响应与目标TLS协商问题；当前日志是否存在、是否足够区分均UNKNOWN。本轮不访问该日志、不启动任何新probe或用户输入。没有此类证据时应明确原因未定并结束本支，不再凭短timeout/换实现盲修。

读取身份：
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/readonly_core.py` — SHA256 `54b09fc1d32186dfca56c0a8eb15b6172b335693824489676ba47c627c7af5bc`
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/readonly_collector.py` — SHA256 `2284076c49b25393fc057fafcbccb46a4bcf671b67303063f109c5d06077c485`
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/safe-open-phase-candidate/readonly_core.py` — SHA256 `96f67fec33e5d23edc3e67b029ccd695e23fa747176315a784ad62bde92eb82f`
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/public-no-key-phase-probe/probe.py` — SHA256 `462ca945308fb3ff5122c071c74c85f533273b0de4de1acdc92622955d62e501`
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/runs/throughput10s-attempt-01/no-key-preparation-receipt.json` — SHA256 `cc7520d9dfbe8e64dd915118a7e2df2f9f307b1fdd917dc69f8fe9a8c30d8f12`
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/runs/throughput10s-attempt-02/no-key-preparation-receipt.json` — SHA256 `fc4dc5b6baacb54f24beb0b713ea18063cfb98d1f3b3e8850abe98a6e18442bf`
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/public-no-key-phase-probe/result.json` — SHA256 `c3ca96b211558a9f43ab92e8636e7ba8ea68629a7515c981f88e57cae3589d86`
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/attempt02-publication/terminal-diagnostic.json` — SHA256 `7e07d232c2f190364848af245dc5b3b11bfc76a34432ac47d66abe1ddd750be6`
- `/Users/USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/http/client.py` — SHA256 `c2c0694155837d72fc710a4138e5d1e53ae1a652b117a2e23a5b1b0db527a0f9`
- `/Users/USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/ssl.py` — SHA256 `db62eeaae59c6e7087dcafb28087cd0bb092087381edc556f97c8cb614484380`

安全原件边界：attempt02诊断7e07d232…保留原HTTPnull/粗OPEN；公开result c3ca96b2…为TimeoutError/TLS_HANDSHAKE、TLS_completedfalse、HTTPnull。TLS类型分类false不是TLS已完成；正文0不是全网络0字节。未扫描归档、私人行情/QC、环境、秘密、Terminal/argv、剪贴板。

资源：本轮静态技术调查Owner主动≤20分钟，保守CPU借记10秒（不是实测历史CPU）；全命令CPU无法精确汇总则UNKNOWN，按本有限预算扣记，不重置前32734CU/63methods/既有6970账，Root下次去重账只追加本轮10一次。新增文档<64KiB，0付款。没有主源码/旧文件/锁/发布/自动化改动。核查结束，Owner停止。
