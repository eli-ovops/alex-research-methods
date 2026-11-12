# Momentum Transformer 独立源码证据审阅

PASS。实质差异与必要修正：无。42份输入当前指纹均匹配；10份保存源码与GitHub blob解码字节、Git SHA1及固定tree相符。完整指纹和定位见review.json。

- 身份：commit `e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624`链接tree `df112de0ede2e830ff336ad72d2249cbc1f4502a`；29 entries/25 blobs，非truncated。LICENSE:1–21为MIT，不能代数据或依赖授权。当前树没有原结果/权重/成交账，不推断作者从未在release或外部公开。
- 成本：deep_momentum_network.py:32–48与momentum_transformer.py:637–639训练SharpeLoss没有成本；backtest.py:442–476先验证选模、生成测试持仓，再合并daily_vol、调用calc_net_returns、保存CSV。classical_strategies.py:62–76按bps乘敞口变化后扣，函数没有try/except吞掉异常；fillna(0)是对缺失diff填零，不是异常捕获。README:4–17的成本入loss属于另一个DeePM项目。
- 首仓：classical_strategies.py:69–73首diff填0，从空仓建立非零首仓时遗漏建仓费；续接旧仓须有之前敞口。结论只限定当前函数，不能追溯认定论文所有结果同错。
- 波动率：backtest.py:113–162默认用测试收益实际annual_volatility得到额外恒定缩放比例；属于事后报告/回测后处理，不自动构成预测信号输入泄漏，也不是当时可执行杠杆。普通零无风险率Sharpe在有限正恒定缩放下不变，不代表收益额或真实执行可复现。数据对齐、train-only scaler与target排除输入有静态支持，不认证全系统无泄漏。
- 论文：paper-v3.passive-text.txt:1555–1585明确作者链接、Pinnacle50连续期货、1990–2020数据及1995–2020扩窗OOS；:2336–2435明确训练raw returns与假设0–3bps成本分析。仓库例程的Quandl100不能代同一快照；历史成本回测不能冒真实成交原账或5000美元账户可交易净收益。
- 文档：CHRIS保存404仅限回执中的精确文档URL，原生InternalError是另一读取层。不能推全球不存在、必须付费或今日免费授权；数据权利与精确快照仍UNKNOWN。MIT代码也没有给出个人现金到整数合约、保证金与fill的完整证据。

结论保持“方法可研究，低成本复制赚钱未获支持”；唯一后续为数据入口提案，不自动启动研究或计算。本轮无新联网、下载、账号读取、源码执行、模型导入/构造、权重读取、新预测、绩效重算、回测、交易、安装或付费。仅新增本目录review.json/md，原件未改。实际模型/effort UNKNOWN。完成停止。
