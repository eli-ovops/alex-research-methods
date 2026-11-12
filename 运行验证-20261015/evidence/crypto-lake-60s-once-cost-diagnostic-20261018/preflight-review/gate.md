# 已授权60秒单次成本诊断：静态gate

**PASS_STATIC_READY_FOR_ONE_AUTHORIZED_FORMAL。** 用户已批准本完整单元；执行Owner可直接按本gate进行唯一正式运行，无需root再批步骤。本审阅未执行helper、读取/重复hash行情或计算真实现金差；实际诊断及最终验收仍待执行Owner与train_forward_review。

最终helper SHA `fbdb6ca16961fc31dfc797ce0bb878a38b67f27bda7837ca40c01a4d072254e0`；config `4fbb1018eef22b253d0f2390eb2bcd0dca1a97ab3fae0b6783bd7952b07e5d1c`。gate.json绑定seal全部6输入（含本次用户授权、最终冻结MD/JSON和文档review）及synthetic-preflight原件identity，不移动方法。

- helper:23–34 Selector在grid<新receipt时才封前值，因此相等receipt完整处理后取末physical，即使跨batch或EOF同样成立；无回找旧好行。feed始终检查全源receipt，包括最后计划端点以后；null/非正/倒退使DATA_INVALID，不排序修复。
- helper:36–44资格固定端点finite-positive且ask>bid、age≤5s；坏行差`exit.bad_after−entry.bad_before`包含两端；gap差`exit.gaps−entry.gaps`不误算进入entry前那一对。原因按冻结优先顺序，多重原因及1438计划总账均保留，先封eligibility后现金计算。
- config固定00:01起、60秒步长、1438入口至23:58，附23:59出口；age/gap均5秒、无250ms分支。helper:79–105先唯一full SHA/size，再唯一五列physical iter_batches≤50000/use_threads=False，核类型/全源row count/stat，不复制源。
- helper:47–62以Fraction.from_float原DOUBLE与精确bps/10000计算`bid_exit(1−f)−ask_entry(1+f)`及标准化bp；精确符号保留负/零/正。展示值有限性检查；Type7以精确p与h定位，在显示array(d)上固定线性插值。不是账户回报，不重复扣spread。
- helper:116–132全日显示全部0/1/5/10/25bp；所有费率共享资格、符号计数守恒、正数计数不得随费率增加。小时仅coverage，无小时成本分布/分类；不输出原价量、逐窗标签/账本，不sum oracle正值。正空间仅NOT_EXCLUDED，负结论限此日/费率/政策，不叫盈利PASS或普遍上界。
- helper:140–165核授权seal/gate/preflight identity、exclusive新formal lock；2CPU/IO、512MiB combined RSS每100ms采样、16MiB预写、累计1800秒与UTC截止。正式失败/超限停，无重试或修改科学规则；后续QC/独立验收须计入同1800秒总预算。

纯合成preflight已有真实exit0回执，0.109177791秒，8项检查覆盖双边费率/符号、Type7、asof/tie/无回找、包含端点的坏行/gap、missing/age、倒退clock、费率单调。fixture明确人为，不作市场或盈利证据；本review只读回执与源码，不重跑。未发现必须修正项。

静态PASS不证明真实对象/hash/扫描/现金结果与资源成功；正式运行后必须由独立Owner审原件、结果seal、资格/fee不变量及退出回执，不重算或重复扫描。采样RSS不是瞬时OS硬限；供应商contains_gapsYes与时钟/PIT/容量未知继续保留，单日不是新鲜OOS。

规则版本保持已核，actual route UNKNOWN。0本review网络、行情文件读取、Owner helper执行、新现金计算、模型/回测/交易。仅preflight-review两交付物保留，无清理项。
