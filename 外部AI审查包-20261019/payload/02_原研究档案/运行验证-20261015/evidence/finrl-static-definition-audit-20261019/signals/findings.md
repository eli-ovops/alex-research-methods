# FinRL-Trading 固定源码：信号与时序审计

**结论：找到可具体复核的规则信号，但此固定实现有配置接线和风险约束落地差异，不能据此认定个人可直接复制净盈利。**仅静态阅读，没有导入/执行来源、运行模型、回测或计算新收益。固定commit：`4409abe925c904e570be78ebfb5e77ac3491dff8`；不是对整个FinRL项目或其他版本的结论。

## 赚钱假说与实际公式（已证源码事实）

1. **组间相对强势轮动**：组内可用资产的单期简单收益等权平均（忽略NaN）；对QQQ作超额。截取最后12个价格观测后再`pct_change`，通常对应11个有效周收益，并非12段收益。累计超额为`prod(1+r_group)-prod(1+r_QQQ)`；组强度按超额均值/未缩放MAD排名（MAD退化回退样本std，仍无有效尺度则NaN再在调用处记0）。最多取两组，且累计超额须>0；这只是相对QQQ趋势过滤，不是保证绝对收益为正。[group_strength.py L67–111、185–241、299–335、368–406；utils/robust_stats.py L210–255]
2. **组内信号**：`residual=r_asset-r_group`，按最新残差的滚动稳健Z分数降序选股；另记录`prod(1+residual)-1`，但排序键是Z分数而非累计残差。Z=`(last-median(window))/median(abs(window-median(window)))`，MAD<1e-6则返回0或有符号10，再截断至±20。它是相对异常/动量规则，不是本次已核的神经网络未来价格模型。[intra_group_ranking.py L171–244、316–330；utils/robust_stats.py L109–159]
3. **市场状态**：SPX当期close低于26周均线、距13周最高close回撤≥10%、VIX稳健Z≥3，三项相加，0/1/≥2映射risk_on/neutral/risk_off。快风险条件是SPX或QQQ三日跌幅≤−3%，或VIX Z及其差分Z分别达3/3.5。[market_regime.py L127–191、209–228、351–364、388–425、450–479]
4. **目标仓位**：正权重、组间等权、每组所选股票等权；例外股票乘1.5；没有合格组则按配置对SPY/QQQ/IAU/XLU/XLV等权保留敞口。最终只按总权重≤1归一，现金为`1-sum(weights)`。[portfolio_builder.py L139–198、224–257、292–327、357–408、479–537]

## 会改变复现判断的具体问题

### S1：组内“12周”实际被接为3期（已证，配置/实现不一致）

engine L149–151用`config.ranking.top_n_per_group`作为`lookback_weeks`；给定YAML该值为3。ranker L395–401传给`compute_asset_score`，L172–173先取最后3期；L201–206再取`min(12,len(residual))`，因此有效完整输入下Z的真实窗口是3而不是12。上游robust_zscore L109–110与154–157默认要求完整window，证实这不是只看变量名的推测。缺值时可能得到NaN并在ranking L238转0；未实际计算任何样本值。

同一`top_n_per_group=3`也被builder L447用为每组最多股票数（L371、535），并未读取YAML各组`max_assets:2`。配置中zscore_window/max_zscore/min_mad_threshold的同数值设置并非全部从配置接线：排名/统计函数使用硬编码12/20/1e-6。不能把配置说明直接当实际行为。

### S2：有效风险cap并未在这条组合路径完整执行（已证代码，是否历史触发UNKNOWN）

market_regime L686–703确实计算effective_group_cap/effective_cash_floor；但builder L452–453只读取慢状态risk_on/risk_off的cash_floor推出总预算1.0/0.7。calculate_risk_budget L119–130对fast直接给0.7、neutral插值0.85，不读取当次effective约束。因此给定YAML fast要求cash≥0.5、group_cap=0.3，并不能由该builder路径保证；neutral配置cash≥0.1的直接映射也被插值替代。

此外先按risk_budget分配后，对例外乘1.5（L384–390），只以max_total=1.0归一（L392–397），可在例外入选时抬高投资额超过先前risk_budget；`validate`仅检查总和≤1（L52–55）。这是条件性约束缺口，不证明所有运行都超限，也不把group_cap偷换成账户止损保证。

engine L243–255将止损结果用于状态/日志，却未将stopped/cooldown列表传给builder；所选权重未在这条调用中显式过滤它们。risk_manager及其他runner执行链未在本子任务额外读取，不能据此认证已实际再次买入或断言所有runtime止损失效。

### S3：状态持续性在engine当前调用链未传入（已证调用边界）

engine L314–322调用detect_market_regime时未传previous_slow_states/current_fast_state；其默认均None（market_regime L638–648），慢状态被空历史判persistence，快状态每次走无既存状态检测。2周持续与10日维持逻辑虽有函数，但不是该engine调用自然获得的跨次状态。其他直接调用者若自行维护状态可能不同，未泛化。

例外历史同样未完：engine L376–385仅把最新Z包装成一行Series，且有维护历史TODO。由此不能认证YAML的4周内至少2次触发M/K规则实际落地；强信号分支及exception_framework未追加读取，不声称整个例外模块永不触发。

## 时钟、宇宙与执行

- **已证当前close被用作信号**：engine DataFrame分支L275–282取`close`；get_data_as_of_date默认include_as_of=True、L391–401用index≤as_of；weekly聚合L207–215包括week_end当日并取最后close；市场状态也用最后当期close。没有在这些信号入口见到统一shift到下一交易时段。此切片阻挡未来日期，不等于信号在该日收盘前已知。
- **条件推断，需与root原件合并**：root另行实读runner称按权重日当日/此前close到下一权重日close加权、未扣成本。若这条路径使用本engine输出，就存在“用收盘信息决定、同时按该close开仓”的不可执行/前视成交假设。**不称所有特征直接使用t+1，不把该runner证据冒本Owner独立读取**；root负责绑定runner原件hash和行号。
- **已证数据处理，仍非PIT认证**：load_daily_csv L71–87读取既有日OHLCV CSV并排序/日期过滤；weekly对齐L560–564前填最多2期；没有检验数据当时首次发布时间。静态YAML固定21个组内股票/ETF，没有按历史日期的成分纳入/退出映射。复权/拆分/分红、退市及历史宇宙选择时点，在已读8文件中未明确保证；不能从名为point-in-time推成无幸存者或修订偏差。
- **订单语义**：这条engine返回目标权重与AuditLog（L249–271）；mode只进入metadata（L259–263）。没有在该路径见到真实股数/现金自融资、报价成交、延迟、拒单、费用和资金流水。类能够写日志不等于已经提供与固定版本绑定的真实成交原账（AuditLog L62–77、权重导出L549–597）。

## 研究边界与下一步

可复用的是相对强弱/稳健排名/风险状态的可读规则框架；公开源码本身不证明独立样本外扣费收益，更不证明个人可交易容量或当前净盈利。当前不宜把任何README收益或输出图直接作为这条具体实现的可复制证明。最小下一项仅是把root已读runner/费用路径与本信号文件固定在同一版本，静态确认真实决策截止与首个可成交价口径；**不自动修代码、调参或开新实验**。

来源身份、HTTP/UTC、API blob与重算Git blob、文本SHA256/bytes见source-receipts.json。共7源码+1既有配置；8次公共GET尝试（首次engine传输EOF，按LOCAL_BLOCKERS和root当时同路成功证据，仅同URI原gh重试一次成功），无HTTP拒绝绕行。没有读取凭证或改认证/TLS/代理，没有运行任何来源。实际model/effort/route UNKNOWN。
