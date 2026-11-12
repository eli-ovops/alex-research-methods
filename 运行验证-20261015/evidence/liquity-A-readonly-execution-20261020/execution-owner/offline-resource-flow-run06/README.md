# run06 完整资源/一次输入候选，未应用/未运行

新auth dbf66a…精确引用完整提案/审阅/旧extra2h9db20和peak9b6c，旧文件不改。旧auth/旧peak截止仍校验其原始历史值，新effective_resource_limits overlay再精确覆盖CPU18000、盘8GiB(保留1MiB)、08:29:58–10:29:58/累计7.5h、主动9h预算含旧8h预留+新1h；其他帽不变。运行Budget/实际Evidence/forecast/OS RLIMIT/累计prior一致；OS CPU只给18000减Rootprior与本进程配置childCPU后的进程余额，不能重置累计CPU。全新run06仅承接1824CU/41methods/最新CPUledger>=6676，人工历史仍UNKNOWN，operating-costs原件不填零。

两阶段：Root先签root/run06-preinput-release.json，status RELEASED_READONLY_A_PREINPUT，其他字段与正式release相同（精确code/binding/run/auth、peak、effective_limits、priorCPU、activebudget）。Owner在Root明确放行后仅执行一次 `readonly_collector.py --prepare-input <binding>`：无key旧样本按当前UTC含等待零点预筛+actualstatvfs+quota/身份+一次existingroute strictTLS，无目标HTTP/API/RPC；独立no-key-preparation.once.lock及带UTC/十分钟或入口截止更早到期的receipt。失败结束本单，不反复probe。旧waitCPU未单存，预筛使用旧完整周期CPUmax作为明确标记的保守样本代理，非未来保证；输入后全部新块检查仍须完成。

Root核PASSreceipt后签root/remaining-preflight-run06-release.json，status RELEASED_READONLY_A_PREFLIGHT，额外绑定no_key_preparation={path,sha256}；再唯一打开已审launcher。collector只本地重核receipt/hash/代码/auth/到期、当前样本预筛+实际盘，不再publicprobe。首次入口<=09:29:58且余>=1200s，新activebudget used+reserved<=3600且reserve>=1200；输入等待alarm在10:09:58以前结束以留20分钟，输入后恢复10:29:58启动alarm。input-entry.once.lock确保只有一次真实TTY隐藏输入。任何失败终止，不自动新入口/重连/降低覆盖。正式运行所有新身份/五runtime/独立B/WS/count/fullscans/timeliness/resource照原协议；只有完整PASS同进程ARMED，先取消启动alarm，按T1/全部累计帽观察原14UTC日。未ARMED不称运行。

Root两份release还须 resource_flow_authorization_sha256=dbf66…、effective_limits完整等同该auth，new_active_work_budget={used_seconds_conservative:int,input_preflight_and_closeout_reserved_seconds:int>=1200}且sum<=3600。正式release加有效prep receipt，最终prior>=新CPUledger6676。无需用户再答已输入；Root仅看安全stage/PID，不看Terminal/key。

检查只针对新overlay/CPU与盘一致性/oldforecast/时间窗/过期/单输入单probe/旧父auth保留；所有socket.create_connection禁止网络，标准库+既存官方封存输入。7PASS原回执，初次测试夹具漏authorized_peak导致1ERROR已保留initial回执，修夹具后受影响7项PASS。无模型/网络/安装/新钱包/交易。所有源码/锁/旧原件尚未改。静态与测试不证明新实际准入/利润。
