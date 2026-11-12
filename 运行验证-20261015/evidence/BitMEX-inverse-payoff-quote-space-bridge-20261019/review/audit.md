# Inverse payoff与quote空间：独立限定验收

**PASS：条件符号桥梁正确；费用与历史产品认证仍PARTIAL，无必须修正项。**全部引用hash一致，真实native2017官方文章L45–48支持固定USD面额及XBT毛损益，L62–64区分抵押品美元敞口；非2024规格。费用页实际404停，首次search仅选定身份转录不冒raw全文。保存schema的摘录与原JSON类型一致，不是实际历史值。

Q>0、Pe/Px>0且每边同率f按各笔Q/P以币收取、无其它流且端点假定成交时：

`N=Q[(1−f)/Pe−(1+f)/Px]=Q*C/(Pe*Px)`，`C=Px(1−f)−Pe(1+f)`。

因此**单笔**native净交易PnL与C严格同号（含零）；正分母bps归一也只传递单笔sign。这不是spot账户公式、ROI或盈利证据。

entry=a/exit=b时，inverse分子为`Px(1−a)−Pe(1+b)`，旧线性quote差为`Px(1−b)−Pe(1+a)`，二者差`(b−a)(Px−Pe)`；异率不能无条件沿用同号。真实手续费币种和Q/P收费基数本轮未从可读正文核实，不能把条件写成历史事实。

**多笔不自动保号：**`ΣNi=Σ[Qi/(Pei*Pxi)]Ci`，权重通常不同；未匹配权重的正ΣC或正平均quote-bps不推出正native总PnL。固定Q也不固定分母。故待批五日报价提案不能由此改名成合约盈利检验。

若抵押品M币、忽略其他流，以独立美元估值Se/Sx计，美元总财富变化`M(Sx−Se)+Sx*N`还含抵押品自身暴露。perp成交价Pe/Px与抵押币spot/index估值可能有basis；旧式`M(Px−Pe)+Px*N`仅在Se=Pe且Sx=Px的显式特殊假设成立。资金费、费用币种/舍入、mark/强平/保证金路径、实际成交/延迟/深度/容量均另有边界；60s不自动免资金费。2017正文与当前schema不能认证2024费率/产品实值。

本轮只纸面符号及本地sourcehash/schema核验，无市场数值/金融代码/模型/回测/交易，Reviewer新增网络0，总官方3读未追加。待批五日协议/许可、旧FAILED均未改，不能凭研究条款或数学身份记净利/财富目标完成。actual route UNKNOWN，无自己后台进程。输入指纹见audit.json。

局部修订R1已核：Owner澄清抵押币独立USD估值价，最新symbolic MD/JSON指纹已绑定，无其余必须修改项。未新增源或市场计算。
