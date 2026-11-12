# 给Kronos维护者的求证草稿v1（尚未发送）

拟发送位置：https://github.com/shiyu-coder/Kronos/issues/85

动作：在既有公开Issue下新增一条评论。仅在人类明确同意这份稿件后发送；本文件保存和工具可用性不构成发送授权。若当前GitHub账号未登录，由用户自行完成登录，不索取密码、验证码或令牌。

## 中文审阅说明

这条留言询问四个可以改变复现判断的细节：论文表10究竟对应哪个权重/数据/框架版本；信号用原价收益率还是标准化价格差；输入最后日期T的信号究竟在T还是T+1成交；0.15%费用按单边还是往返计算。最后询问是否已有可公开的配置、文件校验值及预测/持仓/费用记录。

公开内容只包括下方英文正文。它不包含用户身份、资金、券商、账户、本地50股结果或本地文件，也不要求作者重新分发供应商授权的原始行情。公开发言会显示发送所用GitHub账号身份；公开后可能被引用或缓存。

## 拟公开的完整英文正文

Hi, thank you for releasing Kronos and for the earlier explanations in this thread. I am checking the reproducibility of the Kronos-small investment simulation in Table 10 and Appendix D, separately from the fine-tuning demo. Could you clarify the following?

1. Which exact public model and tokenizer revisions, Qlib version/commit, and market-data snapshot correspond to the Table 10 small results? File checksums or a fixed experiment configuration would be sufficient where the data cannot be redistributed.
2. Was the paper's stock-ranking signal the raw-price expected return in Equation (13), or a difference in per-stock normalized price space as in the demo? Those scores need not preserve the same cross-sectional ordering when the normalization scale differs across stocks.
3. For a signal dated T whose last historical daily bar is T, was the paper's fill at the close of T or the close of the next trading day? The standard Qlib TopkDropoutStrategy queries the previous trading step with shift=1, so I want to distinguish the signal date from the execution date.
4. Is the paper's 0.15% cost charged separately on each buy and sell, or per round trip? How does it map to the demo's open_cost=0.001, close_cost=0.0015, and min_cost=5?

If a fixed configuration or per-date prediction scores, holdings, and cost records for that experiment are already public, a link would be very helpful. No redistribution of vendor-licensed raw market data is requested. Thank you.

## 公开依据（不额外加入留言）

- 论文v1：https://arxiv.org/html/2508.02739v1
- 固定Kronos源码：https://github.com/shiyu-coder/Kronos/blob/67b630e67f6a18c9e9be918d9b4337c960db1e9a/finetune/qlib_test.py
- 固定Qlib策略：https://github.com/microsoft/qlib/blob/54355232463878d2eebb91fe0ee5fa7fa1f5976c/qlib/contrib/strategy/signal_strategy.py
- 作者关于供应商数据的说明：https://github.com/shiyu-coder/Kronos/issues/100

该求证没有预设论文有泄漏或造假，没有声称重训必然改善，也不代表我们已经复现盈利。它不请求新增训练、付费、行情下载、模型推理或交易。
