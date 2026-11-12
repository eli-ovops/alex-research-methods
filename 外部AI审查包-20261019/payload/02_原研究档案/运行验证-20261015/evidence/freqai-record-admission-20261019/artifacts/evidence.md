# FreqAI代码与原始输出准入：框架已固定，特定实跑原账未闭合

本轮5/5公开动作完成。已固定维护方freqtrade/freqtrade的完整仓库树及FreqAI官方说明，取得一份实际小结果元数据；它是测试目录的StrategyTestV3回测夹具，**不能作FreqAI论文逐时预测、真实持仓成交或费用原账**。当前检查范围不足以认证可复制净利、容量或财富目标完成，也不宣称所有版本/外部渠道从未公开结果。

## 身份、版本与取得范围

入口为 [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade)。官方仓库固定 `docs/freqai.md` 实际正文L7–10介绍FreqAI并链接freqtrade.io正式文档；L88–100明确引用JOSS论文 `10.21105/joss.04864`、2022、作者与题名。本Owner不重复读论文，JOSS→repo反向链接由paper Owner独立核；本轮有仓库正式文档→JOSS的实际关联，不用同名fork冒官方。

2026-10-19T04:08:11.956151Z正常公开commits元数据GET200取得commit `b8ca1a9fcd3ca715fda3b731afb6a1667c261517`，Git author/committer日期2026-10-18T17:56:01Z。这个2026提交不是2022论文精确run的绑定；Git日期也不是独立事前发布或当时运行凭证。commit元数据tree SHA为 `a04d31acf25361c1954ae21db04bd65f77081687`，git/trees/commit接口响应sha字段原样为请求commit，分别记录不混称对象。

2026-10-19T04:08:21.165682Z递归tree GET200：216169B，885entries/780blobs，truncated=false，低于2MiB保护上限；完整树保存 `03-tree.response.json`。本轮只按路径/大小分类并读两份小原文，不把所有blobs当已逐一审阅。

两份实际文本均在该tree且Gitblob/size一致：

- `docs/freqai.md`，11870B，2026-10-19T04:08:44.139697Z，SHA256 `784af9a1da69638095f6a21b1dd8a2e1b69b47a02370cb51cd69d8467a4211fa`，blob `ab525e9decfe124ce715356449b30794b5128b67`。保存 `04-freqai.md.inert.txt`。
- `tests/testdata/backtest_results/backtest-result.meta.json`，138B，2026-10-19T04:08:44.139992Z，SHA256 `4ee0840b522473f9c0f36d5410075b660118d849010e88f78200a021de1be987`，blob `57ecdb19d7e40a29b64047866fe09f5036b31633`。保存 `05-backtest-result.meta.json.inert.txt`。

## 真正存在的输出，不能替代什么

| 目录或原件 | 实际状态 | 与目标的关系 |
|---|---|---|
| user_data/backtest_results、data、freqaimodels、logs、notebooks | tree各只有0B .gitkeep | 没有本轮可取的实际用户运行预测/模型/成交日志 |
| tests/testdata/backtest_results/backtest-result.meta.json | 已读全文，顶层StrategyTestV3，run_id `430d0271075ef327edbb23088f4db4ebe51a3dbf`，backtest_start_time `1648904006` | 有真实文件和run_id字段，不等于该run被独立执行验证；没有paper、FreqAI模型或实盘身份绑定 |
| 同目录backtest-result.json 132375B、multistrat 235499B及271B元数据 | 仅tree列路径/大小，未下载 | 位于测试夹具范围；未把结果字段、价格或收益读入。本轮没有输出费用/预测schema认证 |
| tests/testdata交易行情、feather、parquet、zip、hyperopt pickle | 仅元数据存在 | 没取/解包/反序列化，不能当特定策略实际成交账 |
| LICENSE | tree列35141B | 本轮未读取正文，不用公开源码或其他fork的GPL标签替代数据/模型/交易所权利 |

当前路径/说明核查未定位到标注为此论文特定实验的逐时prediction、positions/trades、fee ledger及带版本/日期的交付manifest。只读测试meta不能推“所有原账不存在”，更不能将其backtest_start_time与论文出版年份相近当作同一次实验。

## 可导出功能与原始发布结果分开

固定官方说明L14–25、L44–46列可实时重训、保存模型、dry/live和回测等框架能力；这些是功能说明，不是已发生的原始运行交付。L29–42明确quickstart是dry mode，例策略用于功能展示/测试而非production。L54–64解释训练标签可面向未来，是监督学习概念，不由此认定具体运行泄漏或无泄漏。

可见的两个维护者学习文章链接在L114–115：

- https://emergentmethods.medium.com/real-time-head-to-head-adaptive-modeling-of-financial-market-data-using-xgboost-and-catboost-995a115a7495
- https://emergentmethods.medium.com/freqai-from-price-to-prediction-6fadac18b665

本轮只记录实际出现的链接，未读文章，不把标题中的real-time当原始预测/实付手续费证据；未追新资料或重新运行示例。

## 裁决

最低可证为有论文关联的公开预测框架、固定代码版本和测试夹具元数据。尚未认证特定策略事前信号、模型/参数、真实fill、完整收费/资金成本、开放损失或paper原run。下一项会改变原账可核判断的原件是由维护者/论文明确绑定到某固定版本与时段的实际prediction/trade/fee manifest及输出身份；不能靠框架有export命令或新运行一份结果来替代。

全部5项为一次检索、commit、tree及两份小文本GET，无错误/拒绝重试；已停止。未执行/import来源代码、训练推理/回测或新收益计算，未取市场/模型包、DB/权重/pickle，未登录/注册/读凭证、付费/安装、外发或交易。只写artifacts/，actual model/effort UNKNOWN，PERMISSIONS-2026-10-14-v1/ROUTING-2026-10-13-v4沿用。

## 同轮paper Owner身份交叉补件

已仅从本地 `../paper/03-landing.original.html` 的实际href交叉核到官方JOSS→`https://github.com/freqtrade/freqtrade`、软件归档`https://doi.org/10.5281/zenodo.7431513`、review `https://github.com/openjournals/joss-reviews/issues/4864`。该原件21201B，SHA256 `1b044c3c9a9329ed784ae04f2fb4775ac5bb92c920e6780eb4e90b4f66877bcd`；不重复论文正文，不新增公开读取。由此JOSS与repo身份双向关联已成立；归档具体版本/产物由paper Owner核，本Owner不将2026 HEAD冒成2022论文代码。
