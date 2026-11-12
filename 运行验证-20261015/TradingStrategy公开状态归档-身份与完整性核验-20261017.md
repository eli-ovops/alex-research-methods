# Trading Strategy公开状态归档：身份与完整性核验

**结论：取得了一份完整、可读取的公开State JSON，但它不能作为目标ETH-BTC-USDC momentum的实盘盈利账。文件声明的是另一套Ethereum随机RSI策略；记录仓位/交易为空，使用方说明又明确涉及“交易已执行但状态未写入”的故障。文件可读取、backtest_data为空，都不足以证明目标实盘账完整。**

读取日：北京时间2026-10-17；本轮GitHub原件读取于2026-10-16 UTC约18:25—18:29，逐件回执保留实际时刻、URL、HTTP、原响应和SHA-256。仍只研究，不模型/训练/回测/策略/来源代码、SDK、SQL、EVM执行，不运行测试或Anvil，不账号认证凭证/钱包/安装/付款/交易/外发/监控修改或删除。没有重取受拒网站或执行器。

## 1. 真正取到的文件

固定官方trade-executor提交34fc7eb0b6594d21acc2fc88ab230a95794779f7：

- 路径：tests/mainnet_fork/wbtc-broken-position.json。
- 解码后完整74582字节；SHA-256为889f312502214546e74475750d5bcc5f325571e2afda3b019085337418f29554，Git blob为0965dd906a01e39e91af61802e69dcc762f47ebf。
- 只做Base64、JSON解析和内容指纹核对，没有加载其Python类型、反序列化pickle、恢复交易或执行任何来源代码。
- 先按BTC文件名、协议目录与小文件大小选取，再检查内容；没有按利润排序选择。

[固定原JSON](https://github.com/tradingstrategy-ai/trade-executor/blob/34fc7eb0b6594d21acc2fc88ab230a95794779f7/tests/mainnet_fork/wbtc-broken-position.json)。

|原字段/记录|实际内容|本轮解释|
|---|---|---|
|name|null|没有目标策略名称绑定。|
|backtest_data|null|单个空字段不证明它就是完整实盘账。|
|created_at|2024-07-19 06:01:51 UTC|文件声明时间，不是已独立验证的全部交易起点。|
|last_updated_at|2024-07-24 14:57:01 UTC|不覆盖目标声称的4月1日至8月5日完整账期。|
|deployment.chain_id|1|文件声明Ethereum主网身份；未独立取链上原收据验证。|
|vault_token_name|ETC/BTC Stochastic RSI crossover|按原拼写记录，不据此判断实际币种，也没有绑定目标绩效。|
|记录的open/closed/frozen positions|均0|仅文件内记录，不能推出链上实际没有仓位或交易。|
|从上述仓位取到的trades|0|不构成有盈利或没盈利的证明。|
|reserves|1条|余额存在不能当利润。|
|accounting余额变更引用|cause=correction|纠错引用不是经营收入，未将其美元字段计入收益。|

## 2. 使用它的测试说明为什么重要

实际明确引用该JSON的test_correct_accouting_position_should_be_open.py，指向另一个策略模块strategies/test_only/enzyme-ethereum-btc-eth-stoch-rsi.py。其说明是开仓交易执行过、但状态没有写入；使用Ethereum mainnet fork固定块20377193，配置UNIT_TESTING、UNIT_TEST_FORCE_ANVIL与SKIP_SAVE，测试check-accounts/correct-accounts修复流程。

我们只读这些文本，没有执行测试、启动节点或读取运行环境变量。[固定使用方源码](https://github.com/tradingstrategy-ai/trade-executor/blob/34fc7eb0b6594d21acc2fc88ab230a95794779f7/tests/mainnet_fork/test_correct_accouting_position_should_be_open.py)。

因此：

- “文件在tests目录”不自动说明全部内容都是虚构，它可能包含真实故障的派生材料。
- “有部署地址/交易哈希”也不自动说明账本完整或可用于复现目标收益。
- 这个使用方明确研究缺失记账，不能用JSON里0条交易推断现实没有交易。
- 即使它是真实故障快照，也未绑定目标名称、规则版本和完整账期，不能拿来补运营方自报7.87%的原账。

最初另读的test_frozen_position_and_blacklist.py实际是无关BNB测试，不引用本JSON；已保留这份材料，但不作为本文件来源或目标策略证据。

## 3. 搜索和目录覆盖到哪里

两条GitHub代码搜索分别为：目标名称加JSON扩展名返回0；具体执行器ID返回3条代码/注册结果。搜索覆盖不等于所有大文件内容，因此没有据此说原账不存在。

进一步从固定根git tree取得tests树SHA5155da2cdb7dcfd27f840fde2e68c91e77bb728a，再取得其完整递归元数据：truncated=false，434个文件，其中49个JSON。文件名中没有直接包含eth-btc-usdc或enzyme-polygon-eth-btc的JSON。[固定tests目录](https://github.com/tradingstrategy-ai/trade-executor/tree/34fc7eb0b6594d21acc2fc88ab230a95794779f7/tests)。

这只证明该固定tests树的文件目录已枚举；不证明通用名state.json没有相关内容、不证明其他分支/网站/外部归档没有文件。本轮没有下载49份JSON或数MB至数十MB的大dump/notebook，也没有把文件大小当数据有效性或收益证据。

本地收敛安排先6次位置读取，基于实际发现的state目录和小JSON扩到10次文件级核验，之后仅增2次树元数据完成有限清单。用户已取消总体读取/时间上限；这些调整未扩展模型、策略或交易权限。根总12次GitHub读取后停止联网。

## 4. 发布附件与导出文档

独立子任务读取当时官方发布清单：per_page10实际返回3条2026年发布，三条assets均为空。只说明当前取得清单未提供目标2024快照，不推断历史从未发布或附件从未存在。

[Docker部署文档的固定Git blob](https://api.github.com/repos/tradingstrategy-ai/trade-executor/git/blobs/25a36e235b86cf6268ec34ad35aeeab330c2900f)说明每个执行器有独立域名/状态文件，生产状态与镜像、环境和state volume应对应；示例不是本目标。[strategy-input-recorder固定Git blob](https://api.github.com/repos/tradingstrategy-ai/trade-executor/git/blobs/6241d204df2c4b61ef24ad243574f2d41e99cce0)明确该记录器不是状态归档或重放引擎，且不包含state-file copies；不能把决策输入记录当完整持仓/成交/资金账。这两份不可变blob未在本轮独立绑定到前述34fc提交，不混用版本身份。[本次发布清单原API](https://api.github.com/repos/tradingstrategy-ai/trade-executor/releases?per_page=10&page=1)是读取当时的可变清单；保存的响应与UTC、指纹见protocol/archive-provenance-admission.json及原件。这些是文档机制证据，不是目标实盘文件已取得的证明。

## 5. 对赚钱与复制判断的影响

目标策略的价格趋势假设和历史代码仍可研究。但现在没有完整目标信号、持仓、成交、外部资金流、全部费用及实盘版本，不能独立确认7.87%是怎样取得、是否完整扣费，更不能证明个人复制净优势或资金容量。

本轮的重要发现是一个实际反例：**状态文件中的“没有交易记录”，可能来自记账故障，不能替代真实资产与成交原件。** SHA核验能证明读取了同一文件，不能证明文件经济记录完整。

下一唯一核验将收敛到代码对具体历史状态文件的引用：确认目标策略模块或运行记录，是否指向某一个通用文件名的原始快照，再决定是否值得读取那一个文件。不会盲读全部大JSON、重取受拒服务或用新回测补账。若明确引用仍只得到异名、模拟、故障或缺期文件，就结束该候选的盈利准入，保留研究样本和未核事项；没有证据不宣称它亏钱或不存在原账。

已有Aave借贷正现金流材料已作为避免重复工作的导航复读；其原结论明确是借贷服务收入比较，不能替代当前要找的预测/做市策略样本。因此本轮未改其结论，也未转成新的借贷交易建议。

报告/原件：evidence/tradingstrategy-state-archive-20261017/。本轮新增完整小JSON、使用方故障说明和有限目录清单，改变下一行动，为progress。原FAILED/9400/50/188、AAPL/Issue85和监控不变；财富目标未达、goal active。
