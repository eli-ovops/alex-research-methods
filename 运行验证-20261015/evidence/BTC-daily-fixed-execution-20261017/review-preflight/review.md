# 单次执行前独立源码审阅

**FIX_REQUIRED_BEFORE_FIT：仅两项最小修正须在fit前补齐。** 不是数据/模型失败，也不是新增批准门槛；用户已有执行授权，无需再问。其余所审主链通过，未执行模型。

## 必须修正

1. **年度完整指标缺口**，daily_adapter.py:298–320。当前year对象只有log_growth、USD贡献、费用和区间数，尚未满足中文提案:73的逐年完整报告承诺。最小补足：全部连续账封存后，按holding interval的execution_date归年；使用实际继承的年初权益/BTC/现金与连续账切片计算年末盯市权益、净额、总回报、CAGR、年化波动/Sharpe、回撤、换手、费用和平均敞口。不得重置5000、虚构年界平仓/再开仓或改变候选门槛；真实终点平仓费只折入最后区间/最后年一次，区分年末权益与现金。
2. **零标准差Sharpe约定过宽**，daily_adapter.py:298–300、402–418。当前任何全零q都返回0；protocol.json仅允许cash全零约定0，其余零std应None且不能当有效通过。给metrics传control/is_cash，只对cash且全零返回0，其余sd=0返回None；逐年沿用同规则，保持已有必需指标/基准的None拒绝及原门槛，不新增逐年通过门槛。

## 已通过的核对

- 提案/协议hash绑定准确，handoff与prepared seal全部原件当前指纹相符。预检实际导入Python3.12.14/NumPy2.2.6/Torch2.8.0，CPU6/interop1与确定性请求有收据；不是模型运行证明。
- 逐项核对3650条alignment日期：e−61…e−2共60步、最早原价e−313。TRAIN1825、VALIDATION730、TEST1095窗口；NPZ仅查头部，X为对应N×60×5 float32，价格/量N+1 float64。唯一TRAIN特征日期1884行拟合scaler，常量置0、clip10，无VALIDATION/TEST重拟合。定位:160–248。
- differentiable训练账与独立ledger的25bps自融资、漂移、零量carry、首费及末费折入一次一致；现有无模型合成收据q差0、建仓/清算与终点no-fill检查通过。训练现金图未detach；terminal detach仅用于断言。50bps只复用意图，单独算现金和数量。定位:67–158、341–358。
- LSTM5→16、末步Linear/sigmoid、每窗口零状态、独立seed generator与sorted uniform初始化符合协议。100epochs、64窗口块无detach、一轮一次loss/backward/update、有限梯度与L2裁剪1、最终epoch100，无验证择优。定位:274–296、333–384。
- 四基准、两成本口径、paired log差90日圆形块/10000次/固定seed/线性2.5%分位及原始门槛一致。先封全部模型意图，再封全部连续账，最后metrics/bootstrap，没有提前看heldout评分。定位:321–331、374–422。
- supervisor/fit独占x锁、gate绑定源码/授权/提案/协议/预检/准备seal；prepared文件逐项验hash，fit前再核原CSV。prepare约14.42926秒计入7200累计；UTC总截止13:00:40Z、同进程monotonic、worker+supervisor已知PID采样RSS及worker高水位检查。当前两项run/fit锁均不存在。定位supervise.py:10–68与daily_adapter.py:262–272、333–423。

下一步由原Owner仅修上述report-only/明确约定差异，禁止fit或生成新市场指标；停止后独立复核小diff与无模型合成检查，再由根签发新源码hash绑定gate。无需重跑prepare或改变冻结协议。

本轮仅只读文本/hash、alignment日期及NPZ头部检查、纸面代数；未导入科学库/模型、运行适配器/监督脚本、计算市场收益或账本表现、联网/安装/下载/交易。只新增本review目录两文件，未改原件。实际model/effort UNKNOWN。完成停止。
