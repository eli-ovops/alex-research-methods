# Pendle终稿限定实质审阅

**PASS：限定原账、费用算术与报告语义。整体扣费净收益仍UNKNOWN，不代表盈利案例全部门槛通过。** 无新增实质问题，不增加私人动机/OOS/未来容量为历史原账准入前提。0联网，仅本地被动读取与算术；未执行外来代码/模型/回测/EVM/策略或交易。

四receipt状态成功、hash与normal字段对应，两授权owner/spender/token符合。各gasUsed×effectiveGasPrice相加=0.024929649592073069 ETH；两交易=0.02271832905917778 ETH。本人WETH输入=0.03493856145883593，LOOKS实际输出=392.216257909192283662。PT转换数量差=2.335037994181398255 LOOKS、0.598910097%不是整体ROI。四gas/本金在ETH-WETH一比一假设下=71.352822072%不是亏损率；覆盖这两类支出的门槛=0.000152640819557178997 ETH/LOOKS，非报价/实际兑换/完整成本上界；不计算未知净利。

normal290/0、owner275nonce0..274、历史5失败、nonce262..274无失败均复核；两授权在操作前36/108秒。只把两次相关授权全计入本例，不全扣钱包，不把同索引器分页/nonce连续升级独立全链无漏。LOOKS source继承ERC20decimals18无main覆盖；WETH18沿本项目旧声明，未新增请求。

固定估值100前完整块16940187..16940286，scope早于唯一Sync请求；原件status1/OK/result[]，非报错、非币价0。报告保留空窗口/净利UNKNOWN，未换窗口填有利价格，盈亏平衡门槛也未冒报价。

67源码等旧阶段与本例不混：本例固定源与白皮书内部日期未被升格firstpublic/独立编译；当前fee未回填2023，SY暂停/外部staking依赖、直接机械环节与私人选择边界准确；未把未独证写保密。关键本地链接均存在。报告数字/未知/停下收口无实质夸大。

root inventory41rawGET/2481716bytes逐条hash/bytes核对，13项是只读历史receipt代理请求；child3rawGET/41000bytes，另10queries+5rootnative+1childnative合计60，原生动作计数按执行上下文，抽取bytes不混rawbytes。当前正文未列这组计数，本review只核inventory，不新增正文要求。

报告SHA256：`879a516a07993570821ebaa51943363d1624497183dfac23c3adf62b07950d04`。全部实际输入hash/逐4费/精度及范围见同名JSON。审阅UTC：2026-10-16T10:18:50.579291+00:00；实际model/effort UNKNOWN，未改root或旧证据。

JSON SHA256：`961f1fd307df9bb00fca586c9606b135e0da1330ccab3a54bbf115e30894d702`。
