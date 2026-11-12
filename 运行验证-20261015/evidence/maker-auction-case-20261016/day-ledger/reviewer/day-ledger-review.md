# 固定地址2026-02-05整日原账：独立审阅

**PASS_DEFINED_ADDRESS_DAY_ETH_AND_7ERC20_RECONCILIATION**：在已保存同一提供者数据范围内，ETH及七种ERC20的期初期末与原流量闭合。ETH余额增加**0.742906747030178161 ETH**；WBTC减少**342个原量（0.00000342 WBTC）**，其他六币余额不变。不是“13笔全资产均盈利”，也不是全天Maker/Sidestream净利、全部经济资产/负债或未来容量通过。

本次遵照预先保存的accounting-criteria.md，0联网，仅对既存JSON做被动解码、哈希、多重集合与整数核账；没有运行项目代码、模型、回测、策略、EVM/RPC或交易。实际复核UTC、所有原件路径/bytes/SHA256、每项状态及13笔细表见`day-ledger-review.json`。实际model/effort UNKNOWN，沿用PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4。只新增本Owner两文件，未改原件/root/protocol或旧审阅。

## 范围、状态与覆盖

地址`0xfa0253943c3ff0e43898cba5a7a0da9d17c27995`，Ethereum1。最终时间过滤为**[2026-02-05T00:00:00Z, 2026-02-06T00:00:00Z)**。提供者时间定位和header对应：

- 起点状态块24386914，header timestamp为2026-02-04T23:59:59Z；用于账日前期初余额。
- 终点状态块24394064，header timestamp为2026-02-05T23:59:59Z；用于账日末余额。
- 列表查询为两端各扩1块的24386913—24394065，所有返回行最终均在指定UTC日内。两端余额请求blockno与相应header一致。这是所保存服务数据间的边界核对，不新增独立节点证明。

四组读取回执及其对应原件逐一hash/bytes、记录HTTP200、实际API状态均一致；nonce9607复用旧root receipt并核其原保存hash。

| 返回集合 | page1 / page2 | 结果解释 |
|---|---:|---|
| normal | 13 / 0 | page2 status1/OK，空数组 |
| recorded internal | 35 / 0 | page2 **status0、message No transactions found、result[]**，是明确的空终页，不能误报通用错误或拒绝 |
| ERC20 token-index | 75 / 0 | page2 status1/OK，空数组 |

normal 13个不同hash，全部from=to本地址，nonce连续**9601—9613**；13份receipt均成功，返回集合内失败交易0笔。全部实付gas均已扣，不能凭“只扣成功gas”漏掉存在的失败行；此处是实际没返回失败行。分页结束、nonce连续与独立归档完备是不同层次，后者仍UNKNOWN。

13份receipt合计**297条日志**，日志字段与各自tx/blockHash/区块/transactionIndex一致且无重复键；75条caller ERC20索引与这些receipt中的caller三topic Transfer按(txhash,token,from,to,raw amount)的**多重集合完全相等**，未因同额合并真实多次转账。内部流按(txhash,traceId)无重复，父交易与行内状态、区块/时间吻合。

## ETH账精确勾稽

| 期初/流量/期末 | ETH |
|---|---:|
| 历史期初余额 | 19.012253765061830582 |
| 已记录跨地址native入流 | +76.804602754573124534 |
| 已记录跨地址native出流 | −76.014429239067704233 |
| 13份receipt实际网络费合计 | −0.047266768475242140 |
| 历史期末余额 | 19.755160512092008743 |
| **余额差与流量净额** | **+0.742906747030178161** |

每笔gas均用receipt gasUsed×effectiveGasPrice，与normal字段逐笔相符；13笔自调用value不作跨账户本金或重复费用。unknown角色外付全部保留为出流，不猜builder。大额同笔往返不等于多份利润；总入流76.8 ETH也不是营收。

WETH的caller Transfer净入共27139376866795514484原量。11笔receipt Withdrawal共扣除同量WETH，并与各笔WETH合约native入款一致；没有相应caller Deposit调整。包装/解包修正后的WETH净变化为0，与余额吻合。若只按ERC20 Transfer加总会虚构约27.14 WETH新增持仓；没有把该入款与解包ETH双计。

## 七币存量勾稽

| 合约币种 | 期初原量 | 期末原量 | 变化原量 |
|---|---:|---:|---:|
| WBTC | 343 | 1 | **−342** |
| DAI | 1 | 1 | 0 |
| PAXG | 1 | 1 | 0 |
| USDC | 1 | 1 | 0 |
| USDT | 1 | 1 | 0 |
| WETH | 1 | 1 | 0（含Withdrawal修正） |
| cbBTC | 238 | 238 | 0 |

七合约集合恰覆盖已返回caller ERC20集合；地址和decimals分开核，不能把同symbol当同资产。以上是不变而非全零；未估美元价，不以七币余额代替其他资产和内部负债。

## nonce9602是库存变现，不是已证套利利润

独立复读该receipt的两条caller Transfer：0x152由caller向池`0xbb2b8038a1640196fbe3e38816f3e67cba72d940`付342 WBTC原量；0x153由同池付115535190902990 WETH原量给caller，随后同量Withdrawal。对应库存下降且资产兑换，不能将这笔ETH到账全算新增交易利润。

另有0.831262343642853268 ETH等量收付相抵；剩余可见外付8998658448144wei，gas48515855488716wei。

- 该笔观察ETH净增：**0.000058020676966130 ETH**。
- 实际库存变现所得：0.000115535190902990 ETH。
- 单独剔除这笔变现收入后：**−0.000057514513936860 ETH**，为gas与可见外付，不是一个全资产赚钱案例。
- 全日ETH增量若只剔除此已识别实际变现收入：**0.742791211839275171 ETH**。

最后一项只是有明确原件支持的现金流分类，不是WBTC成本基础损益、统一估值净资产变化或其他债权已核后的全经济利润；没有为342原量WBTC另猜行情或重复扣一个估值成本。

## 可接受层与未通过层

可以接受这个有限结论：**该地址该UTC日，同一提供者的normal、内部流、receipt及历史余额，对ETH和七ERC20给出一致的数量账。**无需取得整个经营实体跨账户多年账或未来长期盈利，才承认这一层历史勾稽。

不能把它升级成全天Maker/Sidestream收益：297日志中只有nonce9607出现已知Take签名，且来自此前已核拍卖emitter。其他交易的私有合约、贷款、NFT、内部DAI/抵押/债权等未完整经济审计。还观察到nonce9601一条涉及caller的四topic Transfer候选（emitter为0xc364…）；本轮未把它纳入七ERC20资产证明或评价其资产权益。

所有13笔的ETH流量各自都为正，但nonce9602消耗库存已足以否定“13笔全资产均净赚”的说法；其他笔是否存在资产/负债变动也不能仅由ETH正额断言。公开bot版本、实际运营者和完整选择规则仍未绑定。

全部数据仍来自同一服务，historical余额/header/receipt的交叉闭合不是独立共识或全资产归档完备证明。账日又是因已知赢家回溯选择，不是代表性样本或事前OOS实验；不年化、不推个人捕获率/财富/未来容量。未发现影响**所限定数量账**通过的数值或文件质量错误，保留上述经济归属与覆盖UNKNOWN。
