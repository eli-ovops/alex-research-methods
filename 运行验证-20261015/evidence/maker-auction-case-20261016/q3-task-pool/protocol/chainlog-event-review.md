# Chainlog变更事件：静态接口通过，历史覆盖待原事件

本地审阅UTC：2026-10-16T06:48:00.945738+00:00；实际model/effort UNKNOWN。沿用PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4。本阶段3次公开GET（源码1、精确签名索引2），未抓历史日志、调用合约或执行网页/项目程序。

**官方主网清单的CHANGELOG地址确为`0xdA0Ab1e0017DEbCd72Be8599041a2aa3bA7e740F`，与给定地址一致。两个地址事件所有参数均NONindexed，不能把三键放在topic1筛选。**

## 身份与原件

地址复用官方chainlog-ui固定commit `d23de00bcb68d91b494edfed5d228a02519d4245`、文件`api/mainnet/1.14.2.json`、blob `5274f5ddb6ecf4d200ec4b86939d1445db083db8`中的`CHANGELOG`项。此来源仍不是Q3时点快照。

本轮通过[公开源码API](https://api.routescan.io/v2/network/mainnet/evm/1/etherscan/api?module=contract&action=getsourcecode&address=0xdA0Ab1e0017DEbCd72Be8599041a2aa3bA7e740F)取得HTTP200、status1/OK、ContractName=ChainLog、Proxy=0、编译器v0.6.12+commit.27d51765的源码/ABI。安全解析标准编译JSON中的ChainLog.sol，与保存文本逐字节一致；源码SHA256 `d3561262bc0215c0efdf07e9cd8b1ef40d8168919455edf78ceb1743bd5e33f9`，SPDX为AGPL-3.0-or-later。

这些是提供者已验证源码声明及静态文本对应，未独立编译或核部署字节码，也未核当前或历史storage。

## 实际事件与topic

| 精确ABI签名 | 参数indexed | topic0 |
|---|---|---|
| UpdateAddress(bytes32,address) | key=false，addr=false | 0xcf0ecd10d1399d98978051da48095f368d6f1fa3292d5fc09135b92aa2a4d733 |
| RemoveAddress(bytes32) | key=false | 0x236084b20b5721ddf3e40ed45b570186612a08edec64abae6894b60f315c54bc |

二者anonymous均false。topic通过4byte事件签名API取得，分别为精确text_signature唯一匹配、id18227/18228，再与已读ABI逐项对应；未安装依赖、自己实现Keccak或用SHA3代替。签名索引仅辅助，不证明部署身份或历史完整性；其created_at也不是合约/规则首次公开时间。

查询只应按Chainlog地址及上述topic0限定，两个事件可分别查询；若提供者支持OR，应按其文档使用，不能猜参数。随后在本地data第一个32字节word筛三键：

```text
MCD_CLIP_ETH_A = 0x4d43445f434c49505f4554485f41000000000000000000000000000000000000
MCD_CLIP_ETH_B = 0x4d43445f434c49505f4554485f42000000000000000000000000000000000000
MCD_CLIP_ETH_C = 0x4d43445f434c49505f4554485f43000000000000000000000000000000000000
```

这些为ASCII右补零bytes32。UpdateAddress的data应为64字节：key，然后左补零的address（高12字节应为零）；RemoveAddress为32字节key。通常仅topic0，没有承载key的topic1。原件须核emitter、topic、长度、tx/block hash、logIndex及返回时有的removed字段，保留异常而非补造；按区块和全局logIndex排序去重。

## 能怎样恢复Q3，缺什么不能略过

源码`setAddress`为public auth，成功新增/更新后都发UpdateAddress；设置相同地址或零地址也会发事件。`removeAddress`为public auth，成功移除后发RemoveAddress；不存在键会revert。构造函数也经setter发初始version及CHANGELOG事件。另有UpdateVersion、UpdateSha256sum、UpdateIPFS等元数据事件，不能只凭版本号重建每个键。

恢复Q3需要：

1. 在2026-07-01T00:00:00Z之前有可证明的键基准状态，例如自部署起完整变更史，或另有明确时点快照并衔接之后变更。
2. 完整取得至2026-10-01T00:00:00Z（不含）的相关Update/Remove，按区块及logIndex有序重放。只取得Q3“无更新”不足以证明期初地址。
3. Remove使键不存在；Update为零地址使getAddress拒绝该值；后续Update可恢复。相同值重设不是迁移。月份区块边界、分页覆盖和提供者返回完整性仍须核，空页不是独立链上完备证明。

即使上述重放闭合，证明的也是**所读registry对这些键的登记历史**。它不保证所有部署均已登记、所有交易只用登记地址，也不自动覆盖键更名、其他registry或registry自身迁移。`CHANGELOG`键发生更新时尤其应保留转移线索，不能只对三键重放就称覆盖全部登记体系。

本分支尚未取得事件，Q3实际键值与有无迁移均UNKNOWN。根统一取事件后再作独立实质审阅，不自行抓全链。三键事件范围也不等于全Maker/Sky市场，Kick数或毛补偿不等于个人净利与未来容量。

实际请求URL、UTC、HTTP头、原回应及hash见`chainlog-source-read-receipt.json`、两个`chainlog-*-signature-read-receipt.json`与同名审阅JSON。0模型/回测/策略/EVM/eth_call/trace/交易，未读凭证、安装依赖、认证账户或外发，未修改其他Owner文件。
