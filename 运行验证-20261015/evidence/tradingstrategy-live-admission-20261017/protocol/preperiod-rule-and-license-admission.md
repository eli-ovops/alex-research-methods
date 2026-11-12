# ETH-BTC-USDC：前期规则与许可准入

**取得同名具体策略模块及2024年3月提交历史、同期AGPL授权声明；未完成与声称4月1日至8月5日实盘/+7.87%结果的精确版本绑定，不能准入为该实盘的完整事前规则。** 本轮不读取成交/利润原账，也不因缺私人动机或bot而否定历史现金事实。

8次GH公开只读GET后停网（每次25秒/1MiB上限）：7次200、`LICENSE`旧路径1次404原件保留。查LOCAL_BLOCKERS后，实际固定根目录清单明确`LICENSE.txt`，第8次按其真实路径取得。没有重试该404、认证变更、依赖安装或下载4.03MB notebook。URL、UTC、原HTTP/header/body保存bytes/SHA、源码Gitblob及sha见read-receipts.json和同名JSON。HTTP捕获bytes含headers，不冒网络流量；实际model/effort UNKNOWN，规则版本沿用。

## 身份与时点

- 官方repo中精确搜索名称，定位`strategies/eth-btc-usdc.py`（另有low-fee等变体，未混为此版）。当前搜索命中的不可变blob `cab4c475586c49191fb5e73b2c39886acef32393`另存，仅作发现，不回填历史。
- 指定路径、`until=2024-04-01T00:00:00Z`历史查询返回3条：首次添加模块的`2077015c8f2767de2078768f1bc85baa16f615d4`（2024-03-22T13:13:38Z），随后`e785c644…`（3月27日）、`1ee698c07a219b1344a2d2a102401c50189b0fe4`（3月28日12:20:23Z）。另读取首次提交完整元数据，文件状态明确added，提交文字称example strategy。
- 具体历史源按3月28日commit固定读取；Git作者/提交日期提供前期版本线索，不独立证明当时公众已能访问、精确首次公开日期、部署或参数未再改。旧日期不等预注册/OOS。
- 源L484–490 metadata为beta、name=`ETH-BTC-USDC momentum`；未见liveID、vault/执行地址、部署image/receipt或对4月实盘的精确绑定。根代理另负责实盘身份，不由同名推定。

## 具体公开规则与重要失配

历史源L43–63 live分支实际是Polygon QuickSwap **WETH/USDC 0.003**及UniswapV3 **WETH/USDC 0.0005**；WBTC/WETH行被注释。代码后续把第一pair变量称btc_pair，不会让该配置自动变成BTC。不能因name/说明声称ETH/BTC而抹除此真实内容，不能据此直接推部署发生错误。

L73–124参数明确：`cycle_1d`、source/target均d1、clock_shift0；RSI8、ETH/BTC RSI5，熊市entry65/exit70、牛市entry80/exit65，200期MA、regime_filter_only_btc=1；allocation0.98、rebalance_threshold0.275、momentum_exponent3.5，stoploss/trailing均None。标题仍称1h、若干注释称8h/1h，不能用注释覆盖实际值。初始现金10000、2019至2024-03-15及0.003费覆盖是回测配置，不是实际本金/费率/收益。

L203–423的decide_trades公开使用前两期RSI阈值穿越、MA regime判断、ETH/BTC RSI变换后3.5次幂动量，已有仓位默认保留直至退出触发；AlphaModel选择最多2信号、归一权重、按98%权益目标及27.5%权益最低交易阈值请求调仓。它引用AlphaModel、PositionManager、指标框架/数据、默认routing，未完整读取各依赖、实际滑点/Gas保护及部署配置；所以取得的是实质策略模块，不冒整套生产完整执行规则。本文只解释静态代码，不执行或修复策略。

L492之后的收益/CAGR、回撤、胜率及交易频率为源内回测/估计叙述，未作证实、更不混成+7.87%实盘原账。来源依赖外部数据/指标；前期代码开放也不能消除多重选择、未来信息、数据和成本风险。

## 许可与结论

同一历史commit的`LICENSE.txt`逐字声明GNU Affero General Public License version3或更新版本（AGPL-3.0-or-later），允许按该许可证复制/修改，含无保证声明。不是MIT或无条件商业部署授权；保留版权/许可、衍生及网络交互等义务应依完整AGPL适用条件判断。本轮文件仅含授权通知、未取得其外链完整条款，不给法律意见。依赖/行情数据/托管服务许可与个人资金准入另属UNKNOWN。

因此：**公开同名模块/参数/同期授权有原件进展；当期实盘精确使用版本、资产配置、完整依赖及参数历史和事前公众可得身份仍未证。** 最小下一证据是根正在核的具体实盘注册/状态中可验证策略版本和配置，不继续扩其他变体/赢家，不要求全部私人动机。未算收益、未运行来源代码/模型/回测/SDK/SQL/EVM/策略/交易；到8GET预算收口。
