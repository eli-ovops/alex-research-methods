# FinMem公开记录准入：实现已绑定，真实测试原账未取得

选定公开实现 [pipiku915/FinMem-LLM-StockTrading](https://github.com/pipiku915/FinMem-LLM-StockTrading)，固定commit `be814aa47970de9bf2fdd6a1d5a60ae5cf361b46`。完整树已取得、truncated=false；该版本的训练/测试输出、checkpoint、结果目录只有.gitkeep，公开Releases接口返回空列表。已读README没有实际交易原账下载链接，管线示例明确是假数据。因此当前不能完成“逐日决策→持仓→成交→全费用→净收益”的原件核账，个人可复制净优势未通过。本结论限定该固定版本/已读说明和Releases，不宣称从未公开、所有历史提交都无输出或方法不可行。

## 公开链与版本

本轮6/6公开动作：一次检索、commit元数据、递归tree、固定README、Releases、固定data-pipeline/README。没有重复读取论文。检索包含其他同名fork/改写线索，仅选一个实现，不据第三方official标签认证作者身份。README L1–21实际自述提供arXiv2311.13743代码且列论文引用；这足够作为对应公开实现候选，论文Owner随后取得的v2完整原件实际href指向该repo：本Owner仅本地复核该href（不重复论文内容/新增网络），因此论文→repo关联已有作者文献正面依据。repo控制人个人身份及论文实验具体commit/run仍未独立绑定；不把作者亲发另设门槛。

- commits?per_page=1实际HTTP200；2026-10-19T03:39:36.143325Z取得HEAD候选。Git author/committer日期均2024-08-18T01:58:13Z，message为Update reflection.py；Git日期不等于独立事前公开证明，更不证明当时已运行。
- 固定tree实际HTTP200；2026-10-19T03:39:43.545352Z，18588B、75entries/59blobs、truncated=false。commit元数据内tree对象SHA为 `3c86d9bd549e62bfbbab34993dd96ad04bef4055`；git/trees/commit接口响应sha字段为所请求commit字符串，两者原样记录，不混称为同一Git对象。
- 固定主README 12013B，2026-10-19T03:39:55.075270Z；Gitblob `011e7c293b68de03aad2c7552465f51f42bb6c55` 与tree、长度均一致。正文更新段日期为2024-01-16/03-11/06-16，属于repo自述，不是原实验封存回执。
- Releases?per_page=100实际HTTP200、正文 `[]`，2026-10-19T03:39:55.075716Z。没有本次可见release资产可取，不从它推断所有tags/外部渠道均为空。
- 固定管线README 7486B，2026-10-19T03:40:13.795758Z；Gitblob `b8d42f0de46d8f3c8a8776e1111d07d01660b2e1` 与tree/长度一致。完整URL/UTC/HTTP/SHA见编号receipt与receipts.json。

## 实际目录与记录缺口

| 目标原件 | 该tree实际证据 | 可核程度 |
|---|---|---|
| 逐日模型输出 | data/04_model_output_log、05_train_model_output、07_test_model_output只有0B .gitkeep | 没有真实输出可验字段、日期或模型响应 |
| 训练/测试checkpoint | data/06_train_checkpoint、08_test_checkpoint只有.gitkeep | 未取得实际状态/版本清单；不读/反序列化pickle或其他权重 |
| 持仓、成交、费用与绩效原账 | data/09_results只有.gitkeep，完整tree未列独立CSV/JSON/日志账单 | 当前版本缺可供实际读取的原账路径，不能核现金/持仓守恒或费用扣除 |
| 输入/样例包 | data/01_raw、02_intermediate、03_model_input亦为.gitkeep；tree另有data-pipeline/Fake-Sample-Data.zip，9621701B | 只查目录元数据，未下载/展开；不能冒充论文真实输入或测试原账 |
| 图/视频/计算脚本 | figures为character/memory_flow/workflow图，FinMem.mp4约19.8MB；有metrics/visualization等脚本 | 未下载图视频、未执行源码；脚本存在不等于保存了实验结果 |

具体条目与blob保留在 `03-tree.response.json`；定向结果目录清单见 `record-path-inventory.json`。本轮最多一份≤1MiB纯文本测试输出的额度没有使用，因为未发现对应实际文件。没有拿脚本、README示例或假样例替代测试输出。完整tree范围不等于逐一读取所有源码/历史分支。

## README解释与权利边界

主README L123–160将功能明确称Simulation，列train/test及checkpoint/result路径；L144说明训练向记忆填信息、测试用记忆与新信息决策。这里的输出路径是将运行时生成的位置，不是已有输出原件；也没有事前封存信号/真实账户、经纪商fill或逐笔费用回执。完整交易费数值、买卖价格时点、融资/数据/模型服务成本不能由README认证，本Owner不执行或扩读代码判断。

管线README L5、L19–20称部分输入为Refinitiv/Reuters Private Dataset；L37–44描述Yahoo/yfinance价格与pickle输出；L80–99明确Fake样例来自TextDB3、不是real stock data，只展示管线，并有人工新闻。上述只是说明，不授权取得/再分发这些来源数据，也不证明论文实际输入可完整重建。正文外链通向数据/API服务和示例来源，不是已提供的真实测试输出原账；本轮未跟这些链接获取数据或注册。

主README的MIT徽章是代码许可自述，tree中LICENSE1114B但本轮未另读许可证正文；不以它认证数据、新闻、模型/API服务使用权。tree显示跟踪.env文件（98B），只记录路径/风险线索，未取内容、未读取任何凭证，不能在未读情况下声称含有效秘密。

## 收口

下一项能改变原账可得性判断的是：与明确版本、数据区间和模型调用绑定的纯文本测试决策/持仓/成交/费用输出及清单原件，或真实公开资产的具体入口。当前不能靠运行代码生成一份新模拟账来替代作者原结果。保持同一案例收口，不再搜供应商/其他实现，不启动模型或回测。

实际model/effort UNKNOWN；PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4沿用。无源码执行/import、模型/训练/回测/新收益计算、行情/权重/DB下载或反序列化、安装、账号登录/凭证/APIkey、付费、外发、交易；未修改其他目录或旧证据。

## 同轮论文Owner的身份补件

仅复用本地 `../paper/03-paper-v2.original.html`（268877B，SHA256 `033158fd0d7990bac65afc4fabb1349566ac38ad24cb9eedebdce3be67739286`）的实际anchor href `https://github.com/pipiku915/FinMem-LLM-StockTrading/`，UTF8原件零基字节偏移27637。链接是论文内原件，不依赖搜索official标签。此补件改进项目关联，不填补输出.gitkeep、空Releases或原始run缺口。最后第6读已用于管线README，未追加LICENSE读取；代码MIT正文仍未核、数据/服务权利不推定。
