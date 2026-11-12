# 固定大额USDC原账与分层ETH成本独立审阅

**限定PASS：实际USDC收支、本人三笔费用及五笔资金注入的保守gas敏感性均可复算。此文件不计算价格或单币净利。** 实际UTC/完整输入hash见同名JSON；实际model/effort UNKNOWN。0联网/外来代码/模型/回测/策略/EVM/交易，不改root或旧案。

## 实际数量与关闭

Supply为普通supply(0x617ba037)，不是小额例的permit。本人nonce0实际approve USDC给Pool，金额199761000000raw，成功Approval日志一致；nonce1本人→aToken实际Transfer同量，nonce2 MaxUint提现aToken→本人200036254721raw。供给、提现均成功，收据hash/blockHash/height/from/to及gas与normal索引相符。

实际投入**199761USDC**，取回**200036.254721USDC**，数量盈余**275.254721USDC**，持有1209312秒。初始外来USDC本金不另算收入，提款全额也不是利息。

aToken Mint与Burn净显示199760999999raw，比底层实投少1raw。按两个事件index及源码floor算出scaled mint168952991284，初始显示和最终底层兑付均精确复现；成功MaxUint路径销毁全部scaled余额，支持本仓位关闭，未独立读取历史存储映射。Burn的balanceIncrease为275254722raw，实际现金余量275254721raw，保留1raw取整差，不能双记收益或虚构费用。

## 两种费用范围不能混称

| 本人主成本 | 实付gasUsed×effectiveGasPrice（wei） |
|---|---:|
| approve | 35572228880524 |
| supply | 126230788883234 |
| withdraw | 118839563283114 |
| 合计 | **280642581046872 = 0.000280642581046872ETH** |

另按价格读取前固定的敏感性范围，计全部4笔native入金和1笔USDC本金注入的实际收据gas，各只算一次：32886000000000、32886000000000、1071644301000、22680000000000、133187706993600wei，合计**222711351294600wei = 0.000222711351294600ETH**。加主成本为**0.000503353932341472ETH**。这些额外费用由其他地址支付，保守分配不表示本人实际承担，更不表示全实体成本已齐。

normal共7行，owner仅3出站nonce0–2，其余4笔native入金；全部成功，无返回本人失败交易。native value是索引所记资金注入，不是收入；标准receipt没有value字段，此处receipt核的是成功状态、地址/区块和实际gas，不冒充它独立证明native金额。

USDC原始本金由**0xc0b3bb1a5bc31bd4f2b70b1ddbad0e4e9a873780**转入本人，收据Transfer与历史日志相符；这是199761USDC本金，现实身份、是否同人、对价/购买或融资成本UNKNOWN。它与native小额入金的0xc0b3f650…不是同一地址，不能按相似前缀合并。其他native来源91604…亦不自动视作同人。

## 返回历史与边界

旧candidate05 Pool topic2首4条与新末0；Pool topic3为1/0；aToken topic1、topic2均3/0；normal7/0；USDC出1/0、入2/0。总计**7个成功空末页**，包含first-history已取Pool topic2末页。返回Pool仅Supply/Withdraw及抵押开关，未观察借款；aToken Transfer只有Null铸给本人与本人销毁，未观察额外aToken来源。USDC入2包含原始本金和最终提款，不能把两者加作利息。

这是同提供商返回范围，不是独立全链无漏或实体外部债务为0。来源身份、法币取得/退出、融资、税务和运营成本未核；不要求为了认可限定持仓原账而审完整实体多年经营，但也不把相关未知成本写成0。

原本金上限筛选仍不合格、0 eligible不改。USDC余量与ETH费用先分列，不直接异币相减，不称美元/全钱包净利；后续历史spot只可另作标价而非真实兑换。没有读取报价或按收益重选案例，没有资本或期限因果推断、alpha/容量/财富目标证明。
