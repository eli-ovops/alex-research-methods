# Q3固定范围与单位独立审阅

限定PASS：固定六地址、2026-07-01至2026-10-01 UTC半开区间及继承的Liquidation topic可以用于下一步原始事件计数。scope SHA为`0fddd67bf68d087eabba2a6baee35bc154acce5aa502189e1d22c4e53909dd78`。本审阅0网络，不预读季度结果。

旧三地址与已保存官方部署清单相符；实际保存ABI均为非anonymous、十个非indexed uint256。新WETH已核部署源码及同一接口也是这一形态。因此预期仅topic0，data为320字节（含0x的十六进制字符串长度642）。同名字段并不自动证明币种或完整版本身份。

从0计第2字段的遗留名为`_boldGasCompensation`。已核新WETH部署源码实际emit的是`totals.ETHGasCompensation`，付款走`WETH.transferFrom`；第3字段才为`collGasCompensation`，走ActivePool抵押币付款。不能据遗留字段名记作BOLD。新wstETH/rETH六月实际付款已逐笔与事件对应，但不替代未知的完整部署源码身份或Q3每条事件的到账证据。旧三部署目前只有官方地址、ABI及历史阳性控制，旧事件字段的实际付款币种不因新部署机制相似而自动通过。

先按事件原量保留固定WETH和各抵押币的向量；尚无付款证据的行只能称“事件报告毛补偿”。若季度非空，需要具体指出哪些同tx付款日志、接收者、原量与顺序已有或缺失，再决定下一项有限核验；不自动读取所有钱包或收据。事件本身没有接收者、调用者、仓位ID和实际gas。多仓位批处理可以只emit一次，不能将事件数当仓位数、参与者数或所有尝试数。

后续检查应分别报告事件数、unique tx，按blockHash/txHash/logIndex去重，验证地址/topic/十字段与UTC过滤，并区别成功空数组、错误/null和坏字段。失败尝试不在成功事件集合内。六地址不是全协议迁移完整性证明；任何零结果只限固定地址、签名、提供商与期间。

没有新增私人bot、现实主体或未来OOS门槛；不作定价、净利润、个人捕获率或容量结论。实际model/effort为UNKNOWN。读取UTC、全部输入SHA、六地址逐项证据及接口原句见同名JSON。
