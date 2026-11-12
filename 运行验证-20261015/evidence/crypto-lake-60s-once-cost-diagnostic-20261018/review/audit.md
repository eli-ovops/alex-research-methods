# 固定60秒成本诊断独立原件验收

**PASS_VALID_FIXED_60S_COST_SPACE_DIAGNOSTIC_RESEARCH_ONLY，无必须修正项。**本用户已批准完整单元；冻结方案、授权、source/config/seal、合成preflight、静态gate、唯一formal及结果seal身份/时序一致。Reviewer不重hash/scan267MB源、不运行helper或重算真实窗口cost。

静态实现符合：receipt-asof最后物理行（含equal跨batch），最新无效不回找；全源继续检查clock，即使已过最后端点。两端age≤5秒、inclusive内部BBO全有效与gap≤5秒，固定原因优先级；prefix差不错误纳入entry之前的gap。原序不修复，所有计划窗口有去向。

实际1438计划=1438合格+0排除；全原因0。24小时只有资格覆盖，首尾各59、其余60，合计一致，无小时费用成绩。资格seal先于五费用统一计算。Fraction从原float64精确比率计算，每边f=bps/10000，C=bid_exit(1−f)−ask_entry(1+f)，S=10000C/ask_entry；不重复扣spread。Exact符号先于double展示，Type7保留全部负/零/正，不汇成P&L。

|每边bp|负|零|正|
|---:|---:|---:|---:|
|0|760|2|676|
|1|1126|0|312|
|5|1424|0|14|
|10|1438|0|0|
|25|1438|0|0|

五档共享1438资格，符号/比例/分类、分位顺序及跨费用单调一致；本Reviewer只验汇总恒等，没有重算实际cost。0/1/5bp必要报价空间未排除；10/25bp在此政策未观察到正空间。这是已见单日、固定60秒long-only ask入bid出的条件结果，不是预测/盈利PASS、可用信号或所有交易的先知上界。S不是账户回报；不证明1BTC成交、USDT=USD、实际费率/滑点/容量。

机械资格全过不撤销contains_gaps=Yes，也不认证clock同步/PIT或源完整性。ns仍来源条件解释，单日非新鲜OOS。没有因此授权下一模型或策略实验，旧FAILED不变。

纯合成一次0.109177791s仅验实现；formal一次1.319730875s，累计1.428908666s，采样RSS271630336B、exit0无活worker。Owner说明/静态gate及Reviewer检查另计同1800s预算；Reviewer不冒受Owner监督器覆盖，RSS采样非瞬时硬峰。0新增网络、来源重读、模型/回测/交易。actual route UNKNOWN；输入hash与资源在audit.json，无自己后台进程。
