# FinAgent公开实现与原账准入：README已读，完整结果链未核

本轮取得arXiv2402.18485v3完整官方HTML，未从正文/摘要定位作者代码入口；随后按已观察候选读取DVampire/FinAgent README，作为身份未证的公开实现线索。作者绑定未知只限制“官方复现”称谓，不阻止检查公开实现。README已固定blob，仍无固定commit/完整tree/结果文件清单，不能据此判不存在原账。完整个人可复制净优势验收未通过。

## 已取得的官方身份与覆盖

论文为 [A Multimodal Foundation Agent for Financial Trading: Tool-Augmented, Diversified, and Generalist, v3](https://arxiv.org/html/2402.18485v3)，版本日2024-06-28。官方[摘要页](https://arxiv.org/abs/2402.18485v3) L8–29确认作者、v1 2024-02-28与v3 2024-06-28 10:35:56 UTC。精确HTML原件为 `04-paper-v3.original.html`，2026-10-19T03:21:25.084487Z、HTTP200、2845157B，SHA256 `e208bb7d855b36f67ce8b36940f5748f14de5ac90fa0f4f7f74875844dd7d8d3`。本次完整响应长度与Content-Length相同。

首个普通GET触及本地2MiB保护上限，非HTTP/权限拒绝；记录为未保存完整原文、已读取2097153B即停止，而非零下载。查LOCAL_BLOCKERS相关正文大小限制后，原生find两次定向定位；再用8MiB保护上限普通GET取得完整同一文档，未改认证、身份或TLS。随后第6项仅读取既有DVampire/FinAgent候选README，合计6/6动作后停止；未扩搜其他项目。

完整HTML被动解析为 `04-paper.passive-text.txt`，没有执行HTML/脚本/示例代码。对全部HTML anchor href与被动文本中的github、source/code availability、URL等作静态定位：唯一正文GitHub文本是pyecharts绘图库脚注（passive-text L8146；对应native turn1030view0 L553）。真正href中的GitHub为arXiv反馈与LaTeXML工具链。它们都不是作者FinAgent实现。完整URL清单另存 `04-paper-link-inventory.json`。这个定位可以支持“此版本所取正文未给出直接作者代码URL”，不能支持“所有作者页面或所有论文版本都没给”。

原生find原件：`02-paper-find-github.native.txt`、`03-paper-find-code.native.txt`。两者只是命中片段，不称全文；其中Appendix E的Main Entry/Run Step（native turn1033view0 L649–779，对应passive-text L11491起）展示数据集、环境、prompt与step流程，属于论文内代码示意，不是可校验repo/path/commit，更不是实际运行日志。实际摘要页全文L0–162另存 `05-paper-abstract.native.txt`；L92–116是第三方Code Finder等功能开关，未展开作者实现URL，也未操作这些服务。

## 证据链状态

| 环节 | 本轮结论 |
|---|---|
| 论文规则身份 | 官方v3及版本日已绑定；实验定义由论文Owner另核，本Owner不重算结果 |
| repo身份 | DVampire/FinAgent公开README实际已读；论文作者归属及同实验对应关系UNKNOWN |
| 固定commit、tree完整性 | 未取commit/tree；只有README文件blob，不冒充仓库revision或树已扫完 |
| signal/position/trades/cost原件 | README未列这些文件；未取tree，真实存在/路径仍UNKNOWN |
| checkpoint/model/API snapshot manifest | 未取得；UNKNOWN；没有下载权重 |
| 未来数据/费用实际实现 | 论文示意流程不足以认证当前信息截断、真实成交时刻或全费用账；不能据此判已证泄漏，也不能判因果通过 |
| 净收益性质 | 作者实验汇总不能升为独立核账/实盘证明；92.27的ARR年化定义由论文Owner核，不在此改称累计净收益 |

## 第6项公开README：实际含义与限度

实际GET `https://api.github.com/repos/DVampire/FinAgent/readme`，2026-10-19T03:23:08.420913Z、HTTP200，完整API响应2779B保存 `06-readme.response.json`；解码惰性文本 `06-README.md.inert.txt` 1463B，SHA256 `b431a4139874bb7862ba6c3ed96439c567f9736684e101f95bf1db85aea229a6`。GitHub返回的blob SHA与本地Git blob SHA均为 `19828785aa1da5fb3dede65c6bff9bb28abfb5ac`。API返回main分支README路径，不把它当固定commit，文档发布日期UNKNOWN。

README L1只有FinAgent标题，未包含论文标题、作者、arXiv号或结果复现绑定。L3–18是安装说明；L20–32是环境变量的明确示例占位符；L34–44列 `tools/download_prices.py`、`tools/download_news.py`、`tools/data_process.py`；L46–50列 `main.py` 与 `main_mi_w_decision.py`。这些只是README明示的准备/运行入口，不是本轮已存在核实的tree文件，更不是实验输出。没有执行这些指令、读本地.env、索取key或下载数据。README未给signal/position/trades/cost、checkpoint或结果manifest路径、时间戳、哈希，也未声明费用/模拟与实盘归属。

下一项会改变原账可核判断的最小原件，是这个候选公开实现的固定commit+完整tree元数据，及其中实际列出的结果/日志清单；是否与论文同实验仍须单独绑定。作者亲自发布不是额外准入前提；代码/结果本身的可复核性才是核心。根Owner可根据线索决定是否另设有限核验，本Owner6/6停止。不下载权重/行情/DB，不执行代码、模型、训练、回测或收益计算，无安装、注册/登录/凭证、付费、外发或交易。model/effort实际UNKNOWN；规则PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4、HANDOFF-2026-10-10-v2沿用。
