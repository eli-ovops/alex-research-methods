# profit producer 的独立会计口径审阅

**不准把本支路的 `net_wei` 当作完整净盈利证明；保留源码学习价值，不据此认定项目不赚钱。** 已知 quote 是补偿候选估值、builder ack／Recorded 不是上链结果，上一单元已封存；本轮补到真实 producer 后，问题从“profit 来源未知”收敛为下列具体口径。

1. **来源是收据事件原量，含匹配零值，非经营净额。** `01-inclusion-feed.source.rs` L147–190 读取指定交易 receipt；L200–224 只把 `REGISTRY_WETH` 的 `Transfer.to==profit_sink` 原 uint256 相加，不按 from 筛，不扣转出，也不排除 sink 自转。`any=true` 不要求 value>0，因此 Included 不能称正收入；它不是模型／模拟估计，也不是已证新增财富。溢出／符号位越界、缺 sink 或无匹配事件会 withheld，失败读取不推进，是有价值的未知保护。原量未做精度或价格转换；`REGISTRY_WETH` 的实际常量、与 Executor 部署 WETH 一致性及精度本轮未独立读到，不能仅凭字段名 wei 认证链／币种／18 位或地址所有权。
2. **转入前可以已经承担内部费用，仍须区分门槛与真正净流。** `03-executor.source.sol` L253–307 在各组清算、兑换和还款结算后，以 WETH 余额增量作 gross，再减 plan 的 `gasCostWei` 和模块给出的 `govCost` 作竞价／minProfit 门槛；这是源码计算，不是实际网络收费 receipt 核验。L314–335 的默认 msg.value=0 支路先提 WETH 并向 coinbase 支付 bid；不能再把同一 bid 机械扣第二次。wallet-funded 支路改用 msg.value，并退未用预算，不能一律视为 WETH 转入内已扣。L340–357 的 sweep 转的是**整个余额**，不是 keep，因此可含 standing 余额，且不自动等于已扣真实网络费的单笔净利润；不 sweep 的留存也不能被 feed 当无收入。闪贷本金／premium 等回调结算与兑换成本已可能体现在末端余额，不能再从 sink 收款重复减全套本金和内部支出。这里只读了核心及相应回调，没有审 module、PlanDecoder 或真实部署。
3. **下游没有把这个数自动补成完整账。** feed L333–358 把成功 profit 直写 `OutcomeRow.net_wei`；Reverted 等写 None，成功 gas_used 也只是 gas 数量。失败 receipt 虽读到 gas_used，结果写账支路不保留该 gas，因此不能把 None 当零费。`02-pnl-ledger.source.rs` L31–47 明确 outcomes 与全费用表分离；L261–283 直接 INSERT、不去重，schema 无 tx_hash／trace 唯一键。单次 watcher 内每 trace resolve 一次不等于跨 trace、重启或来源事件的会计幂等证明；本轮没有证实实际发生重复。L285–304 的 sum/reconcile 读另一张 `liquidations` 表，不会为本 producer 自动补扣；未读 books 不等于全项目无实现。feed L45–47／78 初启不回补历史，L230–234 允许无账库继续观察，L325–358 使用写入时本机时间，不能据此认证固定历史期间／成功失败全集／链上交易日期。

**新增文件许可边界：** Executor L1 是 `SPDX-License-Identifier: UNLICENSED`。上轮 Cargo 的 `MIT OR Apache-2.0` 声明仍成立，但不得通盖这个 Solidity 文件；本轮未取得可据以复用此文件的额外授权，不作违法或全仓库无许可结论。

**唯一有信息量的下一原件：** 一份可定位的、固定期间成功与失败全覆盖的实际执行原账，能对应交易 hash、执行／sink 地址、原 receipt、库存／资本与实际费用。其用途是区分“事件收款／预置门槛”与真实历史净表现；没有这样的公开入口，本项目盈利证据就到本轮收口，不再串读源码追正利润、不运行、不要求私人选单规则。六月旧 V2 正净数量事实保留，不强求先归给本仓库才承认旧事实。

实质范围：producer 全文 L1–368；ledger 全文 L1–510（含测试，仅静态读）；Executor L1–360、363–409、478–610、678–715，另全文关键词定位。未完整审其 callback 认证与所有外部依赖；未获得任何实际账库／链上原件，没有金融重算、新网络、源码执行、模型、回测、账户或交易。三个固定字节身份和最终正文绑定留在本目录回执。actual model/effort=`UNKNOWN`。
