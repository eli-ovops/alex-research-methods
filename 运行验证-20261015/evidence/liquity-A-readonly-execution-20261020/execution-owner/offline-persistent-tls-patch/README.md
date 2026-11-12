UNAPPLIED/NO LIVE：持久HTTPS候选与run02可审参数。

本机stdlib原件表明urllib每RPC强制Connection:close、新建TLS；这不证明本案EOF成因。三方案比较：OPEN失败重连重发会改变no-retry，未采纳；同服务严格默认TLS的HTTPSConnection复用一个成功读取组，失败关闭并锁死，不重发，范围最小；系统curl-q可用但不同TLS后端/HTTP2/AsynchDNS与子进程预算、stdin-config/输出错误脱敏需额外审查，不优先，不实际请求。

candidate_readonly_core.py保留白名单、CU/方法计数、strictTLS默认CA+hostname、15s总时限及分读剩余时间、8MiB体积、正常源原件/schema、失败不落rawbody。固定HOST443直连、path仅内存，不读proxy/env/credential，不redirect，不debug，不retry。成功server close只使下一新逻辑调用新建连接；任何OPEN/READ/HTTP/schema/body/disk错误关连接并failed latch，后续call拒绝。新HTTP异常仅固定白名单标识，无message/URL/repr/traceback。HTTPResponse.will_close分离socket时仍从response原socket设置剩余timeout，缺控制则failclosed。

candidate_readonly_collector.py仅新增成功启动身份组/snapshot fence/结果审计结束的close及finally cleanup，避免WS/newHeads或T0长等待携带闲置旧socket。状态/筛选/时效/费用/forecasts不改。参数集成固定remaining-preflight-20261020-02，独立runs/run02阶段/锁/证据，旧run01及A/diagnostic锁、原件保留，local160CU/10methods、CPU floor6117且Root最终release继续加所有新工作；08:10:50硬截止、既有全帽不变。

bindings与launcher是模板，不是运行入口；复用仍有效extra2h auth9db20...与Root新quota bc5a...，不伪造human approval。Root修复决定/精确run02 release及代码应用后方可有live；当前根目录core/collector/入口/release全未动，模板不能先用。Root最终priorCPU须高于6117+本候选30s+其它Owner/Root成本，不得清零。

证据链：首版11项mock安全测试PASS（baseline core46ee...留存）；run02 metadata只做1项静态AST定向PASS；最终READ timeout/evidence cleanup两保护只做2新+1受影响normalclose检查PASS。全部0network/0secret，既有35/7不无故重跑。测试不是真实EOF复现，不证明旧原因已知或已修复/实际速度/预算14日够/盈利。候选与模板冻结交原reviewer，仅ROOT可决定应用并开唯一入口，用户再次本地隐藏输入，不恢复旧key。

review-v2最小修复：真实HTTPResponse在Content-Length耗尽时会fp=None；READ循环先检查isclosed/length，已完整结束则退出，已关闭却仍欠已声明字节或EOF时length>0则RPC_INCOMPLETE_BODY失败。新增真实HTTPResponse+BytesIO假socket的close/Content-Length成功及截断检查，不联网。15秒仅各阶段elapsed/剩余I/O timeout，不宣任意DNS/连续header/body内部操作绝对精确15秒硬终止；此为原guard边界，未扩大重构。
