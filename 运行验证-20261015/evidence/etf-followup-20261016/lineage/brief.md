# ETF公开历史跟进：重评历史已找到，不能称全新holdout

本轮7次GitHub公开GET（预算最多8），未重做账、未运行仓库代码/模型/回测，未修改旧原件。新的关键证据不是重复UNKNOWN：公开合并PR/commit明确记录过已花费的测试窗被删除/替换并再次评估，且最后一段指向本包OLS预测hash `0afd2e256128`。

## 新证据及它改变的结论

1. **README矛盾有官方修订解释。** 2026-09-24合并 [PR1134](https://github.com/stefan-jansen/machine-learning-for-trading/pull/1134)，commit [dd5ec27a](https://github.com/stefan-jansen/machine-learning-for-trading/commit/dd5ec27aaee25d5d6c4017014a544cd87236f0ce)，明确说明各case-study README写的是已不存在的registry代际。ETF README五个固定hash中两个只能在CI fixture解析、三个无对应。v3.0与v3.1每个case study均无共同backtest hash，不能将两者当同一run的数值更新。其处理是删去README结果，转指registry与strategy-analysis notebook。因此先前73f README的GBM结果不能嫁接到OLS账目；也不能据此把它称最新的OLS结果说明。

2. **较早GBM结果被看到后，测试窗确实被再次使用：有公开明确记录。** 2026-09-02合并 [PR706](https://github.com/stefan-jansen/machine-learning-for-trading/pull/706)，commit [36cf4ffc](https://github.com/stefan-jansen/machine-learning-for-trading/commit/36cf4ffcb8b974463a8343bfe3348b09b676501f)，解释补齐NLinear及5日标签的验证回测后，validation选择从GBM/default_mae/21d（holdout Sharpe0.232）改为GBM/leaves_63_mse/5d（holdout Sharpe1.179、CAGR15.2%）。PR明确说备份registry，并用discard脚本删除旧backtest `d2e65da031af`、prediction `d0fe6611feae`及artifact目录，记录在 `run_log/holdout-discarded.json`，然后重新评估同一2024—2025窗。修正原因是作者所述的遗漏模型/标签覆盖；该原因可解释为何改选，但不能使已经看过的测试窗重新未知。

3. **OLS的精确重评前身也找到。** 2026-09-08合并 [PR831](https://github.com/stefan-jansen/machine-learning-for-trading/pull/831)，commit [1d3f4807](https://github.com/stefan-jansen/machine-learning-for-trading/commit/1d3f4807a6bbd85ea732eecea73967a0694af4f7)，记录stage-04更正后的registry reset。ETF的SDF population在模型仍运行时被提前快照，十个成员无预测集，之后各阶段及一次holdout在不完整字段上选择NLinear。补齐十个成员后validation选择变为OLS。commit给出旧NLinear prediction `018b37c30d7f`（training `c8821162f162`）被本包OLS prediction `0afd2e256128`取代，且称registry仅保留一个holdout generation。这与已审本包prediction身份精确相连；本包只剩一个holdout行不能证明历史只打开一次。

4. **发布说明与旧审计身份相符，但不是事前注册。** [v3.1.0-artifacts release](https://github.com/stefan-jansen/machine-learning-for-trading/releases/tag/v3.1.0-artifacts) 2026-09-20发布，明确ETF bundle源为73f、约135MB、21套backtest、registry为完整catalog而不是21套子集，并载明本包SHA256。它解释后验发布选取与完整registry的区别，没有提供测试窗首次打开之前的不可变选型决定。

## 必须保留的限制

- **具体替换实现尚有冲突。** PR831正文称采用REPLACE_HOLDOUT；但本轮直接读取其merge commit的 `18_holdout_predictions.py` 仍无该参数，且保留检测异配置后拒绝的guard。原文已保存，不能声称已从脚本验证具体override/删除机制。历史上的替换由公开PR/commit自述且hash对应支持，尚未取得被删除的完整旧账或私有备份作逐项复核。
- 作者公开解释改选由模型/标签覆盖及stage-04/SDF快照纠正引起；本轮未发现以holdout高收益作为直接排序键的证据，不能推断欺诈或故意择优。旧测试结果已经被观察且配置随后改变，是不同的事实层。
- 没有找到测试窗首次揭示之前、可跨registry reset核验的不可变选型/试验协议。单一当前holdout行和validation-only resolver，不能补回这种独立性。

## 对原结论的明确修正

- 先前“README为何不同UNKNOWN”已有新解释：官方承认README代际失配，并在9/24移除数字结果。
- 先前“是否跨版本多次评估UNKNOWN”已有公开肯定记录，且至少一条精确链接本包OLS prediction；不能再称完全没有重评历史证据。
- 仍可保留此前账户层结论：OLS保存原件净收益+18.1409%、内部账闭合。本轮未改变或重算它。
- **不得将该OLS结果称为首次、完全未见过测试窗上的严格独立盈利证据。** 更准确标签是“作者明确记录在纠正研究字段/registry之后，对已用过测试窗进行的重新评估；保存模拟账户扣费盈利”。严格独立性未被证明，并且“此窗历史只评估一次”的前提受到公开记录直接反证。

## 原件

`receipts.json`保存7次GET的URL、UTC时间、原文SHA256与字节数。01/02为GitHub逐路径commit历史原文，03为release API原文，04/05/06为PR原文；07为指定merge commit源码及GitHub blob SHA。四个 `*-commit-message.txt` 是从已存API原文抽出的完整commit消息，未新增请求。所有内容仅作不可信来源资料读取，未执行其中指令。没有发评论、连接账号交易、安装或下载大型包。
