# 六月成功集合：会改变净额的会计边界

限定完成：复读9份已有WETH成功HTML、原State和补偿事件；**未计算新的13笔净额**，未读新4笔派生结果，0联网/EVM/策略/模型/回测/交易。协议资格公开与此账户私人bot/现实动机分开，不增新门槛。

## 必须处理的四个实质问题

1. **不能同时扣顶层value与其后相同外付。** 79575…From实际发.080876378911391592ETH给奖励接收wrapper339c…，wrapper同量转dadb…。在显式From+wrapper执行组合并时，前者是内部筹资流，外边界只扣外付一次；单From账则扣其value，不再加扣wrapper转出。该笔奖励仍可能以WETH留wrapper，不能只看FromETH或把缺unwrap当未获收入。
2. **self-value与微额跨地址value不能乱归费。** 7eb…/a739…的From=To=rewardrecipient，1026/1235wei是自转，非外部本金或费用。ace…From给另一wrapper492wei，需peraddress列清；显式组合内部可抵消，不额外重复扣。role未知不改变流量。
3. **From不总是最终受益者。** 6a970…gas由0000000008eb…付，协议奖励先到94d…，native最后付0012…，并非返From。应分别列gas payer/protocol recipient/final payee；合并可叫明确边界的“执行侧留存”，不能声称同一现实主体或From个人利润。其他From与wrapper不同者同理。
4. **WETH到ETH及中间回款不双计。** 同笔补偿WETH、Withdrawal、WETH合约付ETH是一个经济金额；wrapper返From/其他明确保留接收者是分配，不再计新收入/组合成本。外付未知角色仍列实际from/to，条件性保守扣除不强求builder/现实身份，也不擅称贿赂。协议SP/SurplusPool/借款人抵押流及其他BOLD铸币不算执行奖励。

## gas与缺表边界

9份HTML实际GasPrice×GasUsed精确等于TransactionFee，逐项及原文char spans见JSON；不拿maxfee/base/priority再叠扣。4新笔后续应靠root取得receipt，不将旧event-index附带gas字段直接升级真实收据验证。gas永远在实际From只扣一次。

8份HTML真实native父行已按`td id=tb_internaltx_N`所在<tr>重读，金额仅从独立金额<td>取，地址从完整clipboard字段取；未把Loading细节子行/ttr当资金行，亦未把截断地址末尾数字读进金额。第9直接调用2f7f…没有internal表不能填零；已存State中From ETH .499614777326661640→.494401019361517756，差正好为.005213757965143884gas，另有既有.0475WETH实际增证明。这支持本笔From的已观察资产差，不是完整trace不存在证明。

保留wstETH/rETH资产向量，未兑换不凭名字当ETH；已实际换币则输入和输出不能都留下。成功集合是扣可见成功费用后的条件性留存，未含全体失败/运维/融资，也不证明个人可捕获量。旧七尝试六失败正账保持，不用成功集合替代。若未知归属重要则按地址/资产列UNKNOWN及边界，不要求全实体/私人bot/未来OOS来承认观察数量。

所有9 HTML/gas/value/native行、State关键原文位置（UTF8解码Unicode字符偏移，非字节offset）及原文件SHA见JSON。审阅UTC：2026-10-16T10:46:32.772865+00:00。实际model/effort UNKNOWN，继承未改；只写本Owner，不改root/旧材料。

JSON SHA256：`3a446b0fef041177ba941dfd11eeef516f8e5837aee1526f5802d76f90fbab20`。
