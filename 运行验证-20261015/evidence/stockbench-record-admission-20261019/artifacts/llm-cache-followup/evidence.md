# StockBench LLM cache补核：固定路径缺llm节点，停止

本轮仅1/4次普通公开元数据GET即收口。固定commit `ce8b2b3483590646ad3b650ac8221f43f76fd091` 的 `storage/cache` 一层完整目录中**没有llm条目**，无法沿文档所述`cache/llm/by_run/{RUN_ID}`定位日志。本轮未取得真实小LLM响应/decision日志；不猜未列路径、不换到新闻/行情目录，也不据此声称所有历史版本/外部存储都无原始日志。

## 输入链与实际原件

复用旧artifacts/05-storage-tree.response.json：storage树 `f9553f735d6bd2d797541bec519cbd8028adee40` 实际列cache子树 `940aa1aa74d5285ba0fe541ee504b37ff424d1b4`。root另核storage/README中by_run路径，本Owner不重取其正文，不修改旧evidence.md/receipts.json。

实际GET：[固定cache目录元数据](https://api.github.com/repos/ChenYXxxx/stockbench/git/trees/940aa1aa74d5285ba0fe541ee504b37ff424d1b4)。2026-10-19T04:22:49.446627Z，HTTP200、1244B、truncated=false、5entries；响应sha与旧storage条目的cache树SHA一致。原件 `01-cache-tree.response.json`，SHA256 `75579030818c75be9f0786a074ff5a239c9f1f39182b6bf769b05e53100977b7`，低于2MiB保护上限。这里完整的是cache这一层，不冒称完整递归仓库树。

| cache子项 | 类型 | SHA |
|---|---|---|
| corporate_actions | tree | 759a11a9aee1364d53ab4861128af2a39f56d4ed |
| financials | tree | b10987dcb1fe62b2b2a6349c94716a52651f7ee9 |
| news | tree | 45b8c4fce4b3a3f164110b4edd5bbc66fad3b654 |
| news_by_day | tree | 1854f6cd4689e20decf14701cf3501694d56796f |
| stock_indicators | tree | 746b1d481bf6b9a53de30719497dd8610952ec0b |

以上子目录均未读取。本层没有llm/by_run、候选run或日志blob，所以“字典序首个run/文件”选择规则没有可用对象，不改为按模型名/收益或其他路径挑样。

## 限定判断

storage说明的路径不足以证明这些LLM日志在该commit实际发布。当前能确认的是目录路径不闭合，而非已读日志schema、消息日期、模型身份、版本、策略行动或费用。所有这些记录级字段仍UNKNOWN。也未取得paper原run绑定、完整样本、真实成交费账或无泄漏证明。

本次无错误/拒绝/重试；没有读取记录正文或凭证字段，未执行源码/模型、训练、回测、金融统计，未取新闻/行情/数据/权重包、DB或archives，未安装/注册/认证、付款、外发或交易。只写本新子目录，旧报告/原件不改。actual model/effort UNKNOWN；PERMISSIONS/ROUTING沿既有有效版本。预算剩余不强行增加查询，终态停止。
