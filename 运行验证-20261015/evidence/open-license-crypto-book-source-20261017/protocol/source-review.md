# 唯一开放许可订单簿候选

**YES_LIMITED：原发布页给出了真实订单簿自采说明和明确数据 CC0；尚不能把它当已就绪的因果预测输入。**

候选为 Martin Søgaard Nielsen（Kaggle `martinsn`）发布的 [High Frequency Crypto Limit Order Book Data](https://www.kaggle.com/datasets/martinsn/high-frequency-crypto-limit-order-book-data)，数据集ID1567989、version1。官方完整HTML的 JSON-LD 将 creator、数据说明及 CC0 直接绑定，修改时间2021-09-02T15:56:55.86Z，不冒首次公开证明。不是从转载许可证或代码许可证推数据许可。

发布者说明通过 Coinbase WebSocket 采集、重建约12天 BTC/ETH/ADA 订单簿，含两侧各15档和1秒/1分钟/5分钟快照。这是原发布者采集自述，未读取行情作独立验证。被其致谢的 `sadighian/crypto-rl` README 支持记录/回放及特征导出的工具角色，但当前分支不等于该数据集历史生成版本；未运行任何命令。

数据本身明确标 [CC0](https://creativecommons.org/publicdomain/zero/1.0/legalcode.en)。在发布者可处分的权利范围内，它支持个人专用统计研究、修改及派生汇总的外部复核，不含NC限制或旧Tardis式外部服务书面执行权条件。CC0不替发布者清除第三方权利，也不给质量保证；本轮没有取得本候选的明确相反限制，不能仅凭一般保留句否定CC0或一律要求授权信。旧Tardis合同不能自动移植到独立取得的数据。

## 字段能支持到哪里

`midpoint`、`spread`、档位相对中价距离属于价格状态描述。`market_notional`、`cancel_notional`是成交/撤单类别，不是静态挂单quantity；`limit_notional`只有“limit order volume”的说明，尚不能判定是静态存量还是新增委托流。不能直接填进旧方案Qb/Qa。

精确时间字段、UTC/精度、交易所还是采集器时钟、分箱起止和特征截止时点均未在所读卡片中明确。1秒频率不自动证明因果可得性；缺口/重启/连续性也未验证。约12天不等于有跨市场状态的稳健样本。以上不否定研究价值，但不支持沿用旧Kraken34日或直接宣称六特征可算。

## 访问与规模

官方元数据列ZIP **1,041,602,262 bytes**，同时 `isAccessibleForFree=true`、`requiresSubscription=true`。这是并存标签，不能直接推收费或确定必须账号。未点击下载；匿名访问、成员列表/大小、实际ZIP完整性仍UNKNOWN。普通GET只取得元数据HTML200/11350B；原生两次提取0行保留，不当作全文或拒绝。

唯一下一最小问题：该version1的BTC1秒产品，是否有发布者文件清单/表头/schema元数据，明确时钟与分箱截止、静态挂单字段及文件大小/访问方式。只核字段元数据，不取行情行；随后若可用，也须在看结果前另立新协议版本，不能静默换进旧方案。

本轮10个公开动作（4query、4open、1click、1HTML GET），5次原生调用，行情/样本/权重下载及模型运行均0。原始返回、UTC回执、HTML、被动JSON-LD和11输入指纹保存在同目录；实际model/effort UNKNOWN。没有取得预测成绩或实盘净利润，旧结果保持。
