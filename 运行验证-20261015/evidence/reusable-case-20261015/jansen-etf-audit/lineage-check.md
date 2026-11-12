# ETF OLS holdout lineage窄范围复核

结论：`89e706faf2fe` 的OLS/5日标签/周度交易谱系能够在原始registry、保存spec以及冻结源码notebook输出之间匹配；它与同一冻结commit README所述GBM/21日标签/月度交易是两条不同链。不能把README的GBM推导、benchmark检验或选择调整统计嫁接到OLS的+18.1409%账目。现有证据支持“保存的正收益holdout身份与内部账目成立”，不充分支持“跨版本从未见过测试窗、从未后验重选”。严格fresh holdout独立性：UNKNOWN；也没有证据足以断言作者确实后验挑选。

## 已确认

1. 冻结源commit `73f066b4d225fe5419d1bc67bec7bf24c7e0fec7` 的 `case_studies/etfs/19_holdout_backtest.ipynb` 保存输出（cell 5/9/11）直接写出：
   - Selected configuration `18c7a8419306`, `ols (fwd_ret_5d)`；
   - Holdout training `5ff0fa98f34e`, prediction `0afd2e256128`, backtest `89e706faf2fe`；
   - validation Sharpe 1.023、common-support 1.028；holdout Sharpe 1.310、CAGR8.7%、maxDD−5.63%、398 trades。
   这与已审压缩包原件匹配。无需执行notebook，输出只是原文保存证据。
   来源：https://github.com/stefan-jansen/machine-learning-for-trading/blob/73f066b4d225fe5419d1bc67bec7bf24c7e0fec7/case_studies/etfs/19_holdout_backtest.ipynb

2. 但同commit README第51—57行叙述另一链：`gbm/default_mae`, `fwd_ret_21d`, validation `fb287093aa02`/prediction `ac905a96646f`；2026-08-31 holdout training `882301dc3655`/prediction `d0fe6611feae`/backtest `d2e65da031af`，CAGR2.2%、Sharpe0.232。该README五个身份在本次registry均没有对应行。不同的不仅收益数字，还有模型、标签、频率、止损配置与身份；不能解释为同一run的单纯四舍五入或daily/equity口径差异。
   来源：https://github.com/stefan-jansen/machine-learning-for-trading/blob/73f066b4d225fe5419d1bc67bec7bf24c7e0fec7/case_studies/etfs/README.md#results-at-a-glance

3. 全registry有2,308个backtest，stage/split分布：validation signal1818、allocation378、risk_overlay60、cost_sensitivity51；唯一holdout为89e7。此前21套原件是发布选取的artifact子集，不是研究试验总量。现存registry没有第二个候选holdout供本次从中选优。

4. 原始运行commit注册为`19b5193c`，training.runtime/spec.provenance给出完整 `19b5193c6c7faaf3596b100234725d555ab20c86`；release的SOURCE_COMMIT是73f。因此发布锁源版本与实际账目运行版本必须分开。本次额外只读取得19b的18/19脚本及strategy_analysis，未执行。

5. 19b `strategy_analysis.py:533—818` 的公开选择规则从 `p.split='validation'` 中选择跨signal/allocation/risk_overlay候选，以保存Sharpe排序；存在conformal候选时再按共同时间支持比较，不以holdout收益决定赢家。73f的carrier_pins为 `{}`，没有ETF人工固定pin。当前完整registry直接SQL按原始保存Sharpe排序的第一名也为18c7 OLS/fwd_ret5d（1.023346），与保存notebook的选择吻合；未重新计算共同支持收益或执行resolver。
   来源：https://github.com/stefan-jansen/machine-learning-for-trading/blob/19b5193c6c7faaf3596b100234725d555ab20c86/case_studies/utils/strategy_analysis.py#L533
   来源：https://github.com/stefan-jansen/machine-learning-for-trading/blob/73f066b4d225fe5419d1bc67bec7bf24c7e0fec7/case_studies/utils/carrier_pins.py#L36

6. 现存时间顺序与同一链的事前validation选择相容：OLS validation training 2026-09-06T14:02:53Z；validation prediction 9/6T14:03:03Z；18c7 validation backtest 9/7T05:48:36Z；holdout training 9/7T15:38:09Z、prediction15:38:10Z、backtest15:38:39Z。18c7与89e7的strategy相同：HRP/top10/vol_window63、weekly_friday_close、6% trailing stop。holdout模型重新训练，train 2006-01-03—2023-11-29，test2024—2025，源spec记录21D标签buffer。

7. 19b `18_holdout_predictions.py:224—259` 已有保护：扫描现存holdout generation，若不同refit/checkpoint已存在则拒绝切换；文本也承认可以通过registry lifecycle退役旧评估且必须记录原因。该保护代码存在，不等于证明历史上每次都运行/未绕过；本次没有执行。
   来源：https://github.com/stefan-jansen/machine-learning-for-trading/blob/19b5193c6c7faaf3596b100234725d555ab20c86/case_studies/etfs/18_holdout_predictions.py#L224

## UNKNOWN与使用界限

- 无法确定README的GBM链是旧版、其他registry快照、尚未同步文档，还是来源错误；冻结树同时保留相互不同的结论，作者未在本次原件给出明确修订映射。
- README明确声称2026-08-31已经观察同一2024—2025窗的另一GBM holdout；OLS run登记于9/7。该历史声称本身未由本包旧账证实，但足以使“此窗从未被观察”不能当作已证实。不能把本包只剩一个holdout行理解为历史上只做过一次。
- registry `decision_artifacts`、`candidate_sets`、`artifact_supersessions`为空；没有可供本次核验的不可变、带时间的事前选择声明或旧GBM→新OLS退役依据。官方population记录验证候选集合，但不证明作者从未看过测试窗。是否依据旧holdout结果改选OLS：UNKNOWN。
- 全registry 2,308次试验说明validation搜索广；本次不重跑选择调整统计，也不把README针对771/GBM等其他链的DSR、PBO及benchmark统计套到OLS。
- `training_runs.runtime_json`/spec.provenance只记录Python3.14.3、joblib1.5.3、numpy2.3.5、scikit-learn1.7.2与19b source_commit；未记录ml4t-backtest版本。实际backtest engine版本UNKNOWN，由根另取原始锁文件核验，不以73f较新锁版本替代。
- 账目闭合、模型身份匹配、数据许可、执行价语义及严格样本外独立性属于不同证据层。本次未新增行情、未执行代码/模型/回测，未把+18.14%升级为可交易优势或真实成交结果。

## 本次证据与预算

新增源码10个文件、370,458字节，含73f必要脚本/notebook及19b实际运行源3文件；URL、blob SHA、SHA256与UTC读取时间在 `lineage-source/source-receipt.json`。本地只读SQL及结果存 `lineage-registry-selects.json`；原始registry及已审账户原件未改动，未重做账目。
