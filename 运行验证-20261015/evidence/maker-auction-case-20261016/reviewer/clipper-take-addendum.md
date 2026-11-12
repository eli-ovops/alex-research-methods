# Clipper Take日志、偿还与实际抵押量：独立补充

结论：**PASS_TAKE_LOG_AND_PAYMENT_AMOUNT_CORRESPONDENCE**。receipt中唯一目标Take日志将真实拍卖id106与同笔抵押取得及DAI偿还对应起来；请求数量与实际数量不同，`usr`不是竞价人。它不证明私有外层采用Sidestream bot，也不新增全策略或完整期间盈利结论。

仅本地静态读取指定Clipper source/ABI原件、receipt、根cashflow crosscheck及已存normal input；实际UTC、输入bytes/SHA256、逐项检查及全部原量见`clipper-take-addendum.json`。0联网、模型、回测、编译、EVM、下载代码或策略执行。实际model/effort UNKNOWN，沿用PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4，只新增本Owner两文件。

## 唯一事件及字段

提供者source API返回ContractName Clipper、Proxy0、CompilerVersion v0.6.12；安全解析其标准编译JSON中的Clipper.sol和ABI，未执行脚本或编译。ABI的Take为非anonymous，indexed字段为id与usr，五个非indexed uint256依次max/price/owe/tab/lot。

receipt的emitter `0x71eb894330e8a4b96b8d6056962e7f116f50e06f`仅有一条该Take topic，logIndex **0x12b**；topics3个、data160bytes，tx/blockHash/区块/transactionIndex与receipt一致。id=**106**。

| 字段 | 精确显示值 | 源码含义/单位 |
|---|---:|---|
| max | 1984.1667924596281306526788695 | 调用者最大可接受拍卖价格，ray（10^27）；DAI/抵押品单位 |
| price | 1964.325124535031849346152080805 | 该次take使用的实际拍卖价格，ray；低于max |
| owe | 30887.306726180869414833925266508363764551865793483 | 该次需要移动的内部DAI债务，rad（10^45） |
| tab | 0 | 本次take扣除owe后的剩余债务，rad |
| lot | 2.000032052345989452 | 本次take扣除slice后的局部剩余抵押量，wad（10^18），**不是本次成交量** |

`usr = 0xabb98818e8ed05b07c784f99784003f6388d53f9`。源码Sale注释为Liquidated CDP；kick的usr是剩余抵押接收地址，take从`sales[id].usr`读取它，不是从msg.sender取得。因此不能把它称竞价人、callee、利润收款人或确认其现实身份。

源码take327—415行先计算/调整slice与owe，再更新局部tab/lot，最后emit。tab=0且lot>0时，源码将剩余内部抵押记回usr并删除拍卖；日志仍保留局部lot值。因此不能据此说2.000032…还留在持续拍卖待买，也不能将它算给买方的收益。未猜测任何抵押品registry/分支名称。

## 偿还的rad→wad向上取整

实际owe原量为：

`30887306726180869414833925266508363764551865793483 rad`。

按已读callee的`ceil(owe / 10^27)`得到：

`30887306726180869414834 DAI wad = 30887.306726180869414834 DAI`。

它与本receipt中callee→零地址的DAI Transfer（0x125，Join对应流）完全相同。取整导致的多出量为74733491636235448134206517 rad，小于10^27 rad，即不到1个DAI最小单位（10^-18 DAI）；没有把rad误当18位数直接除算。

## 请求上限与真实slice

在既存opaque自调用input中，按唯一已知内层selector `0x81a794cb`**条件解码**得到id106、max与Take.max相同、who为该callee。请求amt是：

**17.724163633411058706抵押单位的数量上限（wad精度）**（原量17724163633411058706）。

它不是实际买入量。receipt中对应join→callee的唯一WETH Transfer原量为15724131581065069254，即**15.724131581065069254 WETH**。该值还精确等于源码债务封顶分支的`floor(owe / price)`。计算余数1222309512590404858178336724013小于price，向下取整关系成立。

请求上限减实际量=2000032052345989452，恰为Take.lot；实际slice加日志剩余lot=17.724163633411058706。这个对应支持债务封顶及剩余量解释，而非“所有请求数量均成交”。仍未把条件内层解码升级为私有外层完整语义验证。

## 通过与未知的层次

新增可绑定层是：**指定emitter、真实auction id106、Take使用价格/债务、实际WETH取得和DAI向上取整偿还**。此前净ETH观察结论不因本次扩大范围。

来源仍是同提供者的verified-source声明和receipt；Proxy0不等于独立代理或编译验证。本次没有独立部署字节码对照，没有重查历史registry、拍卖起始记录或前后状态。公共接口与同类公开参数并不证明该交易由Sidestream运营、运行其bot、采用其私有阈值或预先锁定择单。完整策略账期、失败费及其他经营成本仍不由Take日志补齐。
