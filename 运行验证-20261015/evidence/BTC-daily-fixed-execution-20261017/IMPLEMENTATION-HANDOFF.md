# 阶段一交接：拟合前停止

**STOPPED_BEFORE_MODEL_FIT_OR_FORWARD。** 唯一prepare执行session63609，supervisor PID12322、worker PID12323已exit0，无活进程；fit-started.json不存在，网络构造/拟合/市场模型预测均0。

最短审阅入口：daily_adapter.py（独立方法适配）、supervise.py（已知PID资源监督）、artifacts/preflight.json、artifacts/health-prepare.json、artifacts/prepared-seal.json；全部具体hash见implementation-handoff.json。

## 实际执行
- 开始2026-10-17T09:08:02.057206Z，结束09:08:16.486444Z。14.429261秒保守计入未来7200秒累计预算；总工时截止仍13:00:40Z。
- 实导Python3.12.14、NumPy2.2.6、Torch2.8.0。Torch intra6/interop1、确定性请求，BLAS/OMP等6；-I -B和PYTHONDONTWRITEBYTECODE=1，不改旧env、不安装、不联网。
- 已知worker采样峰RSS186466304B，新盘约5.23MB，stderr为空。准备后仅资源硬化：未来run监督同时计已知worker+supervisor RSS并加最终worker峰值检查；旧源码快照保留，不重做数据预检。
- PYTHONHASHSEED环境项在-I下不保证控制Pythonhash；算法不依赖hash迭代随机性。Torch显式Generator与未来NumPybootstrap各用固定seed20261017。

## 数据与预检
完整源CSV实际SHA与冻结值相等，不复制CSV。再次静态聚合7780439分钟为5402完整UTC标签日，两个已知部分首尾日仅留metadata、不修复。
- train1825、validation730、final_test1095个60×5窗口；最后日期只平仓。e−2特征截止，最早原价e−313，312个原价标签。
- 仅TRAIN窗口唯一特征行拟合均值/总体std，其他段不重拟合，固定clip±10；原价格未改。
- 三段00:10参考柱零量数量403/11/23（含终点参考检查），全部保留；三段终点量均为正。未产生仓位，不能把这些数量说成实际未成交数量。
- 已保存prepared-inputs.npz/scalers.json/alignment-manifest.csv/daily-source-inputs.csv及seal。没有市场收益/Sharpe/MSE汇总或模型outputs。
- 合成现金夹具检验：现金/单位守恒、首末费用、no-fill、终点不能假清算，并比对独立标量记账与可微Tensor记账；这是合成记账验证，不是市场或策略通过。不构造LSTM、不forward、不backward。

## 实现固定口径
LSTM5→16→Linear1→sigmoid，60步，每窗口零隐状态；CPU全部参数sorted named显式seed初始化。单fit/100epochs，完整训练期单loss/backward/update，不shuffle/detach/earlystop/search。实际正式fit尚未开始。
训练25bps使用与最终独立现金账同一带漂移phi、自融资/首末费用/no-fill规则；50bps复用意图信号，各自现金/单位路径。最终仓位全封存后才记账，全部账再封存后才评分。指标/两强基准/买持有和现金参照/90日blockbootstrap/门槛均按冻结协议。
监督器已知子进程不派生计算进程；仅ps读取已知PID，非扫描其他用户。旧preflight收据反映资源硬化前的worker采样值，不能冒已实测后续训练峰值。

## 后续只可由具体内部gate启动一次
当前不执行。root审阅gate应为JSON：allow_fit=true、allow_scoring=true，source_inputs按绝对路径绑定daily_adapter.py、supervise.py、authorization-and-budget.json、冻结protocol和中文提案、artifacts/preflight.json、artifacts/prepared-seal.json的sha256。运行时还会核prepared seal的每个文件及原CSV。
使用现有.venv/bin/python -I -B supervise.py run --approval /absolute/root-gate.json；父环境必须PYTHONDONTWRITEBYTECODE=1，监督器设置内部线程/离线/缓存。单次supervisor-run-started.json与fit-started.json均exclusive create，不能因超时重发。源码/身份/资源/数值失败按范围停止，不重训或换参数。
未知仍包括实际训练耗时/内存、历史数据可用时钟、真实交易费用/成交和容量；健康通过不消除这些。实现不等于净优势通过，旧FAILED/现金/全局状态未改。


待独立审阅明确的报告口径差异：当前metrics的year字段只有log_growth/net_USD_contribution/cost_USD/intervals；没有逐年独立Sharpe/波动/回撤/换手/平均敞口和完整年段权益。机器协议写year-by-year contributions，中文提案“全部区段、基准、成本、年份均报告”更宽，可能要求逐年完整指标。现仅披露，不改冻结方案、不计算市场成绩；需在任何fit前由root审阅确定并完成必要实现澄清。
