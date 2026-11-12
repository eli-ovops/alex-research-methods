# Fast Lane 2023交易前规则：有限来源准入

**取得早期官方协议意图/参与与报酬规格披露；未取得可绑定block16862554实际目标实现的事前源码版本/审计。** 不用2025bot或资料商latest实现回填。原交易真实报酬与gas事实不受此来源缺口否定，但未满足完整事前公开策略及净盈利准入。

本轮3次GH GET（上限4，收敛提前停），2次native web调用（1open、1search含2queries），无账数据请求。每次GH25秒/1MiB cap；原HTTP/header/body、精确URL/UTC/hash与结果见read-receipts.json。native保存工具抽取返回而非原HTML/网络bytes；精确请求UTC与HTTP状态未返回，标UNKNOWN，保存UTC不冒读取时刻。actual model/effort UNKNOWN；规则版本沿用。0来源代码/ABI/SDK/SQL/EVM/trace/模型/回测/策略/交易执行、安装、认证、付款或外发。

## 已有事前披露到哪层

[官方治理POC](https://gov.bancor.network/t/proposal-improved-value-capture-and-fast-lane-poc/4142)显示开帖2022-11-16；L328–335的11月21日回复明确说从exempt wallet改为任何找到机会者可用的合约，caller获10%利润、上限100BNT。正文功能段L71–84要求寻找跨池机会、计预期gas/交易费后提交。它是可参与机制及成本意识规格，不是完整实现/价格最小回报guard/白名单校验的源码证据，不保证每笔经济净利。

今天原帖有修改迹象（帖日期2022-11-16但Snapshot预期2023-02-05）；不拿最初帖日期给今天全部文字加事前时间戳，也不把现在读到的带日期帖当当时不可变归档。11月回复支持历史公开讨论早于结果的来源等级，精确首公开仍未独证。此POC本身未明示实际0x41eeba…完整部署身份；与目标的地址对应仍依赖已读同日更新讨论及真实交易，不拿泛规则作逐字节实现绑定。

## 官方代码发布与查询边界

- 官方fastlane-bot默认分支历史查询`until=2023-03-19T15:07:35Z`返回HTTP200空列表。只能说当前该分支可达历史查询无符合项；不证明旧分支/移除历史/其他repo或私有阶段当时不曾公开。
- 已由官方README链接观察的v1.0 release，实际published_at=2023-07-24T12:54:42Z、created_at=2023-05-23T18:33:31Z。说明它为BNT起讫单三角的原始bot并即将弃用，但两个时间均晚于3月19日交易；release字段不是精确源码首公开，更不是该笔使用bot证明。target_commitish是main，不固定历史提交身份。
- 在官方org精确合约类名`contract BancorArbitrage`代码搜索返回0；仅限这一次搜索范围，不能推官方从未有源。第二次native搜索未给所需早期Fast Lane审计/源码原件，搜索中的Carbon审计及2023年后续POL讨论不移植到此合约。

旧官方3月19日更新页说机会发现bot将开源；这与后来发布原件相容，但不是对所有可能先前发布的否定。今日MIT入口或最新ABI也不能自动覆盖2023实现许可和完整发单规则。

## 唯一最小剩余证据

根负责查的历史实现地址/升级原事件，是把实际0x41eeba3355d7d6ff628b7982f3f9d055c39488cb在block16862554的逻辑与具体源码版本连接的下一入口；本子任务没有重复取槽位、升级日志或访问受拒资源。若取得实现，应再按该原件具体源码/发布记录判断公开权限、报酬、价格/费用约束及许可，不能由规格补实现。完整机会选择程序若仍未公开要列具体缺项，不默认要求所有私人bot/秘密来承认已核单笔现金。

最终状态：`PARTIAL_PREPERIOD_DISCLOSURE_IMPLEMENTATION_SOURCE_BINDING_UNKNOWN`，profit_case_admitted=false。未新取大源码包、账户或收益，停止扩展。
