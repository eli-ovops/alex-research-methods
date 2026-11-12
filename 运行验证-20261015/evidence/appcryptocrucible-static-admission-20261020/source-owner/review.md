# appCryptoCrucible/liquidation 静态准入

**可以保留为有实质实现的学习样本；本轮没有把它验成可直接运营、低成本或已可复制净盈利的程序。** 与旧README线索相比，新证据是固定源码、workspace许可声明和可定位的资格/奖励/发送/结果状态逻辑。没有新盈利原账，也没有绑定六月旧Liquity V2正例。

## 固定身份与许可

读取2026-10-19 19:10:57–19:12:18 UTC，10次匿名GitHub REST GET均HTTP200，随后停止全部网络。默认分支 `main` 解析至 commit `364059aba56e773da01f6507224cf530bbbb1b09`，tree `0958f715725a563f8ebcbf44c81cc133a2e59f22`，author/committer日期均2026-10-10T10:16:37Z。这是当前ref指向及提交元数据，不是首次公开时间或历史运行证明。

recursive tree共947项、`truncated=false`。API `license=null`，tree未见常见LICENSE/COPYING/NOTICE文件名；**但实际根 Cargo.toml L36–39 明确声明 `MIT OR Apache-2.0`**，不能再把API null解释为没有许可。它是workspace许可声明；各子crate是否继承、源码例外、依赖和完整通知条件本轮未逐项核，不一概宣称所有文件与运行栈已完成许可审计。全部七个取得blob均核本地 `SHA1("blob <len>\0"+bytes)` 等于REST与固定tree的blob SHA，且大小一致；见 `fixed-identity-and-blob-bindings.json`。

## 会改变复用判断的五项事实

1. **资格并非只有宣传文字。** `liquity-v2/src/health.rs` L127–165检查unpriced/unmapped资产并计入再分配、利息/批次费用；L179–220按分支MCR算ICR，要求开放且债务非零，PAUSED阻断，严格ICR<MCR才Liquidatable；L239–240以active/zombie作为开放状态。L197把BOLD的协议ICR计价基准固定为1，并非BOLD市场价格预测。代码读取PriceVector；本轮未核oracle订阅/更新、状态镜像、`is_active_or_zombie`底层定义及生产参数，所以未认证对当前链状态一定判断正确。
2. **Liquity收入模型是奖励，不是清算者借BOLD偿债后取全部抵押品。** `quote.rs` L20–40在健康检查后，把固定WETH gas补偿和按SP offset推得的抵押物补偿一起计预算；L50–87保留两类资产/合并同币，L91–99的最大偿还额为零。不同于先前cranker只预算固定项，本项目使用可变补偿及资产价值比较。固定补偿常量、`coll_gas_from_offset`数学实现及退出兑换路径未取得，不能据这些函数名认证常量/舍入/兑现价格正确，更不能将notional当实际净收入。
3. **资源和运维需求有明确自述。** README L3、7–10、35、89描述生产路径为Linux Reth ExEx、共置Lighthouse及已同步节点，首启重放保留日志；另有standalone路径。L360–410描述registry维护、receipt filter、watcher和books配套。它不是据此就不可供个人研究，但不能称为普通电脑、免费公共RPC即可零成本运行的轻脚本。本轮未测硬件、同步、运行维护、延迟或竞争份额。
4. **发送/模拟/成本仍是候选与估计层。** `exec_worker.rs` L128–142调用sign_and_gate，再异步send；L154–193的RPC复核由chain client及rpc_verify控制，不是所有路径必然执行同一复核。L199–229模拟失败/回退不发，并将模拟gas加五分之一作gas limit；这不是已支付费用、全成本或必成交保证。`submit.rs` L44–72的live开关/租约位默认关闭；L173–208向curated builders并发发送、首个接收即返回。L116–123、254–262的trait回执只是Recorded。未读完整ExecPath/risk/profit或链上Executor，故未认证实际成本门槛和支付/归集代码完整。commit响应自带path.rs仅diff片段，可辅助定位，不当完整文件身份验收。
5. **结果状态设计不能替代真实账。** `inclusion.rs` L16–17明确live competitor resolution比例未测；L40–62的profit由上游InclusionObs必填提供，缺失不补零，incomplete不能当Dropped（L117–118）；L129–184按交易/仓位匹配Included、Reverted、竞争结果。L224–225还警告未接来源时计数不是胜率。本轮未读inclusion_feed的实际收据金额/费用计算，也未取得生产日志或完整books；代码中的测试、模拟、Recorded和builder ack均不证明历史净赚。README实际链接仅设计指南/覆盖/说明入口，未出现可独立验其V2全费净利的交易账链接；这只限定本次读取范围，不宣称整个仓库或外界永远不存在记录。

## 实际覆盖与剩余边界

完整字节取得：README、根Cargo、health.rs、quote.rs、exec_worker.rs、submit.rs、inclusion.rs。实质阅读：Cargo全文；health/quote全文；worker L1–260；submit L1–285；inclusion L1–269；README L1–14、35、89、268–354、358–412、482–491及标题/目标词定位。其余测试段仅少量关键词定位，没有运行测试；README其余段、子crate manifests、math/config/apply/oracle/route/risk/Executor/实时feed与books未审。947项tree是目录身份覆盖，绝非947文件内容审计；大receipt-filter TOML没有下载或当成经营账。

有意义的可学习结构已明确：协议资格与奖励报价分离、零偿还奖励型清算、模拟失败不发、live发送门控、把builder接收与链上结果分开、未知profit不填零。当前缺口是本轮尚未审到的实现闭环、实际运行及全费原账，不表示仓库缺少相应实现，也不是已经证明这一程序无价值。没有因这些缺口自动启动安装、模拟、回测、部署或交易。

唯一可定位的后续静态问题是“真实profit输入怎样生成、扣除哪些费用”：固定tree已列 `crates/liq-bot/src/inclusion_feed.rs`，blob `b8de0e614ba72fa8efdb5c3ce65efa281d92d2c2`、12749B。它是可供以后限定读取的真实入口，本轮未取得/未读该blob，未认证其扣费口径；不据此扩大到全947项或启动运行。

原始REST、URL/UTC/HTTP/哈希、安全响应头、解码源码和blob映射均在本目录。无本地配置/凭证或排除私人目录访问；来源说明和源码命令均未执行，未安装/clone、调用EVM、模型/回测、金融算术、账户、注册、付款或对外发送。actual model/effort为UNKNOWN。
