# Kronos-small：其他免费数据项目筛选

读取日期：2026-10-14。沿用个人预测研究目标，不注册、付费、联系供应商、取得行情文件/权重、开发、运行模型、回测或交易。只检查公开来源、许可、接口与字段说明。Owner 为本会话，execution_evidence 为唯一只读研究/审查者。

## 1. 结论

额外核查四个免费数据候选。**当前最接近加密货币小时预测研究的是 CryptoDataDownload 的免费历史 OHLCV 档案；HistData 可以作为外汇报价研究候选。** Kraken 的原始小时档案有数据质量来源优势，但完整用途仍待核；Coin Metrics 的非商业数据许可明确，所需免费小时 OHLC 覆盖未确认。

这是候选筛选，没有验证实际文件、模型效果、净利润或实盘权限。四者均不能据本轮证据宣称“未来交易的数据和执行全部免费”。

| 项目 | 免费部分与研究依据 | 与 Kronos 的适配 | 当前判断 |
|---|---|---|---|
| CryptoDataDownload | 日/小时/分钟历史 CSV；网站明确提到机器学习，数据页采用 CC BY-NC-SA 4.0 | 小时 OHLCV 形式较直接；仍需固定交易所、币对、时区及具体文件 | 加密货币历史研究优先候选；仅非商业范围有依据，上游权限与实际文件待核 |
| HistData | 免费网页历史下载；官方说明供自有策略及 EA（自动交易程序）测试 | Tick/M1 即逐条报价/分钟柱；M1 是 Bid（买方报价）OHLC，须按预定规则聚合小时 | 私人离线外汇研究候选；完整许可证、持续前瞻源与生产用途 UNKNOWN |
| Kraken 官方档案 | 官方公开 OHLCVT CSV 下载；包含60分钟柱 | 直接成交形成的四价；无成交时缺柱。完整档案是大型分卷 ZIP | 来源直接，但用途和轻量取得方式仍需明确 |
| Coin Metrics Community | 免费免 key 数据，CC BY-NC 4.0 | 有市场/链上数据子集；小时参考价不等于小时 OHLC | 许可明确的非商业辅助数据源；本轮不能列为已确认的小时 OHLC 主源 |

主要原始来源：[CDD 数据页](https://www.cryptodatadownload.com/data/)、[HistData About](https://www.histdata.com/about-us/)、[Kraken 档案说明](https://support.kraken.com/articles/360047124832-downloadable-historical-ohlcvt-open-high-low-close-volume-trades-data)、[Coin Metrics Community](https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data)

## 2. CryptoDataDownload：当前最接近免费小时研究

官网提供以交易所/证券/频率组织的历史 CSV，公开写明机器学习、策略测试等用途；数据页列 CC BY-NC-SA 4.0（署名、非商业、相同方式共享）。小时档案不要求购买 Plus+；部分分钟等粒度可能要求免费账户。Bitstamp 页面也明列日/小时 CSV 及字段，但动态表未返回具体币对的日期清单，不能保证某一文件的覆盖和完整性。[数据页](https://www.cryptodatadownload.com/data/)、[Bitstamp 档案页面](https://www.cryptodatadownload.com/data/bitstamp/)

更新于2023-09-20、当前可读的条款限定非商业用途，并提示资料可能受上游第三方权利限制。它支持私人模型研究的用途解释，不构成全部上游授权核验。不能通过转载 Coinbase/Binance 资料规避已知源限制；后续只按某个具体来源分别判断。[CDD 条款](https://www.cryptodatadownload.com/terms-of-use/)

Bitstamp 原始 API 文档说明，公司商用其交易所数据需签 Data License Agreement；并提供小时 OHLC 参数及排除未结束柱的选项。我们未取得任何商业合同或执行权。个人自有账户实盘的准确归类和额外费用仍未闭合。[Bitstamp 原始 API 文档](https://www.bitstamp.net/api/)

**研究判断：**可以继续只读核 CDD 某一现货小时文件的元数据、来源与字段。没有必要为了取得基础历史柱先购买增强数据服务；每日更新的历史档案也不能当作已确认的实时执行源。

## 3. HistData：免费外汇研究，价格含义不同

官方说明分享资料帮助策略/EA测试；免费网页提供按币对、年、月组织的 Tick 和 M1。M1 四价基于 Bid，成交量不提供；Generic ASCII Tick 另含 Ask，可用于研究买卖价差。时间采用固定 EST、不随夏令时调整；不能机械当作纽约当地时钟。[About](https://www.histdata.com/about-us/)、[FAQ](https://www.histdata.com/f-a-q/)、[字段规范](https://www.histdata.com/f-a-q/data-files-detailed-specification/)

**适配推断：**分钟报价可按事先固定的小时边界聚合，配合 Kronos 四价输入；预测目标应称报价变化。Bid 收盘上升不直接等于可实现收益，真实买入价、卖出价、价差及场所仍要核。聚合尚未开展，也不能把此结果混称原 BTCUSDT 方案。

公开用途支持私人离线研究；本轮未找到完整可据以确认实盘、商用、再分发的许可证。免费网页下载与付费 FTP/SFTP 便利服务分别处理；不用购买后者才能取得基础历史文件。更新时间、特定币对历史范围和前瞻取数延迟未核，不保证持续实验数据源。[下载说明](https://www.histdata.com/download-free-forex-data/)

## 4. Kraken：原始档案可取，但免费接口有历史上限

2026-09-16 更新的官方说明列真实 OHLCVT，包括60分钟频率，完整历史截至2026-06-30；约2GB分卷提供，另有季度增量。只包含有成交的区间。这个原始入口与第三方档案不同；没有下载任何分卷。[官方说明](https://support.kraken.com/articles/360047124832-downloadable-historical-ohlcvt-open-high-low-close-volume-trades-data)

公开 OHLC 接口只返回最近最多720项，且最后一项是未结束柱；`since` 无法取得更老历史。因此不能认为免费接口能一次取全历史，或直接把最后一项输入模型。[当前 OHLC 文档](https://docs.kraken.com/api-reference/market-data/get-ohlc-data)

全球条款更新于2026-10-06，§8允许为本人利益使用，但§9另有限制自动化、复制和第三方应用等；旧 API 指南仍要求某些用途、尤其非个人商业用途先获许可。当前指南迁移后未出现同一 Notices 段，不能由删除/未显示推断约束已撤销。我们只读全球版相关部分，没有确认用户适用辖区、完整补充条款或专门模型用途。[全球条款](https://www.kraken.com/legal/global-terms)、[旧 API Notices](https://docs-legacy.kraken.com/api/docs/guides/global-intro/)、[当前指南](https://docs.kraken.com/exchange/guides/overview)

**判断：**数据来源和小时结构已核，有私人使用的一般依据；完整模型/自动化用途及生产权限仍 UNKNOWN，不作为当前完全闭合许可链的首选。

## 5. Coin Metrics：许可清楚，小时 OHLC 权益待核

Community 文档和官方数据仓库将免费数据按 CC BY-NC 4.0 提供。私人非商业模型研究有正面依据，需署名、链接许可并说明修改；以赚钱为目的的用途不能仅凭“个人账户”认定为非商业。[Community 文档](https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data)、[官方仓库](https://github.com/coinmetrics/data/blob/master/README.md)、[CC 许可](https://creativecommons.org/licenses/by-nc/4.0/)

免费提供网络/市场数据子集、有限 Atlas 和 Reference Rates；细粒度参考价限最近7个点，不能替代80根小时四价。免费限流10请求/6秒/IP。通用 API 文档列 market-candles 与小时频率，不证明特定免费市场和历史已开放。[Community 文档](https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data)、[通用 API](https://docs.coinmetrics.io/api/v4/)

本轮目录元数据读取被工具报为 inaccessible，未取得服务端权益答复、未重试、未取价格。小时 OHLC 免费覆盖仍 UNKNOWN。不能把单一参考价格复制四次当四价，也不能把此结果总结成 Community 只有日线价格。

## 6. 收敛决定与来源日期

按现阶段目标，优先继续核 **CDD 的一个现货小时数据源**；HistData 作为外汇研究备选。四项中，所读 CDD 与 Coin Metrics 数据许可证均有非商业限制，Kraken/HistData 未来生产授权未闭合。源码开源、数据下载不收费与实盘用途许可是不同事实；没有合适权限就留缺口，不换工具规避。

发布日期/更新日：CDD条款2023-09-20；Kraken档案2026-09-16、全球条款2026-10-06；其余所读页面未标可确认发布日期。读取均为2026-10-14。没有检查真实行情连续性、固定权重后的预测、费用后回报或资金容量。

公开文档快照及文件指纹记录在同目录 `kronos-free-data-projects-20261014.json`。Exa MCP 未配置，原错已记录；已有公开网页读取通路完成研究，没有安装或修改工具配置。
