# PT到期、负收益和收费规则：本地补充审阅

限定PASS：当前两份官方说明页可支持下述机械规则；**不等于2023 LOOKS固定实例/费率/事前源码或盈利已过关。** 0新联网，仅被动读根已存HTML并核SHA256与bytes；未读取候选收益、执行例程或合约。原pt-mechanism-review保留初读状态，本补充优先澄清其1:1条件。

- 到期前`redeemPY`须PT与等量YT，到期后仅PT。直接返回SY；如果要其他币，还涉及SY底层兑回或swap，不能把步骤等同于到期自动收到美元。
- 当前文档给出SY=PY/适用PYindex；到期后用postExpiry.firstPYIndex快照。pyIndexCurrent=max(SY.exchangeRate,stored)，只升不降。**底层负收益持续时，PT按计价资产衡量可少于名义预期**：官方教学例120PT→100SY，SY每份1.15则只值115计价单位。非本例观测，也非预测。因而“1PT=1accounting unit”不能无条件保证。
- first interaction after expiry通常由updateData初始化，也可显式setPostExpiryData；这不等于固定钟点自动发交易/强制keeper。未兑回期间后续SY利息/points给Treasury，并非PT持有人额外延长期收益。用户仍需赎回操作，但无须把未知私人动机或每个选择披露当成机械规则成立前提。
- 当前费用页5%针对YT收益/points，**不是PT本金5%**；PTswap费按剩余期限、该池tier计算。页面说到期后兑回底层无Pendle protocol fee、仍有网络gas，不证明全部底层wrapper/兑换/外部路径免费。
- 费用页当前还包含2024后的安排，因此不能把当前5%/tier/分配规则回填2023候选。当前两页未给精确首次发布日期；源版本和历史部署绑定待根提供的源码原件另审。示例MIT标签不替代全部源码/依赖许可。页面示例明确未经审计，本轮未执行。

来源为官方实际索引链接：

1. https://docs.pendle.finance/pendle-v2-dev/Contracts/YieldTokenization （读取2026-10-16T09:58:09.102931Z；96091 bytes；SHA256 5ca13d982f0c6525cf793563aeea79cc2bf2d4b599cffeec992e819613ddd103）
2. https://docs.pendle.finance/pendle-v2/ProtocolMechanics/Mechanisms/Fees （读取2026-10-16T09:58:08.857371Z；21177 bytes；SHA256 fccf575f078323a4a3b7d4f273796778e5b9e7a3b9cfc7d3a4f2c17771a6af96）

两页发布日期UNKNOWN。原文抽取及逐行定位、回执与指纹见source-rule-review.json。现只核公开机械环节；资产/期限/本金/成交价格是投资者选择，不因此断言需要私有预测或不可复制。固定LOOKS候选信息仅父代理告知，未审市场金额，不以稳定币/正收益更换对象。

审阅UTC：2026-10-16T10:00:27.912009+00:00。JSON SHA256：`c4bb28c1655fa55fd1e2bc0df6483729637ca1815ae194f726fc6c6343d7a1da`。实际model/effort UNKNOWN，继承未改。
