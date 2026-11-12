# notional、订单流与时点：限定源码结论

**PASS_LIMITED：固定工具的notional确由price×size形成；不等于已证明2021 CSV的单位、时钟或生成版本。** 只补3份固定blob，均HTTP200且Git blob匹配，未运行源码。

`PriceLevel`（101–119）分别增减quantity及price×quantity；静态notional getter舍入至2位小数（65–72）。若实际price是报价币/基础币、size是基础币，乘积才是报价币；当前CSV历史缩放未独证。结合旧Book的float32存放，不能把它直接称原始BTC数量或精确美分。

`limit/market/cancel_notional`另累加price×size（147–178），正输入时各为正累计，不能把撤单字段本身当负数或把limit当静态存量。`clear_trackers`只清流，不清库存；旧Book仅清附近档位，深层不保证同一全局时间箱。Coinbase的`change`会改存量，却未记入limit/cancel；preload也走insert/add_limit。故不能擅用“存量变化=新增−撤单−成交”完整恒等式。

`CoinbaseOrderBook:171–180`按maker侧匹配方向，把bid上的成交price×size加到sell_tracker，ask上的加到buy_tracker；不是成交笔数。最终buys/sells的导出、累计/清零/EMA在未读基类/Tracker中，仍UNKNOWN，不再扩GET。

时钟也不能混：新事件经`db.new_tick(msg)`持久化，`last_tick_time`另读msg.time；preload.time用本地now及配置TIMEZONE。旧Simulator读取tick.system_time，但本3份文件没有定义它的写入来源。它先把旧状态填到跨越的网格，再应用触发的新tick；这是带条件的历史网格解释，不证明实际CSV每行都是新报价、真实到达时点或严格60秒。sequence检查与gap返回False也不替代未读调用方的恢复行为。

**唯一决策影响：** 可以继续只写新源的一页方法协议，明确用“静态notional失衡”而非假称基础币quantity失衡，暂不混用arrivalflow/buys/sells。保留system_time及真实时序/分箱/历史映射条件，不按漂亮结果改窗口、不套旧Kraken34日。确需时钟定义时，明确定位是固定树Database.new_tick，而非漫游全部源码；即便读到它也不自动绑定2021数据，当前不再请求。

JSON绑定15实际输入、完整3GET回执及源SHA。模型/训练/预测/评分/回测/模拟/交易、行情/权重下载、账号/付款/外发均0。实际model/effort UNKNOWN，旧FAILED及现金不变。
