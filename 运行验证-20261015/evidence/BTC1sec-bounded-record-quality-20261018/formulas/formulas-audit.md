# 固定工具公式核验

结论：属性与renderer公式已取得原文；具体CoinbaseBook事件到属性的映射仍未读，实际2021 CSV的历史生成绑定仍UNKNOWN。本轮未读价格样本，也未运行源码。

固定commit `078081e5715cadeae9c798a3d759c9d59d2041bc`。P=`price_level.py`，C=`coinbase_orderbook.py`，O=`orderbook.py`，均为本目录对应inert文件。3次普通公开GET全部HTTP200，合计18,495B，每份≤128KiB。原URL、精确UTC、SHA256与本地计算Git blob见source-receipts.json；未读取独立tree，**Git blob仅本地计算，不能称独立tree匹配**。

| 项目 | 已核源码公式/行为 | 边界 |
|---|---|---|
| 状态notional | P:101–119加/减quantity×price；P:65–72返回round(_notional,2)，P:180–186允许直接set_notional | 需具体connector才能确定调用路径/输入；不是原币量属性quantity，也未证明所有路径都经乘法累计 |
| limit/market/cancel | P:147–178分别累计quantity×price；P:74–99分别round到2位；P:133–145清零；P:188–204允许直接增量notional | 都是已处理事件统计；精确事件分类、size/remaining_size/new_size及撤单/成交区分在未读CoinbaseBook，不冒称已经映射完整 |
| 经济单位/变换 | 在price为quote/base、quantity为base条件下，乘积为quote金额；所读属性层只有round(2)而非log/百分比变换 | 这是量纲推断，不认证实际CSV美元单位、归一化或历史配置。既有Book另存float32；不保证精确币值 |
| midpoint/spread | O:75–81取最优bid/ask，midpoint=(ask+bid)/2，spread=round(ask-bid,4) | 固定renderer为绝对价格与绝对价差；不是bps。绝对值单位继承输入price，实际2021文件另需绑定 |
| distance | 已有tool-book:175为price/midpoint−1，不乘100 | 固定实现是有符号无量纲比率；发布卡称“%”与此不同，不能未经历史绑定宣称CSV错或自行缩放 |
| feature命名 | O:94–119输出midpoint/spread/buys/sells；两侧按distance、notional、可选cancel/limit/market_notional和row编号命名 | 名称与输出排列对应；MAX_BOOK_ROWS、INCLUDE_ORDERFLOW实际配置未读，不能认证历史列数。buys/sells来自未读TradeTracker属性，不能只凭名称宣称其无额外变换 |

C:59–85把初始snapshot price/size转float后送入bids/asks.insert_order；C:155–188将open/done/match/change分派到具体book。C:171–179直接按msg.price×msg.size记trade notional，买卖方向按resting side转为主动成交方向；但具体book如何更新PriceLevel仍未读。未取得CoinbaseBook，因此不能把以上分派等同完整数量映射证明。

时钟新增证据：C:146–148先db.new_tick，再令last_tick_time=msg.time；结合已保存Database.new_tick:58–63本地dt.now覆写system_time、Simulator:210–229以system_time比较而用last_tick_time初始化网格，可确定固定实现涉及不同字段来源。它不证明两个时钟同步，也不证明实际2021生成使用这一版本；不把代码差异直接叫实际未来泄漏。

最小剩余证据：实际2021 version1生成版本/配置与字段字典；若仅继续核固定工具具体映射，缺C/O实际导入的`data_recorder/coinbase_connector/coinbase_book.py`与TradeTracker、配置。当前3GET已尽，不追加读取、不访问旧受拒tree。

0来源执行/模型/回测/收益计算/行情下载或prefix价格样本读取；actual runtime UNKNOWN。原文、回执及两报告仅在本formulas目录保留，无清理项。
