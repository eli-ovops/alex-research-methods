# 固定源码的版本与经营口径审阅

**受限通过静态学习样本准入；must_fix=[]。尚未验成可运行、全费净盈利或能复现六月旧 V2 正例的程序。** 本审阅只覆盖下列五个取得源码的生产路径；没有网络、来源代码执行或金融算术。

1. **V2 资格与收入模型确有实现。** `06-health.source.rs` L112–176 计入再分配、利息和批次债务；L179–240 使用分支 MCR、开放状态和严格 ICR<MCR 资格，BOLD 的协议计价基准不等于市场 peg 预测。`07-quote.source.rs` L20–40 对固定 WETH gas 补偿及 SP offset 对应的抵押补偿估值，L91–99 最大偿 BOLD 为零；不能将借 BOLD/闪贷或取得整个 trove 抵押物当这一路清算的通用条件。数学、状态 decoder、active/zombie 底层定义及线上配置未审，故不是实时资格或精确补偿常量认证。
2. **毛报价、模拟、发送与实收分层明确。** `07-quote.source.rs` L32–40 的 notional 是补偿候选估值；`08-worker.source.rs` L146–229 的复核受 chain client/rpc_verify 控制，模拟成功与 gas 安全余量不是实际费用或净收入；`09-submit.source.rs` L113–124、251–263 的 Recorded 以及 L173–239 的 builder 首次 ack 都不等于上链。L309–427 中 modest 的 priority_wei 与其他 auction_bps 是不同单位，不能把 intended_bid 统一当已付金额。完整 ExecPath、Executor 和费用账未取得，本轮不判定它们缺少实现；失败/竞争分类与可回退 bundle 也不能代替失败手续费、builder 结算及持续运维成本的真实账。
3. **Included.profit 仍须上游原件定义。** `10-inclusion.source.rs` L40–62 要求上游 profit，不补缺失值；L129–145 只是复制到结果。注释的 attested 是类型/输入约定，本轮未验独立证明。L16–17、224–225 明示竞争结果率未实测；L117–118、197–243 对 incomplete/None 不伪造 Dropped，是可学的未知保护，但不能认证胜率、历史收益或完整会计。测试样例没有当生产记录。

固定身份据已读 Source 回执：commit `364059aba56e773da01f6507224cf530bbbb1b09`、tree `0958f715725a563f8ebcbf44c81cc133a2e59f22`。本人将五个源码的 SHA256 与本地 Git blob SHA1 逐一同固定 bindings 核对，均一致；没有独立重验全部 947 项 tree/41 件 manifest。Cargo 的 `MIT OR Apache-2.0` workspace 声明由 Root/Source 实读确认，本人未重读 Cargo/README，不将 metadata=null 视为无许可，也不作依赖与通知条件的全面审计。生产配置和 Standalone 的区别由 Root 负责，不据 Reth 名称推定个人不可用。

本人的实质范围：health 全文 L1–246；quote 全文 L1–107；worker L1–270（生产实现至 L261）；submit L1–455；inclusion L1–269。另读 Source 的 review、receipt 和 fixed-identity-and-blob-bindings。未读测试主体、inclusion_feed、Executor、math/layout/decoder、完整 ExecPath 或真实生产账；没有绑定六月旧 V2 七次盈利原账，也不抹去该原账已有事实。

**唯一已定位的后续静态原件**：`crates/liq-bot/src/inclusion_feed.rs`，固定 tree blob `b8de0e614ba72fa8efdb5c3ce65efa281d92d2c2`，12749B；问题是 profit 如何从真实收据/资产变化产生、包含哪些费用。本轮未取得/未读，不追加第 11 GET、不启动部署或模型。actual model/effort=`UNKNOWN`。
