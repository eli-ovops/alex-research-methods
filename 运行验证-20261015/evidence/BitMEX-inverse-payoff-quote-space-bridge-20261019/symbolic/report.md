# 逆向合约与报价空间：条件符号桥梁

结论：在正价格、正USD面额、相同entry/exit费率且费用按各自成交币值收取的假设下，单笔逆向long净盈亏与quote-C严格同号。这个结论不自动传递到多笔未匹配权重的合计，也不认证实际2024产品条款、成交、资金费或账户财富。这里只作纸面教学推导，未执行金融代码或使用任何行情数值；封存提案不修改，新增实验仍未批准。

## 一、假设与单笔恒等式

设Pe>0为入场价，Px>0为出场价，价格均以USD/币表示；Q>0为固定USD合约面额。假设逆向long毛盈亏（币单位）为

\[
G=Q(1/P_e-1/P_x).
\]

同一无量纲费率f作用于两个方向，各自费用为Qf/Pe和Qf/Px；没有额外资金费、费用舍入或其他现金流。则

\[
N=G-Qf/P_e-Qf/P_x
=Q[(1-f)/P_e-(1+f)/P_x]
=\frac{Q}{P_eP_x}\,[P_x(1-f)-P_e(1+f)].
\]

令C=Px(1−f)−Pe(1+f)。因Q/(PePx)>0，sign(N)=sign(C)，包括等于零。若另用正mid作bps归一化S=10000C/mid，单笔sign(S)亦相同。f在公式中为小数费率，不能直接把bps数值填入。这是相同费用收取假设下的代数身份，不是把现货库存现金模型认作逆向合约。

## 二、不同费率的交叉位置

设entry费率a、exit费率b。假设原生币费用分别Qa/Pe、Qb/Px，则

\[
N_{a,b}=\frac{Q}{P_eP_x}\,[P_x(1-a)-P_e(1+b)].
\]

常规线性报价现金差使用的是Cquote=Px(1−b)−Pe(1+a)。费率在乘上另一端价格后出现交叉：逆向分子用entry费率乘Px、exit费率乘Pe，不能在a≠b时照搬Cquote。二者之差为

\[
\{P_x(1-a)-P_e(1+b)\}-C_{quote}=(b-a)(P_x-P_e).
\]

a=b时回到同号结论；a≠b时不能无条件保证同号。若实际费用存在maker rebate、不同收费币种、最低费用或舍入，还需明确各自现金流，不能仅靠makerFee/takerFee字段名称完成桥接。

## 三、聚合与风险暴露

对多笔交易，Ntotal=Σ[Qi/(PeiPxi)]Ci。每个权重为正，只能保证每笔符号及正/负/零计数对应；ΣCi>0、报价bps均值>0或按窗口均值>0，不自动保证Ntotal>0。各笔都非负且至少一笔严格正、或者按完全对应正权重聚合，是不同的附加条件。固定每笔Q也不使价格分母恒定；本报告不据此重新核算旧结果。

若初始抵押品为M币、忽略其他流动，交易后币权益为M+N。另设Se、Sx为入/出场时抵押币的独立USD估值价，则总美元财富变化一般为Sx(M+N)−SeM=M(Sx−Se)+SxN。永续合约成交价Pe/Px与抵押币spot/index估值Se/Sx可能存在basis，不能默认相等。旧式M(Px−Pe)+PxN仅在另加Se=Pe、Sx=Px的特殊估值假设下成立，不是实际换汇价或财富证明。抵押品本身的美元方向暴露，与衍生品交易的N不同。A/B交易次数、持仓时段和抵押品配置不同，也可能产生不同暴露；报价空间差不能单独归因于新增预测信息。

资金费若记为支付的币流F，完整交易净值还要扣F（收款可按负F表示）。资金费时点与费率、费用币种与精度需原证；不因为持有60秒就自动假定零资金费。杠杆/保证金约束、mark、强平/减仓、路径中的保证金不足、实际入出场fill与容量，都可能使端点假想交易无法完成。quote所见ask/bid不是已成交凭证；没有把报价空间改名为已实现PnL、ROI或容量。

## 四、已存官方schema能证明什么

复用已成功取得的官方 [BitMEX/api-connectors swagger.json](https://github.com/BitMEX/api-connectors/blob/master/swagger.json)，原本实际GET时间2026-10-18 15:49:34.238208–15:49:34.918362 UTC；271584B/SHA256 `fed3c4d181f96aa58d67a00fb156a02274c06bcf4866a8b2de867e174dd18525`。master当前快照、无固定历史commit，APIinfo1.2.0不是2024绑定。

- Instrument从L6930起；L6965–7035包括positionCurrency/quoteCurrency/settlCurrency字符串、multiplier等int64转换字段、isInverse/isQuanto布尔；L7062–7094为makerFee/takerFee/fundingTimestamp/fundingRate等类型。
- Position从L7628起；L7639–7647为currency/quoteCurrency，L7832–7840 realisedPnl/unrealisedPnl为int64，L7872起liquidationPrice为double。

这些仅证明API schema存在分币种、逆向标志、乘数、费用、资金费及原生PnL/清算字段。所读属性没有实例值或足够收费基准描述；不能从int64认定某历史币单位，也不能从isInverse布尔类型认定2024XBTUSD的实际取值。类型不是账本、官方产品公式或2024费率证据。局部惰性摘录及hash见schema-excerpts.json；没有调用API、SDK、账户或源码。

## 五、证据与停止边界

本轮0新网络、0行情读取/数值收益计算、0来源执行/模型/交易/安装/付款，仅静态JSON文本读取、文件指纹与人工代数。actual assistant model/route UNKNOWN。最小剩余证据是适用历史合约的实际面额/结算币、原生毛盈亏及两端收费基准与附加现金流；由source Owner另核，不能用本推导替代。研究用途权利仍沿既有partial边界，旧FAILED与待批提案均不改。
