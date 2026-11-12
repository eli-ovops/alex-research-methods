# Momentum Transformer源码核验

**决策：保留为可研究的持仓目标方法，不准入“低成本复制就赚钱”案例。** 已取得作者明确链接的MIT代码及完整固定Git树；但成本只是回测假设，缺当前数据权利、精确原结果/权重及真实成交费用记录。未运行。

版本：`e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624`，Git记录2026-03-19；tree完整、非truncated。论文作者为Wood/Giegerich/Roberts/Zohren，实读v3（2022-11-22），论文§IV直接链接本repo。不是2019原论文的精确实现。源码/回执指纹见source-audit.json。

| 链条 | 已核与缺口 |
|---|---|
| 信号 | 历史归一收益/MACD→因果attention-LSTM→tanh持仓强度；不是预测价格或胜率 |
| 持仓 | 信号再按目标波动率/资产波动率缩放；没有个人现金→整数合约→实际订单的完整转换 |
| 对齐/风险 | 特征时点t的目标是下一日波动率缩放收益；target不进输入；训练段拟合scalers。不能保证收盘后仍可在收盘价成交 |
| 成本 | 训练loss不含成本，最终后处理才扣bps×敞口绝对变化；不是已支付费用 |
| 样本外 | 论文是历史扩窗回测，未证真实账户或公开规则后实盘 |
| 原记录 | 当前Git树无结果CSV/固定权重/成交费用账；代码会生成这些，不等于已发布记录。release/外部附件未查 |

## 会影响下一步的具体源码事实

1. **成本不在训练里。** `deep_momentum_network.py:32–48`直接对持仓×目标收益求Sharpe；`momentum_transformer.py:637–639`使用此loss。`classical_strategies.py:62–76`随后才扣`bps×1e−4×敞口变化`。README顶部“成本进入loss”属于新DeePM项目，不能移用于本仓库。
2. **首行成本置零有条件遗漏。** 上述费用函数第72行把首个diff填0；若从空仓开始且首敞口非零，就漏初始建仓。若接续旧仓，也需之前敞口才可准确核算。仅证明当前commit行为，不认定旧论文结果一定同错。
3. **额外波动重标是事后展示比例。** `backtest.py:144–160`用测试结果实际波动率计算比例，不能当预先可执行杠杆。恒定缩放并不自动改变Sharpe，但不能直接采用其规模/收益额。
4. **不是交易执行器。** `deep_momentum_network.py:451–499`的position是连续信号，未绑定合约乘数、手数/保证金、fill。点差、冲击、融资及最低佣金没有独立完整建模；不能宣称全费净利。

源码精确定位：[输出与loss](https://github.com/kieranjwood/trading-momentum-transformer/blob/e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624/mom_trans/momentum_transformer.py#L612)、[费用](https://github.com/kieranjwood/trading-momentum-transformer/blob/e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624/mom_trans/classical_strategies.py#L62)、[下一日目标](https://github.com/kieranjwood/trading-momentum-transformer/blob/e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624/mom_trans/data_prep.py#L90)

## 数据与可复用性

[原论文](https://arxiv.org/html/2112.08534v3)用Pinnacle的50条连续期货，1995–2020历史评估；仓库例程改为Quandl100资产。二者不是相同数据快照。成本按假设换手率扣除，论文也明说训练使用raw returns；不能把“成本后”翻译为真实实付全费。

README称CHRIS免费且需账户/APIkey。本轮官方文档原生读取失败；查本地阻断后对同公开URL一次普通HTTPS得到404并保留，停止。**今日免费可得性/个人数据权利UNKNOWN，404不是数据全球不存在。** MIT实读允许软件复用并保留声明，不覆盖供应商数据和第三方依赖。

方法值得保留之处是直接连接持仓、风险、收益与换手，而不是让价格MSE代替全部经济目标。但默认配置达50轮随机搜索、最多300epochs、32workers；没有本机耗时/运行验证，不能承诺低成本。当前仓库无固定权重/原结果链，也不能归因“下载代码即可复现分数”。

唯一下一步提案：只核一个当前合法可得、有快照身份的日频期货数据入口是否能承接此方法；不自动训练或海选其他模型。当前不承诺利润、容量或财富目标。

本轮只读：10份源码/许可证、固定commit/tree、原论文和数据文档；全部保存小于5MiB。源码/模型运行、训练/预测/回测/交易、数据/权重下载、安装与付费均0。新读取已停止，旧FAILED及现金事实未改。
