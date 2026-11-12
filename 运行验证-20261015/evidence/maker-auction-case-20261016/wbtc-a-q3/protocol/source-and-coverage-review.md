# WBTC-A身份与Q3覆盖：限定层PASS

本地审阅UTC：2026-10-16T06:58:05.816700+00:00；实际model/effort UNKNOWN。沿用PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4。仅新增一次公开getsourcecode GET，未查季度事件或执行合约。

**官方MCD_CLIP_WBTC_A对应`0x0227b54adbfaeec5f1ed1dfa11f54dcff9076e2c`；在同一Chainlog已返回历史中，Q3期初已登记该值，季度无更新或移除。新取提供者Clipper源码与既有ETH-B逐字节相同，构造ilk=WBTC-A。**

## 官方来源及季度衔接

复用官方chainlog-ui固定commit `d23de00bcb68d91b494edfed5d228a02519d4245`、`api/mainnet/1.14.2.json`、blob `5274f5ddb6ecf4d200ec4b86939d1445db083db8`，该键精确指向目标地址。

本地重读Chainlog Update/Remove原始四页及回执，hash、长度、HTTP200与成功状态相符。799条返回按区块/全局logIndex排序，筛非indexed data首word得到WBTC-A仅一次Update：区块12381609、logIndex174、2021-05-06T15:45:10Z，交易`0x42e122bb5c4addef1bd8c74402178ac982ef813d72c7f846743efd6f8b3cd092`。Q3 [2026-07-01,2026-10-01)无该键Update/Remove，期初/期末均为目标地址。

这支持该registry返回历史内的季度地址衔接，未把旧版本文件单独当Q3快照；仍不排除平行登记簿、更名键、未登记部署或同提供商遗漏。

## 一次新源码GET

[实际请求](https://api.routescan.io/v2/network/mainnet/evm/1/etherscan/api?module=contract&action=getsourcecode&address=0x0227b54adbfaeec5f1ed1dfa11f54dcff9076e2c)及完整HTTP头、原JSON、起止UTC、bytes/hash保存在本目录。HTTP200，status1/OK，ContractName=Clipper、Proxy=0、编译器v0.6.12+commit.27d51765；构造第四word为WBTC-A。

安全解析标准编译JSON得到Clipper.sol 17745字节，SHA256为`c558766018f21ed5665fab015319a8cded1157fb20bf1ff4c65ea74b2f38d0a8`，与已审ETH-B源码逐字节相同；四个事件ABI也逐项相同。SPDX为AGPL-3.0-or-later，可按许可研究复用。未独立编译/核运行时字节码；今日提供者源码不证明首次公开/部署时间（UNKNOWN），同代码不等于分支参数相同。

## 季度事件应如何区分

下列签名topic复用既存精确签名映射，前提是本轮新源码和ABI均与已审版本相同；未新增签名请求或自行计算Keccak。

| 事件完整签名 | indexed字段 | data字段顺序 | topic0 |
|---|---|---|---|
| Kick(uint256,uint256,uint256,uint256,address,address,uint256) | id、usr、kpr | top、tab、lot、coin | 0x7c5bfdc0a5e8192f6cd4972f382cec69116862fb62e6abff8003874c58e064b8 |
| Redo(uint256,uint256,uint256,uint256,address,address,uint256) | id、usr、kpr | top、tab、lot、coin | 0x275de7ecdd375b5e8049319f8b350686131c219dd4dc450a08e9cf83b03c865f |
| Take(uint256,uint256,uint256,uint256,uint256,uint256,address) | id、usr | max、price、owe、tab、lot | 0x05e309fd6ce72f2ab888a20056bb4210df08daed86f21f95053deb19964d86b1 |
| Yank(uint256) | 无 | id | 0x2c5d2826eb5903b8fc201cf48094b858f42f61c7eaac9aaf43ebed490138144e |

四者anonymous均false。Kick是新启动；Redo是已有拍卖重置，不能当另一新拍卖。Yank的id在data，不能只筛topic1求完整拍卖生命周期；Take的usr为余抵接收仓位，不是买方身份。

top/max/price是ray价格；tab/owe/**coin为rad内部DAI（10⁻⁴⁵ DAI/原量）**。lot为Vat规范化抵押量wad，不能直接当WBTC ERC20的10⁻⁸原量。Kick在激励开启时`coin=tip+floor(tab×chip/WAD)`并经vat.suck记入内部信用；Redo还要求拍卖需重置，且tab及lot×feedPrice满足chost才发此补偿，否则coin可以为0。汇总应读实际事件coin，并分开Kick/Redo，不能套ETH-B二月参数估WBTC-A本季补偿。

本分支尚未读取WBTC-A季度事件；数量、内部毛额及个人盈利均未在此审定，等待根原件。即便随后有正coin，也不是已提现代币收入、净利或未来个人份额。所有输入指纹与事件完整ABI见同名JSON。

全程无EVM/eth_call/trace/模拟、模型/回测/策略、安装、认证/凭证、付款、交易/广播或外发；未改其他Owner文件。
