# Liquity V2已验证源码身份：静态独立复核

复核日期：2026-10-16。范围仅根保存HTML、既存GitHub源码及commit回执；没有联网、执行网页或下载的项目代码、编译、模型、回测、交易。没有汇总或复核主任务16笔交易。

## 结论

在所提供Etherscan Exact Match页面的源码包内，`src/TroveManager.sol`、`src/Dependencies/Constants.sol`与已保存的GitHub pre-event版本均**字节完全相同**。不是删除空格、换行或注释后才相同。由此可以将这两份静态源码身份与该页面展示的已验证合约源码对应起来。

不能由此单独证明：页面/链上验证机构没有错误、完整45文件都与某Git commit相同、字节码被本轮独立复编译核验、首次公开时点，或所有成功交易的收益已闭合。这些层次没有被替代。

## 输入和安全解析

HTML输入：`../root/v2-contract-original.html`，地址标题为`0x7bcb64B2c9206a5B699eD43363f6F98D4776Cf5A`的Liquity V2 WETH TroveManager。HTML SHA256：见`extracted-verified-comparison.json`。

安全解析方法：定位`var editor_contractJsonData`字符串字面量；按显式白名单规则解析字符串转义，再用标准`json.loads`解析数据。页面中的`\``按字面反引号处理，没有执行模板字符串、脚本、eval或Function。初次严格解析因该转义停止；只在检查实际上下文并查LOCAL_BLOCKERS后支持此明确转义，再成功解析。未运行任何HTML或源码。

解析对象只有`language`与`sources`，共45份源文件，**没有settings字段**。输出虽然名为`extracted-verified-standard-input.json`，实质是页面编辑器源文件包，不能声称它独立保存了全部标准编译配置。页面另外展示solc `v0.8.24+commit.e11b9ed9`、优化200 runs、EVM Cancun及Exact Match标签；本轮未编译。

## 精确比较结果

| 文件 | 页面解出UTF-8字节 | 既存GitHub字节 | 精确相同 | SHA256（两端一致） |
|---|---:|---:|---|---|
|TroveManager.sol|89534|89534|是|8b18c9fe6480a8966eea792e5f23e4b1e1aff2536f16f3c9a9162ba39d818490|
|Constants.sol|3687|3687|是|7c83831f63c06866ab9f5bdecb4197beb24b516879676a7145e87849584aeba3|

比较对象为`contracts__src__TroveManager.sol`与`contracts__src__Dependencies__Constants.sol`。原文件未改。另测仅统一CRLF/LF、统一尾部换行也相同，但精确相同优先，不依赖规范化结论。

输出：`extracted-verified-TroveManager.sol`、`extracted-verified-Constants.sol`、`extracted-verified-standard-input.json`、`extracted-verified-comparison.json`。前两份为HTML源包中content字段解码后的原始UTF-8源文本。

## 调用权限与真实补偿规则

解出TroveManager417行`batchLiquidateTroves(uint256[] memory)`为public，无owner/角色/清算者白名单修饰或调用者鉴权。空数组失败；遍历时要求Trove处于active/zombie且ICR<MCR；没有任何债务被清算则441行revert NothingToLiquidate。补偿在475行之后向msg.sender转出，失败不会保留补偿。

这证明所读执行入口无需清算者协议特权，也无需为调用本身先部署私人bot；不证明特定From地址是无代码/无委托EOA，也不证明所传ID能被清算。寻找机会、事务打包、gas设置及竞争仍是调用者行为，本次未审完整运行选择策略。

Constants第13行固定补偿为每个成功清算Trove `0.0375 ether`，以WETH从GasPool转出；第40-41行可变补偿除数200、上限2个抵押资产单位。关键是TroveManager375行传给计算器的参数为`collSPPortion`：只有稳定池抵销债务对应的抵押部分；redistribution段没有再计算可变补偿。稳定池不足时，不能无条件以全部Trove抵押物乘0.5%。

_sendGasCompensation537-545行分别`WETH.transferFrom(gasPoolAddress,liquidator,eth)`与`ActivePool.sendColl(liquidator,coll)`。WETH分支两项都是WETH；不是native ETH自动到账，不能混同V1的200LUSD。实际数量仍以每笔成功事件、Transfer/trace及余额为准，不能用公式代替到账证据。

## 许可

两份解出源文本第一行均`SPDX-License-Identifier: BUSL-1.1`，与GitHub源码完全一致。既存`contracts__LICENSE`表明Liquity V2核心代码是Business Source License1.1，许可非生产复制/修改/研究，2027-09-01 Change Date及GPLv2-or-later转换，Additional Use Grant另列。这里不能写成当前MIT/GPL全面开源授权。Additional Use Grant本轮未读取，不对生产部署/衍生项目权利作判断。

公开合约入口的调用权限、源码复制许可与复刻完整生产系统属于不同问题；不能因为BUSL就否认代码存在公开普通入口，也不能因为入口public就推断任意生产复制无限授权。

## 时间身份：能够与不能够证明

既存`preevent-source-commit.json`记录commit `cc2a420067e47cafc1b1b1309045b341f9ced1b1`、committer日期2025-05-13T14:56:19Z。当前数据证明：已保存、标为此GitHub版本的两份源码，与目标地址Etherscan页面的对应源码字节相同；其记录的提交日期早于本次候选2026-02-05交易。

**Git作者/committer时间戳由提交者可设置；今天能读取该commit，不足以独立证明当日已经向公众发布。** 本轮没有带可靠公开时间的当时发行公告、第三方存档、首次verification timestamp、历史签名发布或不可变预注册原件。因此严格“首次公开时点”和“整个具体选择策略结果前公开冻结”仍UNKNOWN。

本轮也没有编译45份源文件、核部署creation bytecode/constructor参数、或从节点独立读取runtime bytecode。Etherscan Exact Match是页面提供的验证声明；本轮确证的是页面源包与既存源文件的身份，不能把它改写为本轮独立完成了字节码验证。

## 收尾

源码文件身份比较通过，调用入口及补偿实现可以按解出源码具体解释；首次公开时点、完整运行策略预锁及逐笔净盈利仍不由此证明。本报告不汇总主任务16笔、不改任何其他文件。所有新提取文件为研究证据保留。


## 当前补充：独立审计终版与官方上线记录（2026-10-16追加）

本节保留上文当时的证据状态，不回写或抹去旧判断。追加输入来自主任务已保存的审计PDF、第5页图、审计终版两份源码、官方上线HTML及获取回执。本次无联网、网页执行、编译、模型或回测。

### 审计终版源码与部署验证源码再次逐字节相同

我未仅采用主任务comparison布尔值，而是直接读取`../root/audit-final-TroveManager.sol`与`../root/audit-final-Constants.sol`字节，分别与本分支从Etherscan源包抽出的两个文件比较：

- TroveManager：89534字节，双方SHA256 `8b18c9fe6480a8966eea792e5f23e4b1e1aff2536f16f3c9a9162ba39d818490`，`bytes == bytes`为true。
- Constants：3687字节，双方SHA256 `7c83831f63c06866ab9f5bdecb4197beb24b516879676a7145e87849584aeba3`，`bytes == bytes`为true。

所以现在对这两份文件有三端一致链：此前GitHub版本 → 第三方审计列明的最终commit版本 → 目标地址Etherscan Exact Match源包。仍未升级为本轮独立编译字节码或全部依赖45文件身份比较。

### 第三方审计日期的准确含义

审计方原始PDF：
https://reports.chainsecurity.com/Liquity/ChainSecurity_Liquity_Bold_Audit.pdf

已保存文件`../root/chainsecurity-bold-audit-20250514.pdf`的SHA256为`65b618db460b537b11f0a6a50adc0144793818ebb61c3e5b86963e735b42fd0c`，独立重算与获取回执一致。我实读提供的`audit-page5.png`表格：Final Version列为2025-05-14，commit `abe7cbfbd465fba3812282c51773455766a70e96`。该页说明表中日期是审计方**收到相关代码版本**的日期，不能改写为GitHub首次公开日期、PDF首次发布日期或部署日期。

表格还列出更早的不同版本；这些不能当成与最终源码逐字相同的证明。本次只对上述Final Version关联的两份源文件实比，并确认页面审计范围清单包含TroveManager及Constants。

固定最终源链接：
https://github.com/liquity/bold/blob/abe7cbfbd465fba3812282c51773455766a70e96/contracts/src/TroveManager.sol
https://github.com/liquity/bold/blob/abe7cbfbd465fba3812282c51773455766a70e96/contracts/src/Dependencies/Constants.sol

### 官方2025-05-19上线记录支持公开披露，但不是当日抓取存档

官方原页面：
https://www.liquity.org/blog/liquity-v2-is-live

我用静态HTML解析读取已保存页面正文，确认文章署名Sam Lekhak、正文日期May19,2025、标题Liquity V2 is LIVE，且含`https://github.com/liquity/bold/`等仓库链接。没有执行HTML的脚本。文件SHA256 `5666d8c591b4b341daecf935b31090534d052cea7dc2bc4c2f714866f84c4e6e`，独立重算与获取回执一致。获取回执为2026-10-16T02:47:07.215402Z。

它是今天从官方域名取得、载明2025上线日期的原始记录，**不是2025-05-19当日的第三方网页存档**；文中通用GitHub链接也不是对每个文件首次公开时刻的时间戳。站点当前导航的再上线提示不等于该旧文章的历史内容全部失效，亦不把导航日期混入正文日期。

### 更新后的实质判断

相比只有可由提交者设置的Git时间，现在增加了独立审计方列明最终版本及收到日期、官方带日期上线文章和源码仓库公开入口，且最终版本关键文件与目标验证源逐字节一致。**这些相互衔接的原始记录共同支持：清算机制在2026年结果出现前已经存在，并有公开披露记录。** 不宜继续笼统说“事前机制只有当前代码、完全没有公开时间证据”。

结论同时保持精确边界：

- 可以支持“有充分历史记录支撑的事前公开协议机制”，而非只有事后私人bot自述。
- 不能给出精确、独立确认的first-public timestamp，也不能将2025-05-14审计收件日称为首次公开时间。
- 不能由通用协议代码公开，推断某个账户的Trove选择、提交时机、gas策略、私有路由或完整执行策略事前已预锁；这些仍UNKNOWN。
- 两份关键源码相同不等于部署、许可、净盈利、全策略长期表现全部通过。BUSL及Additional Use Grant边界、每笔成功/失败的到账与费用、全部账户记录仍按各自原件层验证；本节不代主任务汇总16笔。

该补充使“协议机制早于结果、并有公开披露”的证据明显增强，精确首次公开时点与私人执行策略预锁仍未闭合。审阅范围内没有发现需要推翻主任务所述三端源文件一致性的实质问题。
