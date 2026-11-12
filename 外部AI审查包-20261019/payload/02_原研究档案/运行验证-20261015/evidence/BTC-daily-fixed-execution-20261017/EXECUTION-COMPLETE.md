# 单次离线单元执行回执

**完成且结果NOT_SUPPORTED；停止，无活进程。** 这不是实际交易利润，也不否定所有预测/持仓方法。

唯一正式session34980，supervisor14752/worker14753，2026-10-17T09:20:21.583426Z—09:20:51.530207Z，exit0；100epochs，单fit锁，未调参/重训/重跑测试。正式运行29.946792s，加预检/合成44.479362s；事后只读哈希校验0.724812s，累计 **45.204174s**。峰worker+supervisor采样RSS478478336B，run结束盘17.85MB；stderr0B。全部远低于冻结预算，UTC截止未触及。

目标/权重/scaler/settings全部封存→两成本所有模型/基准连续账封存→统一评分，顺序已核。原CSV完整hash与7个gate源码hash未变，各seal实际文件指纹全一致。没有联网、安装、付款、账户或交易；只执行批准的历史代理评估。

## 固定门槛全部报告
- 验证正净额：通过。
- 测试正净额：通过。
- 相对两主基准Sharpe至少+0.20：未过。
- 测试25bps日频估值回撤≤35%：通过。
- 两主基准paired log差均值/97.5%单侧下界：未过。
- 50bps正净额且超过两主基准：未过（LSTM本身正，但未超过）。
- 50bps回撤≤40%：通过。
- 全部终点实际代理平仓有效：通过。

测试LSTM25bps由5000到8157.527982USD，Sharpe0.970275、固定日估值DD16.46035%；风险缩放买持有20717.174880/Sharpe1.389153，固定趋势10487.608454/Sharpe0.934019。LSTM50bps末7876.549890USD。这些仅为固定25/50bps假设、Close代理和no-fill规则下的**历史虚拟现金账**；同风险上限不保证相同实现风险，正净额不是独立alpha或未来个人利润。

最短终审入口：artifacts/evaluation-results.json（全部三段/两成本/五控制/年度指标/门槛），artifacts/execution-completion.json（实际input指纹与封存/身份检查），artifacts/session-003-run.receipt.json、session-004-readonly-hash-verification.receipt.json及三份结果seal。无需加载模型或重新评分。原FAILED/旧权重/旧现金证据/全局状态未改，本轮目标未达成。

