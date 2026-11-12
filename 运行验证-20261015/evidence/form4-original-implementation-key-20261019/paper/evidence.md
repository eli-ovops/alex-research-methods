# CMP原实现资料指向：找到附录入口，尚无身份字典/代码绑定

结论：已封存论文明确给出Internet Appendix的一般入口，而且取得的PDF自身含该附录；这构成可交给root有限核验的具体线索。本文没有读到精确原作者代码、数据字典或复制manifest链接，不能把“本轮未找到”写成不存在。身份键仍UNKNOWN，未因本轮而解决。

## 输入与读取边界

唯一输入：`/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/form4-opportunistic-buy-signal-admission-20261019/paper/02-harvard.passive.txt`，182024B，SHA256 `1251a11d4d5bce3369d2057b04f7c95e9d1401a9a6717b7d993ce15cdf38e5ae`。

只关键词定位并读取六处短上下文；行号为LF口径。不重新解释A1或人/公司分类段，不读取新论文、真实申报或价格数据，不访问下面任一URL。

## 实际指向

| LF定位 | 原文线索 | 能支持与不能支持 |
|---|---|---|
| 1–22 | Harvard保存稿标识`http://nrs.harvard.edu/urn-3:HUL.InstRepos:33785679`，另列保存稿OAP条款和无障碍链接 | 大学保存稿及使用条款入口，不是作者代码、数据字典或复制数据授权。 |
| 645–690 | 主交易来源为Thomson Reuters insider filings database；Form4；合并CRSP/Compustat；明确排除行权和私人交易 | 有数据库身份及范围说明，没有personID、CIK或CUSIP的供应商字段映射、跨公司聚合键或公开数据字典链接。 |
| 1670–1705 | Thomson数据库`role-code`用于识别outside/independent directors，指脚注21 | role-code是角色属性线索，不是个人唯一键；没有给取值表、代码数值或字典URL。 |
| 2238–2275 | 脚注4：`http://www.afajof.org/supplements.asp`；脚注8：Jeng et al. (2003)讨论Form4数据问题 | 前者是明确Internet Appendix一般入口；后者是文献线索，不是已取得供应商字典。另两条SEC whatwedo链接只是背景，不冒技术schema或复制资料。 |
| 2908–2927 | 本PDF已有“Internet Appendix for Decoding Inside Information”；引文模板`http://www.afajof.org/IA/[].asp` | 附录确已包含；带`[]`的URL是占位模板，不能拼接、猜页号或称实际可用精确路径。Wiley对补充内容的免责声明也不等于数据/代码许可。 |
| 2401–2432 | 脚注21讨论两类人的属性比较；脚注22感谢Diego Garcia、Oyvind Norli提供州级业务数据 | 脚注21没有补role-code字典；脚注22不是身份数据库的代码/字段字典交付，更不是免费原始数据下载许可。 |

关键词定位未命中明确的personID、insider identifier、CUSIP、data dictionary、replication/code availability声明。`replicating`等普通叙述不当复制包链接。这里是这份被动文本的有界检查，不排除作者网站、期刊附件或其它版本另有交付。

## 影响决定的最小下一入口

若root在自己的公网预算内继续，应优先核上述**原文实际给出的**附录入口能否指向同论文的原实现/字典，而不是以Thomson角色字段猜个人键。本轮不联网、不自动追链接，不把已有Internet Appendix的存在升级为代码/数据已开放。若入口只重复现有附录，身份实现仍需明确原件，不以继续翻同一表格制造进展。

0网络、0来源程序/XML/模型执行、0个人分类/信号、0金融计算、0价格读取、0回测、0账户/付款/交易或外发。actual model/effort/route=UNKNOWN。规则沿PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4、HANDOFF-2026-10-10-v2。
