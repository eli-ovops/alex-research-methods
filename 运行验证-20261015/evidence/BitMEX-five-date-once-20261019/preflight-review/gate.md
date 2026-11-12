# 五日完整离线检验：静态method/code gate

PASS_STATIC_ONLY。允许唯一Owner按用户已批准的封存整单唯一执行，无需再请root或用户逐步批准。此gate不是下载成功、模型有效、数据QC通过或盈利结论；正式/依赖/数据/资源失败即停，科学有效负结果不修模型。

已完整读取授权、7270B原proposal、1845B固定cohort及原review；小输入hash匹配。授权4136B/SHA256 `d93c0f806899404e636acee16969d90328f716cd56a6aa425e1dd949dc149671`明确批准新五日整单，旧blocked授权缺口已解除；不改旧FAILED、提案和历史结果。

## 最终代码与预检身份

adapter.py16543B/SHA256 `673ec7f16399ddce98f895963ac655d1d0dbae04396bde2ab5b705cef1614636`；supervise.py3937B/SHA256 `5b46ae2849797de7777d2fb66a98d4379f42a73c3054eb874ec1f9c9854c7766`；config5071B/SHA256 `56f2161f63ac970ff39ec89dcd9110e83b4ee80d67cdd6bec58185b20631ce1b`；最终seal1973B/SHA256 `440dd1f856174ec1a379e33a9eb53221f9632044620eaf10ece1c964215b9162`。8项inputs逐字节/hash验证；两源码仅AST静态解析，未执行。

复用唯一实际health：session-health exit0/PASS、0.216140292s、采样combinedRSS53018624B，Python3.12.14/NumPy2.2.6、各线程环境1；health-preflight声明无市场读/fit。它对应修正前seal e6576b24…，不冒最终源码已执行预检；完整diff证实唯一变动是测试80%检查时序，health函数、依赖、算法未变，故不重跑预检。精确原件身份见gate.json。

## 静态支持的主链

- 下载：四个固定对象各一次normalGET；默认TLS、匿名/noCookie/no凭证、无自动redirect/retry。HTTP200、exact ETag/Content-Length及identity编码在body前核；流式限长/SHA，额外1字节检查超量，无新增HEAD或其他市场请求。固定Jan复用旧文件，不复制；复用文件SHA与gzip读取同流累计，EOF后与既有expected全SHA核对，之后才允许拟合。新下载SHA在下载流取得，scan前后stat防变；不冒独立已知新文件全SHA。
- 读取：逐文件一次gzip/CSV流，完整EOF/CRC，8192B logical record，六字段，固定XBTUSD、四字段finitepositive且ask>bid、时间D9/date校验，任何坏目标行或倒序停止；无修补/排序/择币。重复时间原序最后目标行as-of。间隔>5秒只描述，不作为另加排除规则。原始与minute采样数组仅本地，不发给assistant，不落展开CSV。
- 时点：minute样本00:01–23:59供固定00:02–23:58的1437候选；查询只有query<新timestamp才结算上一值，因此≤query且同刻最后physical。年龄≤5秒且非负；current mask仅当前/过去，x仅过去60秒mid变化、当前spread和I。未来y/score可本地缓存，但预测函数不读它们；测试future覆盖停止已移至预测信号封存之后。
- 拟合：tx/ty仅前三训练日共同可评分行；训练均值/总体标准差，零方差列置零。A用前2特征、B用前3，各一次solve，系数惩罚alpha1；中心化y/z处理截距，不惩罚截距。训练权重/缩放先封存；无测试调参、日期/参数选择或再拟合。
- 预测与评分：两测试日所有current/past合格窗口先预测，触发仅prediction>当前spread_bps+2×fee_bps；两日predictions/signals全部封存后，才检验测试80%覆盖并评分。共同score mask用于M0/A/B误差；未来端点不足的已触发信号逐模型/费用统计，任何非零使cost不可判定且不得过门，没有删后声称正空间。
- 统计：按minute//20产生每测试日72钟面块，不跨日；d0与dA共用PCG64 seed0每次各日抽72块索引；固定1000次、按可评分行等权，空抽停止，2.5%/97.5%线性分位数。不重拟合，不把分钟或事件当独立长期证据。
- 成本与门槛：5/10bps均报告，小数费率f/10000入固定quote-C/mid式；A/B信号为long-only、每窗两端不净额化、未操作为零。无信号子集不同情况下费用均值单调的额外断言。原5%两日/两基线MSE改善、两个CI下界、B5两日空间正/总≥30/日≥10以及future-unscorable门均保留。输出只称报价空间，非inverse nativePnL、账户回报或净alpha；信号不足和技术/数据不可判定不伪装科学通过。
- 生命周期：exclusive formal-started.lock、exclusive输出，gate/source exactinputs匹配；supervisor已try/finally处理Popen/ps/保存异常，terminate→wait3→kill/wait；无重试或另起进程观察。512MiB sampledRSS、1GiB写前disk检查、线程1≤2、1680s含health保留120s验收、全工作deadline02:49:06Z。采样不是OS硬限，最终1800s合计及资源仍须runtime验收。

## 唯一preformal修正

初版scan在测试预测封存前依据future score覆盖率作80%停止。已集中要求将测试检查移至predictions-and-signals-seal后、评分前；训练检查保持。已逐行核与adapter.pre-review-order-fix.py.txt完整diff，只此参数/调用/检查位置变动，规则阈值未变，health不重跑，正式锁核时不存在。

本gate审阅0新网络、0行情读取/解压、0模型或费用计算；仅代码/小回执/指纹/AST。未添加完美NTP、真实fee认证或新方法门槛。actual assistant model/route UNKNOWN。实际source身份、EOF/CRC、权重/预测封存顺序、结果和无活动worker由唯一执行及train_forward_review独立验收。
