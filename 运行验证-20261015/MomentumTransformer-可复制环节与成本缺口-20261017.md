# Momentum Transformer：可复制环节与成本缺口

核验日期2026-10-17。研究Owner只读获取作者原件，独立审阅者随后核对原文与源码，PMO核对关键代码及文件指纹。本轮新增模型运行、训练、预测、回测、交易与付款均为0；仍未证明个人持续净盈利或Gerko财富1%的实现路径。

**结论：有可合法复用的作者代码，适合保留为方法研究样本；尚未取得足以复现盈利的完整证据链。** 成本不进训练本身不证明策略无效，但这里的费用是后处理假设，并非实际成交费用。不能由“代码开放”推出“下载后即可复制收益”。

固定源码版本为`e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624`，Git记录2026-03-19。完整Git树与10份源码/许可证身份已核。[MIT许可](https://github.com/kieranjwood/trading-momentum-transformer/blob/e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624/LICENSE)允许按其条件复用软件；它不能代替行情数据授权。所读[论文v3](https://arxiv.org/html/2112.08534v3)日期2022-11-22；当前代码不能自动认定为该论文实验时的同一版本。

模型读取历史收益与趋势特征，输出连续的持仓方向和强度，再按波动风险调整敞口。收益来自所持方向与随后价格变化相符的时段；这不消除趋势反转、错误持仓和费用侵蚀。[输出代码](https://github.com/kieranjwood/trading-momentum-transformer/blob/e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624/mom_trans/momentum_transformer.py#L612)。这些是公开替代方法的机制，不是XTX私人策略。

| 本轮新核事实 | 对复制的实际影响 |
|---|---|
| 当前SharpeLoss对持仓乘收益计算风险收益比，未含换手费；费用在回测后处理扣除 | 不能把README新DeePM项目的功能套到这个版本；必须核最终全成本结果，不能只看训练目标 |
| 净收益函数把首行持仓差分填0；作者有初始成本TODO | 若从空仓开始、首仓非零，会漏该次建仓费；若继承旧仓也需要前一敞口。影响大小未核，不能据此推翻所有论文结果 |
| 部分组合展示用测试期间实际波动率事后重标规模 | 不能把该倍数当预先可执行杠杆；这不自动证明预测信号泄漏，恒定缩放本身也不自动改变夏普比率 |
| 输出为连续信号及假设收益，未绑定真实合约/成交 | 还需要现金、合约乘数、手数、保证金、成交时序与实际费用核算；目前没有个人5000美元可交易净收益证据 |

[训练目标源码](https://github.com/kieranjwood/trading-momentum-transformer/blob/e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624/mom_trans/deep_momentum_network.py#L32)、[成本源码](https://github.com/kieranjwood/trading-momentum-transformer/blob/e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624/mom_trans/classical_strategies.py#L62)、[组合展示重标](https://github.com/kieranjwood/trading-momentum-transformer/blob/e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624/mom_trans/backtest.py#L144)。

论文与仓库例程使用不同来源/范围的数据，不能混为同一快照。仓库所指CHRIS精确文档入口本轮返回404；这只说明该次该入口，不能推成数据全球不存在、必须付费或个人研究不许可。今日免费可得性、快照和适用数据权利仍UNKNOWN。

当前完整Git树未取得原始结果CSV、固定权重、实际成交和费用原账；未查release及所有外部附件，不能断言作者从未公开。论文成绩是历史样本外回测，也不等同于规则发表后的实盘。本轮核查没有把当前代码的口径问题反推到旧论文全部结果。

个人可以借鉴历史特征到持仓、波动风险缩放、按敞口换手扣费的研究流程；具体复制时仍需处理首笔和边界成本。默认配置含较多搜索与训练工作，未作本机运行测量，不能承诺轻量或免费算力足够。模型是否有可执行优势、完整净收益、回撤与资金容量，仍需独立证据。

唯一下一步：只读核一个当前合法可得、版本可固定的日频期货数据入口，确认历史范围、换月/调整方式、费用和个人研究权限。它只检查能否开展独立研究，不等于已复现论文收益；数据满足后也不自动启动新实验。

[完整来源、读取UTC与指纹](</Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/MomentumTransformer-source-audit-20261017/source-audit.json>)；[源码核验正文](</Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/MomentumTransformer-source-audit-20261017/source-audit.md>)；[独立审阅](</Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/MomentumTransformer-source-audit-20261017/review/review.md>)。全部研究原件保留，旧FAILED及现金事实不变。
