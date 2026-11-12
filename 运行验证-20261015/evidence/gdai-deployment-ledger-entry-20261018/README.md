# gDAI 历史实现与现金流入口核验

当前结论（2026-10-18）：**取得并绑定了所选 Arbitrum gDAI 代理的初始 GToken 实现；仍未取得完整实际存赎与费用原账，未证实盈利或容量。** 这是具体源码与身份的研究进展，不是预测优势或财富进展。

本轮仅公开／本地资料研究。未运行或编译来源代码、模型、训练、回测、新策略／账户收益核算、链上调用、钱包连接、付款或交易。已完成的 2020 诊断及其他封存结果保持原结论。

## 本轮补齐了什么

| 层次 | 新证据 | 可以证明的范围 |
|---|---|---|
| 历史介绍 | Gains Network Medium 原介绍当前显示 2022-12-07，正文仍称未来上线 | 支持带历史日期的上线前机制介绍；没有独立 2022 页面快照，不能证明当年字节或精确首次发布时间 |
| 地址配置 | 固定 subgraph tree 的 Arbitrum config 与官网地址相同 | 配置字面匹配；该仓库与官网所链 GainsNetwork 账户的组织关联尚未独立绑定 |
| 部署代理 | 独立 Sourcify 既有验证记录，chain 42161／proxy d85E...B91B，block 49275523 | 提供商记录 creation/runtime exact_match，目标是 TransparentUpgradeableProxy；不是 GToken 全部业务代码 |
| 初始实现 | 代理构造参数指向 388277...8093；同链另一记录包含 GToken v6.3、block 49275518 | 取得初始实现源码与源文件 MIT 标记；不证明当前实现、完整升级史或 2022 年事前公开 |
| 现金流定义 | 初始实现与相关 ABI 有 Deposit／Withdraw／Reward 等字段 | 能确定要核哪些事件；尚未取得实际历史事件与完整现金账 |

代理及初始实现的 Sourcify 验证日期分别为 2024-08-08 11:46:49Z／10:35:36Z。这是提供商记录的验证时间，不是部署日期或最早公开日期。没有本地编译、重验证或独立节点运行时比对；exact_match 应表述为提供商的验证结论。

此前 owner 的指定 v6.1 Git 树检查及 root 08:14 配置核查中“实现未取得”，是当时的阶段快照；其后独立 Sourcify 两原件已补齐**初始**实现。历史记录不覆盖本页当前结论；当前与后续实现仍 UNKNOWN。

## 从初始代码看，钱怎样进出

见 root/GToken.initial.source.txt。这里只核函数允许的行为，不声称真实发生过对应交易。

- L721–730 distributeReward：调用者先实际转入资产，再增加每份奖励及累计奖励。没有角色限定；任何具备余额、授权并满足执行条件的调用者均可注入奖励。因此，**不能将全部 RewardDistributed 事件自动认定为平台交易手续费**，还要核调用者、资金源及当时交易收费逻辑。允许其他注资不等于已经发生注资，更不是漏洞或造假结论。
- L733–758 sendAssets：只允许 pnlHandler 调用，检查资产和单日盈亏限制后对外付款。它是赔付与风控通道，不保证金库盈利。
- L761–785 receiveAssets：资产实入后调整盈亏相关账户，同样没有该函数层面的角色限定。事件名及会计分类本身不能证明每笔实入都来自交易者亏损。
- L423–431 份额兑换价取决于累计奖励及纳入定价的盈亏；负的交易者盈亏形成缓冲，不能把所有对手亏损直接写成持有人利润。
- 提款受已有请求、对应 epoch 份额桶、feed 计数、额度与授权约束，最终才烧份额并转出资产。不能只据介绍文章把所有历史提款窗口固定成“头两天”。

收入机制仍是提供交易对手资金、承担赔付风险并分取费用。源码能复用的部分是账户、权限和风险约束的实现思路；本轮没有取得可复制的价格预测模型，也没有证明个人参与会有正收益。复制合约不会自动产生交易客户和付费需求，此项为商业机制推断。

## 查账时必须剔除的误判

完整 README 已按固定 blob 取得：totalAssetsDeposited／Withdrawn 也计入按估值换算的 gDAI 转入转出。转给另一个钱包可能没有任何 DAI 到账。它与官网 FAQ 的 Estimated Earnings 限制一致，因此这些汇总字段不能替代真实存入／赎回、DAI Transfer 和交易费用原件。

初始验证记录的五个选定事件 schema 与取得的 subgraph ABI 对应字段一致；这不证明全 ABI 一致、所有历史升级兼容、已获得日志或索引完整。config 中 graft 配置和 startBlock 也不能单独证明完整、独立的历史账。

## 当前仍缺的证据

1. 所选核账期间的实际部署版本及升级边界，不能将初始实现套到后续全部记录。
2. 一个连续的存入—持有／转移—最终赎回周期：实际资产和份额流、失败交易、费用付款人与网络费用；没有用汇总估值或其他钱包转账冒充结算。
3. 奖励入款的真实来源归因，以及净收益是否足以补偿赔付、退出和币价风险。
4. 扣费后的持续优势与资金容量。当前 Gerko 财富分母仍未确证，本轮没有缩小财富目标或把研究文件当实际财富。

若以后取得实际账户周期，先只核原件是否齐备。没有新增收益核算、回测或运行许可；不得自动执行新实验。

## 访问边界与后续收敛

官网所链 Arbiscan 目标地址页先在 web 不可读，随后正常公开 GET 一次明确 403，已停止该资源，没有改浏览器／身份／代理重取。Sourcify 是另一个独立验证资料来源，不是被拒页面的代理。仅请求既有 lookup 字段，没有 POST 验证任务或 proxyResolution。

本轮共 20 次保守计数的公开检索／读取／尝试：Owner 6（文章／检索／Git 元数据及 ABI），root 14（Arbiscan 两次工具／正常读取尝试、官网所链 Git 账户、两个固定 blob、独立来源发现及文档、两次 Sourcify lookup 等）。所有 HTTP／原生响应、UTC、hash、惰性源文件均保留。20 不是盈利样本数量。

Blockscout 由 Arbitrum 官方链信息页列为独立浏览器；本轮其首页原生读取为 0 行，未测试它的历史数据 API，也未确认费用或个人使用条件。不能写成“已免费取得完整链账”，不自动申请额度、连接钱包或购买服务。

**下一步仅沿同一合约，查独立公开历史索引能否提供原始日志和交易费用。** 先核免费范围、具体字段与版本；不读已拒 Arbiscan，不追 APY，不扩其他金库，不运行账户收益核算。只有估算汇总则停止该路径。此处没有需要用户提供账号或凭证的事项。

## 原始来源与日期

- [原介绍文章](https://medium.com/gains-network/introducing-gtoken-vaults-ea98f10a49d5)：当前页面日期 2022-12-07；读取 2026-10-18 UTC。未取得独立当年快照。
- [官网 Arbitrum 地址](https://docs.gains.trade/what-is-gains-network/contract-addresses/arbitrum-mainnet.md)：前一阶段已保存；未标可确认发表日期。
- [固定 subgraph Git 树](https://api.github.com/repos/GainsNetwork-org/gtoken-subgraph/git/trees/18ad6359dc210d2a6836f50743f288fdaf2c4ba5)：tree 身份不是 commit 日期；README／config／ABI blob 已单独固化。
- [Sourcify 代理记录](https://sourcify.dev/server/v2/contract/42161/0xd85E038593d7A098614721EaE955EC2022B9B91B?fields=sources,compilation,metadata,deployment,abi,creationBytecode.transformationValues)：读取 2026-10-18 08:17:55 UTC。
- [Sourcify 初始 GToken 记录](https://sourcify.dev/server/v2/contract/42161/0x38827724dd5abac83828151a6636f250ede58093?fields=sources,compilation,metadata,deployment,abi)：读取 2026-10-18 08:18:50 UTC。
- [Sourcify lookup 说明](https://docs.sourcify.dev/blog/apiv2-lookup-endpoints/)：2025-02-11；[当前 API 说明](https://docs.sourcify.dev/docs/api/) 已提示 v1 停用，未请求 v1 或执行验证任务。
- [Arbitrum 官方链信息](https://docs.arbitrum.io/chain-info)：读取 2026-10-18 UTC，页内未提供可确认的统一发表日期。

来源许可标记仅就取得的初始源码声明；不扩展成第三方数据许可、平台参与许可或所有后续版本许可。独立身份审阅已通过，范围见 review/identity-review.json；Owner 钱流静态审阅及 root 源码核读不等于实际运行、审计或真实账盈利证明。所有证据保留，无清理项。

