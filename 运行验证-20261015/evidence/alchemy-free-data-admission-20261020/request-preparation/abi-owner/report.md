# 两项只读功能调用的本地ABI准备

2026-10-19 UTC；只读已有公开原件，未联网、调用RPC/EVM、订阅或运行旧源码/适配器。**按Root最新决定，功能候选是同一已存验证TM的`getTroveIdsCount()`＋`shutdownTime()`；不再以另一Registry的部署ABI作为这次纯功能检查前提。** 这只是缩小不必要的依赖，不是修改金融策略或择优挑结果；两函数当前值均未读取。

## 已绑定候选

- Ethereum WETH TroveManager：`0x7bcb64B2c9206a5B699eD43363f6F98D4776Cf5A`。已存Etherscan原页`evidence/direct-protocol-case-20261016/root/v2-contract-original.html`在2026-10-16T02:38:08.463364Z取得，SHA256 `3a69cb262a8cca814a2a3069d6fc200967f0db96ea473c4746ca2eda72798c19`。原页literal addressContract/litreadContractAddress及Contract Name支持这个地址/名称，`pre#js-copytextarea2`是该页ABI。此为当日提供者验证声明，不是当前链runtime独立核验。
- 原页ABI直接明确两函数均无参数、`view`、返回一个`uint256`。`getTroveIdsCount()`由已存实现返回`TroveIds.length`；`shutdownTime()`只作为简单scalar功能读，不扩成资格或收益判定。
- **工程编码**：Ethereum Keccak-256(signature)前4字节：`getTroveIdsCount()`→`0x4aff96e1`；`shutdownTime()`→`0x58569081`。使用本地独立编码运算，并通过空串Keccak及`transfer(address,uint256)`→`a9059cbb`已知向量检查；没有执行来源程序。**这些命名selector映射是工程派生，不冒充原页明载的方法-selector表。** 原页bytecode中确有4aff96e1原字面，也不能单靠存在便声称已核当前链调用成功。

## 原MCR缺口保留

该TM原页ABI没有`MCR()`或`addressesRegistry()`。已存TM源码把MCR设为internal immutable；构造参数原文指向`0x20F7C9ad66983F6523a0881d0f82406541417526`。

固定审计commit `abe7cbfbd465fba3812282c51773455766a70e96`的AddressesRegistry源码L36明确`uint256 public immutable MCR`；复用IAddressesRegistry接口L45声明无参数返回uint256，未标view。具体public getter的只读属性可由Solidity语义解释，不能据接口未标view就推定需要发交易。源码于2026-10-16T04:32:15.758865Z公开读取，其sha/date与接口证据均已列入concrete-bindings和manifest。

`MCR()`工程selector为`0x794e5724`。**精确20F7部署ABI/runtime仍未在选读原件中取得**；不能把审计源码或TM内嵌的接口期待升级为该Registry实际部署确认。此缺口不作为count＋shutdownTime功能准备的硬门槛，不补查MCR数值或资格/补偿逻辑。

## 旧新部署不能混配

既有官方旧清单`direct-protocol-case-20261016/liquity-v2/contracts__addresses__1.json`列的是旧WETH TM `0x81d78814df42da2cab0e8870c477bc3ed861de66`、旧AddressesRegistry `0x38e1f07b954cfab7239d7acab49997fbaad96476`，顶层CollateralRegistry为`0xd99de73b95236f69a559117ecd6f519af780f3f7`。其legacy-WETH ABI和旧固定ref清单不替代新7bcb/20F7。既有审计比对只确认TM/Constants与audit-final文本相同，不覆盖所有接口、部署bytecode或当前链状态。

## 交付及仍未验层

`concrete-bindings.json`保存原页ABI条目、每字段原路径/hash/日期、工程Keccak完整输出、旧新部署警告及缺口。`manifest.json`记录选读原件身份。仅形成可审阅请求的静态依据；是否使用文档demo、是否实际请求、固定区块一致性、返回值与canonical状态均留给Root之后具体授权，未在此运行。没有自行注册或读取key，账户也不被本报告额外设置成纯功能检查的全局硬前提。

选读唯一原件约1.78MB；包含数次对同TM页的必要字面定位，累计读取按文件全长上界估算仍低于8MiB，细项见receipt。不全扫原件或私人目录；无金融计算、模型、回测、交易或新网络，实际model/effort/CPU/RSS=UNKNOWN。
