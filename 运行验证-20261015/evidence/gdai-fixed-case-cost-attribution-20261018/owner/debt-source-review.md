# 固定gDAI案例：借贷与资产精度原件

限定取得DAI历史精度和借／还实际资产原量；Pool历史逻辑、精确利息拆分及抵押token精度仍UNKNOWN。没有核算总收益、年化、容量或换币。

## DAI直接源码绑定

[Sourcify既有记录](https://sourcify.dev/server/v2/contract/42161/0xda10009cbd5d07dd0cecc66161fc93d7c9000da1?fields=sources%2Ccompilation%2Cmetadata%2Cdeployment%2Cabi%2CcreationBytecode.transformationValues)返回HTTP200、19,714字节，creation/runtime均exact_match。`contracts/l2/dai.sol:Dai`部署block1336824早于样本；源码L41–44为常量name=Dai Stablecoin、symbol=DAI、version=2、decimals=18。直接部署匹配和常量支持该精度，不借用UI或其他代币定义。L1为AGPL-3.0-or-later；verifiedAt2024-08-08不证明源码2023之前已公开，也不证明DAI当时实际美元兑换价格。

## 借／还事件与实转

既有官方[Aave IPool源码](https://raw.githubusercontent.com/aave/aave-v3-core/master/contracts/interfaces/IPool.sol)的L58–76、L78–91、L50–56分别定义Borrow、Repay、Withdraw。纯数学Keccak得到的三个topic0与原件精确相同，按32字节原量解析，无ABI库或EVM。当前master的语义匹配不等于历史Pool运行码绑定。

| 原件 | 实际字段与同笔转账 |
|---|---|
| id62，tx `0x8c00149ace02e00b73973543bbe336070e42a0c0a6b89cb44228f23f03678d8e` | Borrow reserve=DAI；user/onBehalfOf均固定EOA4250…5a90；amount原量850000000000000000000，与同笔DAI→该EOA的Transfer相等。interestRateMode=2，接口注释L64为Variable；borrowRate为ray，不是固定持有期账单。 |
| id104，tx `0x58c9f923902d04d37a4ddb66404555017d6c7b2f589c3fd47b71752615e62c7b` | Repay user/repayer均该EOA；amount原量850110166431858826003，useATokens=false，与该EOA实际转出DAI相等。 |
| id106，tx `0x2e429720739b79fc922b27ccbc114a18ab6a40bf0dd8dc9656f8094d7881786c` | Pool Withdraw reserve=`0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9`，user/to均该EOA；原量1607252017与底层token实转相等。未按猜定精度换成人类单位。 |

偿还时债务token烧毁原量850000000000000000001与实际支付DAI不是同一个数，不能拿债务token Transfer当本次真实还款或费用。借还资产支付可确认，但完整期初债务、期间变化、实际Pool／债务token实现及指数计算未重建，不能将原量差无条件称精确利息；本轮未做该差额计算。

## Pool及抵押资产的源码缺口

Pool `0x794a…14ad`的独立Sourcify归档200、runtime exact_match，取得AGPL-3.0代理源码，但creationMatch、deployment、constructor均无值。代理的initialize(_logic,_data)与构造admin不同，不能从admin推出初始logic。历史实现／升级链未绑定。

唯一一次官方RPC `eth_getLogs`（block0..9999999、Pool Upgraded）返回HTTP403，已停止该端点全部请求；没有换工具／身份／host重取。请求、UTC和HTTPError文本保留，**响应body及其SHA为UNKNOWN／未捕获**，没有为补body再请求，也不把拒绝当没有升级。

抵押reserve的独立Sourcify200、36,579字节仅有MIT TransparentUpgradeableProxy，runtime为match，creation/deployment/constructor缺失。未取得历史底层实现及decimals，不能凭熟悉地址写死USDT6位。初始抵押投入及持有期间机会成本、获得／退出费用未全绑定，抵押退回不是新利润，也不是免费资金。

## 原件与停止回执

实际使用上一阶段两份raw receipt（known-approval-funding、official-arbitrum-fixed-ui-discovered-case-details）及已存IPool原生文本。派单少前缀的文件名只作定位歧义，用rg定位真实文件后读，没有重试不存在路径。

本轮5/8请求即停止：Pool归档成功、DAI urllib TLS EOF、查BLOCKERS后同URI普通curl默认TLS成功、官方RPC403、抵押token归档成功。TLS EOF不是HTTP拒绝，curl未改身份／TLS／proxy；RPC403及Arbiscan旧403均未重取，旧历史state方法也未重试。各来源URL、UTC、HTTP层级、原始payload及回执SHA／字节见`debt-source-review.json`。actual model/effort UNKNOWN；eth_call／trace／EVM、源码执行、模型／回测、账户／付款／安装／交易均0。完成停止，整体盈利案例尚未成立。
