# StockBench原始交付审查：固定实现已核，结果身份仍PARTIAL

本轮5/5公开动作完成。已固定作者repo提交，实际取得根目录、storage一层目录及主README；完整递归tree超过本地2MiB保护上限，未取得完整正文，**不能声称全仓库无原始记录**。主README的运行后导出位置不等于已发布实跑；尚未绑定逐时decision/actions、positions/trades、costs或publicbaseline原始输出。

## 论文与repo身份、版本

作者repo [ChenYXxxx/stockbench](https://github.com/ChenYXxxx/stockbench)，官网stockbench.github.io，论文arXiv2510.02209。主README实际L5–7同时指向这三个入口；paper Owner独立取得的v2链接表亦含同一repo/site。本Owner仅复用链接身份，不重复论文内容。v1/v2日期及历史测试性质由paper Owner报告，不能用本轮代码GET认证真实资金或前向实跑。

2026-10-19T04:20:03.151875Z正常GET commits?per_page=1取得commit `ce8b2b3483590646ad3b650ac8221f43f76fd091`。Git author/committer均2025-10-28T08:14:26Z，message为Update README.md/change paper url。Git日期不是独立事前公开/运行回执；本提交也未绑定为论文原始实验。commit元数据的root tree SHA为 `80db7bcb3eced4a1ea571528acad712faf0a51d1`；树接口按commit请求的响应sha字段为commit字符串，原样保留，不混为同一对象。

## 读取与截断边界

| 公开动作 | 实际结果 |
|---|---|
| 1 commit元数据 | HTTP200，4397B，固定上述提交 |
| 2 recursive tree | HTTP200，读取2097153B达到2MiB本地保护后停止；未保留完整JSON，总长/完整hash/entries/truncated UNKNOWN |
| 3 nonrecursive根tree | HTTP200，2354B，10entries/truncated=false，仅根层，不称整仓库完整 |
| 4 固定README | HTTP200，4171B，Gitblob `69a3960a233d6e9ba90158806c250ca9ca232edc` 与根tree及size一致 |
| 5 固定storage子tree | HTTP200，820B，3entries/truncated=false；响应SHA与根层storage SHA一致，只是一层完整 |

读取UTC、URL、完整小原件SHA与状态见编号receipt/receipts.json。第2项是本地cap，不是403/安全拒绝；查LOCAL_BLOCKERS正文上限案例后未重试同一超限全树，只读取更小的非递归已固定目录。不会把本地截断当GitHub返回truncated=true，也不会宣称有完整递归tree。

## storage的实际线索

固定storage树SHA `f9553f735d6bd2d797541bec519cbd8028adee40`，实际三项为：

| storage下路径 | 类型/大小 | 树对象身份 | 本轮状态 |
|---|---|---|---|
| README.md | blob /11203B | c9a19aef431f44e1e3e044055d73e7cbb95f4f8b | 真实存在的小说明，尚未读取 |
| cache/ | tree | 940aa1aa74d5285ba0fe541ee504b37ff424d1b4 | 子层未知；不能直接认定为actions或行情 |
| parquet/ | tree | 62863a0f960cf69531ce942a5b622cafb1e7b44f | 子层未知，未取数据 |

这说明已核storage顶层没有reports条目，但**不等于cache/parquet没有任何原始decision或数据，也不覆盖历史分支、外部仓库/发布资产**。没有取得小原始输出文件，不编造path/blob/size。最小未读入口为固定 `storage/README.md`，其合法构造URL是 `https://raw.githubusercontent.com/ChenYXxxx/stockbench/ce8b2b3483590646ad3b650ac8221f43f76fd091/storage/README.md`；已将11203B/blob线索交root，由root判断必要schema核验，本Owner不追加第6读。

## README已说明什么，没有证明什么

保存 `04-README.md.inert.txt`，SHA256 `6c924e7e4955f132ed724f61bd7d3d3eb1fdc3ed016d6828d12b618540a40e8b`。

- L20–35将平台明确描述为历史市场数据模拟benchmark，目标是DJIA按权重选20股；不是该repo已经以真实资金前向盈利的证明。“post-2024零训练污染”是作者宣传表述，本轮无模型知识截止/消息/调用原件认证，不据此通过无泄漏。
- L67–96给运行回测及自动保存 `storage/reports/backtest/` 的使用说明；L98–101列return、Sortino、drawdown指标。它只是输出功能与预期位置，不是该位置已经发布的原始run清单。没有实际逐笔费用或开放损失明细，本Owner未运行产生结果。
- L57–65及L138–140指向Polygon、Finnhub、OpenAI数据/服务；未请求API、注册或读key。原始数据、新闻与模型服务授权不能从框架代码许可推定。
- L10、L130–132自述Apache2.0；根tree实际列LICENSE11358B，但本轮未读取正文。准确结论是许可自述与LICENSE位置可见，不认证全文条款或数据/模型权利。
- README未给特定paper策略/模型组合的不可变决策/成交/fee manifest或publicbaseline原账路径；未读stockbench/代码、config、scripts，故不对代码手续费公式、输出schema或全部基准文件存在性下结论。

## 收口

当前有作者论文↔repo入口、固定提交、可核小目录与README，未闭合“特定原始run→预测/持仓成交→完整costs→报告”的交付链。最小下一原件是上述storage说明或实际结果manifest；不能通过新运行一个回测来替代原发布结果。即便有输出，仍需分历史模拟、事前封存和真实实盘，不自动认证净利/容量/财富完成。

无源码执行/import、训练推理/模型/回测/新收益计算，未下载市场/模型/新闻包、DB/pickle/archives，未安装/登录注册/读凭证、付款、对外发送或交易。只写artifacts/，actual model/effort UNKNOWN；PERMISSIONS/ROUTING沿用已核版本，5项后停止。
