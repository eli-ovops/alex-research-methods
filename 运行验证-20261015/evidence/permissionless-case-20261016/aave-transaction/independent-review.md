# Aave清算交易：独立静态正增量核验

审阅UTC：2026-10-16T02:28:52.392820+00:00。只读完整保存的Etherscan交易/状态HTML及derived文件，并从HTML独立解析事件/调用与执行整数、Decimal算术；未联网，未执行仓库、模型、回测或交易。“独立”指不同审阅者对保存原件核算，不冒充独立归档节点复核。

## 可确认的正结论

对象：[0x41eddc70253a40cea41587aab1c46c057a1c7247b9aefd1e79917dd00c6b4715](https://etherscan.io/tx/0x41eddc70253a40cea41587aab1c46c057a1c7247b9aefd1e79917dd00c6b4715)，浏览器记为Success，block14759771，2022-05-12 07:19:37 UTC。

在本交易地址集合范围内，**bot净增1.298550505781938468 WETH，USDT净变化0；sender支付0.846085432925289514 ETH交易gas。按WETH可1:1赎回ETH的协议数量单位合并，扣除该笔gas后净增0.452465072856648954 ETH-equivalent，严格为正。** 这是真实已发生交易原件所支持的单笔余额增量，不是策略模拟。缺少长期/完整bot源码，不应否认这一已核正数；同样不应把它扩为长期或全成本结果。

### 双路径核对

|项目|原件金额|核对|
|---|---|---|
|Sushi池→bot USDT，log157|39,330.045609|来源流入|
|bot→Aave aUSDT，log182|39,330.045609|与流入相等，bot USDT净0|
|Aave aWETH→bot WETH，log179|22.807119537915495237|清算获得的WETH|
|bot→Sushi池 WETH，log184|21.508569032133556769|用于flash-swap的兑换/偿付|
|bot WETH流量净额|1.298550505781938468|与状态差完全一致|
|bot WETH state|110.535859782729284022→111.834410288511222490|状态HTML的storage mapping input明确为bot `0xabcf5d4be599f1c7f71fcbcae4643a2aa849f4c8`|
|sender ETH state|1.974119040991498119→1.128033608066208605|下降0.846085432925289514|
|实际gas数量×有效gas价|698,639×1,211.048099126 Gwei|0.846085432925289514 ETH，精确等于sender下降|

上述22.807119537915495237−21.508569032133556769−0.846085432925289514 = **0.452465072856648954**，无四舍五入误差。不是将网页即时美元估值拼到历史gas；本次未使用美元换算。

## 全事件、调用与资金来源核验

从完整HTML独立数得30个log（157—186），与derived一致。全部8条ERC20 Transfer均已审：四条为上述bot的USDT/WETH实物流转，另四条属于aUSDT/aWETH给Treasury的铸记、被清算人的variable-debt/aWETH烧记。没有把Approval、RewardsAccrued、Mint/Burn重复当作现金转移或bot奖励收入。没有发现额外bot代币转出使上述净额漏减。

从HTML按精确ID `tb_internaltx_[数字]`定位并读取父tr，得到131条实际internal trace，全部value=0 ETH；页面另含detail/loading节点，不能把它们重复计作trace。top-level交易value也是0 ETH，故没有额外普通ETH value转移；sender ETH状态下降又与全部gas精确闭合。HTML未显示该交易中的额外ETH小费/贿赂转账。此结论限于已保存explorer数据，不扩为所有历史交易/链下款项均无成本。

资金顺序支持**SushiSwap/Uniswap V2式flash-swap**：trace32 bot调用池Swap，trace33池USDT Transfer，trace34池回调bot Uniswap V2Call，之后trace41进入Aave Liquidation Call，trace125/126发生WETH抵押品交付和USDT偿债，trace129 bot向池转WETH，最后Swap log186记录amount0In=21.508569032133556769 WETH、amount1Out=39,330.045609 USDT。即先收USDT、回调中清算、后补WETH以满足该次swap。不能把该USDT来源写成“Aave flashLoan”；Aave在此是清算场所。

函数标签为Etherscan解码结果，尚非本地复核所有call calldata/bytecode；但相互独立的Transfer顺序、Swap事件金额及余额变化均与flash-swap解释相容。没有为了补本金而虚构bot先投入39,330USDT。

## 费用不重复扣，正数的归属不外推

- 21.508569032133556769 WETH是本次真实池回款，包含该swap实际价格与执行规则的影响；不能在净WETH差额之后再机械扣相同交易价差或估计flash-swap费用。
- 使用实际gasUsed×effective gasPrice，已含该笔基础费与优先费，不再把burnt fee/矿工收入另扣一次。不能用gasLimit或maxFee替代实付gas，也不能把网页“节省gas”当收入。
- WETH余额在bot合约，ETH费用在sender；本次核的是操作相关地址集合按1:1单位的合计变化，**不是单钱包已收到0.452465... ETH现金**。sender对bot利润的最终受益/提取权、之后是否提现及提现成本未据此证明。
- 未含后续unwrap、withdraw/转账gas、部署费、基础设施/链下维护、其他成功及失败交易、历史损失、税费或其他未公开费用。因此可以说“扣本笔可见链上gas后为正”，不能说“全成本运营净利润”或“普通人长期稳定盈利”。
- 借到的USDT、bot交易前110.535859... WETH余额、或gas支出，均不能在没有明确资本占用/归属/时间/风险定义时擅自用作ROI分母；不计算美元ROI、年化或容量。

## 准入缺口与证据等级

已经取得完整原始explorer HTML，比仅截图/摘要/选定DOM行更强，但Ethereum JSON-RPC receipt/trace原字节及独立归档节点证明尚未取得；应明确为explorer层账目核验。状态差为同一explorer提供的补充证明，不能当两个独立服务的交叉认证。

bot合约源码未验证；事前Aave V2协议代码仅说明开放清算规则，不能替代此bot完整实现、事前固定参数、寻单逻辑、部署版本及个人复用许可。选择单笔成功交易也不是全样本前向账户表现。普通账户可调用协议、能阅读开源协议，不等于已证明拥有bot的相同实现和机会；本轮不作个人执行或资金建议。

建议收录标签：**“已发生、完整explorer事件及余额差可复核的单笔清算/flash-swap正增量；扣本笔gas后为正，非全策略、全成本、单钱包提现或可直接复用源码案例。”**

## 本次所读原件hash

- etherscan-transaction-advanced-original.html SHA256：30a90e283da4746d6fb8c1b423474bfcef034bd9332b0499db038dcb593c9bd5
- etherscan-state-original.html SHA256：6beb9e73dae515a920f2429802bed89e096c559c31cc0316f887ee130e1e677b

未修改上述原HTML、derived JSON或其他人文件，只写本独立审阅。
