# BTC1sec：已有采集与聚合代码的语义边界

结论：固定工具实现可证明本地入缓冲时间与网格快照生成顺序，并区分状态量与已观察的历史订单流统计；不能据此认证实际2021 BTC_1sec的生成时钟、经济单位或可得时间。未取得新的源码或行情。

工具固定commit `078081e5715cadeae9c798a3d759c9d59d2041bc`。证据根：`运行验证-20261015/evidence/`。简称 B=`open-license-crypto-book-source-20261017/protocol/schema/tool-book.inert-source.txt`，S=同目录`tool-simulator.inert-source.txt`，D=`BTC1min-public-access-and-clock-20261017/protocol/database.inert-source.txt`。三份源码SHA256、Git blob与原回执均本次重核一致，详见JSON。

| 问题 | 已证代码行为 | 推断及UNKNOWN |
|---|---|---|
| 原tick system_time | D:55–63在recording分支调用本机dt.now(tz=self.tz)，覆写index/system_time，再append内存；满BATCH_SIZE才collection.write | 属本地采集处理/入缓冲时钟，非直接交易所事件时钟，亦不是精确写盘时钟；距网络接收/交易所事件延迟、TIMEZONE实际值和2021绑定UNKNOWN |
| 快照时钟 | S:210–229从tick.system_time读取输入时间，但首次网格起点来自order_book.last_tick_time | 后者赋值依赖未读connector/orderbook，初始时钟一致性不能补猜。输出system_time是网格标签，不是保留每条事件原时间 |
| 1sec聚合选择 | S:234–261按SNAPSHOT_RATE算跨过间隔数；先render_book一次，重复放入所有跨过网格标签，再处理本次tick | 是已有状态保持式快照；本函数没有mean/min聚合，也未调用resample.last。不能将整个实际1秒文件称为已核标准last规则；精确SNAPSHOT_RATE和是否另有重采样配置未读 |
| label可用时间 | S:253–261需读到跨界tick才执行这些历史标签的快照追加；该tick在快照后应用 | 状态条件性只含此前已处理消息，但实际生成可晚于标签，尤其缺消息间隔。没有available_at/发布延迟记录，不证明标签当时在线已可用；也不据此宣称实际数据未来泄漏 |
| midpoint/spread | S:253、269–271仅委托order_book.render_book/feature_names；B仅接收midpoint计算距离 | 指定三份源码没有midpoint/spread输出公式，不能由本范围证明绝对价/百分比。原发布卡把它们描述为中价与买卖价差，但这是发布者定义，不是此代码公式认证 |
| bids/asks_notional_0 | B:175–178把level.notional直接放入float32 _notionals，另有独立cumulative_notional；B:210与250按最优档起枚举 | 已证是当前level属性而非limit流累计；未读PriceLevel.notional实现，原币量、quote/USD量、变换及实际导出命名映射UNKNOWN。不能凭notional名称补公式或单位 |
| limit/cancel/market | B:30–33、182–193单列arrival统计，195–228与232–272说明自上次snapshot累计并读取、clear_trackers；可由INCLUDE_ORDERFLOW控制 | 属已观察消息的过去区间统计候选，不能当未来/未见订单流，亦不等于静态深度。事件分类、单位及累加公式在未读PriceLevel/connector中；筛选局部档位不证明全市场完整流 |

额外限定：S:253–257跨多个间隔只render一次，因此同一状态及当次flow向量可复制到多个标签；不能未经核实逐行求和当独立区间新流。S:274–280会dropna，网格生成不保证导出连续。B:27–33使用float32，不证明十进制无损。D:90–97从查询内首个有load_book日期的最后一个load_book标记截起，S:198–208依赖warm-up完成标记；这提供初始化流程线索，不认证真实book完整。

最小剩余证据：一份发布者针对version1 BTC_1sec的生成版本/配置与字段字典原件，绑定历史commit、价格层/renderer经济公式、时区、快照及后续重采样规则、标签与实际可得时间。若以后仅审工具代码，缺的具体依赖是PriceLevel、具体Coinbase/orderbook renderer及配置；本任务不取新代码。没有这些原件时，可以保留以上条件性代码解释，不能升级为真实2021文件认证。

0联网/来源执行/模型/回测/收益计算/行情CSV、压缩包或parquet读取。未复读LSTM或测试结果；actual runtime UNKNOWN。仅本semantics目录两份报告，原证据保持，无清理项。
