# 固定源码的 profit 生成口径

**本轮已核出实际生成链：成功 receipt 中转给 sink 的 WETH 标准Transfer原量之和，被直接写成 `net_wei`。它可以代表收款观察，不能单凭字段名证明全费净利；也不能把已在合约内支付的 builder 竞价再扣一次。** 本轮没有取得任何真实运行收据/账本、执行源码或计算利润。

固定版本仍为 commit `364059aba56e773da01f6507224cf530bbbb1b09`、tree `0958f715725a563f8ebcbf44c81cc133a2e59f22`。复读前单元completion及身份bindings后，新取三份紧邻原件，均与固定tree的blob/大小和本地Git blob SHA1一致。3/4 GET、全部HTTP200，19:24:54 UTC后停止网络，没有为用满预算继续扩张。

## 1. producer 的实际输入与输出

`crates/liq-bot/src/inclusion_feed.rs`（本地 `01-inclusion-feed.source.rs`）全文368行已读。

- L147–190按tracked tx取receipt，读取status/block/gas_used。成功必须已配置非零profit_sink，并有可接受的WETH转入；否则Withheld。失败receipt虽然读得gas_used并构造Reverted观察，但后续L342–344将Reverted的net_wei/gas_used均写None，**这条生产接口不提供失败实际网络费**，不等于费用为零。
- L200–224只选 `REGISTRY_WETH` 合约、Transfer topic、可解码且 `to==sink` 的日志，checked-add原量，返回I256。没有检查from必须为Executor，没有减sink转出，也没有按logIndex去重。它可能包含同receipt中其它来源/自转；这是接口容许的情况，不是本轮发现真实污染或重复。无匹配/溢出/值超出正I256范围返回None；有合法零值Transfer则可以得到Some(0)，与“未知填零”不同。
- L333–358把Included.profit原样写 `OutcomeRow.net_wei`，gas_used另列，没有在这里用effectiveGasPrice/actual fee计算扣款，也没有扣竞价或运营费用。该WETH常量实际地址、18位精度及sink实益归属本轮未另核，不从字段名扩大为已认证ETH账户净额。

## 2. 必须结合 Executor 理解竞价与扫款

`contracts/src/Executor.sol`（本地 `03-executor.source.sol`）关键段已读，未编译或绑定部署。

- L252–299在借款前记录WETH余额，结算各group及利润兑换后测余额增量，再减计划字段 `p.gasCostWei` 与govCost，作为门槛/竞价基数；L305–307据此检查keep/minProfit。**这是合约中的预算/门槛逻辑，不是producer按真实receipt收费重新扣净。** 本轮未追计划gasCostWei的上游生成或govCost子模块计算。
- **WETH-funded**：msg.value为零时，L314–324先withdraw WETH支付bid给coinbase，然后才可扫款；这项builder付款已经减少合约余款，不能再从sink观察额重复扣。
- **wallet-funded**：msg.value非零时，用外部随交易带入的ETH支付bid并退未花部分；相应竞价支出不会同额减少WETH扫款。不能沿用上一分支的扣费解释。
- L338–357的F_SWEEP调用把**当时整个WETH余额**转sink，不只转本笔keep；可能包括站存余额。F_SWEEP未开时可留在合约，后续permissionless sweep再付固定sink。因此缺少本笔转sink不证明没有收益，某次转入较大也不证明全是该笔新增收益。实际偿债、兑换和竞价可以已在合约内部影响余款；不把这些成本机械地再次从sink入账扣除。

## 3. 直接账簿没有自动补成全费净账

`crates/liq-risk/src/ledger.rs`（本地 `02-pnl-ledger.source.rs`）L31–47明确把 `liquidation_outcomes` 与另一个细分费用的 `liquidations` 表分开，注释称后者是另一个尚未接入的pass。L261–282只是插入producer给的net_wei/gas_used，没有后扣费用。L285–304的sum_net/按日reconcile读取的是另一个liquidations表，不是本轮producer写的outcomes；不能把存在reconcile函数当成这条收款接口已经自动核对全费。

schema L39–47只有自增id、trace_id等，没有tx_hash或trace唯一约束；L261–263明说insert_outcome不去重、幂等由调用方负责。旧已验inclusion watcher按trace管理并移除终态，可以限制同进程同trace重复，但不证明同tx不同trace、重启重放、数据库重入均已去重。本轮没有发现真实重复账。producer遍历日志也没有自行核logIndex唯一性，不能将未做验证写成已经存在重复。

缺失处理有实质设计：读取失败不返回观察；无sink/无有效转入为incomplete，旧watcher不据此判Dropped。L45–47、78首启动从当时head起，不回填历史；L325–355账簿ts_unix用处理时系统钟，而非receipt区块时间。ledger路径缺失或打开失败可继续跟踪但不落账（L230–234、294–299）。因此这三份源码本身不证明历史全量、期间归属或持久化完整性。

## 4. 新文件级许可边界与结论

Executor.sol L1实际为 `SPDX-License-Identifier: UNLICENSED`。这与旧已核根Rust workspace的 `MIT OR Apache-2.0` 声明必须分列；**本轮未取得这个Solidity文件的复用许可，不能用workspace声明批准其复用**。这不是违法判断，也不妨碍本轮已授权静态阅读。

可保留的学习价值是：把实际receipt转入、合约预算/竞价及账簿状态分层，并对缺失留空。新增决定性限制是：`net_wei`不自动等于逐笔/期间全费净利，失败费用没有从该接口形成金额记录，扫款存在整余额与付款分支差异。这不是“整个项目漏扣所有费用”或“代码没有完整账工具”的结论；未读books/其它调用方，未核真实部署和实绩。与六月旧V2正账没有新增绑定，也没有新增盈利或容量证据。

精确原URL/UTC/HTTP、原REST、完整解码字节、SHA256/Git blob及实际读取覆盖见identity、coverage、manifest、receipt。无新行情/账户读取、网络费重算、金额汇总、模型/回测、EVM/RPC执行、源码运行、安装、注册、付款、凭证或外发。actual model/effort与实际CPU/RSS峰值均UNKNOWN，未冒资源测量验收。
