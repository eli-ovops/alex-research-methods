# 拍卖106所在Clipper：起价、时间、重置与事件范围

**PASS_STATIC_SOURCE_MECHANISM_WITH_HISTORICAL_UNKNOWNS**。已存提供者源码/ABI及构造参数可条件性绑定ilk=ETH-B，并明确起价、重置和take边界；它们不足以重建真实连续价格曲线、证明每秒单调下降或确认最后一次take是唯一买家。仅审机制，不重复旧净收益整账。

本轮0联网，安全解析已存JSON和构造hex；Clipper.sol与API标准编译JSON源文本逐字节一致。未编译、执行源码、调用EVM或运行模型/策略/回测/交易。实际UTC、输入hash及全部ABI字段见`source-price-rules.json`；actualmodel/effort UNKNOWN，规则PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4沿用。只新增本Owner两文件，不改其他源或报告。

## 条件性构造绑定

源码constructor为`(address vat_,address spotter_,address dog_,bytes32 ilk_)`，API ConstructorArguments恰128bytes，三个地址前补零正确：

| 参数 | 解码结果 |
|---|---|
| vat_ | `0x35d1b3f3d7966a1dfe207aa4514c12a259a0492b` |
| spotter_ | `0x65c79fcb50ca1594b025960e539ed7a9a6d434a3` |
| dog_ | `0x135954d155898d42c90d2a57824c690e0c7bef1b` |
| ilk_ | `0x4554482d42000000000000000000000000000000000000000000000000000000`，去末尾零字节为ASCII **ETH-B** |

源码61—64、137—144行把ilk设为immutable并赋构造值，故**如果提供者返回的源码/构造数据准确对应该部署**，支持此Clipper的抵押类型标识为ETH-B。API的ContractName Clipper、Proxy0不是独立字节码/代理验证；未取得创建交易、编译对照或独立immutable读取。本轮不把前提抹去，也不由该名字猜更多registry地址。

## Kick起价和价格查询

Clipper源码200—217、229—265行可读出以下整数规则（RAY=10^27，WAD=10^18，BLN=10^9）：

1. `spotter.ilks(ilk)`取得pip，`pip.peek()`取得val/has，has为false则拒绝起价。
2. `feedPrice = floor((val × BLN) × RAY / spotter.par())`。
3. `top = floor(feedPrice × buf / RAY)`，要求top>0；注释的经济表达为val×buf/par，实际按上述分步整数舍入。
4. Kick增加本合约kicks成为id，记录tab（DAI rad，10^45）、lot（抵押wad）、usr，`tic=block.timestamp`，保存top并发Kick。它不是市场实际成交价。

buf在constructor初始化RAY，但可由授权file改变；因此不能用构造默认值充当拍卖106当时值。spotter、dog、calc等地址和buf/tail/cusp/chip/tip等参数也可被相应file路径更新。当前输入没有它们的真实历史值、oracle价格或更新链。

当前拍卖价格并非写死在Clipper：`price=calc.price(top, block.timestamp−tic)`（454—456行）。calc只以AbacusLike接口出现，**没有具体算法实现和历史calc地址**。不能据此断言线性/指数、每秒下降、分段阶梯、当时精确斜率或与现货同步。实际时间采用区块timestamp；事件不自带独立发现/广播时间。

## Redo、停止条件及max

`done = elapsed > tail OR floor(price×RAY/top) < cusp`。比较是严格大于/小于并含整数舍入；单项等于阈值并不会因该项触发。getStatus还要求sale的usr非零才返回needsRedo。

Redo要求sale存在且done=true，再设置新tic为当前区块时间，重新取得oracle/feedPrice和buf形成新top。它不是延续旧起点的同一条必降曲线；新top可能改变，而实际变化需原事件验证。Kick/Redo中的coin是可能发给kpr的DAI内部激励（rad），不是成交收入；tip/chip/资格和实际支付仍需按事件核，不默认正数。

权限也不同：Kick有auth且stopped<1；Redo不要求auth但stopped<2；Take不要求auth但stopped<3，均有锁。Take要求sale存在、无需重置、`max>=price`；max只是买方允许的最高**拍卖**价格（DAI/抵押ray），不是DEX滑点、gas或经济净利保证。Yank是auth取消流程，将剩余内部抵押给调用者并_remove，不是买家take。

## Take的实际数量、债务和余抵

源码327—415行：slice=min(lot,amt)，owe=slice×price。若owe超过tab，则把owe封顶为tab，slice向下取整为owe/price；剩余债务低于chost的部分成交又可能进一步缩量。随后局部tab减owe、lot减slice；向who转内部抵押，按data条件回调，向msg.sender收内部DAI。

- `amt`是请求上限，未保证全部成交；Take事件也没有直接包含amt或slice字段。实际slice须结合有明确对应的资产日志/参数/状态，而不是把Take.lot当成交量。
- Take的owe是本次内部DAI付款（rad），tab/lot是此次操作后局部剩余量；usr来自原Sale，是被清算CDP/剩余抵押接收者，不是竞价人或套利利润接收人。
- lot归零则删除sale；否则tab归零则把剩余内部抵押给usr并删除；否则保留新tab/lot。即便Take.lot非零，sale也可能已因tab=0删除，不能把它解释成仍可买的库存。
- 已存UniswapV3Callee把owe向上取整为`ceil(owe/RAY)`个DAI最小单位来join偿还，并使路由最低DAI输出为该值加minProfit（DAI wad）。余DAI给to，和usr不同；该门槛不含ETH gas或私人T规则。

本报告不重新核拍卖106实际正净金额或推测其他买家的收益。

## Kick/Redo/Take/Yank怎样才不漏

| 事件签名 | topics数 | data bytes | 拍卖id位置/经济信息 |
|---|---:|---:|---|
| Kick(uint256,uint256,uint256,uint256,address,address,uint256) | 4 | 128 | indexed id；top/tab/lot/coin在data，usr/kpr在topics。记录开始和激励接收地址，不记录买家。 |
| Redo(uint256,uint256,uint256,uint256,address,address,uint256) | 4 | 128 | indexed id；新top与当时tab/lot/coin；不是新拍卖id。 |
| Take(uint256,uint256,uint256,uint256,uint256,uint256,address) | 3 | 160 | indexed id与usr；data依次max/price/owe/tab/lot。没有竞价人地址字段。 |
| Yank(uint256) | **1** | **32** | **id非indexed，必须从data解码。** |

因此Kick/Redo/Take可以同emitter加topic1=id过滤，**Yank必须单独按topic0与emitter的范围取日志，再解data筛id106**；用同一topic1条件取四类会漏取消。File事件还存在uint256与address两个重载签名，重建参数沿革时不能混作同一种。

历史事件需明确网络、emitter、起止块，按block/transactionIndex/logIndex排序和去重，审分页/状态/缺字段/重组标志；Kick/Redo的tic需与相应块时间对应。此处只给静态完整性要求，未实际取得或审这些历史页。

即使某提供者只返回一次Take，也不证明全历史只有一个买家：事件本身没写买家，失败或未上链尝试不产生Take，查询可能有范围/索引遗漏。根另核真实历史后才能给返回集合层的结论；不以这些机制假装完成采集或价格回放。
