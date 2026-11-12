# Deribit 个人 ETH 期权条件：有限来源准入

结论：已找到个人准入、ETH 反向期权规格与费用的官方文本；居住地、当地合法性、具体账号资格及数据复用授权未核，当前不满足本阶段完整渠道准入。不是盈利或不可行裁定。

本轮 4/4 读取（2 search query、2 open，3 次 web 工具调用），不再联网。后端为受支持内置 web；按根已记录 Exa blocker 未重试。快照是工具原生文本返回，不是原始 HTTP body/header；保存字节不是网络流量。UTC 2026-10-16T22:59:39Z 为末次读取后观察时间，各次请求精确起止未单独捕获。实际 model/effort UNKNOWN。无源码/模型/回测/EVM/交易执行，无账户或付款。

| 条件 | 实读证据及结论 |
|---|---|
| 中国内地、香港 | 官方显式限制名单的本次返回未列两地；Rulebook 还排除当地使用违法或平台提供服务违法的司法辖区。不能由未列名推出合法可用；用户所在地未答，香港券商账户不证明居住地。 |
| 个人资格 | Rulebook L112–139：18 岁及法律能力、非限制人士/地区、经验与资源、KYC/AML、资料与风险同意、技术条件；平台可加条件。没有核用户是否符合。 |
| 合约与最小单位 | Inverse Options 本次官方索引全文返回：ETH 乘数 1 ETH，最小订单 1 合约；未把乘数错当最小只需少量保证金，也未独核数量递增步长。不同线性/USDC产品不沿用此值。 |
| 抵押/保证金 | ETH 反向期权的保证金币种 ETH；标准保证金卖 call 的初始系数 max(0.15−max((K−I)/I,0),0.1)+期权标价，维持系数 .075+标价。只是规格，未核具体账户风控、组合/跨币模式或足额持有 ETH 能否免强平。 |
| 到期 | 欧式自动处理；2026-08-01 起价内先转同到期期货，再结算 ETH，不能说按 strike 真卖出整枚 ETH 得美元。 |
| 交易费 | 费表标准 options maker/taker 均 3bps（0.03%）基础资产计价，premium cap12.5%；不能视为成交价差、整套成本或已享优惠。 |
| 交割及其他 | BTC/ETH options通常 .015%，cap12.5%期权价值；daily options免交割。新到期两步不重复收交割费。清算另有费用，非主动普通平仓费。出入金/网络/换币成本及具体账户层未齐。 |
| 成交原件与数据用途 | 本预算未实读 public trade API、历史保留/字段、完整个人账单及数据使用许可，均 UNKNOWN。匿名撮合规则不等完整匿名公开个人 P&L。 |

来源定位：

- [Rulebook](https://support.deribit.com/hc/en-us/articles/25944555524125-Deribit-Exchange-Rulebook-Deribit-FZE)：Version2.0，适用2026-08-13，页面更新2026-09-15 10:24（时区未示）；资格L112–139、保证金模式L232–244、初始/维持要求L325–329。限制司法辖区 Appendix F 及当地违法兜底见 read1 官方索引返回；未声称保存完整1394行原页。
- [Restricted Jurisdictions](https://support.deribit.com/hc/en-us/articles/25944487427741-Restricted-Jurisdictions)：read1官方索引文本，更新时间仅“6 days ago”，不强造精确日期；中文搜索结果是较旧翻译，不替代英文当前口径。
- [Fees](https://support.deribit.com/hc/en-us/articles/25944746248989-Fees)：read1官方索引文本 Trading Fees/Delivery fees/Liquidation fees；更新仅“16 days ago”。read2/3合并工具返回中 Fees open只有标题/258总行，不能伪称费用全文由open取得。
- [Inverse Options](https://support.deribit.com/hc/en-us/articles/31424939096093-Inverse-Options)：read4官方索引返回 Contract specifications、Settlement Process Change。更新“14 days ago”；其生效日2026-08-01是正文明确日期。只作当前资料商平台声明，不证明具体市场可成交或投资收益。

最重要缺口是个人居住地与对应法律/平台适用性尚未建立；另外公开成交数据与用途许可未实读。不能据此宣称5000美元足够或合法可操作，也不把未知判为所有个人永远不能用。保留既有20ETH历史正现金事实；本轮仅当前渠道研究。

