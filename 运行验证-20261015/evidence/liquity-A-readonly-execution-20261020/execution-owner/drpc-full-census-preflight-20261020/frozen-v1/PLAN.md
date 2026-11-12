# dRPC 原A完整状态与资源预检：候选未执行，绝不ARMED

Root及原Reviewer精确审阅本manifest/源码后，Root明确指令才唯一运行preflight.py。项目.venv/bin/python -B -E -S、stdin DEVNULL/固定安全env。仅本新目录写入，原core54b09…/collector228407…/binding2b4d…及旧锁/归档全保留。主入口不应用本候选，不调用run_live/main/prepare/input。原T0=2026-10-21T00:00Z/T1=2026-11-04T00:00Z不变，已过T0即停。

## 执行序列（网络前冻结）

1. 本目录preflight.once独占；核旧binding完整SHA、5 ABI/runtime记录SHA/chain1/address、必要方法和tuple/selector版本、常量和费用defaults源SHA、匿名公共政策原件SHA。只调用冻结Bindings构造器，不借旧PASS认证实时身份。
2. 系统已有HTTPS loopback IP literal/有效port/PAC关闭路线只读一次、内存驻留；RPC和WS均用固定eth.drpc.org CONNECT及SNI/默认CA/hostname/CERT_REQUIRED。无auth/key/env读取/DIRECT或名称回退/修改设置。失败即停、不自动恢复。
3. HTTP eth_chainId一次；eth_getBlockByNumber latest,false一次冻结B/H；5合约同H以EIP1898 {blockHash:H,requireCanonical:true}各eth_getCode一次，与封存onchainBytecode解码后逐字节/sha比较。关闭成功identity连接组。
4. 精确复用original.independent_preflight_reference：BlockCypher免token chainroot及固定B两GET（间隔1秒），固定chain/height/hash/Block.time与h.timestamp一致。root.time不冒block.time。原函数独立严格TLS+ProxyHandler({})/NoRedirect，无token/UA改装、无备用。两GET另计metadata，不计Ethereum方法；源错误原体只保留bytes/hash/固定类别，原正验证不动。失败即本单结束，不以dRPC自身日期代替。
5. 一个匿名WSS连接，严格101/accept/Upgrade/Connection，无扩展/压缩/协议协商。一次eth_subscribe newHeads。先保留原3个wait_samples通知/CPU/物理盘；第3头作initial完整snapshot，随后3个常规完整snapshot用于投影。因此正常共6个连续前向通知、4个扫描头。不是把initial额外count扣成稳态数据，也不混入methods的max。原forward_head/ChainTrack/timely原样调用：不同连续parent/number/hash、陈旧30秒/未来2秒、处理<12秒、无socket pending/backlog、重复头不计样本/有界次数、重组/缺块停。
6. 原Scanner.snapshot原样复用：initial count/padding32分组（N105仅上次事实，本次不固定）；每H base+完整IDs+全部status/latest债务/抵押和应计分量，registry MCR、SP、oracle原mode/lastGood/ethUsdOracle，fetchPrice永远是最后非持久eth_call子调用。原self.usd_anchor=None（预检在T0前，不偷设正式USD锚）；qualify和固定费用/风险/失败语义不改。不根据结果换规则，不拿0候选推永远无机会。
7. aggregate仅在HashScanner子类把input改data、bare H改EIP1898对象，outer from零/gas30000000/MC3/ABI编码及decoder原样；snapshot返回metadata同步为新语义，number fence仍同B/H。加同H initial count与base count一致性断言，跨H N允许在padding内正常变化；超padding、ID缺/重复、响应不全、依赖地址/初始runtime不符停。初始5个runtime只认证初始H，未谎称每个后续H都另取过5个getCode。
8. 每snapshot成功关闭HTTP组，下一新完整scan可以新HTTP组；不是失败后的重连/重发。WS只有一条且不重连。3 measured完成后最多一次eth_unsubscribe并收true ACK，再关闭；任何异常不补发，保留成功扫描事实与失败层。
9. 直接复用原forecast（三稳态完整周期，含通知+scan+保存的盘/CPU/CU/method差额），含旧已用、当前至原T0等待、14日100800块、每100块日志、1000条detail双方法/192MiB/120CPU审计储备、磁盘1MiB安全边界。失败details保留所有已算分项，并另列各原帽比较布尔；不以先触发disk就隐去CPU。全部PASS只写PASS_BOUNDED_FULL_CENSUS_PREFLIGHT_ONLY_NOT_ARMED，永无观察循环。

## 精确复用与最小接线

adapters.py只import冻结原源码定义；不触发旧入口。原Scanner.snapshot、qualify、forecast、timely、ChainTrack及Bindings不重写。DataEvidence仅data长度cachekey取代input长度，并加本单6MiB安全空间检查；原gzip+fixed64 delta/base SHA/可完整还原/缓存深度算法不变。RPC继承原class并保留其单方法失败锁/timeout/响应体/返回schema/安全异常逻辑；只换匿名destination连接类、4方法allowlist、证据分列bodybytes/hash/工程标签。原TLS路线必要片段仅固定目标改变。WS复用已通过的一次匿名probe的Wire/完整header schema，接入原Budget/Evidence/Tracker，非重新实现策略。

WS每消息≤64KiB/总接收≤128KiB、帧≤16/control≤8、规范mask/长度/fragment/UTF8/JSON、Ping→masked Pong；这些保守适配帽可能拒绝合法扩展消息，届时是适配不足/UNKNOWN，不泛称provider无能力。完整规范公共通知与响应gzip保存；错误不存原文。应用层UTC+monotonic是读取时刻，不是NIC/provider wire或全球最快。收到消息先留验证原件再delivered硬帽，不漏记已送数据。

## 三层资源，绝不伪造匿名余额

历史Alchemy32734CU保持；当前工程影子32945、全供应商方法71、CPU保守guard7365承接。shadow是旧Alchemy费表的项目工程等效刻度、不是dRPC实账或新Alchemy账。Budget保留25M/400000/10秒3000本地刻度/18000CPU/8GiB-1MiB/原2线程1GiB全帽。匿名实际CU、月余额、SLA仍UNKNOWN，不将25M填为provider余额。dRPC文档subscribe20/每通知20与unsubscribeUNKNOWN单列；公开免费policy作为本有界预检资格，明确拒绝/429/付款要求即停、不充值/切付费。

每方法attempt前按旧表借记，WS ack和通知按原ceil(wirebytes/25)工程delivery计量；wirebytes保守含本次交错控制帧，非dRPC供应商字节计费。RPC batch未使用，MC3内部子调用不是RPC batch。已知free服务backend2s、JSONbatch3、logs10000、120000CU/min/IP（高需求可50400且网络可另限）仍独立约束；并不把网络整roundtrip15秒误叫backend2秒保证，共享IP其它负载UNKNOWN，实际error/limit必停。

本单最多30外层方法（通常identity7+subscribe1+initial4+稳态9+unsubscribe1=22；正常到全方法93），另metadata2GET；新文件6MiB/单RPCbody1MiB/WS64KiB、执行CPU15秒/整wall180秒/RSS目标128MiB采样监视，原1GiB帽亦保留。CPU自限15+alarm180，外层合计父子/monitor CPU和wall/RSS/目录采样超限终止；采样不能证明所有瞬时峰或短命子进程绝无漏记，不冒macOS kernel RSS硬帽。Owner准备及执行60秒保守预留/Root20/独审10已合入7365，不重复追加。

## 检查与覆盖

唯一6项受影响离线检查exit0：5份Bindings、只复用原snapshot/economic/forecast身份、不调用旧live入口、EIP对象/data/from/gas编码、data-key lossless delta roundtrip（仅对旧公开head字节的合成变化，不是新链状态）、累计方法上限。无preflight.run、scutil/TLS/API/WS，非策略/收益测试。之后仅加metadata尝试计数，不影响已查接线；compile静态核。原raw/代码不改，不重复既有旧suite。新增代码/完整review-package.diff/精确manifest供Root和原Reviewer一次审。
