# 固定预测提案的原始依据与边界

**PASS_LIMITED：足以形成可审阅的固定提案，不是实验或盈利通过。** 已保存两份原生工具返回、逐次回执、`proposal.json` 和 `draft-protocol.md`。本轮6次逻辑 open、2次原生调用；没有 HTTP 行情请求、实现、训练、推理、评分、回测或交易。实际 model/effort 均 UNKNOWN。

实际读取的四个原始入口：

- [Cont 等：The Price Impact of Order Book Events](https://arxiv.org/abs/1011.6402)，只读作者摘要和提交记录，首次提交2010-11-29，v3为2011-04-13。它提供美股短区间研究动机，不证明本题60秒。
- [Gould、Bonart：Queue Imbalance as a One-Tick-Ahead Price Predictor](https://arxiv.org/abs/1512.03492)，只读作者摘要和提交记录，v1为2015-12-11。下一 tick 与本题 BTC 60秒不是同一命题。
- [XGBoost 官方参数](https://xgboost.readthedocs.io/en/release_3.0.0/parameter.html)，页面实际标3.0.5，读取 CPU/hist/正则、平方损失、base_score、种子定义。路径名不冒实际运行版本。
- [Ridge 官方文档](https://scikit-learn.org/1.6/modules/generated/sklearn.linear_model.Ridge.html)，实际标1.6.1，读取平方误差加 L2、alpha/截距与 SVD 说明。

六特征、60秒、5秒 quote-age、两小时窗口、各模型数值与1%门槛都是本提案选择，不是论文已验证最优值。34日只是固定日历候选；没有文件或有效样本数量证明。旧版16测试日与新版3日分开；后者即使通过也不足以证明稳健显著或持续赚钱。

已有官方 schema 支持双时戳、标准化 quotes、边数及 raw 断线标记的区别。CSV 无断线记录，整日 GET 不支持 HEAD/Range。报价长期不更新不等于断线；5秒筛选只是限定研究域。标准化 BBO 不要求每个 raw 前缀自带完整快照；供应商重建及更早历史仍有假设，观察到断线后的恢复规则另列。

Tardis 专用统计例外不覆盖基础/通用 AI；上游 Kraken 经第三方接收后的此项离线适用仍 UNKNOWN。§9.5 的外部提供方条件涉及 Data/Manipulated/Derived Data；当前 Codex 工作流未证满足，汇总误差或收益也不能自动送来审阅。提案保留合格本地处理及结果复核路径未就绪的条件，不索取账户、不擅自要求一律授权信。

`source-review.json` 逐个绑定14个实际输入的绝对路径、SHA256和字节；回执把原生抽取与 HTTP 正文/流量区分，单次精确 UTC 未捕获则记 UNKNOWN。唯一下一问题是该固定输入计划在既有适用条件及硬资源上限内是否可取得并一致归一，当前未执行，也不因保存配置获得执行授权。
