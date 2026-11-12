# Liquity V2：16条合约直接调用及六月调用地址补充核账

独立静态审阅UTC：2026-10-16T02:51:57.675263+00:00。未联网，未运行仓库代码、模型、回测或交易。所有金额以原HTML精确整数/Decimal读取，不采用列表截短gas或即时美元估值。

## 16/16逐笔校验通过

输入为指定合约`0x7bcb64b2c9206a5b699ed43363f6f98d4776cf5a`页面列出的16条直接交易及逐笔原HTML。hash、block、UTC日期、From、To、status与index逐笔相符；所有top-level value=0 ETH、selector=0xef49a6b4；每笔实际gasUsed×effectiveGasPrice与完整页面transaction fee精确相等。14笔均为NothingToLiquidate失败且没有已提交log；2笔成功。原件时间范围2025-11-03—2026-06-06。

|UTC时间|交易|status|nonce|gas ETH|日志|
|---|---|---|---:|---:|---:|
|2025-11-03T15:31:59+00:00|[0x838d5df711…](https://etherscan.io/tx/0x838d5df71144f142895ee248242f96ad9b8056591c6c3feb2c81ca2649d5516f)|Fail|0|0.000616795631148368|0|
|2026-01-20T22:37:47+00:00|[0x9ac9d68da9…](https://etherscan.io/tx/0x9ac9d68da922d3b7a95b41917391a275fbea1d68de57cc5a8dae9e339feb0df9)|Fail|1|0.000153111722610824|0|
|2026-02-05T15:22:59+00:00|[0xc9a8bd99d2…](https://etherscan.io/tx/0xc9a8bd99d2884e0ff855afdeb85dd7a1946e2404c4eb78b1e4c1f4db8f92af88)|Success|116|0.004505740248664468|22|
|2026-02-05T15:26:35+00:00|[0xd7462e338c…](https://etherscan.io/tx/0xd7462e338cbc5ec2c2ca22c24f7a73422cdb3206b59ce6d164f9eb16cddfb8de)|Fail|2|0.002150647680341453|0|
|2026-02-05T15:57:23+00:00|[0xb2346116f3…](https://etherscan.io/tx/0xb2346116f3437c1227243e90c361900f8035284f9911f12e602a5af38691e3fe)|Fail|4|0.002556195|0|
|2026-02-05T15:57:23+00:00|[0x23250ee17d…](https://etherscan.io/tx/0x23250ee17de07b4905a5b246e41b64283c877333e27d9911284c2593a7ec88e9)|Fail|3|0.002556195|0|
|2026-02-05T22:19:35+00:00|[0x9c06addedd…](https://etherscan.io/tx/0x9c06addedd2b7f86a7e69271712c54fb74a0f7a73163f045aa6897ee49a2643c)|Fail|5|0.000722340177710652|0|
|2026-02-05T22:19:35+00:00|[0x43bac61c4a…](https://etherscan.io/tx/0x43bac61c4af998970c4e61835d04f27450acaa52e1b6af6eba1cab858fcad1ef)|Fail|90|0.000722340177884104|0|
|2026-06-03T20:56:59+00:00|[0xd735a6c630…](https://etherscan.io/tx/0xd735a6c630f9f2ea8e9228bd74e43be6981f4c15e796e64d1b87f04fbac1eed0)|Fail|0|0.000090712853669174|0|
|2026-06-04T02:11:11+00:00|[0x3bed4c84e3…](https://etherscan.io/tx/0x3bed4c84e32eff7bec90ba68af4c0acc729fdcdbf3140e64ece3cbb1aaf25234)|Fail|1|0.000294509819669186|0|
|2026-06-04T02:21:11+00:00|[0xf772691e32…](https://etherscan.io/tx/0xf772691e3260e86c11ff604309d29e6c6e3a5578dd5febe5c3c589e0d7e0df49)|Fail|2280|0.000165337301101426|0|
|2026-06-05T06:24:59+00:00|[0x2f7f282bae…](https://etherscan.io/tx/0x2f7f282bae9388e4b4f3ebf36d09725a39eb221efe59445bbea7b2a73e35d4c3)|Success|2|0.005213757965143884|24|
|2026-06-05T13:58:47+00:00|[0xdf785ba735…](https://etherscan.io/tx/0xdf785ba73557d97f358c22855d380a580e180542d756c780fba52a13ca4efa3a)|Fail|4|0.000220910677688402|0|
|2026-06-05T13:58:47+00:00|[0x055ab0a615…](https://etherscan.io/tx/0x055ab0a6155ca152fa3c0081e87098e659bbae91aaaa1f92735bde4b69ec0bf1)|Fail|2287|0.00022091067776202|0|
|2026-06-05T19:02:23+00:00|[0xe0c886a77e…](https://etherscan.io/tx/0xe0c886a77e08172462b5267a760d1dc7d9a5c2c5f4d3901170ab478f7a428678)|Fail|5|0.000344542401934248|0|
|2026-06-06T04:39:47+00:00|[0x0ab8b84c27…](https://etherscan.io/tx/0x0ab8b84c27b20e7fe06d76c7f4d571ec5f074c004cf2174dfa37795dcfc00c8b)|Fail|6|0.000107712779063974|0|

完整hash、所有raw input、每笔原HTML SHA256、全部log raw data、Transfer地址和原始uint均在all16-ledger-derived.json。ERC721的Transfer按indexed tokenId另列，不当作同名ERC20金额或收入。

## 各From分别核算，不合并为一人

|From地址|本合约成功/失败|WETH收款净额|全部直接调用gas ETH|失败调用gas ETH|WETH减本范围gas：1:1单位折合|
|---|---:|---:|---:|---:|---:|
|0x000000000004fbf65b56ae13b507556c2c06bff5|1/5|0.0475|0.006272146497168868|0.001058388532024984|0.041227853502831132|
|0x5c30163146992fcca045948eb58695edce191510|0/3|0|0.001108588156747550|0.001108588156747550|-0.001108588156747550|
|0x3b802e5f90e55fe4751cca24697df6228627be19|0/6|0|0.008755285211811297|0.008755285211811297|-0.008755285211811297|
|0x23245f620d1e910ad76e6b6de4f8284a53c9ad2d|1/0|0.172818867812976406|0.004505740248664468|0|0.168313127564311938|

14次失败的gas统计合计0.010922261900583831 ETH；这是样本费用合计，不把四个From解释为同一个账户或策略。两个有成功收款的From可见收入减本合约调用gas为正，另外两个From在这一范围为负，不能只呈现赢家。

## 两笔成功：Transfer与State独立静态解析相符

2026-06-05成功`0x2f7f…d4c3`有24个log：From直接收到两笔WETH，原始整数37,500,000,000,000,000与10,000,000,000,000,000，合计0.0475。2026-02-05成功`0xc9a8…af88`有22个log：From直接收到37,500,000,000,000,000与135,318,867,812,976,406，合计0.172818867812976406。全部Transfer中，其他ERC20（BOLD）只在协议账户铸记/烧记与流转；NFT是其他trove持有人烧毁tokenId。未见这两笔里有ERC20从调用者转出或额外其他token到账调用者。不能把协议其他账户转账、trove debt更新或NFT编号加作清算人利润。

由父任务新增两份原始State HTML，本审阅者另行从top-level地址行与WETH slot3的Input地址解码核对：

|成功笔|From ETH before→after|ETH减少|From WETH raw before→after|状态核对|
|---|---|---:|---|---|
|0x2f7f282bae…|0.49961477732666164→0.494401019361517756|0.005213757965143884|0→47500000000000000|ETH减少=gas；WETH增量=Transfer净额|
|0xc9a8bd99d2…|1.159982638675570428→1.15547689842690596|0.004505740248664468|1→172818867812976407|ETH减少=gas；WETH增量=Transfer净额|

两笔成功的State证明ETH/WETH余额净变化与受限交易核算相符。普通交易HTML没有加载完整internal trace，不能将0条已加载trace解释为没有内部调用/ETH流；但两成功From的ETH净下降已由State精确等于gas，故不再仅靠“没有trace”猜测账户ETH净额。State和交易来自同一个explorer，不是独立归档节点原字节。

## 六月From的补充：已补齐nonce3，普通交易8/8

原16合约范围内该From只有6笔，nonce为0,1,2,4,5,6，确实缺3。父任务随后取得地址页Latest8/total8及全部8笔原HTML：7 outgoing、1 incoming。缺nonce3是向**另一个wstETH Trove Manager**发起的失败清算`0x84370d2f…623560`，gas0.002127313628530002 ETH，不能漏掉，也不能塞回原WETH合约16条范围。补齐后outgoing nonce精确为0—6连续。

新增funding`0xcad5e2d5…86af`为0.5 ETH外部资金转入；它不是交易收入。该笔gas0.000049398203232 ETH由funding sender支付，未据此转嫁为接收地址的gas；可能的交易所提现费或资金来源成本未闭合。

|六月目标地址普通交易闭合项目|精确数量|
|---|---:|
|普通交易：1次funding+7次清算|8笔；清算1成功、6失败|
|目标地址7次实际gas|0.008399460125698870 ETH|
|其中6次失败gas|0.003185702160554986 ETH|
|已收WETH|0.0475|
|原地址页ETH snapshot|0.49160053987430113|
|原地址页WETH snapshot|0.0475|
|ETH snapshot=0.5−7次gas|精确相等|
|ETH+WETH−外部funding：1:1单位折合|0.039100539874301130|

这进一步支持该地址在所示全部普通交易范围内，扣成功和失败gas后仍有正的ETH/WETH数量增量。尚不等于全部钱包运营成本收益：原地址页另显示102.90000014 KONG，本轮未取其完整token转账链、未给其估值或当作收入；普通交易列表和连续nonce覆盖不了被动token、internal、跨链/链下或其他权利。没有将有KONG解释为亏损/盈利，也没有将页面$0估值当作独立价格证据。

## 边界与建议表述

- 16条是指定合约的direct transaction集合，8条是一个地址explorer声称的全部normal transaction集合；它们均不覆盖完整协议调用、所有钱包、内部交易、全token或全部经济活动。不能把16笔当所有清算次数，也不能把8笔当所有运营收入成本。
- 相同地址的连续nonce仅证明该地址发出普通交易序列覆盖0—6；不能识别真实个人、证明账户没有其他链/地址，也不能证明寻单程序与公开协议源码相同。其他From绝不合并。
- WETH收款是实物token，gas支出是ETH；使用1:1赎回数量可比较，但尚未实际unwrap/提现，之后gas、部署、维护、数据/节点、搜索/竞价、其他地址失败交易、税费及资金成本未含。不能称美元ROI、长期全成本净收益或可持续容量。
- 实付gas含base+priority，不再另扣burn/tip；收款中协议补偿不能再按估计“gas compensation费用”重复扣。
- 单笔及受限集合正增量是可确认的证据，不能因为全策略未闭合而否认；相反，也不能因协议清算规则事前公开，就宣称caller完整策略源码、运行身份、所有竞争成本与个人复用条件已齐。

建议标注：“两笔真实清算在成功State与全部Transfer相互核对后，调用者收到的WETH减实付gas为正；按各From加入该合约范围失败调用费用后，两个From仍为正、两个From为负。六月地址另补齐其全部8条普通交易和nonce0—6，加入另一branch失败费后为+0.039100539874301130 ETH-equivalent；这是该地址已观察ETH/WETH资金流的受限正增量，不是完整钱包/长期运营净收益。”

仅写all16-ledger-derived.json、all16-independent-review.md及新增授权june-caller-wallet-ledger-derived.json；未改父任务原件或其他工作者文件。
