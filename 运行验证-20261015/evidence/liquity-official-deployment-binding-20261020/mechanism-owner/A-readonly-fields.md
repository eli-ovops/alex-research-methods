# A 最小只读字段 → 已核入口映射

这是静态准备，未启动 A、未开发客户端、未发送任何链请求或执行 ABI/EVM。所有当前值均为 UNKNOWN。表中“需只读调用”指未来客户端以明确固定块执行 `eth_call`，不是本轮已经读取；`view` 仍需节点执行只读 EVM 才能取得链状态。

范围：Ethereum chain 1，TM `0x7bcb64B2c9206a5B699eD43363f6F98D4776Cf5A`。新 Sourcify 验证档案的 ABI/源码身份已核；依赖合约的具体部署 ABI/runtime 尚不能仅凭 TM 验证档案认证。

| A字段 | 精确入口 / 返回 | 来源与可用层级 | 未来读取要求与边界 |
|---|---|---|---|
| ID数量 | TM `getTroveIdsCount()` → `uint256` | 新Sourcify ABI直接确认；TM L218–220 | 需只读调用；记固定B/hash |
| ID全集分页 | TM `getTroveFromTroveIdsArray(uint256 _index)` → `uint256` | 新ABI；TM L222–223 | 同B读完index `0..N−1`；分页只是客户端分组，不是合约范围函数。检查唯一ID、返回数=N。跨B不能沿旧index续读，因为L1136–1150 swap-and-pop |
| 单仓状态 | TM `getTroveStatus(uint256 _troveId)` → `uint8`（`ITroveManager.Status`） | 新ABI；TM L1153–1155；已存接口L16–22枚举 nonExistent/active/closedByOwner/closedByLiquidation/zombie | 需同B只读调用；身份为uint256 ID，不是owner地址。返回枚举对应源码；不因存在ID就默认active |
| 单仓最新量 | TM `getLatestTroveData(uint256 _troveId)` → `trove` tuple | 新ABI；TM L955–1013 | 同B只读调用；按ABI字段序，不按旧raw Troves结构臆解 |
| latest tuple精确顺序 | `entireDebt, entireColl, redistBoldDebtGain, redistCollGain, accruedInterest, recordedDebt, annualInterestRate, weightedRecordedDebt, accruedBatchManagementFee, lastInterestRateAdjTime`，均uint256 | 新ABI十组件已读 | 包含利息/再分配/批管理费的债务口径；**不含price、status、MCR或可执行保证** |
| 条件ICR | TM `getCurrentICR(uint256 _troveId,uint256 _price)` → `uint256` | 新ABI；TM L943–946 | 参数price由调用方提供；即使调用成功也不是执行oracle验证，不可用任意市场报价替代协议路径 |
| 分支shutdown时间 | TM `shutdownTime()` → `uint256` | 新ABI；TM public L120，计息L1159–1167 | 同B只读调用；非零不自动等于batch清算禁用，须保留真实价格路径/计息影响 |
| SP地址 | TM `stabilityPool()` → `address` | 新ABI直接确认；构造L198 | 可在B读取并与官方表SP比较；地址相同不代替SP代码/接口绑定 |
| SortedTroves地址 | TM `sortedTroves()` → `address` | 新ABI直接确认 | 可核地址；该链表按利率，不替代完整ID数组/zombie |
| MCR | **TM没有 `MCR()`**；已存AddressesRegistry具体源L36声明`uint256 public immutable MCR`，可生成`MCR()`→uint256 | TM L36是internal immutable，L191在构造时从registry取值；registry源为旧固定审计版声明 | 从官方地址表registry `0x20f7c9ad66983f6523a0881d0f82406541417526`读取之前，须绑定该部署ABI/源码与构造关系。当前registry返回值与TM构造时MCR是否一致不能仅凭表声明；本轮未读实际值 |
| oracle合约地址 | **TM没有 `priceFeed()`或`addressesRegistry()` getter**；旧AddressesRegistry源L16 public `priceFeed`，对应getter `priceFeed()`→address | TM继承LiquityBase L20 internal priceFeed，构造L29从registry取；新TM ABI无上述两方法 | 官方表priceFeed `0xcc5f8102eb670c89a4a3c567c[REDACTED_PHONE]c24f`是地址声明。应绑定registry/部署关系与feed ABI，不能直接向TM假造这两个调用 |
| oracle模式/末次有效价 | feed `priceSource()`、`lastGoodPrice()` | 旧MainnetPriceFeedBase L16/19 public源声明；不是本次TM ABI | 须绑定具体feed部署ABI。模式枚举数值/实际值尚未在该部署ABI核定，不自行填0/1/2；同B读取后解释 |
| oracle主依赖/容忍陈旧/精度 | feed `ethUsdOracle()` → public Oracle结构getter，字段顺序 `aggregator, stalenessThreshold, decimals` | 旧MainnetPriceFeedBase L21–25、38–50源声明 | 须绑定feed ABI；aggregator地址不能从ETH/USD名称推定；不能把旧构造assert(decimals==8)写成当前实读 |
| oracle轮次/答复 | aggregator `latestRoundData()` → `roundId,answer,startedAt,updatedAt,answeredInRound`；另`decimals()` | 旧MainnetPriceFeedBase L46、86–93明确实际调用形状 | 还需精确aggregator及其ABI绑定；这些不是TM字段。成功/正answer/updatedAt及陈旧度由feed路径判定，block.timestamp取B；未来执行还会重新取价 |
| 执行取价路径 | feed `fetchPrice()` → `(uint256,bool)` | 旧WETHPriceFeed L19–44源；**非view，会更新lastGood/可能shutdown** | 不作为A最小无状态getter；本轮不调用。即便将来用只读eth_call模拟，也不等于真实入块执行价格或实际状态写入 |
| SP存量 | SP `getTotalBoldDeposits()` → `uint256` | 新TM源L433确实调用；旧IStabilityPool L76声明external view | SP精确部署ABI仍须绑定；不能向TM调用这个方法。full-SP-covered单仓还须按TM L431–436扣保留量，并与该候选同B entireDebt对应；批内每仓SP递减，不把同一余额重复分配 |

**本次最重要的调用清单纠偏：**只读公开字段不等于所有字段都在 TM ABI。`MCR/priceFeed/addressesRegistry` 均不能列为已证 TM getter。此前静态说明的“registry可读”只能指另一个具体registry合约，不能推成TM可直接读其registry。此表补充，不修改旧已封稿。

计数/分页时先固定B及hash，然后所有count/index/status/latest/SP/oracle输入都明确请求该B；不要依赖每个请求各自的latest。固定块请求支持方式、重组前后hash校验由Root请求方案确定；任何混块、缺页、错误或配额中断保留并标不完整，不以0补齐。MultiTroveGetter的排序批读不能消除zombie遗漏。HTTP批量是否支持、CU是否节省均未实测，不能以此表承诺免费额度扫描完整性。

## 输入指纹与实际覆盖

路径相对`运行验证-20261015/evidence/`；SHA256：

- `liquity-official-deployment-binding-20261020/root/sourcify-record.body`：`002c37f8674d4fef6fb721a70d1ad26af02ee4a678aba0ae4bdd27222265f202`；本轮仅读必要ABI方法投影、已提取TM关键行，不审proxyResolution/全编译输出。
- 同单元`mechanism-owner/sourcify-TroveManager.sol`：`8b18c9fe6480a8966eea792e5f23e4b1e1aff2536f16f3c9a9162ba39d818490`。
- 同单元`mechanism-owner/sourcify-Constants.sol`：`7c83831f63c06866ab9f5bdecb4197beb24b516879676a7145e87849584aeba3`；复用相关常量身份，不计算金额。
- `complete-ledger-case-20261016/liquity-opportunity-inputs/protocol/contracts__src__AddressesRegistry.sol`：`9bebcddd7b64dd68ea6195417ae2a0b398e8296c342d938307df5b39d3b5b34b`；定向L8–75。
- 同目录`reused__src__Interfaces__IStabilityPool.sol`：`e0254e31b726221f9ff1d41966baaad8c041f4147ee7058b61ca847cf0812e09`；L76。
- 同目录`reused__src__Dependencies__LiquityBase.sol`：`dfd09ff802a56daedc1ce0b0c6fe2d50fad6eb7a436cd28b05baa63b6d9fcec7`；L17–34。
- 同目录`contracts__src__PriceFeeds__MainnetPriceFeedBase.sol`：`e89b5c3872e31ffe10a87abee3bebc69a94c5e79df503989afc3d7936e0e82ca`；L11–124相关字段及校验，沿已读文本。
- 同目录`contracts__src__PriceFeeds__WETHPriceFeed.sol`：`a5fc82403d5a568c72d7bd9f3aee2dcd316b39f335fb6fa98c70cc1c3698e048`；沿已读L19–44。

来源文本/ABI只用于工程字段准备；0网络/链调用/ABI执行/观察/模型/金额计算/交易。实际model/effort/CPU/RSS UNKNOWN。
