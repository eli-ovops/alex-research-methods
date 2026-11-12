# 既有 WETH 部署绑定：可复用证据及剩余层级

结论：**目标 `0x7bcb64B2c9206a5B699eD43363f6F98D4776Cf5A` 已有官方固定版本地址文件、精确地址 Etherscan Exact Match 页面，以及两份关键源文件与审计终版逐字节一致的记录。旧档案盘点未定位该 TM 的 Sourcify 回执；随后 Root 在本单取得独立 Sourcify 原件，本 Owner 静态核到三项 exact_match、明确 ABI，且 TM/Constants 再次字节同一，详见§4。** 这些均不替代未来块的运行状态读取。

以下路径均相对 `运行验证-20261015/evidence/`。零联网、RPC、源码/ABI/EVM执行、模拟、模型、财务计算及交易；只写本 Owner 目录。

## 1. 精确部署与版本证据

| 已存原件 | 定位/版本 | 可以支持的层级 |
|---|---|---|
| `direct-protocol-case-20261016/root/current-official-addresses1.json` | L21–34：WETH、collToken、registry、SP、TM、priceFeed、GasPool；L11/14：collateralRegistry、MultiTroveGetter | 官方 GitHub 地址声明，不是当前链 getter 结果 |
| 同 root `license-and-address-read-receipts.json` | 第三条，2026-10-16T02:39:16.507524Z，`https://api.github.com/repos/liquity/bold/contents/contracts/addresses/1.json?ref=d262669ef3c4d37bf0544df3bb2624c07b8a5ee0` | 固定 commit `d262669ef3c4d37bf0544df3bb2624c07b8a5ee0` 的来源回执；本地地址文件5994B |
| 同 root `v2-contract-original.html`、`v2-contract-get-receipt.json` | URL `https://etherscan.io/address/0x7bcb64B2c9206a5B699eD43363f6F98D4776Cf5A`；2026-10-16T02:38:08.463364Z HTTP200、1256341B | 浏览器提供的该精确地址 Exact Match 验证声明及源包；并非本轮独立编译/链上 code 查询 |
| `direct-protocol-case-20261016/liquity-v2/extracted-verified-comparison.json`、`verified-source-review.md` | 45份编辑器源文件包；TM/Constants 两份原字节与旧 GitHub 源一致 | 两份关键源码身份可以复用，不扩成全部45份独立同版本证明；源包无 settings，不能称完整标准编译输入 |
| 同 root `audit-final-source-comparison.json`；同 liquity-v2 `verified-source-review.md`“当前补充” | 审计终版 `abe7cbfbd465fba3812282c51773455766a70e96`；TM/Constants 两份 SHA 完全一致 | 旧 GitHub、审计终版、目标验证页源包三端关键文件一致；审计收件日不是首次公开日 |
| 同 root `deployment-read-receipt.json`、`deployment-original.html` | 精确创建交易 `0x98f9d0232b889d1679c2685820c1cd2976f674b10c5173691a46988135f783ee`，页面记2025-05-19 09:19:47UTC | 历史部署页面与地址变更事件的来源；不是当前运行态或本轮独立重放 |

**重要纠偏：**`direct-protocol-case-20261016/liquity-v2/contracts__addresses__1.json` 是另一份旧部署地址配置，其 collateralRegistry/registry/SP/priceFeed/GasPool 均不同；不能按相同文件名套给本目标。应选上表的 `root/current-official-addresses1.json`，并保持版本标识。

本轮 Sourcify 查找限上述 direct-protocol 案、完整账案例的 liquity-opportunity-inputs、十月任务单元的 JSON/MD，以及已存 Sourcify/metadata 文件名盘点。唯一旧 tree 命中是 `contracts/sourcify-chains.json`、`contracts/sourcify-config.js` 两个仓库工具路径，**不是该地址的服务验证记录**。结论为“本次范围未定位”，不推全项目绝无该记录，更不推 Sourcify 未验证/无代码。没有目标 Sourcify 原件就没有可据其回执提供的历史查询 URL；本稿不虚构已请求 URL。

## 2. 可复用地址/源码/接口与仍未知

官方固定地址文件明确给出：

- registry `0x20f7c9ad66983f6523a0881d0f82406541417526`（L23）；
- ActivePool `0xeb5a8c825582965f1d84606e078620a84ab16afe`（L24）；
- SortedTroves `0xa25269e41bd072513849f2e64ad221e84f3063f4`（L28）；
- SP `0x5721cbbd64fc7ae3ef44a0a3f9a790a9264cf9bf`（L29）；
- priceFeed `0xcc5f8102eb670c89a4a3c567c[REDACTED_PHONE]c24f`（L33）；
- GasPool `0x7b9ab3de4036cae51f1fa4ec0a2c2fd606bcf921`（L34）；
- WETH `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2`（L22）；
- MultiTroveGetter `0xfa61db085510c64b83056db3a7acf3b6f631d235`（L14）。

可直接复用 TM/Constants、源包提取的接口/类型和事件字段作静态请求设计；`complete-ledger-case-20261016/liquity-opportunity-inputs/protocol/` 已保存固定审计 commit 的 MultiTroveGetter、SortedTroves、WETHPriceFeed、MainnetPriceFeedBase、AddressesRegistry，获取 URL/blob 核对见 `receipts.json`/`source-reuse-and-integrity.json`。接口/类型来自目标验证源包的复用，不扩称其每份都独立比对了审计 Git 版本。未定位到单独封存并完整验收的该 TM JSON ABI文件；可以复用已核函数/事件源声明，不将源码接口自动写成提供者当前 ABI认证。

仍未由这些文档证明：未来块的 runtime/hash/代理或依赖状态、当前 getter 与地址表完全一致、MCR/staleness/SP存量/priceSource/shutdown 的实际值、完整依赖编译配置与历史连续性、批量请求可达/大小/gas/CU/时效。这里是未来观测预检层，不是缺少协议说明；不用 H 私人实现作为前提。Root 本轮新读官方表与上述地址相符是另一条当前官方声明，本 Owner 未读其新原件，故不将该口头转述列为自己的独立读取。

## 3. 全集/批量读取已经研究到哪一步

已有 `liquity-opportunity-inputs/protocol/static-source-findings.md` L5–25、L33–37 明确：ID数组不是风险排序、跨块 swap-and-pop 的漏项风险、zombie、latest债务、MCR、SP与执行价格差异。因此不用再立“寻找全集读取方法”的研究。

`contracts__src__MultiTroveGetter.sol` L17–54 / L88–125 的批量方法按 SortedTroves 头尾偏移分页；L58–85获取 latest data但不返回status。`reused__src__Interfaces__IMultiTroveGetter.sol` L31–39仅列两个排序读取方法，没有 TroveIds 数组起点分页。TM L694–705 将 zombie 移出链表，故 MTG 只能作为 active 批读优化，不能冒充全集。TM L218–223 的 count/index 与同块固定身份仍是完整 ID 基线。HTTP batch 与合约批读不同，不能凭减少 HTTP 数就认定减少 CU。

本轮之前的 `liquity-personal-net-edge-minimal-plan-20261020/mechanism-owner/mechanism-plan.md` §2–5 已整理同块全集、按块刷新、接收时钟、oracle路径与影子记录字段。**这些是明确适配说明，尚不是已实现、已接入或已验证吞吐的适配器。** 下一步可复用现成字段/接口，不重复研究，更不把当前无运行回执写成实现失败。

输入 SHA 与本轮覆盖见 `input-hashes.tsv`。actual model/effort/CPU/RSS：UNKNOWN。

## 4. 本单新原件追加：Sourcify 独立记录已核

本节更新上文旧档盘点阶段的“未定位 Sourcify/独立 JSON ABI”状态，不回写旧单元。Root正常读取的完整原件 `../root/sourcify-record.body` 为1182544B，SHA256 `002c37f8674d4fef6fb721a70d1ad26af02ee4a678aba0ae4bdd27222265f202`。同目录 `sourcify-record.receipt.json` 记2026-10-20T02:04:08.143432Z至02:04:10.906296Z、HTTP200、一次请求、无重定向，真实 URL：

`https://sourcify.dev/server/v2/contract/1/0x7bcb64B2c9206a5B699eD43363f6F98D4776Cf5A?fields=all`

本 Owner只解析数据、未发请求：chainId=`1`、address精确相符；match/creationMatch/runtimeMatch均`exact_match`；verifiedAt=`2025-05-21T14:51:43Z`；编译记录solc`0.8.24+commit.e11b9ed9`、`src/TroveManager.sol:TroveManager`。deployment记录transactionHash=`0x98f9d0232b889d1679c2685820c1cd2976f674b10c5173691a46988135f783ee`、blockNumber=`22516078`、transactionIndex=`11`。这是验证服务已有记录，不是本次客户端独立编译、历史节点状态查询或首次公开时点证明。

按sources.content原字符串UTF-8提取（无补换行），本目录：

- `sourcify-TroveManager.sol` SHA `8b18c9fe6480a8966eea792e5f23e4b1e1aff2536f16f3c9a9162ba39d818490`；
- `sourcify-Constants.sol` SHA `7c83831f63c06866ab9f5bdecb4197beb24b516879676a7145e87849584aeba3`。

两者与旧 ExactMatch提取/审计终版逐字节哈希相同。新TM L417仍是public batch入口；L475把msg.sender传入补偿函数；L537–544仍分别从GasPool转WETH、由ActivePool发送抵押物给该调用者。没有新增白名单/资金垫还条件的源码差异。

原件 ABI 现已明确含 `getTroveIdsCount()`、`getTroveFromTroveIdsArray(uint256)`、`getLatestTroveData(uint256)` 三个view入口，以及 `batchLiquidateTroves(uint256[])` nonpayable入口；selected ABI、精确身份和部署字段保存在本目录 `sourcify-identity-and-selected-abi.json`。此项解决所需接口的验证档案来源，仍不证明当前块状态、提供者调用可达或扫描性能。

原件存在proxyResolution顶层字段，但本 Owner未读取/使用其值，也未使用runtimeBytecode来推当前节点状态；其余巨型编译输出未全文审读。仅两关键源和四个必要ABI入口完成本次对应核验，不扩称全部依赖、所有ABI或生产运行已经验收。
