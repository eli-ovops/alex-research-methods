# 正式A匿名入口：只准备、未发布、未联网、未ARMED

本目录是唯一隔离正式候选，不改原core/collector/binding、已结束的attempt和预检原件。T0=2026-10-21T00:00:00Z，T1=2026-11-04T00:00:00Z；原14日coverage、全集/因果/oracle-last/fence/费用/episode/审计/经济门不变。无key、真实TTY、Terminal、账号、模型、钱包、签名、广播、交易或付款。本候选没有守护服务、自动化或系统睡眠设置变更。

## 交付与精确复用

- adapters.py从已实测预检适配器逐字节继承主体，移除临时30方法和6MiB目录限制；原工程Budget累计25M/400000/10秒3000/18000CPU/1GiB保留，Evidence仍累计8GiB-1MiB、data-key delta完整还原。RPC仅扩至实际必需的7只读方法：chainId/getBlockByNumber/getCode/eth_call/getLogs/getTransactionByHash/getTransactionReceipt；eth_send*/wallet/sign无路径。日志返回达到10000条即记录原体后完整性UNKNOWN停止，不将provider截断当零或完整。
- stream.py复制已通过MF1/MF2的PublicStream/终态守卫，保留strictUpgrade/TLS、单WS/无重连、已recv字节成功失败恰一次工程结算、error不存原文。FormalWire将预检全局180s/16frame/128KiB累计帽移除；仅每条message≤1MiB、每条最多16frame/8control，累计字节/方法/CU/CPU/盘按正式Budget。每条消息接收≤60秒，无消息/断线即停。临时TimedWire仅用于有界首次Upgrade/ACK，正式头接收改用FormalWire。消息尾计数保留16项/通知样本保留128项，全部原体和预算记录仍归档，不把内存ring当丢弃原件。
- observer_loop.py保留原run_live从tracker/Episodes到窗口结束的完整正文：T0后每个新区块完整Scanner/qualify、首个因果可用协议价冻结USD锚、一次episode/每日选择、100块Liquidation posthoc audit、1000detail/192MiB/120CPU allowance、oracle policy skip、重组invalidations和coverage UNKNOWN都保留。仅加所有预热头也走parent/number连续性检查，以及首个完整正式snapshot的OBSERVING状态证据。未重写或测试策略结果。
- observer.py负责Root精确发布、累计用量、必要新接口刷新、原forecast和状态/终态。绝不调用旧run_live/prepare/getpass；无重跑旧完整预检。正常结束仍只是WINDOW_ENDED_PENDING_INDEPENDENT_REVIEW，不自动经济通过。terminal归档保存失败强制STOPPED/非0，已失败层另存；当前活进程/ever_ARMED与历史状态分开。

## 发布前后最小动作

当前binding.template.json为PENDING_ROOT_BIND_AND_RELEASE，故不可激活；binding.json/formal-start.once/evidence/runtime-stage/terminal均不存在。Root实质验收本候选及精确diff后，可仅将template的publication_status改为BOUND_FORMAL_A_WAIT_ROOT_RELEASE并保存binding.json；其它值不变。Root另写固定root/dRPC-formal-A-Root-release-20261020.json，schema必须含：

    status: RELEASED_FORMAL_A_ANONYMOUS_READONLY
    binding_sha256: 实际binding.json SHA
    code_sha256: adapters.py/stream.py/observer_loop.py/observer.py四文件完整SHA
    limits: 与template limits逐字同值
    T0/T1: 原固定窗口
    prior_usage: {Alchemy_CU:32734, shadow_CU:不小于33850, methods:不小于93, CPU_guard:不小于7440}
    startup_deadline_UTC: Root发布时指定的有效启动截止，必须当前UTC<deadline<=T0

该release受Root唯一目录控制；其自身SHA在运行证据记录，不作互相引用的循环hash。若需改源码/经济/资源/启动算法，先同Owner集中修复审差异；不能用新Root配置绕过硬编码原帽。Root后续静审/发布实际CPU预留必须更新prior_usage，当前7440只是含Owner60+此前5秒独审借记的保守floor，非精确实耗或新资源池。

只有Root明确正式启动单后，可通过普通受控进程执行项目.venv/bin/python -B -E -S 本目录observer.py；stdin DEVNULL、固定安全env。无需用户复制任何地址或再次输入。Owner本次不启动、不应用、不控制Terminal。Root可沿原liquity-a-14只读监测，不新增自动化。发布后若本单失败，唯一once/终态保留，不自动再启动/换provider/改参数/重连或移T0。

## 启动时仍需的新读（不是重复已通过预检）

1. 读取并核Root真实完整预检验收e9e07e4…、旧result e8c21ac…、所有源码/binding/ABI/runtime/常量/政策hash；原完整3 measured cycles保留，不挑最快。核有效Root新release，建立本目录唯一formal-start.once。核当前物理盘、CPU/方法/工程影子及原T0是否仍可完整覆盖；不读浏览器/凭证/环境值。
2. 新初始B/H：一次chainId、一次latest header、5个同H EIP1898 getCode逐字节runtime比较。启动兼容性一次getLogs(TM,B..B)，按该B的transactions第一列hash各读一次transaction/receipt并核同B/H/hash，再number fence。块无交易/任何接口失败即本单停，不换块挑样本。这只是必要7方法接线，不是盈利样本/钱包史/执行交易。接口0日志只证明该范围本次返回，未证明未来容量。
3. 原独立参考层精确两BlockCypher公开GET：chainroot及固定B，ETH.main/height/hash/Block.time一致；不把root.time当块时间，不扩源/重试。无key dRPC RPC/WSS均只读一次的同一既有systemloopback IP/port，CONNECT/SNI固定eth.drpc.org/defaultCA/hostname/CERT_REQUIRED、PACfalse。独立参考沿原明确直连/NoProxy安全路径；其拒绝/错误同样停止。
4. 一个新WS，ACK绑定，先一头initial完整snapshot，再下一连续头1个稳态完整snapshot；原N可变，不能固定105，初始原padding公式不得超过已准入上界160。第一个initial额外count只作为startup实际借记；新稳态measure scope与旧3个完全相同：通知+完整同H扫描+保存，methods仍3。P/N增长、ID不全/重复、依赖改变、oracle异常/不支持mode、陈旧/积压/处理≥12秒按原门停，不缩全集。
5. 按原forecast把旧3周期+新1周期取各项max，旧/新wait样本及通知字节也取保守max；加入最新累计用量、当前物理盘、至原T0等待和审计储备，另核实际filesystem free够追加预估与安全空间。不得丢旧最慢样本/把current4方法initial当稳态3方法，也不重新优化经济规则。全部PASS才取消“启动”alarm（防止它误杀正确ARMED的14日进程）、写ARMED_ACTIVE_PROCESS/PID/T0/T1。观察仍同进程，无第二输入或重启。

正常启动预计19外层方法：identity7+3新审计方法+1fence+subscribe1+initial4+steady3=19（逐项实际记账，不按预计填数）；独立metadata两GET另列。正式方法帽400000不采用临时30。任何额外重复/控制帧不是无成本：控制不是RPC但接收bytes进影子结算，失败即停。

## 资源与事实边界

保留历史Alchemy32734CU；工程影子当前33850、全供应商methods93、当前future CPU floor7440。项目25M是原费表工程等效硬帽，不是dRPC余额或账单；匿名actualCU/月余额/长期SLA/共享IP其它负载UNKNOWN。dRPC免费backend timeout2s、JSONbatch3、logs10000、每IP通常120000CU/min（高需可50400且网络可不同）独立适用；不用HTTP roundtrip15秒冒后台2秒或免费资格保证。现有公开free政策允许本有界技术接线，真实拒绝/429/收费要求必停，不切paid。

正式无预检30method/6MiB/180秒/全局16frame限制：累计25M/400k/18kCPU/8GiB盘/1GiBRAM/2线程/付款0。RPCbody8MiB、WS每message1MiB是原类尺度的有界防护，单头通常远小但不写假精确大小。CPU OS限制按18000减Root最新guard/子进程旧借记，进程CPU/RSS每方法/接收chunk核；macOS RSS是可得peak监测而非硬RLIMIT_AS保证。源码准备新增≤2MiB/Owner≤45min主动/≤60CPU预留，观察实际写盘另归原8GiB且Root未发布前0网络/0样本。

原实际预检历史投影（不改旧账）为未来工程15152905+已用33850、methods305408+93、disk7023411200B、CPU13520.668605（当时guard7365）。新release必须从最新guard/当前盘/等待更新，不机械复制历史PASS。匿名服务未知不填0；实际人工/基础设施成本没有实耗账仍UNKNOWN，不能用CPU、AI wall或人工预算冒成本0。A只是情景观察，不认证个人真实成交/利润/alpha/容量。

## 离线验收与未完成

本次仅8项针对正式接线的合成护栏一次PASS：累计>16frame/>128KiB且起始早于180秒仍可读、每消息控制限制、7方法allowlist、logs10000 fail-closed、PENDING模板不激活、终态保存失败不能成功、原完整经济/Episodes/audit正文（剔除明确continuity/状态证据新增后）逐字一致、方法累计不重置且不再临时30封顶。无策略执行/收益计算、无系统route/TLS/API/WS、无客户端main；检查并非实际14日或未来稳定性证明。

尚未：正式Root独审发布/填真实binding与release、上述必要新读与同进程ARMED、任何T0后样本。所有新参数发布与主code hash须精确验收，Owner不自行启动。
