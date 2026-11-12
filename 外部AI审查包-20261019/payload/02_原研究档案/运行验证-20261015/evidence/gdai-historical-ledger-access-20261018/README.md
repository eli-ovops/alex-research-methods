# gDAI 固定案例：历史原账入口与成本边界

读取日：2026-10-18 UTC。结论：已取得实际存入、申请、赎回及相关资产转账原件，并补齐已观察区间内的发送交易序号；**尚未接纳为扣费盈利案例，也没有新增可证明的财富进展**。

## 本轮新增证据

- Arbitrum 官方公共 RPC 正常返回既有历史交易、回执和事件。初始部署交易与上轮 Sourcify 档案相符。这只是公开历史数据读取，没有执行合约、模型、策略或交易。
- 在查看金额前，固定从部署块 49275523 起的查询窗口，按 block/transactionIndex/logIndex 选择最早返回的 Withdraw。首次 12M 区间因明确 10M 上限返回错误；在没有候选结果时保存错误并一次改正。有效窗口为 49275523—59275522，返回 146 条 Withdraw，之后没有替换样本。
- 固定赎回交易：[ea25cb…1465c](https://arbitrum.blockscout.com/tx/0xea25cb68567595cb126982947271f4b74f1376479150b6b040a85463f314465c)，owner 为 `0x4250f21a947ba6fed45cfcea4da15c30ad925a90`。存入、申请、铸造与销毁的份额原量一致；存赎资产金额各与同笔实际 Transfer 对应。
- 旧状态定位方法返回 `historical state ... is not available` 后停止。通过独立 Blockscout 正常公开网页定位缺失 hash，再取官方 RPC 原件，确认 nonce40 是成功的其他合约交易；该回执没有所选本金资产的 Transfer，不足以证明经济上无关。
- 同一发送地址 nonce36—44 的九笔完整 transaction/receipt 已对应。它是有限区间的发送记录连续性，不是该实体全账、完整交易策略或全部成本证明。

## 为什么仍不能把存赎差额叫净利润

公开网页在入金前标出 borrow、赎回后标出 repay。原始回执确认同资产从资金池体系转入，随后存入金库；赎回后同资产向资金池体系转出。借贷接口的字段定义已取得，但未独立绑定当时资金池部署代码和全部负债，因此暂保留为强借贷线索。

| 顺序 | 已保留原始记录 | 仍需确认 |
|---|---|---|
| nonce36 | 外部资金池体系向该地址转入本金资产 | 借贷完整身份、初始负债及抵押资金边界 |
| nonce37—39 | 授权、存入、申请赎回 | 相关费用和时间边界 |
| nonce40 | 其他合约成功交易及费用字段 | 与该案例的经济关联、费用是否应分摊 |
| nonce41 | 赎回、份额销毁、资产到账 | 不能用到账总额当利润 |
| nonce42—44 | 授权、向资金池体系返还资产、其他抵押资产退出线索 | 利息、抵押资产成本/收益、完整退出边界 |

未在本阶段计算差额、收益率、利息金额、gas 合计或 ETH/DAI 换算。资产原量与九笔列表见 原始字段汇总（未随包收录；原相对路径：`运行验证-20261015/evidence/gdai-historical-ledger-access-20261018/root/same-case-nonce-gap-and-funding-cost-boundary.json`）。代币精度及同期汇价未作为既定前提。

## 费用口径

Arbitrum 官方 Nitro 设计文档支持：普通交易的实际收费使用回执 `gasUsed × effectiveGasPrice`；`gasUsedForL1` 是其中的 L1 分项，不能重复加算。不得用 gasLimit 或最高出价替代实际费用。当前文档含后来的 tip/ArbOS 规则；没有把新规则倒套到 2023，也没有取得当年归档文档或余额差核对。见 字段审阅（未随包收录；原相对路径：`运行验证-20261015/evidence/gdai-historical-ledger-access-20261018/owner/fee-definition-review.md`） 与其原生来源快照。

## 来源与证据限度

- [Arbitrum 官方链资料](https://docs.arbitrum.io/chain-info)：确认公共端点与独立浏览器入口；本轮成功读取不代表商业 SLA 或全面数据再授权。
- [Blockscout API 官方说明](https://docs.blockscout.com/devs/apis)、[PRO 套餐](https://docs.blockscout.com/devs/pro-api)：当前文档称旧实例 API 弃用，PRO 需账号/key；本轮未注册或开 key。普通公开网页实际可读，与 PRO API 权限分开。
- [Ethereum JSON-RPC 参考](https://ethereum.org/developers/docs/apis/json-rpc/)：历史交易与回执读取字段。只使用白名单只读方法，没有运行文档中的交易或合约示例
- [Arbitrum Gas and fees](https://developer.arbitrum.io/how-arbitrum-works/deep-dives/gas-and-fees)：总费与 L1 分项定义；文档具体发布日 UNKNOWN。
- [Aave IPool 接口](https://raw.githubusercontent.com/aave/aave-v3-core/master/contracts/interfaces/IPool.sol)：Borrow/Repay 字段定义。读取的是当前公开文件，不是当时部署版本身份或事前代码公开证明。
- Blockscout UI 是派生索引；真正的 nonce、status、资产转账与费用字段以保存的 RPC 原件为准。网页相对年龄和当前美元价格没有用于历史估值。
- 单一提供商返回结果、NFT 窗口内空数组及事件名均有边界。933 条 RewardDistributed 不能自动全归为交易费；初始源码允许外部出资，真实付款方与资金来源仍需核实。

## 当前研究决定

保留此固定样本，继续只读核清借贷/抵押与费用边界；不切换到更漂亮的赢家。若完整净额可核，也只得到一笔历史结算证据；仍需事前规则、独立重复表现、尾部风险和容量证据，才可能支持低成本复制。该公开金库的收费和风险承担机制不是 XTX 的私人价格预测模型。

本轮未运行模型、训练、策略、回测、EVM 或交易；未连接钱包/账户、读凭证、安装、付费、发送消息或改变既有实验结论。独立原件验收结果由同目录 root-acceptance.json 记录。
