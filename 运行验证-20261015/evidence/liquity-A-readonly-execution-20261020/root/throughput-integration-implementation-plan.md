# 完整续接候选的离线集成执行计划

绑定规范为`root/吞吐修正后的完整续接方案.md`（SHA256 `3ed1d74a5d3f08b6391e95b3a44f3c53d11888f1a31afb1d1b2d8b7f06e365c3`）及其最终验收`root/throughput-integration-plan-final-acceptance.json`。只执行隔离准备，不发布真实release或启动观察。用户最新常设批准覆盖必要、免费、可逆的技术修正；本计划不扩大到交易、密钥保存或新经济假设。

## Global Constraints

- 旧run06及其他尝试的停止、源码、绑定、锁、记录和用量全部保留；不在原入口应用候选，不删除、覆盖或复活旧尝试。
- 本任务零网络、零TLS/API、零账户/钱包/凭证/剪贴板/Terminal访问，零模型/训练/收益回测/交易/付费/安装。仅标准库离线检查，不执行真实客户端入口。
- 不控制或借其他UI、osascript、shell驱动Terminal；将来如有真实发布，只能用户本人启动已发布脚本并隐藏输入一次，执行者读取脱敏回执。
- 原状态完整性、时效、覆盖、经济和失败即停条件保留。候选与fixture不等于真实服务、完整免费余额、正式观察或净收益；无自动重试/重连、丢消息、改接收时间或付费回退。
- 唯一Owner实现，Reviewer只读审，Root审原件；不派子agent，不同写，实际model/effort不可核则UNKNOWN。

## Task 1: 制作完整隔离集成包与必要检查

先读上面的绑定规范和最终验收。工作根为本计划所在root目录的上一级A执行目录。所有实现仅写`execution-owner/offline-throughput10s-integration/`；报告写`root/throughput-integration-task-1-report.md`。不要写真实run目录、Root授权/配额/发布文件或现有主源。旧core为a2f7d56b…、collector为4dd5774b…；精确完整hash沿绑定验收，不匹配先停。

唯一执行Owner `/root/annual_c_execute`，唯一Reviewer `/root/review_reports_annual`。独立本轮最多15分钟主动工作（Owner8分钟、Reviewer4分钟、Root3分钟），CPU共享60秒、最多2线程、内存128MiB、新增磁盘512KiB、新增付款0；旧账与原观察18000秒CPU/8GiB/25M CU/400k方法等总帽不重置。超限或所需改动明显超本任务即报告，不扩大。

必须直接复用Task1已验core候选，SHA256 `54b09fc1d32186dfca56c0a8eb15b6172b335693824489676ba47c627c7af5bc`，不再改Budget、不重跑该同码7项。collector最小适配遵从已验完整方案：新run标识`throughput10s-attempt-01`；新binding/两阶段release/prep/三类once路径彼此一致；旧输入期限/旧代码hash/1824CU及41方法起账不能复用。所有原URI公开常量、五runtime、数据及经济规则保持，禁止请求任何端点或读取地址。

明确绑定本地窗口10.0秒/容量3000 CU/名义300 CU/s/项目保守口径；总CU按原规则累计，不因换窗口重定价。forecast/admission/release元数据一致，但不冒充provider token bucket或真实账户共享余额。

原绝对T0固定`2026-10-21T00:00:00Z`、T1固定`2026-11-04T00:00:00Z`。必须核它们与实际下一零点及14日期间一致；错配、T0已过或无法从T0完整覆盖即停，不自动平移、拼接。启动alarm只在所有真实门通过后按原逻辑取消，正式T1及总额守卫保留。

旧累计CU32734、方法62不可下降。Root最新去重CPU保守prior的向上取整值为6729秒；本次新独立离线工作最多再预留60秒，未来guard建议prior至少6789秒（是预算借记/预留，不是实际历史CPU或严格上界，最终仍须Root发布去重ledger）。不得把UI32495替换本地32734。所有旧文件和本包均计入原盘帽，不清理凑空间。

未来Root技术overlay须显式引用旧授权和最终验收，只覆盖列明新技术run/一次有界准备输入预检窗口/累计账/本地窗口语义；不能悄改旧auth、降低原帽或删门。Root真实overlay/preinput/formal release在本任务均不存在、不可生成有效版本。可交付明确DRAFT且不能用于网络或输入的schema示例；实际客户端缺精确Root发布或拿DRAFT、旧scope/过期scope时，必须在任何TLS、RPC、隐藏输入前安全退出。没有绕门开关、参数、fixture标志或自动授权。保留真实输入仅RAM、严格TLS/固定获准路线、一次失败结束和脱敏规则。

必要离线检查仅针对新增接线与身份：①原总账/CPU prior承接且任何下降拒绝；②DRAFT/缺release/旧run或代码hash错配拒绝；③原T0/T1错配、过期、跨日自动平移拒绝；④请求节流等待分支用虚拟时钟在10秒边界释放，累计及收到时间不改；⑤release/prep/binding/run/三类once身份一致且已用新once拒绝；⑥实际五runtime/完整状态/WS/fence/时效/积压/资源及经济门均保留，新增元数据没有跳过这些路径。可AST抽取必要纯逻辑或用临时fixture容器，不导入执行完整客户端；如静态检查而非真实调用验证，逐项说明，不用stub声称真实门已PASS。

不要给未来用户一个可意外绕门联网的默认启动文件。可交付新launcher文本/明确非激活模板，路径指向新binding，不能带RPC地址参数；Root正式发布前缺release就退出。不能为检查启动它、打开Terminal或新建真实once锁。

交付manifest、全部实际局部diff含上下文/基线/候选hash、必要检查源码/逐项输入预期实得/真实命令退出及stdout/stderr、资源与新增文件用途。独立Reviewer审同一brief、Owner报告和完整review-package.diff，不重跑Owner已成功同码检查。若不能在份额内完成，报告具体未完，不将局部通过写成完整集成通过。

完成仅指一个离线完整候选及必需审查可接受；旧A仍终止，实际新准备、输入、API预检、ARMED、14日观察、个人净收益和容量均未验证。
