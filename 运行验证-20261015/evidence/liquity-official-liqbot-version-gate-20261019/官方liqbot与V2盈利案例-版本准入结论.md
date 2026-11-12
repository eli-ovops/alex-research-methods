# 官方liqbot与V2盈利案例：版本准入结论

读取日期：2026-10-19 UTC。结论：**关闭官方 `liquity/liqbot` 固定版本作为既有2026年6月Liquity V2七次直接清算净正案例的复现代码候选。** 这是源码语义不相容与历史执行绑定缺失，不是撤销历史盈利，也不证明所有V2清算策略不可行。

## 本次新增的决定性证据

通过匿名GitHub REST GET固定当前master到commit `f4d0fdd67ff71be7aba1328dfd1d59d46a8dde95`、tree `c4fad56e2319403a03de6429b45beb4b1617fba7`。作者和提交日期均为2022-03-16T08:18:43Z；提交日期不能证明首次公开时间或历史分支映射。

本核查单元合计6次公开GET：ref、commit、LICENSE、package.json、src/index.ts、src/liquidation.ts，均HTTP200。四个文件的Contents API blob标识均与本地Git blob哈希相同；不是完整仓库或依赖审计。未访问配置或凭证，未安装或运行任何机器人/模型，未执行eth_call、交易或新收益核算。

|固定公开源码|实际内容|与既有V2案例的区别|
|---|---|---|
|src/index.ts L35–43|recoveryMode、全局名义抵押率及最低抵押率触发检查|不能直接替代V2按分支MCR、仓位状态和当前债务/价格的检查|
|src/liquidation.ts L38–41、63、83|按ascendingCollateralRatio取得仓位，抽取ownerAddress，再populate.liquidate(addresses)|既有V2接口按uint256 trove ID枚举/清算；V2原生SortedTroves按年利率排序，不是按抵押风险排序|
|src/liquidation.ts L123–141|读取collateralGasCompensation、lusdGasCompensation，输出ETH＋LUSD补偿|不能套用到已有V2案例的BOLD稳定池及WETH/分支抵押补偿规则|

公开固定来源：[清算控制源码](https://github.com/liquity/liqbot/blob/f4d0fdd67ff71be7aba1328dfd1d59d46a8dde95/src/liquidation.ts#L38)、[入口判断](https://github.com/liquity/liqbot/blob/f4d0fdd67ff71be7aba1328dfd1d59d46a8dde95/src/index.ts#L35)。本地原文及获取时间、URL、API原响应、SHA256分别在 `source-owner/`、`identity-owner/`。

V2旧原件复用而非本次新GET：`../complete-ledger-case-20261016/liquity-opportunity-inputs/protocol/contracts__src__SortedTroves.sol` L15–24明确按借款人年利率排序；同目录 `reused__src__Interfaces__ITroveManager.sol` L50–58有trove ID枚举和uint256[]清算入口。固定审计版本 `abe7cbfbd465fba3812282c51773455766a70e96`；[固定V2排序源码](https://github.com/liquity/bold/blob/abe7cbfbd465fba3812282c51773455766a70e96/contracts/src/SortedTroves.sol#L15)。其余V2状态、补偿、混合许可边界沿用该目录 `static-source-findings.md`，不冒称本次新核生产部署。

## 第一性原理：能借鉴什么，还不能声称什么

这类清算服务的收入来源是协议按规则支付的清算补偿，不要求先预测BTC或ETH下一根K线。能否赚钱仍取决于成功取得机会的补偿，是否超过所有成功/失败费用及竞争开支；公开触发条件并不等于个人已能及时捕获机会。

本次已读控制文件可学习的部分：读取状态和候选 → 估计补偿与最大网络费 → 费用过高则跳过 → 执行后按实际gas及minerCut显示该笔结果。见 `src/liquidation.ts` L89–103、123–141。**这里只静态读懂流程；没有执行、验证估计精度或测得个人收益。** `strategy.ts`的完整选单规则与`execution.ts`的补偿估计实现本单元未读，不称完整拆解。

成功分支中的profit日志也不等于完整策略账。本次已读文件的失败分支返回FAILURE，不能仅凭其成功日志核全体尝试成本；尚未审全仓库，亦不推断仓库其他位置必然没有记账功能。

LICENSE是MIT，允许相应软件使用/修改/分发时须保留通知且无担保；只绑定该仓库该文件的许可，不能泛化为V2核心、所有依赖或生产部署的许可结论。package依赖带版本范围，本轮没有安装、锁定或审计依赖。

## 保留的旧正事实与未补齐的缺口

已有Liquity V2 2026-06-03至06-06七次直接清算尝试，1成功6失败，所有已界定尝试的网络费纳入，限定ETH/WETH净数量增加 `0.039100539874301130` ETH-equivalent。这里只引用已有验收结论，**没有重算**；不等于美元ROI、完整实体利润或未来盈利概率。原件：`../complete-ledger-case-20261016/scope-audit/reviewer/previous-scope-audit-conclusion.md`。

本次关闭的是“找到官方旧bot就已经拿到这组V2盈利的完整复现程序”这一对应关系。仍缺同版本、事前公开的完整机会选择/发送/竞价规则及其与执行者的绑定；容量、未来样本外与个人完整成本仍未证。缺这些材料不能反过来抹去旧历史净增。

下一安全动作只限公开资料：查V2对应的公开keeper/清算实现及已验证执行合约，先核版本、许可、公开时间和调用身份，再决定是否有资格进入复用案例；**不改写旧bot、不部署、不运行、不把V1结果换成V2结果**。本次6次GET上限已用完，不追加读取。

## 本轮进度与目标边界

上一个对年度2026方案的复核答复没有新增市场结果或改变已固定方案，按目标进展记为NO_PROGRESS，不记作新实验。此前Liquity旧正事实复述同样没有新增绑定证据。

本次新增固定源码足以排除一个错误的复现候选，对下一行动有实质影响，记为 `PROGRESS_FIXED_PUBLIC_BOT_VERSION_MISMATCH_CANDIDATE_REJECTED`。没有新增独立盈利证据，财富目标仍未达成。仍有具体可做的只读来源核查，不构成无安全行动可做的阻断，也不存在经核验的在途外部等待。

年度2026方案继续保持未执行；不改变既有FAILED/NOT_SUPPORTED、AAPL或Issue85安排。Hypedexer邮件仍只是待批准草稿，没有发送。新资料与回执作为版本核查证据保留，无清理。
