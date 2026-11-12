# 三分支官方名称通过；Q3迁移覆盖UNKNOWN

读取/收口UTC：2026-10-16T06:42:18.702360+00:00。规则PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4；实际model/effort UNKNOWN。本轮6次公开小型搜索/GET预算已用完，不追加事件或状态读取。

**官方版本化清单精确绑定三个目标地址，但未取得2026年第三季度的登记快照或完整变更史，不能证明该季度没有替代地址或迁移。**

| 正式登记键 | 官方清单地址 |
|---|---|
| MCD_CLIP_ETH_A | 0xc67963a226eddd77B91aD8c421630A1b0AdFF270 |
| MCD_CLIP_ETH_B | 0x71eb894330e8a4b96b8d6056962e7F116F50e06F |
| MCD_CLIP_ETH_C | 0xc2b12567523e3f3CBd9931492b91fe65b240bc47 |

## 固定原件与身份范围

来源为官方`sky-ecosystem/chainlog-ui`仓库的`api/mainnet/1.14.2.json`，固定commit `d23de00bcb68d91b494edfed5d228a02519d4245`，Git blob `5274f5ddb6ecf4d200ec4b86939d1445db083db8`。

- [固定文件](https://github.com/sky-ecosystem/chainlog-ui/blob/d23de00bcb68d91b494edfed5d228a02519d4245/api/mainnet/1.14.2.json)
- [实际GET](https://api.github.com/repositories/427019981/contents/api/mainnet/1.14.2.json?ref=d23de00bcb68d91b494edfed5d228a02519d4245)
- [不可变blob](https://api.github.com/repositories/427019981/git/blobs/5274f5ddb6ecf4d200ec4b86939d1445db083db8)

HTTP200原回应、API返回的html_url/download_url/git_url/sha、起止UTC及hash均保存于`request-6.receipt.json`。仅按数据base64解码，重算Git blob SHA-1匹配API sha；提取JSON SHA256为`0b0cc0efbec7d8be31f664cc9bc03a53e0a0756ebe7585af47daf97a2bfb5295`。三个键逐项与任务地址比较一致。

官方旧域名`https://chainlog.makerdao.com/api/mainnet/active.json`返回308，Location明确为`https://chainlog.skyeco.com/`。随后只读新首页HTTP200，源码链接到上述官方仓库，故仓库归属有官方网页入口支持。新页展示登记信息的逻辑依赖动态链读取；本分支未执行网页脚本或RPC，没有取得live registry结果。重定向也不证明旧API仍提供active.json，不能将响应当当前地址JSON。

## 当前与季度边界

`1.14.2`仅为所读文件的版本标签，不声称是当前激活版本。固定Git ref证明本次读取的文件身份，不单独证明首次公开、部署或激活日期。本轮没有读取其提交时间，更未将Git时间当Q3链上状态证明。

Q3账期为2026-07-01T00:00:00Z（含）至2026-10-01T00:00:00Z（不含）。期间这三个正式键是否改指其他Clipper、是否存在替代部署或迁移、登记版本的适用起止区块，均为**UNKNOWN**。本轮不以未找到迁移记录断言未迁移；也不将此版本文件称Q3快照。

根取得的三地址Q3事件可以称“这三个已命名合约在指定季度的返回事件集合”。当前补充不能将其升级为“三抵押品该季度所有部署”或“Maker/Sky全协议”。即使补齐部署变更史，这三个分支仍不等于全部市场。

本轮仅补正式名称/登记地址来源，不重复根的Q3事件请求。Kick笔数和内部补偿毛额不能自动成为个人可取得收入、扣费净利、胜出率或未来容量。

## 原件收据与未读项

6次读取中，第1次官方组织代码搜索仅在工具回执保留、未保存完整独立原件，精确UTC/hash记UNKNOWN，不用于最终身份结论；第2次搜索零结果；第3/4次为旧域重定向及新官方首页；第5次搜索定位固定官方清单，第6次取得该清单。第5次HTTP原件先遇本地换行分隔解析错误，随后仅对同一保存文本重新解析，没有网络重试。各已存原件hash和真实URL均列入JSON。

会改变覆盖结论的最小新原件是：覆盖Q3前后且明确这些键适用地址/区块的官方registry版本变更史或治理执行记录。本轮预算内未取得，停止扩展。

只做静态文本、JSON、base64和hash核对；无模型、回测、策略、EVM/RPC执行、安装、账户、交易、付款或外发，未改root及其他Owner文件。
