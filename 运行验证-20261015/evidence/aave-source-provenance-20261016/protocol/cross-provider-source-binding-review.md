# 当前跨提供商源码身份独审

审阅 UTC：2026-10-16T09:47:01.985660+00:00。限定结论：**PASS：当前返回的67个源码单元、ABI与构造参数声明跨源对应；不通过本层推导首次公开或独立字节码验证。**

仅本地被动读取、结构比较、UTF-8 SHA256；0联网/编译/EVM/外来代码执行/模型/回测/交易。实际 model/effort：UNKNOWN；继承设置未改。

| 对象 | 源单元 | 路径集合与全部原文 | ABI项/有序结构 | 构造参数原字符串 | Sourcify verifiedAt（平台记录） |
|---|---:|---|---|---|---|
| pool | 42 | 精确相同 | 96 / 相同 | 精确相同 | 2026-05-29T09:33:00Z |
| atoken | 25 | 精确相同 | 56 / 相同 | 精确相同 | 2026-03-20T17:12:50Z |

## 会改变结论的差异

1. 两份 `compilation.compilerSettings` 与 Routescan 标准输入都仅差缺少 `outputSelection`；完整对象并非相同。公共设置均为 optimizer enabled=true/runs=200、cancun、viaIR=false、bytecodeHash=none/appendCBOR=true/useLiteralContent=false。完整原值与逐项差异保存在JSON，未删注释、规范化路径或改写源码。
2. `metadata.settings`是另一组实际返回：增加 compilationTarget；缺 outputSelection、viaIR、metadata.appendCBOR/useLiteralContent；libraries从嵌套映射变为FQN映射，aToken地址大小写也不同；remappings顺序及全局前导冒号有差异。这里只记录表示差异，未编译证明其等价。Routescan compiler raw有前导v，Sourcify没有；数值版本均0.8.27+commit.40a35a09。
3. Pool的五项 library transformation 使用实际逻辑单元FQN，输入settings却以PoolInstance.sol作为五个库的命名空间。按库名逐一对应后地址字节一致，但键并不相同。aToken输入有六项库配置，creation transformation未返回libraries字段；不能据此宣称六库均实际链接，也不能以未返回字段证明未链接。

## 身份与时间边界

Pool目标为 `lib/aave-v3-origin-private/src/contracts/instances/PoolInstance.sol:PoolInstance`；aToken为 `lib/aave-v3-origin/src/contracts/instances/ATokenInstance.sol:ATokenInstance`。二者metadata.compilationTarget与compilation目标一致；private路径名本身不证明历史保密。全部67个metadata.source声明的路径也与当前源码集合相同，其Keccak/存储URLs仅记录，未访问或独立验证。

两份match、creationMatch、runtimeMatch均为 `match`，不是 `exact_match`。当前读取的官方说明区分两等级；本报告不把较低等级改称精确编译匹配。所选返回creationBytecode只有transformationValues，没有实际链上/重编字节码；deployment及构造参数均是平台声明对应，非本次独立链上部署验证。

两平台ABI有序数据完全一致；Pool构造参数为2个address，aToken为3个address，逐词保留在JSON。ProviderProxy=0不替代独立编译或字节码身份检查。

verifiedAt时间数值均早于2026-08-18T03:15:11Z入场；这里仅称平台记录。当前返回字节与该历史字段的关联语义、回填/导入/替换可能性，以及首次公开/事前可获取，等待根分支官方实现核验，本层均不单独判PASS。今日跨源内容一致不等于两个独立历史存档，也不推出完整投资决策公开、个人净利或容量。

## 来源与输入指纹

- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-source-provenance-20261016/root/lookup-read-receipts.json`：ba96d412eabaea5b2b97d0408316ee7e7b4ef6f592e3c87172e40bf762617703（1528 bytes）
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-usdc-cashflow-baseline-20261016/root/period-implementation-source-read-receipts.json`：51bcc9c1c4df5e6d0c1fc49e4146ddd036f4271d4409fb4c146b9453744617c2（1391 bytes）
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-source-provenance-20261016/root/fixed-scope-before-requests.json`：a1f7c6c5115c986562ba65cef92c291348d8d2954aefa5571b006d444693a65f（3320 bytes）
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-usdc-large-cycle-cost-20261016/root/next-source-provenance-scope-before-requests.json`：a1f7c6c5115c986562ba65cef92c291348d8d2954aefa5571b006d444693a65f（3320 bytes）
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-source-provenance-20261016/root/official-discovery-and-docs-native.json`：b10cb81e059e10a4d8072b21915e54a2e9f1c09382a1ab5aa2a4dc7c29cfa2c1（61530 bytes）
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-source-provenance-20261016/root/pool-sourcify-lookup.original.json`：625f3c6bd2e1bbe2338941406518ca9daaaa06b3e2ca414a022bd3d10cca3077（430506 bytes）
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-usdc-cashflow-baseline-20261016/root/pool-period-implementation-source.original.json`：574ae497cceed8ac0f3c9ee67c74ebbc4e50f64002af4e8d571b837d8cf3f239（394450 bytes）
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-source-provenance-20261016/root/atoken-sourcify-lookup.original.json`：a1e90b5869ac79dd6acbb3d4ce146157d99b3163b0b215afa973965ebe07e638（223762 bytes）
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-usdc-cashflow-baseline-20261016/root/atoken-period-implementation-source.original.json`：9977756ee822528f48d5b042293ab3244c6af2f4dd68cf9c6fa3efa630068572（208123 bytes）

配套逐单元/完整settings差异JSON SHA256：`0fd6d10e136481aba6cd34a60ec2441ec2def319c2822d5a796188d07c99b63c`。原件、旧审阅均未改。

## 后续官方时间/等级语义交叉审（保留前段当时边界）

0联网补读根新存固定commit `a0bab83b54a87f6a4b6aa04a5cdf6dbe08f13189`源码与回执：database-util行453—454实际把GET的verified_at选择为`verified_contracts.created_at`；database行392—419可将sourcify_matches指针更新到更优verified_contract，注释明确旧verified_contracts不删。这支持当前关联验证记录的创建时间早于入场；不是首次网页公开时间，亦未独立绑定该固定commit就是当时线上运行版本。不能由当前source返回加日期，直接证明同字节自该时持续公开可取。

官方Exact Match vs Match页L89—92将match界定为除metadata hash等差异的字节码对应，仍排除libraries/immutables；因此可据平台声明说功能匹配，不得改称精确原始源码或独立编译通过。两家当前67份原文精确一致是本次直接比较所得，和平台match等级是不同层。事前平台验证记录得到补强；首次公开/历史实际公开服务仍未独证，不追加投资策略或收益结论。

新增输入指纹：
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-source-provenance-20261016/root/sourcify-database-util.original.ts`：9523332932286c44ed73f27e83b5ae440559ddab2eb77a22d8259309932ec32e（38858 bytes）
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-source-provenance-20261016/root/sourcify-database.original.ts`：4d4a2b067425aa39e72f79460e7fbd5d8c78f6ac07155b650e2f5df2359bfa56（36300 bytes）
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-source-provenance-20261016/root/semantics-fixed-source-receipts.json`：68b4741f4f1cb50a266eec57e80f86f22cd6d3342c544666cefa991e06d12e0c（4614 bytes）
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/aave-source-provenance-20261016/root/exact-match-doc-native-read.json`：1a9318d6610350d2c70aaf97cf27c1faffdf711fce8024073c484c67574e1e86（7703 bytes）

更新后JSON SHA256：`38d588f3e86840fb74d76962c63ed07a34de6dec5d08039911c99ff5aae7fddc`。
