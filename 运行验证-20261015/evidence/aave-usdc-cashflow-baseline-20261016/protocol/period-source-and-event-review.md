# 提款周源码、事件与升级绑定独立审阅

**限定PASS。** 仅同提供商历史升级返回、声明源码、ABI与记账语义层通过，不是独立编译/链状态/实际收益验收。0联网、未读候选金额或盈利，无模型/回测/源码执行/EVM/交易。实际model/effort UNKNOWN。实际UTC、全部输入hash与内嵌源码模块hash见同名JSON；未修改root或旧证据。

## 事件与实际资金

Pool声明ABI的Supply(address,address,address,uint256,uint16)：reserve/onBehalfOf/referralCode为indexed；user、amount在data，依此顺序。Withdraw(address,address,address,uint256)：reserve/user/to均indexed，amount是唯一data字段。均非anonymous。辅助签名库不是第一权威，本轮按真实ABI核字段，未安装或以SHA3冒充Keccak。

Pool.sol把调用人经参数传到SupplyLogic。executeSupply L40–92先更新reserve状态，再算scaled amount、校验、更新rate/virtual balance，把实际底层币从user转至aToken，给onBehalfOf铸份额，Supply记录实际请求底层量。

executeWithdraw L106–175先更新状态，读取scaledBalanceOf(user)。MaxUint分支直接选**全部scaled余额**，底层实际量=该余额按nextLiquidityIndex的getATokenBalance计算；TokenMath L66–70使用rayMulFloor。非MaxUint路径按请求底层量换算向上取整的burn份额。AToken.burn L81–99销scaled余额，再safeTransfer实际底层币；Withdraw事件及返回值是actual amountToWithdraw。MaxUint输入不是实际提款金额，更不是利息金额。

AToken.balanceOf L134–138按normalized income指数换算；转账经scaled换算及Pool.finalizeTransfer，不能当无抵押约束的自由移走。ScaledBalanceTokenBase L69–133区分先前指数、当前指数、balanceIncrease和新的余额；Mint/Burn事件可能包含已累计利息，部分burn甚至发Mint。**真正底层Transfer与Withdraw、用户原始Supply及外来aToken要另行对账**；不能用aToken Burn的Transfer数值替代现金流。

## 利率与协议份额

ReserveLogic L85–100先更新indexes与Treasury累计；L211–242用当前liquidity rate的线性利息更新供给指数，用变量借款利率的复利计算更新借款指数。L130–175把reserveFactor、变量债务、virtual balance等传入外部利率策略并保存返回利率。完整利率模型实现尚未核，不据此自行补一个完整供给率公式或数字。

L183–203以scaled变量债务乘借款指数增量得到新增债息，再percentMul(reserveFactor)，换成供给scaled量记入accruedToTreasury。内嵌PercentageMath分母1e4是编码精度，**不是已取到的RF具体值**。这是Treasury累计权利的记账，不是已观察实际提款或个人利润；不能把借款全部利息归供给人，也不能无依据在最终实际到账后再重复扣同一协议份额。

## 升级与许可边界

两个proxy ABI的Upgraded(address)均一个indexed implementation，data应为空。独立核10+3条原件地址/topic、indexed地址、高位、去重/排序，以及各terminal page2成功空：

| Proxy | 最后返回升级UTC/高度 | Implementation | 选定周返回升级 |
|---|---|---|---|
| Pool87870… | 2026-05-29 08:50:47 / 25199939 | 0x728a138a4823392c2efa55e028d434f526fe03cf | 0 |
| aEthUSDC98c23… | 2026-01-16 14:36:11 / 24247927 | 0xadc45df3cf1584624c97338bef33363bf5b97ada | 0 |

日志query从0到25928920。两实现provider分别声明PoolInstance/ATokenInstance、Proxy0，原件/回执hash吻合；这缩小该提款周版本缺口，仍是同提供商返回与源码验证声明，无独立编译或状态根证明。持有期最长180天，**若实际Supply早于5月29日，不能把提款周Pool实现回填其存款时点**；按真实时点界定源语义，不因此按盈亏改筛选。

主要Pool、SupplyLogic、ReserveLogic及AToken源头SPDX为BUSL-1.1；ScaledBalanceTokenBase等辅助文件可为MIT，不是整套MIT。具体BUSL文本、ChangeDate/AdditionalUseGrant、所有依赖及商业fork权利尚未完整核，不能把仅公开可读误写成已获完整商业复制许可。文件路径含private是provider包内路径标签，不证明这份今天已返回的源码仍秘密，也不能证明其首次公开时间。

本审阅未独核5166条Withdraw群组及29个transactionIndex='0x'的全量数；这些是root后续原始数据层范围。不得修补其字段，候选排序应继续使用block/globalLogIndex。RF实际值、当时费率模型、完整许可及精确首次公开仍UNKNOWN，无收益或安全结论。
