# KMLM SEC财报原件：两对象访问拒绝，收入归因仍未核

**本轮没有取得正式财报正文、Statement of Operations、期货损益/现金利息/费用表或审计意见，相关归因继续UNKNOWN。** 两个明确SEC对象均返回访问策略403后停止，2/8公开动作，余6不使用。没有把旧摘要当全文，没有改查好年份/半年报，也没有重取发行方已403的当前PDF或已404的旧PDF。

事前选择规则已保存于 `selection-before-read.json`：截至2026-10-19，选择KMLM最新已结束完整财政年度的正式SEC年度/N-CSR，同期间有效修订优先，不按盈亏选期。旧官方索引/发行方身份记录提供CIK1547576、series S000070143、class C000223083及KMLM/ISIN US5007676522的定位线索。旧SEC检索还给出精确2026 NCSR URL及其年度股东报告期间摘录，但本轮没有由新财报正文确认主体、期间或审计范围，也无法完成最新完整财年及修订核验。

| 实际新请求 | UTC、HTTP、字节 | 实际原件及限制 |
|---|---|---|
| `https://data.sec.gov/submissions/CIK0001547576.json` | 2026-10-19 19:44:43–19:44:44 UTC；HTTP403；4819B | `01-SEC-submissions.source`，SHA256 `aceba63df63c22039f884b6419377051a03d0d2afe8d4cdb971c67062c445800`；返回HTML访问拒绝，不是submissions JSON |
| `https://www.sec.gov/Archives/edgar/data/1547576/000182912626006162/kraneshares_ncsr.htm` | 2026-10-19 19:46:05 UTC；HTTP403；4819B | `02-SEC-fixed-annual-body.source`，SHA256 `f5c62132f8c39b5dcf50e6ddd8913fa41201d45b81560d85c9b98f1ac9a8bce8`；返回访问拒绝，不是年报正文 |

第二个对象是旧材料已明示的独立申报文件，Root明确限定允许在metadata拒绝后用同一默认身份、普通严格TLS读取一次；它不是被拒metadata的镜像或重取。该对象同样拒绝后，本轮所有SEC读取立即停止，没有换UA/身份/代理/工具、改认证、追加其它CIK/submissions地址或猜文件路径。

两原响应标题均为 `Your Request Originates from an Undeclared Automated Tool`，正文说明自动流量声明问题。此为当前读取条件下的真实来源访问阻断，不是HTTP UNKNOWN、缺失文件、无数据、需要付费/登录或基金亏损证明。原拒绝正文、必要安全响应头、精确UTC/URL/HTTP和哈希均保留；拒绝页中的操作建议没有被执行。

旧索引摘要只作为 `prior-SEC-2026-annual-lead-not-body.txt` 与 `prior-lead-identity.json` 保存。其所述April 1, 2025至March 31, 2026不能升级为本轮已读/已审年度财报。新原件未包含任何可用于同期间利息、期货已实现/未实现、费用及audit coverage的表格，因此没有复制金额、加减归因、重算NAV或新增收益判断。

此前已取得的真实基金运行后官方NAV披露继续保留；本轮没有新增审计财报支持，也不推翻旧运行证据。模型/个人复刻gate没有重开，未恢复私人权重或逐笔规则，也未扩大到其它基金。尚缺的同期间正式Statement of Operations与审计覆盖原件仍明确未读，不能写成不存在。

前置有限阅读仅两份旧报告、旧搜索中SEC线索与LOCAL_BLOCKERS对应段。本轮没有PDF正文，未触发PDF处理或下载；原HTTP错误体共9638B，低于单件1MiB/总8MiB限制。完整身份层级、未读范围、manifest与receipt在本目录。无模型/回测、来源代码/EVM/RPC、金融核算、账户/凭证、交易、安装、注册、付款、外发或私人行情/QC读取。实际model/effort及CPU/RSS无平台测量回执，均UNKNOWN。
