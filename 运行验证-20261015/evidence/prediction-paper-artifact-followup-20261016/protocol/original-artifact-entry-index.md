# 作者原始包入口有限续查

**结论：6次预算内读取后仍未取得目标论文作者代码/数据发布包；不能据此断言不存在。** 本轮新增了正式出版版与作者/机构来源，但没有关闭逐笔映射、固定重建代码/去重、全费用原账或数据复用许可缺口。

共2条搜索query、4页公开open（4个web工具调用），均返回可读结果，无拒绝或重试；没有GitHubAPI、认证、下载大包或运行程序。actual model/effort均UNKNOWN，规则沿用PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4。每次请求URL/query、请求前UTC、结果、保存响应SHA见同名JSON；原生工具未给HTTP状态/精确远端完成时刻，均保留UNKNOWN，不用抽取大小冒网络bytes。

| 实读一级入口 | 新取得的证据 | 原包判断 |
|---|---|---|
| https://luciannakiffer.com/publications/ | 共同作者列目标论文、四作者、AFT2025及PDF链接。 | 目标项未列代码/数据。“Data Observatory”在前一篇36Coins论文下面，不能错挂本篇。 |
| https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.AFT.2025.27 | 出版商确认正式论文日期2025-10-06、24页、DOI、四作者；论文许可CC BY4.0。 | 文件区仅PDF/实验HTML。全站Supplementary Materials导航不等本篇附件，未取得代码/数据包；论文许可不外推到它们。 |
| https://networks.imdea.org/team/imdea-networks-team/people/oriol-saguillo/ | 首作者机构身份、目标论文及机构PDF入口。 | 目标项未给源码仓库/数据下载；其他新论文不代替本篇。 |
| https://dspace.networks.imdea.org/handle/20.500.12761/1941?show=full | 作者/标题/会议一致；item元数据accessioned和available标2025-07-18T13:10:57Z，issued为2025-10。 | 文件区只列AFT_Polymarket_Arbitrage_Arxiv.pdf（10.20MB），未下载。open access不是数据/代码明确复用许可。 |

机构item的available标签早于arXiv2025-08-05，但不是逐文件首次公开的独立存档，也不是交易样本期前规则/程序已封存的证明。不能将四个不同日期修成一个精确firstpublic时间。

两次搜索只作为定位；其中同作者2026另一篇的订单簿数据、第三方机器人/自动复现工具均未继续读取，不混成目标论文附件。保存原生响应含搜索线索，不当数据原件。本轮没有取得新真实交易数据或独立盈利证据，没有访问钱包/模型、SQL、SDK、EVM或开展新实验。

这项有限阴性结果足以维持“本研究尚未取得原包”的状态，不需要等作者回复，也不排除其他独立原件。能够改变结论的是目标论文作者明确关联的固定归档/仓库、实际文件清单和许可；本轮没有发出消息或设置监控。
