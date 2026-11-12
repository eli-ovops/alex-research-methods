# Topic新命中：源码可读，Maker及币种归属未证

审阅UTC：2026-10-16T07:02:28.404346+00:00；实际model/effort UNKNOWN。规则PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4。本轮只对指定三个地址各一次普通公开getsourcecode GET，未扩大协议或事件抓取。

**三个新emitter均有提供者已验证Clipper源码，Kick/Redo ABI精确匹配已知签名；但三者构造Vat/Spotter/Dog均不匹配官方Maker登记值，不能把这些命中自动归为Maker任务或DAI收入。**

## 身份比较

官方固定清单及已保存Chainlog历史在对应已观察事件时点给出的值为：MCD_VAT=`0x35d1b3f3d7966a1dfe207aa4514c12a259a0492b`、MCD_SPOT=`0x65c79fcb50ca1594b025960e539ed7a9a6d434a3`、MCD_DOG=`0x135954d155898d42c90d2a57824c690e0c7bef1b`。对799条原始变更重新按区块/logIndex重放，各新emitter在其观察时点均无任何登记键直接指向它；这只限所读registry历史，不能证明不存在其他关系或平行登记簿。

| emitter | 构造ilk（保留大小写） | 构造Vat | 源码注释 |
|---|---|---|---|
| 0x62b7a353928142a18c07026a33f8089d1c7378f4 | paxg | 0xbc22e8c15bc476ef4fd0124c5a03b23607e30d2c | rwaUSD auction module 2.0 |
| 0x9e9b46f8162d8af11563239f0abd1b321ae1a9e8 | usdy | 同上 | 同上 |
| 0x8c458b36f537629a21e83fb9fad1fe1c5c55f6f2 | WBTC-A | 0x62ee80cb1e96b113b5aea31f1c6fcb9ae64fd453 | Dai auction module 2.0 |

前两个的构造Spotter=`0xf3aee748355bb07cbe702b4ff8dbe6118b34e2a2`、Dog=`0x15a36d5caf263160c2a49dde6429c045fb711ddd`。第三个的Spotter=`0xec9cc5051b105b6131568c26efa20724c02ff02a`、Dog=`0x8dd542a492c87234d8fba21a939c4053602f541c`。这六项也都不同于上述官方登记值。

所读源码的Vat/ilk声明immutable；Spotter/Dog可经授权file改变，故构造后者不是当前状态证明。没有读这些替代Vat、token或Join的实现、部署关系、运营者声明。`paxg/usdy/WBTC-A`只是构造标识，不能据此独立确认实际抵押代币。第三份注释里的Dai同样不是DAI代币绑定证明。

## ABI与源码差异

三回应均HTTP200、API status1/OK、ContractName=Clipper、Proxy=0、编译器v0.6.12+commit.27d51765。安全解码标准编译JSON中的`src/clip.sol`；三者SPDX均为AGPL-3.0-or-later。源码hash：

- 62b7…与9e9b…逐字节相同，17251字节，SHA256 `77f33be2a8fceece1b68ec1eb851b8ba9f9ea292f2c3e285a383bd107cb0e7f8`。
- 8c458…为17250字节，SHA256 `1ea897fc0e8e0964a2e5098716d86fdcd93d11e0b2e4f65998eb1b7650d167de`。
- 三者均**不与**此前官方ETH-B源码逐字节相同。没有把空白/注释差异简单归一化成完整语义等价，也未独立编译或核运行时字节码；首次公开/部署时点UNKNOWN。

三者Kick、Redo、Yank的完整ABI与已审Maker版本逐项相同；Kick/Redo仍为id、usr、kpr indexed及top、tab、lot、coin四个data word。但前两个Take多了`address indexed sender`，签名为`Take(address,uint256,uint256,uint256,uint256,uint256,uint256,address)`，不同于已审Maker Take；不能将旧Take topic无条件用于它们。完整ABI与实际原URL/UTC/hash均保存在同名JSON及各地址原件/回执。

## 金额可以说到哪一层

源码使用rad/wad/ray约定，并以`vat.suck(vow,kpr,coin)`记内部补偿；这支持按各自源码解释事件为内部账面coin字段。**不能仅凭四个uint word或源码注释，将原量换成已验证的DAI收入，或把三个系统coin相加称Maker全市场补偿。** 替代Vat的实际计量实现、可兑换代币、发行者、汇率、提现及费用均未核；rwaUSD只是源码注释自称，也未在此独立证实其代币身份。

本子任务只核来源/身份，不重复根的季度返回计数核验；后续收到完整派生数据再审。没有原账证明个人已兑现净利、私人bot公开绑定、未来任务容量或可捕获份额。

本轮全部输入指纹见`identity-and-source-review.json`。无EVM/eth_call/trace/模拟、模型/回测/策略、安装、认证/凭证、付款、交易/广播或外发；其他Owner文件未改。
