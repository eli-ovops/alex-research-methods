# 吞吐修正后的完整续接方案（静态修订稿，未实施）

结论：已验候选只有Budget窗口变化，构造接口仍兼容现collector，但旧release、1824/41起账、已过入口期限及run06 once锁不能直接沿用。局部7项PASS不等于整套可启动。本稿仅准备同一原目标下的一次新技术尝试；旧run06永久保留STOPPED，候选未应用，未创建入口、探测网络或取新数。Root按最新用户常设偏好处理必要执行scope和精确发布，不要求用户重复批准常规技术步骤；本稿自身不是新的实际观察授权。

**唯一基线与最小改动。** Task1最终验收为`root/offline-throughput-window-final-acceptance.json`；候选manifest SHA542d0434…，完整core候选SHA54b09fc1d32186dfca56c0a8eb15b6172b335693824489676ba47c627c7af5bc。当前主core仍a2f7d56b…，collector仍4dd5774b…，未应用。未来只采用该固定候选，不重新挑阈值。其Budget构造签名、charge/delivered/state、共享deque和异常类名不变；collector492调用无需接口适配，WS计价/保存顺序不改。原core134–151仍是1.01s/peak，候选同段变为10.0s/peak*10，名义300而本地容量3000；默认peak100保留。它是本地保守滚动账，不是提供者token bucket或真实账户共享余额。

`collector140–159`的每通知CU、两aggregate+fence成本、100800块/等待/审计和CPU磁盘预测不含1.01常数，也不应因窗口扩大把总CU乘10或除10；`peak300`名义字段可保留。缺的是明确窗口语义元数据：未来新binding/release/admission/forecast应一致写local_window_seconds=10.0、local_window_capacity_CU=3000、nominal_rate_CU_s=300、project_conservative_not_provider_bucket，并校验匹配候选身份。每头平均/最大样本投影不是最坏突发保证；新预检须实际检查10秒共享窗口下RPC节流、WS交付、scan处理时间与积压。累计总帽、费用整数取整/帧头保守口径、实际429即停不变，不加重连/丢消息/延迟收包或修改到达时间。

**最少元数据/身份集成。** 建议唯一新技术run标识`throughput10s-attempt-01`，不是重开run06。`collector7–8`固定run路径；266–272两份release路径/launcher名及代码hash；415–426 prep receipt run/code/binding身份；432、480、494三类once锁均须新路径。旧launcher逐字固定run06 binding，不能调用它再绕锁。新launcher仍仅本项目既有Python3.12、-B -E -S和新binding，无RPC地址参数。所有旧源码/授权/release/锁/归档/原时间戳原样封存；无删除、覆盖或重命名旧锁。

`collector310–334`目前硬绑定旧resource-flow授权hash及08:29:58–10:29:58/09:29:58入口，429–430及463–465又硬编码旧截止；381–386还检查前半窗和余20min。09:29:58入口期限已过，因此仅换core必然不能新输入；不得删该门或悄悄改旧auth。未来以Root书面技术续接scope/补充overlay引用旧授权及Task1验收，给出一次明确有界新准备/入口/预检期限与主动/CPU借记，同时保留CPU18000/8GiB减1MiB/25M/400k/300名义/2线程/1GiB/付款0，除非Root依已有偏好另有明示且可审资源决定。旧历史auth先按原值核验，新overlay只覆盖列明的技术run/窗口/新账来源；运行、OS剩余CPU、预测、写盘、告警必须同一effective limits。现源码硬编码起账检查在357–365，未来需同步新ledger，不是仅改JSON。

**累计账不得回退。** 终态原件与Root终态验收给出32734CU/62方法，含最后失败通知155CU，不能回1824/41、不能扣已发生峰值失败费用。记录的动态CPU预算6677.772639=旧保守prior6676加本次实测动态量，不是历史实际CPU总计。`run06-followup-state.json`另登记28秒保守CPU，旧followup已暂停/活动预算封闭，不挪剩余120秒帽；Task1最终验收另列Owner5+Reviewer5+Root5=15秒。本轮Owner2秒及后续Root/Reviewer/集成/准备/实际进程childCPU须另外归档，Root去重形成最新总prior；最终合计在本稿中UNKNOWN，不拼接旧预留和实际数双算，也不能退回6676。新方法/CU/CPU都是同一总帽下累计，不是新给一份额度。盘按UNIT实际used累计，包括旧失败、候选和本稿，不清理旧文件凑空间；新scope/release发布时本地再核statvfs与8GiB额度，两者不同。

Root新现况文件`throughput-integration-current-quota-observation.json`（SHAf5ae25c7…）显示UI32495/30M、cap300、1app；保持较高本地32734，不用UI或roundedRemaining30M替换。实际余额/其他共享账户消耗实时值UNKNOWN。未来需新鲜hash绑定quota工作ceiling=min(25M,有证据的更严可用值)，非账户余额实时担保；provider错误停，不付费回退。旧人工实耗UNKNOWN不填零；9h授权占用/新主动预算也不等于实际必要人工成本。

**原T0/T1可继续使用的必要条件。** 原T0=2026-10-21 00:00Z，T1=2026-11-04 00:00Z尚未来到；run06正式样本0，预热不补入样本。只有Root明确将唯一新技术尝试绑定这两个原绝对时点，新的无key准备、唯一输入、实际完整预检和资源门在T0前全部PASS，并能从T0连续覆盖，才可保留原窗。当前collector519自动取“下一UTC零点”，未来须加expected_T0/T1精确校验及未赶上即停，防止跨日默默平移；赶不上/中断则停止INCONCLUSIVE，不自动顺延或拼接窗口。ARMED后仍取消启动alarm，只受原T1与累计帽约束。

**一次完整流程，不让用户重复输入。** 集成若获执行scope，由原Owner在新隔离候选仅做上述最小改动，保留Task1包；原Reviewer审集成diff及必要受影响验证，Root实读原件/核基线后精确应用与发布。发布前完成：新授权/账本/绑定、代码身份、旧样本按当时时刻的等待零点和所有累计资源预筛、实际可用盘、Root正常UI免费额度、主动工作/输入预检收尾余量；任何已知不足不打开入口。随后只有一次获发布的无key现有loopback HTTPS路线固定目标严格TLS，0API路径/密钥；失败本尝试结束，不换路。prep有UTC/有效期/代码binding/auth和资源原件，旧run06 prep已过期且身份不符，不能复用。Root验收PASS才签新formal release并唯一打开新真实TTY隐藏输入；用户一次粘贴，密钥仅RAM，不恢复聊天/文件/环境/剪贴板旧值，不再索取“已输入”确认。

输入后同一进程必须全部重新验证：chain1/新固定B/hash；五runtime字节；独立同块身份；WS订阅/三个不同连续正向头；active/zombie全集ID/count/数组完整性；正确oracle/SP/资格；三完整同块扫描/fence、真实接收/形成时刻、年龄/处理耗时/无积压、重组/缺块；新10秒共享本地窗口及CU/方法/CPU/磁盘/等待T0/审计预留的完整投影。旧N105/P160与历史成功不能代替新状态。费用规则、USD锚、经济/全成本/样本门一律不改，人工/维护缺账保持UNKNOWN。所有门PASS才同PID一次ARMED；任何失败、429、超额、时效/覆盖缺口或过期即本尝试结束，不自动另开输入/重试/降采样。

**必要验证及当前未完。** 不重跑Task1同码7项。未来只测新增元数据/授权/ledger及代码hash闭合、请求与WS共用同一Budget的接线、累计先记后判和错误停的真实调用次序（stub限离线）、新run once/过期/原T0约束、改窗后请求节流等待分支对时效守卫的影响，保留安全脱敏/默认严格TLS。真实服务与token bucket/共享余额不靠stub认证。Root再验唯一无key准备和输入后的全部真实层，技术接入、原完整观察、经济意义分层交付；接通/ARMED不叫盈利或容量。

本轮只读静态依赖核验，未执行/导入候选或客户端、未运行7项检查、未取网络/市场/归档/私人目录、未创建实际launcher或改旧稿/源码/锁/自动化。实际model/effort UNKNOWN，继承路由不变。Owner主动保守180秒、独立CPU保守2秒，输出小于64KiB；旧已满followup预算不复活。Root派原Reviewer仅审这一完整方案，未由Owner派agent或Reviewer。
