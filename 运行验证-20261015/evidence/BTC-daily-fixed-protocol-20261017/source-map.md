# 来源映射与适配边界

本轮只读本地既有原件与现有.venv元数据；外网/行情聚合/特征与收益计算/模型导入训练预测回测交易均0。下面是**新实际核对**的源码定位和环境证据，不是新实验证据。

| 已存原件 | 本次具体读取 | 提案采用/改变 |
|---|---|---|
| 固定e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624，mom_trans__deep_momentum_network.py.source.txt | L32–48 SharpeLoss，L502–548 LSTM、tanh、Adam、序列输出 | 采用直接学持仓的风险收益目标；改变为Torch小LSTM最后步、sigmoid long/cash、无搜索；加入自融资成本，不冒原版已有 |
| mom_trans__data_prep.py.source.txt | L82–114价格winsorization、标准化多周期收益、MACD | 只选五种归一化历史收益；不修改价格、不用MACD；明确独立适配 |
| mom_trans__classical_strategies.py.source.txt | L62–76成本后处理/首次diff填0；L107–137收益/波动对齐；L169–220 MACD | 首次和末次收费显式；不复用bfill或测试后波动重标；365日现货替代252日期货 |
| settings__fixed_params.py.source.txt | L1–15默认TFT/252步/50次搜索/300epochs | 全部不是本方案默认；仅一个模型/seed/100epochs，无搜索 |
| LICENSE.source.txt | L1–21 MIT许可 | 软件借鉴保留MIT条件；不替代data许可 |
| paper-v3.passive-text.txt | L1383–1408风险收益目标上下文；L1565–1587原50期货/1990–2020/滚动历史测试 | 只作经济和方法动机；不搬原成绩/年份/真实交易结论 |
| 完整CSV audit.json | 完整数据hash、7,780,439行、零量、时钟和修订局限 | 仅OHLCV，不冒订单簿/XTX；不重算旧LSTM或现金事实 |

原始官方URL：
- [固定仓库](https://github.com/kieranjwood/trading-momentum-transformer/tree/e0352cb0bdbf8045accb1bf1a5705ae0cb9ea624)
- [原论文v3](https://arxiv.org/html/2112.08534v3)，2022-11-22；当前Git版本为2026记录，不保证论文执行同版。
- [固定数据版本](https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data/versions/755)，请求版本/内容hash已封，非服务端独立版本签名。

## 本轮环境新证据
environment-metadata.json记录系统python3 -S的stdlib importlib.metadata，仅指向该项目.venv/lib/python3.12/site-packages，并绑定各METADATA真实hash。观察到NumPy2.2.6、Torch2.8.0、pandas2.2.2、scipy1.18.1；未见TF/Keras/sklearn。pyvenv.cfg的version_info=3.12.14是元数据，不是启动解释器验证。没有运行任何包/site/.pth、构造tensor或运行健康检查，未来可运行性仍UNKNOWN。

固定配置和全部实际输入路径/字节/SHA256列于protocol.json的source_inputs；环境METADATA原件指纹列于environment-metadata.json。当前CSV不重复读入或复制；其完整身份采用刚结束实际全扫原件，未做新聚合。

## 一次执行单元
当前只交文档。以后若一次获准，必要独立适配/健康与非训练预检/源码审阅/单次100epoch训练/封存全部信号/两档现金成本账/统一评估合在同一范围内，不逐步向用户索许可。无实际依赖运行、预算保证、个人实盘资格或收益通过。

最多下一步：顺序独立审阅这一份方案，再集中决定一次有上限的离线执行；不自动实施。

