# CoW baseline公开规则与盈利案例准入

结论：已取得官方固定源码及竞赛记录schema，**未取得可准入的扣费盈利案例**。实际model/effort UNKNOWN，沿用PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4，未覆盖设置。

官方仓库 `cowprotocol/services` 固定commit `82746c5ad016a5f3cfc4b33cc919f4e522f0a929`。8次公开GET均200：一次代码搜索、一次非截断tree、6份固定源码。搜索只返回前20/73项，不是穷尽。既有gh认证只静默核状态，未读凭证/改认证。原URL/UTC/响应指纹、Git blob SHA及html/download/git URL在read-receipts.json；6份解码源码Git blob SHA1均核对。首次公开时间和commit日期本轮未取得，不从今天可读回填历史。

| 项目 | 已核事实和边界 |
|---|---|
| 公开算法 | baseline-domain.rs L1–6、136–269：逐订单在给定链上流动性中找不超过max_hops的候选路径，不跨多路径拆分；boundary L46–114中BUY最小卖出、SELL最大买入。domain L273–304对部分订单逐次减半，solve受auction deadline限制。核心机械规则公开，非预测alpha；routing/solution/liquidity等依赖本轮未全部展开，不称完整实现审计。 |
| 外部依赖与配置 | domain L29–70、142–184、247–257：auction订单/流动性/参考价格/gas price，base_tokens/max_hops/max_partial_attempts/gas offset等是输入。可选V3节点/公开Quoter见boundary L232–254。已读核心没有必须委托私人外部solver的证据；实际配置未知不等于私有政策或个人不能复制。 |
| 费用意义 | domain L224–257用route gas加offset乘auction gas price，再按参考价转换fee；L149–184含缺价估计与fallback。是估费/构造解，不是实际receipt或净收入。competition-model L53–67将sell_amount定义为用户含费流出、buy_amount为用户费后所得；不可再从净额重复减费，用户费不等solver收入。 |
| 实际档案能力 | competition-model L13–50有auctionId、起止块、transactionHashes、solverAddress、score、ranking、clearingPrices、isWinner、filteredOut、txHash等。competition-api L12–50有按id/hash/latest加载handler并用hide_competition_before_block；L54–68说明unfiltered接口受基础设施访问限制。没有读取路由注册、官方host或实际返回，不能称当前匿名档案已实取。 |
| 版本/原账/盈利 | 未有baseline实际build/config与运营地址、auction/settlement绑定。已读response没有receipt实际gas/status、奖励/罚款/报销支付、失败费用、solver限定期初期末资产负债。score或isWinner不能代替利润，未取任何历史盈利账；未查不等不存在其他公开档案。不要求私人bot或全实体多年账来认可另有闭合历史现金。 |
| 许可 | tree有GPL/Apache/MIT文本，已读LICENSE-GPL为GPLv3。该许可有运行/复制等条款，但本轮solvers/Cargo.toml无license字段、两份核心无SPDX，具体组件许可适用说明未取得。因此不能只因根文件存在就把整套或依赖一概称MIT/GPL或已核完整生产授权，也不能断言禁止个人使用。 |

可研究复用的环节是限定路径搜索、部分填单和gas估价；本轮未运行。生产接入/竞赛准入、实际收入规则及净费盈利仍UNKNOWN。源码公开和竞争schema存在都不满足用户完整成功案例要求。

若后续只选一个能改变判断的原件，应是具体baseline运营方公开build/config与真实auction/settlement/reward及限定成本账的绑定记录；本轮不取数据、不扩其他solver。原始来源和实际输入绝对路径/SHA/bytes见同名JSON。

0模型/回测/来源代码/SQL/SDK/EVM/策略执行、0链上/实际auction数据查询、0账户/安装/付款/交易/外发。两次本地写入准备错误发生在产物保存前（编码解析、Path索引拼写），已定点修正，无新网络或环境修改。研究准入完成不等于盈利或财富目标完成。
