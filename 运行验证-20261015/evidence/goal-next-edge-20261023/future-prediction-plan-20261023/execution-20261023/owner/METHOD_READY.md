# METHOD_READY：固定未来报价挑战的执行准备

当前仅准备完成，真实行情读取0、真实拟合0。用户原话“允许这一次完整离线挑战”及范围位于 ../root/authorization.json；方案SHA256 82661a061a639c5ad289fa8d8f64553befaeb4d54960934da705af7ebee5ffea。已完整实读方案、R1闭合、实时输入解释及全局§2/3/4、当前相关LOCAL_BLOCKERS。规则版本沿授权；实际model/effort/speed UNKNOWN。

唯一静态数值代码 challenge.py，无市场模块或策略包导入，无网络接口。默认入口不读源。训练命令 `python3 challenge.py --mode train`；Root的 ../root/train-release.json 必须逐项绑定 code_sha256/proposal_sha256/environment_sha256，环境必须与 environment-prep.json 一致。独审与Root指纹放行前不能调用训练模式。TRAIN_STARTED.json以独占创建防止重复，错误保留failure/usage而不自动重跑。未来模式 `--mode future` 同样需 future-release.json，且11月2日12:00UTC前不读取挑战输入。Root负责两次有界未来文件安排；本代码不自动化、下载或请求今天未来数据。

训练只读取固定两份已封存10月1日缓存，各一次顺读，流内hash/bytes/gzip EOF/CRC和必要身份/L1/local时序检查；仅L1价量列数值化，不重开旧25层、旧标签或金融账。源身份为bitstamp/BTCUSD及kraken/BTC/USD。数据以五个临时typed arrays保存，保留同µs物理序，无排序/去重/修价。严格过去的sample使用searchsorted(side=left)-1，目标标签使用side=right；未找到记录保留NaN和原因，禁止用首个未来值填补。过去记录的值即便过龄也不变更为较早有效行。

格点固定00:01:00至23:59:58每2秒43170点。当前两源年龄≤1秒；100/500ms回看和30个t-2…t-60秒锚点年龄≤5秒；所有取数严格早于各锚点，同戳末行。M0四特征为自身100/500ms log-mid变化×10000、相对mid价差bp、L1数量不平衡；M1追加K的100/500ms变化和当前log-mid基差减30个既往锚点均值。共同预测人口完全由这些t前条件决定；每项missing/age原因及首个互斥原因保留，不按未来标签撤销预测。

标签仅未来B最高买价≤t+1秒的末物理行，年龄≤1秒，除以当前B卖价后减1再×10000；N使用当前买/卖报价比率。训练标签只用于共同训练人口，训练日已见且不报独立成绩。每模型各一次lstsq(rcond=1e-12)：非截距按训练共同已知标签人口均值/总体std标准化；零std机械移除并记录；随后固定添加1截距列，绝不标准化/移除截距。秩/奇异值披露，不更改求解器或正则重拟合。weights.json及MODEL_SEALED.json封存代码/方案/环境/源身份与两套权重，10月31日12:00UTC封存截止不变。

未来输入固定11月1日，Root release提供取得时的bytes/SHA与两个固定owner/future-input/路径；未取得前不声称存在。机械QC通过后按固定权重生成全部有效N/M0/M1预测，以npz及PREDICTIONS_SEALED.json落盘fsync并hash后，代码才调用标签函数。先封存预测人口、缺失和版本链；标签未知只共同不评分。原生文件各一次顺读，后续封存验证只hash小预测文件，不重扫大源。

评分完整保留共同分母MSE/MAE、d0=N-M1平方误差差和d1=M0-M1、UTC288个5分钟块sum/n。共享PCG64(20261023)的1000×288有放回块抽样，以总sum/总n计算，type7线性95%区间；零分母不重抽。主通过条件严格按方案双均值正/双CI下界正、预测覆盖≥50%、已发预测标签覆盖≥80%、≥250非空块；技术/覆盖不合格不可判定，不以MAE翻盘。M1固定七预测桶全部保留n、可评分n、未知标签数与实际Y均值/中位，不挑桶或乘本金。

synthetic-v2检查通过，真实源与真实拟合均0；仅人工OLS一次。覆盖严格/包含边界、同戳末行、1/5秒边界、公式/30锚点、43170格点、标签未知不改变预测人口、零std与截距、OLS/预测往返、M1桶、空块不重抽。第一次合成fixture缺严格早于日首锚点的预热而正确失败，仅补一秒合成历史后通过；failure-synthetic.json、usage-synthetic.json及synthetic-fixture-correction.json保留。没有失败的真实拟合或参数搜索。

已核既有Python3.9.6、NumPy2.0.2/Accelerate合成运行；数值线程环境设1（授权上限2），实际BLAS线程数UNKNOWN。资源以全单600秒CPU、RSS1GiB、新盘192MiB、下载128MiB、主动7200秒、网络等待1800秒为限。已知旧CPU保守预扣36.478407秒；更早项目总量/主动时间UNKNOWN。准备未计量小进程另借记10秒，不冒称实际消耗。两次合成CPU合计0.112881秒，当前已知+保守借记46.591288秒；后续usage逐阶段累加，CPU/RSS/新盘守卫及失败即停保持。未来等待不计CPU/主动工作。当前磁盘18%占用、约1.64e12B可用，仅检查本卷不扩扫。

所有本目录产物用于审阅/封存，保留不清理。保护Library精确目录未访问/stat/hash/search。无安装、付款、凭据、账户/钱包、交易、资金曲线；旧模型/代码/标签/账/STOP均不改。供应商local时钟不代表用户本人接收条件；未来离线通过也只能是该条件下的信息候选，不是赚钱或财富路径完成。
