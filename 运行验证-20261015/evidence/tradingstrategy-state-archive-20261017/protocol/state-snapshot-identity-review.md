# 公开快照身份及有限目录核验

**限定PASS；快照不准入目标实盘或盈利案例。** 原件/回执及实际输入绝对路径、SHA256、bytes和UTC见同名JSON；model/effort实际UNKNOWN。0新网络或来源代码/模型/回测/SDK/SQL/EVM/策略/交易执行。

独立解析74582B的wbtc-broken-position.json：chain1，deployment名称原文是`ETC/BTC Stochastic RSI crossover`，不是本轮Polygon ETH-BTC-USDC目标；created_at为2024-07-19T06:01:51Z，last_updated_at为2024-07-24T14:57:01Z。name及backtest_data均null；open/closed/frozen仓位及其trade记录均0、reserve1。null不是实盘身份证明，0记录不等于真实0交易；accounting correction的usd_value1.486586不能当收入。

正确使用方源码明确引用该JSON，mainnet-fork block20377193，调用test_only/enzyme-ethereum-btc-eth-stoch-rsi.py。测试注释明确“交易已执行但state没写”，用于故障核账修复。因此不能用空仓位/交易字段否定实际成交，也不能把测试运行前的损坏state当完整原账。仅阅读文本，未导入、执行或读取其所指环境凭证。测试environment里的vault地址还与JSON deployment地址不同，不合并成一个已验证生产身份。先前BNB测试不是此文件直接来源，保留但不作关联证据；根观察已正确说明。

固定root tree的tests项确绑定SHA5155da2cdb7dcfd27f840fde2e68c91e77bb728a，递归返回同SHA、truncated=false；独立计数434个blob文件、49个.json。当前限定文件名清单未发现目标标识，不证明generic JSON内容没有目标，更不覆盖全repo其他目录/历史版本/外部发布。没有下载全部JSON或大包，树metadata不是账本。

两份源内容与API base64数据、Gitblob指纹及回执bytes/SHA一致；固定tree回执也匹配。根自设读取步骤由6→10→12只扩有限文件/metadata，未扩本子任务6GET，也未扩执行授权。未发现需改的实质数目或身份错误。目标完整状态、成交现金/Gas、实际规则版本与盈利仍UNKNOWN；本审阅不以私人bot或完整私人动机另设历史现金门槛。
