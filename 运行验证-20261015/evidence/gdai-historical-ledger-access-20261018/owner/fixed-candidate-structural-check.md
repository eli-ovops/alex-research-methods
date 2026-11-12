# 固定gDAI样本：存赎结构检查

限定通过份额对应及同笔资产实转，不是完整账户／全费／盈利核验。样本沿用根已固定的最早Withdraw，不另选钱包；本轮仅本地读4份指定原件。

固定EOA为`0x4250f21a947ba6fed45cfcea4da15c30ad925a90`。Deposit的sender/owner、请求的sender/owner以及Withdraw的sender/owner/receiver均为该EOA；不能一般化为这些角色在所有交易都相同。

| 原件字段 | Deposit | Withdraw |
|---|---|---|
| txhash | `0x9ba47ee40d059ee36d2e05c5c56f844ed5dba071c482a3ffea8f3cdf60c3d516` | `0xea25cb68567595cb126982947271f4b74f1376479150b6b040a85463f314465c` |
| block | 50661501 | 51242185 |
| assets原始整数 | 850000000000000000000 | 851847535814009530728 |
| shares原始整数 | 847807628769834056627 | 847807628769834056627 |
| receipt状态 | 0x1 | 0x1 |
| 同笔asset Transfer | EOA→proxy，与Deposit.assets相等 | proxy→receiver，与Withdraw.assets相等 |
| 同笔proxy份额Transfer | 零地址→owner，与Deposit.shares相等 | owner→零地址，与Withdraw.shares相等 |

asset emitter为初始已绑定`0xda10009cbd5d07dd0cecc66161fc93d7c9000da1`，份额emitter为proxy `0xd85e038593d7a098614721eae955ec2022b9b91b`。各自完整原topics/data、logIndex、blockHash和receipt字段在JSON；未相减assets、计算比率或币价换算。

WithdrawRequested tx `0x765c1f61521a156818c02016652fc478245e9a53a779619c2a8804cd45c9ee77`的shares同为847807628769834056627，currEpoch3、unlockEpoch4。三份shares与mint/burn原量均相等；请求本身没有赎回到账。

## 可见范围与剩余缺口

- holder索引response20/21/22各返回4/4/1条，按blockHash/txhash/logIndex去重为5条：存入、申请、赎回及mint/burn。可见普通份额转移为0、未见锁仓存入／释放事件；不据此宣布所有时期／所有前置权利不存在。
- NFT查询response53/54均为空，仅说明当前查询范围，不能排除所有前置NFT权利。原始返回本身未带完整请求参数，边界须与根查询回执一起解释。
- response8有部署block49275523的初始Upgraded，指向0x388277…8093；不能只凭该结果宣称范围外无升级。
- 相关原件还可见先前asset流入及approval，未计成本／分类。receipt含gasUsed/effectiveGasPrice/gasUsedForL1，但本轮不乘算费用，不把缺项当0。
- 根交易nonce为存入38（0x26）、请求39（0x27）、赎回41（0x29），from相同。**nonce40未归档**，不得认定失败、无关或无费用；其定位归根独占，本轮不联网。
- 索引中的blockTimestamp0是占位，不作为日期；JSON仅在交易详情有实际timestamp时记录时间。

实际inputs的绝对路径、当前SHA256／字节见同名JSON。状态`PASS_LIMITED_SHARE_AND_SAME_TRANSACTION_ASSET_STRUCTURE_NO_PROFIT_ACCOUNTING`。actual model/effort UNKNOWN；网络、链调用、源码／ABI／EVM执行、模型、回测、收益核算、账户连接及交易均0。完成停止。
