# 股票/ETF低频分支：4个候选，未找到全门槛通过者

只读公开研究；未执行候选代码、回测、模型、安装、交易或账号连接。使用 GitHub CLI（静默 auth 通过）和网页检索；4 条 search query，未超过 10 请求。公开原件下载总量远低于 5MB，未抓取大数据。模型运行态不可独立见证：UNKNOWN。

|候选|固定commit / commit UTC|许可门槛|原件检查与结论|
|---|---|---|---|
|Pimvdbos/ml-portfolio-optimization|c2f75ddfb3edf5e27e98788b2200b10b6efa6576 / 2026-10-01T10:03:59Z|GitHub license=null，完整树无LICENSE，README未找到复用许可|有2018—2024七年ETF Stooq gzip CSV，有汇总performance_summary.csv与平均权重，但没有逐期权重/逐腿费用。因未明确许可先淘汰；不使用其盈利为可复用证据。|
|issaiass/Momentum-Signal-Trading|ab1dc9dae37c54e2200ecdfc6160b0d5a932954e / 2026-08-12T18:27:02Z|README 1780明确 all-rights-reserved，直到加入LICENSE|许可硬阻断。README的paper成交/回测自述不作为本次成交原件证据。|
|ShamikOfficial/quant-trading-backtester|4a80a77e6a8f967a01094bfdd073c255e6b0d419 / 2026-09-03T05:08:16Z|MIT|完整树仅样本汇总JSON与equity图，data/sample只有.gitkeep；未保存本次Yahoo原始行情/完整持仓/逐笔费用。摘要中XOM +9.64%（59笔）仅为摘要声称，不能通过全原件门槛。|
|huyukun662-crypto/RiskParity-Momentum-ETF|ec1b5003284bc9d39de22d47e73d74efaec4740f / 2026-04-23T13:39:07Z|LICENSE MIT；数据供应商授权不由MIT替代|最接近，但缺全行情与逐腿费账，README执行时点与源码冲突，未通过。详见下文。|

## 最接近者：A股ETF轮动

原始入口：https://github.com/huyukun662-crypto/RiskParity-Momentum-ETF/tree/ec1b5003284bc9d39de22d47e73d74efaec4740f

- LICENSE为MIT，许可软件复制/修改/复用；README同时称仅供量化研究、学习交流。行情由AkShare路由东方财富后复权close，失败降级新浪不复权close。未核到东方财富/新浪数据再分发及交易使用许可，个人研究/实际交易数据复用权限均应标UNKNOWN，不能由仓库MIT外推。
- IS：README称2020—2023；保存运行脚本却调用2018-01-01—2023-12-31；OOS调用2024-01-01—2026-04-21。WF表列4折测试2023、2024、2025、2026年，不能与单一final OOS混称。
- 静态读取保存NAV（不执行策略）：555日，2024-01-02—2026-04-21；列为日期、strategy、benchmark；strategy 1.0→1.849854079534342，总变动+84.9854079534%；按保存序列计算最大回撤-8.4679318531%。保存metrics报告annual_return 0.3229, sharpe 2.43, max_drawdown -0.0847。这里只证实保存NAV记录，未复核为可交易的净利润。
- 保存rebalances_v5i_final_oos.csv：310行、97个调仓日期、11个ts_code标识（含空仓）；字段 date,kind,ts_code,name,weight,nav。首次调仓2024-05-24，末次2026-04-17。属于目标权重，不是完整实际持仓/逐腿成交账；没有shares、execution_price、cash、fee、slippage。
- trades_2026-04-17.csv只有3条本周目标权重变更（BUY/SELL、上周/本周/差值），不是逐笔成交原件。
- 全树36个parquet缓存；样例510300.SH为3378条close，2012-05-28—2026-04-22。OOS实际目标中的512800.SH、513100.SH、513500.SH、515220.SH、518880.SH未见缓存，需要另取行情才可能复核；未扩展抓取/回测。
- 费用：ParamsV5E.transaction_cost=0.0005；源码从现金按买卖金额扣统一5bp，未保存逐腿费用，也未拆佣金/滑点。没有交易所/经纪商真实费用或真实成交凭证；费用覆盖是否足够UNKNOWN。
- 实质时点冲突：README第508行声称Friday close→Monday open(T+1)；数据fetch函数仅保留close，_rebalance_to(today)从prices.loc[today,c]成交，动量、波动、过热判断亦用today，源码第219—247、330—376行可见。由已读代码证据无法确认README的T+1执行声明，且有同日收盘信号/成交可实现性缺口。
- 经济优势假设：跨ETF动量、风险平价、波动率目标及防御篮子。保存策略净值是作者回测产物，未证明真实交易经济优势。README公开展示多参数OOS敏感度表，缺研究试验总数/预注册时间证据，事后筛选风险UNKNOWN；OOS较IS高不等于自动证实无过拟合。
- 版本混用：metrics_v5i_wf.json为vt=0.11、总体ann=0.2501 / Sharpe 2.13；final OOS表用vt默认0.13。README宣传数字不得直接替代对应逐期账。

## 本地证据

每候选子目录 retrieval.json 记录固定commit、blob_sha、读取UTC与URL；tree.json为GitHub原始树响应。原件读取总量约344KB（含后续源码、README及样例缓存，不含树响应）。huyukun/ 存主要保存NAV/权重/费用实现，huyukun662-crypto/ 存全树及数据获取源码/样例缓存。

安全处理：上游 strategy_a_share_etf_rotation.py 发现疑似硬编码供应商凭证默认值；未打印或使用，保存副本已脱敏，并在该目录retrieval.json标记。该单个源码副本不是字节原件；源URL/blob SHA保留，其他下载文件未改动。不得复述该疑似凭证。

结论仅限本次4个候选的限定筛查：没有找到同时满足明确复用许可、完整真实行情快照、完整逐期/逐腿持仓、逐笔费用及可靠样本外扣费盈利证明的股票/ETF案例；不代表全网不存在。
