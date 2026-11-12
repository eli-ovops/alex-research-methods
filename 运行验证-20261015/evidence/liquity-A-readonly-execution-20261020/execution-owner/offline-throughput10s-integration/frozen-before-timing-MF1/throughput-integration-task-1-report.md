# Task1 隔离吞吐集成候选

状态：DONE_WITH_CONCERNS（离线候选和必要检查已交付，待唯一Reviewer独审；不是发布/实际预检/观察通过）。原A保持停止，原源码/绑定/启动器/锁/用量不变。

候选目录：`/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/offline-throughput10s-integration`；manifest SHA256 `6788c0b8ec6a59287a496b9e8ac21c708bf688f4ae489f755a862630252becfb`。完整review-package.diff SHA256 `b9731cc59cdbcbc68065f33af7c5a06c73a40ce0eeb13db69742edd94ec53f0c`，包含core原始基线→已验候选、collector、binding/launcher模板及新增schema/检查的完整文本差异。core精确复用54b09fc1…，未修改Budget或重跑原7例。

已实现：新run throughput10s-attempt-01、独立两release/prep/三once路径；DRAFT/缺Root发布/旧run/代码不符在TLS/输入前拒绝；历史授权校验保留，新Root overlay只允许明确启动窗口，原资源和经济帽保持。运行账不低于32734CU/62methods/CPU6789（含本轮共享60预留，不是历史实耗）；固定原T0 2026-10-21和T1 2026-11-04，无自动跨日平移；10秒/3000CU本地保守元数据进入binding、release与forecast，CU不重定价。启动alarm通过后原位置取消，观察T1/总额守卫保留。

检查原件：checks-result.json、checks.stdout/stderr、command-receipt.json。最终exit0，8条含细节结果；动态仅新身份/日期纯逻辑、虚拟10秒请求等待与临时once；完整五runtime/状态/fence/WS/时效/积压/资源/经济关键函数AST原样一致属于静态保留证据，不冒充真实服务PASS。缺release/代码hash分支为静态源码验收。首轮exit1是检查误选全源第一个mkdir，失败stdout/stderr.attempt1保留，查询LOCAL_BLOCKERS后仅限定prepare函数内断言；候选源码未因此改变。

资源：候选新增186487B（512KiB内）；检查进程body CPU 0.032652s，命令wall0.025634s；RSS原平台值26722304（macOS bytes），单本机进程，无并行，Owner本轮全准备CPU保守占用10s，计入共享60而非另加60；主动上限480s内收口，占用480s预算，非实际用户劳动。原CPU/盘/用量不清零。

未完：Reviewer独审/Root原件验收；未来真实overlay/新鲜quota/去重CPU账/两个release、实际无key准备及一次本人隐藏输入、同进程新块全预检均未做。DRAFT模板无可运行授权；launcher仅非激活文本，不启动。原固定T0已过/无法完整覆盖、资源不足或任何失败须终止，不重试/重连/复活旧run。完成后独立停止，不自行派Reviewer。
