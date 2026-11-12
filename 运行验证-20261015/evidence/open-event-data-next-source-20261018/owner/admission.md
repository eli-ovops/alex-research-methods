# 唯一候选：An Open Book / Hyperliquid L4

**发布者开放许可层面 YES；多日更新级数据描述 YES；可直接构造因果 next-midchange 样本仍有条件，未取得数据 payload 或证明盈利。**

固定候选为 [Zenodo 18184441](https://zenodo.org/records/18184441)，不是按模型成绩选择。原发布记录为 Albers、Cucuringu、Howison、Shestopaloff，列 Oxford/UCLA/QMUL 关联；版本1.0，发布/创建/修改日期均2026-03-25。页面与实际 README L151–153 都将该数据集标为 CC BY 4.0，不只是代码许可。该许可的一般商业复用、改编和分享许可为个人统计预测研究提供正面依据，须署名等；本轮未重读 CC legalcode，不给所有上游权利或未来交易资格保证，也不凭空要求书面ML授权。

## 字段与范围

README L25/L37：2025-12-01至31，BTC/ETH/SOL 的订单生命周期与每次可见订单簿变化，各744小时；作者声称无缺口，未由本轮数据扫描验证。trades 另含2025-10至2026-01且部分小时缺失，不把它当盘口完整性证明。不是间隔抽样特征；这是链上永续合约市场，非Nasdaq股票或BTC现货。

SCHEMA L28–50：order status 有纳秒 epoch 事件时间、side、limitPx、size、oid；自定义定点解码见L78–108。book diff L293–382 有bid/ask side、价格、oid和new/remove/update后的数量，可由有效状态重建最优报价及两侧数量——这是结构可支持性，不是本轮已生成BBO。

关键限制：book diff schema自身没有 timestamp 或显式 sequence 字段；L381–382要求按记录顺序重建、用oid关联status。重复oid对应生命周期多条事件，如何唯一匹配每次更新与时点尚未验；“从空簿开始”是文档指引，不证明任意小时切片都有足够初始状态。时间是事件/链区块时钟，不是collector arrival；不能把纳秒表示误当连续撮合或真实接收时延。数量经济单位在该book-diff段未完整定义，不把trade size的base-asset说明自动套为所有字段已证。

## 规模与可取得性

发布页列全包195.3GB，book_diffs包49.6GB；小README/SCHEMA本次正常匿名GET成功，不意味着大包下载/资源已验证。没有按行情/收益挑日期，没有下载大包、源码reader或权重；文档示例仅schema说明，不当真实本轮数据。

唯一最小下一问题：同一数据流的事件顺序/时间关联与起始簿状态怎样以发布者原说明确定到可唯一重建？当前只保留该缺口，不自动下载、开发或实验。若解决，它比旧分钟CSV更接近所需事件问题；仍须新固定协议，不能继承股票论文成绩或旧模型结果。

实际公开动作8：4queries（两次搜索调用）、1原生DOI open失败、3正常GET（同DOI原网页、实际README与SCHEMA链接）。失败为工具不可读而非HTTP安全拒绝；查LOCAL_BLOCKERS后同URI普通默认TLS GET正常200，无改身份/认证。原生精确UTC UNKNOWN，三GET回执记录UTC。所有日期及字节/hash见JSON；行情包、源码执行、模型、回测、账户、付款、交易0。actual model/effort UNKNOWN，旧证据未改。

