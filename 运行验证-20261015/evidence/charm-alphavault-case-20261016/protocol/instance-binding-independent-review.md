# 首个脚本实例：源码与初始构造绑定独立审阅

**限定PASS。** 两份Routescan保存响应均status1/OK，读取回执HTTP200，原件bytes/SHA256吻合。被动解码ABI构造参数与独立词法比较均支持root的绑定结论；没有收益、余额或账号读取，没有联网、编译或EVM执行。实际model/effort UNKNOWN，规则版本不变。实际审阅UTC、全部输入hash及逐word解码见同名JSON。

选择范围事前固定为冻结脚本第一个未注释地址0x1cEA471aab8c57118d187315f3d6Ae1834cCD836，未按收益筛选。对应provider声明PassiveStrategy/Proxy0，构造8个完整32字节word；vault构造3个word，地址高位及整数范围均检查：

| 初始参数 | 独立解码 |
|---|---|
| strategy._vault | 0x9bf7b46c7ad5ab62034e9349ab912c0345164322 |
| baseThreshold / limitThreshold | 3600 / 1200 |
| period / minTickMove | 41400秒（11.5小时） / 0 |
| maxTwapDeviation / twapDuration | 100 ticks / 60秒 |
| keeper | 0x04c82c5791bbbdfbdda3e836ccbef567fdb2ea07 |
| vault._pool | 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640 |
| vault._protocolFee | **0** |
| vault._maxTotalSupply | 200000000000000000 raw shares |

该vault的provider声明初始费为0，不是部署示例脚本的5000（0.5%）。这同时不能推出当前费或全历史费为0。

比较方法只按数据解析标准编译JSON；用保留字符串字面量的词法分解去注释/空白，按花括号提取目标contract定义，没有eval或执行网页/源码。与冻结commit 774960877e122da12015878ee3a03dfa58536968的对应contract：

- strategy响应PassiveStrategy：796 tokens精确相同，token SHA256 96c95bc95611cf8b2d14e84552124dbbc8dc62c0844f07e5c9afc1af5cfd7c6a。
- strategy响应中AlphaVault及单独vault响应AlphaVault：分别2657 tokens精确相同，token SHA256均为dea505db0a00d3f609167fa4110b317e9dcacec51f2c5be23e695916e03d006f。

以上是**目标contract的规范化token相同**，不是完整flattened文件逐字节相同、依赖树全同或独立编译字节码证明。CompilerVersion/Proxy0是同提供商声明；没有另一次独立部署验证。

源定义vault/pool为immutable，加上provider构造声明可支持条件性关系，但未读vault实际strategy指针或任何时间点的状态。阈值、keeper、period、费的后续配置/变更历史及实际发送调度仍UNKNOWN；提交日期也不是精确首次公开证明。初始参数和公开公式已减少实现绑定缺口，不把未取历史当已证私有主观择时、不可复制或策略失败，亦不把本层PASS提升为完整历史政策或盈利通过。

原件SHA256：strategy 595d62307504f5bba0e6a43d7e02a58b61b4ff9392367cf355d3a9fe350bb770；vault 562fd7784602dc72b6ec4c15059486bae82e14d2021d2f147fd429c805f77d04。实际请求URL及读取UTC保留root两份原回执并列入本审阅输入指纹，未改原件。
