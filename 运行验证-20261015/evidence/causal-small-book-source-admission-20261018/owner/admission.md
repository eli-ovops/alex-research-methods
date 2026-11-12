# SonarX L2 summary：许可正面，零付款小样本未就绪

**结论：发布者许可 YES；独立快照结构 YES；本轮零付款、无账户且体量明确的小样本准入未成立。**只查这一候选，5/8动作后早停，没有调用S3或下载行情。

[发布者数据页](https://sonarx.com/datasets/hyperliquid/l2-order-book-snapshots) 更新2026-09-16，L10–17说明每市场/区块一份双侧top20快照，排序后的首档为最佳报价，数量为同价位挂单量合计，另有订单数。独立L2快照不需先获取全L3才可研究；但内容完整一致仍未实测，block_time也非collector arrival。

[发布公告](https://www.sonarx.com/blog/sonarx-releases-hyperliquid-order-book-snapshots) 日期2026-02-26，L12–14明确公开数据CC0，并允许任意用途。L59说明按周加载、滞后两天；公告初始仅HIP3，不能以它证明所有standard perp当日已覆盖。

[当前官方文档](https://docs.sonarx.com/datasets/HYPERLIQUID/public-l2-snapshots) L50–63同样明确CC0、top20、每20区块采样；L144当前覆盖HIP3和standard perpetual，非spot。CC0对个人预测研究有明确正面依据，未凭空要求额外ML批准；不作所有上游权利或交易资格保证。

真正阻碍：文档L100及L129明确S3为requester-pays，传输费由请求者承担。因此“免费数据/无需平台账户”不等于本任务零云费用且匿名可取；本轮不配置AWS、不付费、不请求bucket。文档示例给出精确路径
`s3://sonarx-hyperliquid-public/market_data/perp/BTC/l2-summary-snapshots/886370000/886372000.json.gz`，
但未提供其字节数/实际覆盖日期；示例不是文件存在与小体积回执。

日期范围、对象内容hash、数值单位的精确合约映射、断点/缺侧及时间一致性均未实际核验。每20区块快照会跳过中间变化，只可提出“后续观察到的快照价格变化”问题，不能直接冒市场真实下一事件方向；这不否定快照预测研究。

唯一最小缺口：同一发布者是否提供不由请求者承担费用、无需账户且有明确bytes的小型独立快照对象说明。此轮未取得，不联系、不追加来源或实验。若不存在本轮证据，只保留该限制，不推整个方向不可行。

动作：2queries＋2open＋1click，3次原生调用；精确逐次UTC未捕获，读取日2026-10-18。原生全文保存，非HTTP原件；文档示例未当本轮行情读取。行情包、模型、代码执行、回测、安装、账户、付款、交易0。actual model/effort UNKNOWN，旧结果与其他文件不改。

