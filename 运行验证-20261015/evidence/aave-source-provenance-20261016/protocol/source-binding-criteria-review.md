# 既有源码来源绑定与时点判据：0联网预审

**限定PASS：本地输入盘点与后续判据成立；事前公开来源尚未证明。** 实际UTC、完整source-unit清单/本地内容hash/settings/构造word及输入指纹见同名JSON。实际model/effort UNKNOWN，规则PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4沿用。0联网、编译、外来代码/模型/回测/策略/EVM/交易，不改root或旧案。

scope SHA256 a1f7c6c5115c986562ba65cef92c291348d8d2954aefa5571b006d444693a65f；只核Pool728a…、aTokenadc45…，入场截止UTC **2026-08-18 03:15:11**。能证入场前公开可用即可支持对应时点层，精确first-ever可以继续UNKNOWN，不增设必须找到最早一秒的门槛。

## 本地原件结构事实

两源响应均status1/OK，保存hash与scope相符；SourceCode是外包一层大括号的标准Solidity编译输入JSON，仅language/sources/settings。本轮只用JSON数据解析，没有eval或编译。

| 项目 | Pool | aToken |
|---|---|---|
| provider声明 | PoolInstance，Proxy0 | ATokenInstance，Proxy0 |
| source units / ABI项数 | 42 / 96 | 25 / 56 |
| solc声明 | v0.8.27+commit.40a35a09 | 同左 |
| optimizer / EVM / viaIR | enabled、runs200 / cancun / false | 同左 |
| metadata输入选项 | useLiteralContent=false、bytecodeHash=none、appendCBOR=true | 同左 |

Pool入口unit为lib/aave-v3-origin-private/src/contracts/instances/PoolInstance.sol；相关机制单元包括同前缀的protocol/pool/Pool.sol、protocol/libraries/logic/{SupplyLogic,ReserveLogic,ValidationLogic}.sol、protocol/libraries/helpers/TokenMath.sol、interfaces/{IPool,IAToken}.sol。aToken入口为lib/aave-v3-origin/src/contracts/instances/ATokenInstance.sol；关键含protocol/tokenization/AToken.sol、protocol/tokenization/base/ScaledBalanceTokenBase.sol及IncentivizedERC20.sol、protocol/libraries/helpers/TokenMath.sol等。67个精确完整路径和原内容UTF8 SHA256逐项在JSON，未仅按同名文件匹配。

两者outputSelection分别指向各入口unit/contract。原settings中的remappings、metadata、libraries全部保留；Pool配置5个library地址，aToken配置6个，**配置不等于本轮已证明每个都实际链接/执行**，没有编译输出或逐library部署核验。路径含private只是包路径标签，不证明当时秘密；不含private也不证明何时公开。

按ABI解码provider构造声明：Pool的provider=2f39d218133afab8f2b819b1066c7e434ad94e9e、interestRateStrategy_=9ec6f08190dea04a54f8afc53db96134e5e3fdfb；aToken的pool=87870…、rewardsController=8164cc65827dcfe994ab23944cbc90e0aa80bfcb、treasury=464c71f6c2f760dda6093dcb91c24c39e5d6e18c。这是构造参数声明，不是独立部署交易/字节码/状态或这些地址角色的全链证明。

## metadata有/无什么

所有source-unit对象只有content，没有urls或keccak256字段；SwarmSource为空。观察到的settings.metadata只是编译输入选项，**没有独立compiler输出metadata.json、不可变来源URL或逐source的compiler哈希**。因此没有metadata来源链接可访问，本次也没有访问任何URL。JSON内自算SHA256仅是本地指纹，不能冒充Keccak、Git blob或compiler metadata hash。未将源码注释网址当成metadata来源凭证。

## 后续最小实质绑定

1. 明确chain1及这两个implementation地址，区别Pool/aToken proxy、同名实例和相似其他地址。ABI或名称相同只能证明接口相似。
2. 比源码unit内容、入口目标及编译全版本、optimizer、EVM、viaIR、remappings、metadata、library/构造声明。先区分逐字节、规范化文本及contract token相同，不默默删掉差异。能取完整包则完整比对；只读部分就只能通过部分机制身份，不把未读写成相同，也不为缩小的身份结论要求审整个协议生态。
3. 日期记录必须与同一地址/源码包对应，不能把旧时间与另一份今日文件拼成事前公开。Git作者日期、部署/升级日期和今天公开可读，分别不等于源码首次公开；内容寻址hash/URL也不自带公开时间。
4. **Sourcify的verifiedAt、import、createdAt及exact/full、partial、similar-match目前均未有官方语义文档或实际记录进入本子任务，全部UNKNOWN。** 后续先按对应官方版本解释字段，再看它标的是验证、导入、记录创建还是别的事件；不能看字段名猜成首次公开。匹配标签不可自动等于所有依赖、构造/immutable、编译或私人决策完全同一。
5. 若有内容/地址充分绑定、语义明确的官方有日期公开记录早于入场，可按其一手声明等级支持事前可用；仍不必宣称精确首次公开或独立当日网页存档。导入/当前查看时间不能无说明回填首次公开；也不因first-ever未知一律否定更早公开的其他证据。

BUSL-1.1/部分MIT、完整附加使用许可/ChangeDate仍分开核，公开验证不是无条件商用fork授权。本例既有数量和费用标差结论不因来源层待核而改写；即使来源时点补齐，也不能升级为完整投资者入场/退出规则事前公开、预测优势、容量或财富目标通过。
