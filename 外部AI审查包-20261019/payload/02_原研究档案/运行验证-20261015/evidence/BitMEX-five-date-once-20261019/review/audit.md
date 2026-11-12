# 独立失败原件验收

结论：**PASS_FAILURE_CONTAINMENT_TECHNICAL_DATA_UNDETERMINED**。唯一正式作业按失败停止，原件和停止范围可接受；并非模型假设 NOT_SUPPORTED，也不能认定源数据损坏。无必须修改项才能接受本次停止。

四个固定新 GET 均为一次 HTTP200，长度/ETag与冻结对象一致，合计 768,134,748 B；已核小回执SHA、source/config/gate/partial seal绑定及本地文件长度，没有重hash或解压行情。20240101、0401、0701、1001的小QC声明实际读至gzip EOF/CRC；对应可评分窗口1282/1434/1392/1402，各以1437为分母，合格+不合格守恒。第五日压缩下载完整不等于已完成gzip校验。

20250101扫描报 TARGET_CLOCK_FORMAT。adapter.py:85–90只接受D分隔、9位小数，这是适配实现约束；未留拒绝token/行号，合法变体或坏时钟仍UNKNOWN。源码152–163明确五日全扫描返回后才fit；原件目录无all-source seal、权重、预测/信号seal、evaluation/results，故A/B拟合、预测、bootstrap、成本评分均0。不得删第五日救成一日测试，不修改本次规则或重跑。

单次exclusive lock绑定实际gate；正式00:55:37.390784→00:58:12.153520UTC，exit1。监督器finally按已知child终止/等待，终端回执无活worker；不将空stderr当成功。health+formal154.978271501s，Owner另保守5s；合并采样RSS66,568,192B、执行盘768,588,697B，均在scope内。独立小原件检查的实耗/selfRSS另存audit.json，不冒称由Owner监督器覆盖。

只有失败容纳验收通过：预测优势、净收益、原生逆向合约盈亏、稳定性、现实成交/费用及容量均未判定。旧FAILED和冻结提案未改；不声称扫描旧证据全库以证明不变。实际模型/effort/route UNKNOWN。
