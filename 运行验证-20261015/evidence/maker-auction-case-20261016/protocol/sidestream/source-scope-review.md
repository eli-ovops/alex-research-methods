# Sidestream Unified Auctions bot：公开净利规则的实际范围

结论：这个公开bot比auction-keeper的外置model框架更完整：源码已串联市场报价/路由选择、估计毛利、预计交易及授权费、用户最低净利阈值、授权后重新评估和callee购买。它仍是**预估净利过滤程序**，不能仅凭阈值检查称实盘赚钱、所有成本闭合或2022年已部署该版本。

## 固定版本与许可

本次读取的`sidestream-tech/unified-auctions-ui` HEAD为`07cfb299b5143595f04a65366ea117ff13d485e6`，Git committer日期2026-08-25T13:19:33Z。固定tree未截断；6个小blob已取得并重算Git blob SHA及SHA256，实际GET、UTC、路径见`source-receipts.json`：

- [bot/README.md](https://github.com/sidestream-tech/unified-auctions-ui/blob/07cfb299b5143595f04a65366ea117ff13d485e6/bot/README.md)
- [LICENSE](https://github.com/sidestream-tech/unified-auctions-ui/blob/07cfb299b5143595f04a65366ea117ff13d485e6/LICENSE)
- [bot/src/keepers/collateral.ts](https://github.com/sidestream-tech/unified-auctions-ui/blob/07cfb299b5143595f04a65366ea117ff13d485e6/bot/src/keepers/collateral.ts)
- [core/src/auctions.ts](https://github.com/sidestream-tech/unified-auctions-ui/blob/07cfb299b5143595f04a65366ea117ff13d485e6/core/src/auctions.ts)
- [core/src/fees.ts](https://github.com/sidestream-tech/unified-auctions-ui/blob/07cfb299b5143595f04a65366ea117ff13d485e6/core/src/fees.ts)
- [core/src/calleeFunctions/index.ts](https://github.com/sidestream-tech/unified-auctions-ui/blob/07cfb299b5143595f04a65366ea117ff13d485e6/core/src/calleeFunctions/index.ts)

根已实读MIP/官方UI明确链接该repo和bot，这是本分支的来源关联输入，本次未重复浏览UI或MIP。LICENSE为GNU AGPL v3全文；本次未见另行or-later适用声明，不擅自扩为or-later。个人可依AGPL条款研究/复制，分发或提供相关网络服务时仍须遵守其条件；依赖、具体callee合约或外部API的许可未在本预算内完整审阅。

这些文件当前公开与Git日期不独自证明精确首次公开、2022实际部署、某笔交易所用版本或该版本事前锁定。根README、生产部署和暂停状态本轮未读取，均不声称当前服务可用；未读取任何实际env、钱包或私有配置。

## 实际公开决策链

| 环节 | 静态实现 | 已证范围与缺口 |
|---|---|---|
| 启用和机会范围 | bot README列网络、支持类型、抵押品白名单、刷新间隔（说明默认60秒）及最低净利参数；collateral keeper缺少有效阈值时不运行 | 参数名称及意义公开，实际运营阈值/白名单/网络/刷新配置UNKNOWN；README允许负阈值，所以不是强制不亏规则。未读实际配置。 |
| 报价与候选路由 | auctions.ts取得抵债所需数量的市场数据；callee-index按不同callee获取市场价，选择最高有效marketUnitPrice，NaN排后；缓存29秒 | 报价/路由框架公开，具体Uniswap/Curve/1inch helper未深入核验。auto-router路径默认useAutoRouter=false时会跳过，不把支持列表当全部实际启用。 |
| 预估利润 | auctions.ts104—115计算gross，net=gross−combinedSwapFeesDAI；所选market数据送给keeper | gross底层数学helper未读；可以核减费表达式，不能声称已核全部报价假设/价格冲击。 |
| gas与授权估费 | fees.ts以gasPrice×固定gas常数估算；swap722651、bid145438、auth48356、restart209182。按钱包/抵押品授权状态加0—2笔auth估费；授权查询异常时加两笔；ETH费用经报价换DAI | 有授权费考虑，明显强于只看折价。但不是每次真实gasUsed×effectiveGasPrice；getGasPriceForUI与ETH/DAI报价helper未读，不知道与最终支付的偏离。exchangeFee名称对应swap−bid gas差，不是单独核得的DEX协议费。 |
| 阈值及授权顺序 | keeper先查active/finished/market/gross，随后按用户净利门槛判断；通过后checkAndAuthorizeWallet/Collateral，若新授权则递归重新enrich/评估 | 可以确认授权后会重评，不保证授权后仍有可执行交易或赚回已付授权费。实际授权helper及可选启动预授权流程未读，不能泛称一切授权动作都必先通过该分支门槛。 |
| 发单与重复保护 | keeper同auction.id本地Set阻止重叠执行；auctions.ts355—379用所选callee和calldata调用Clipper take，传拍卖index/抵押量/当前unitPrice/callee/data；异常打印后清Set | 不需要外部私人model才能看到这条程序决策链。实际签名、交易提交/替换、失败重试、receipt与callee链上保护仍未全审计。 |
| 执行后显示 | keeper记录前后DAI VAT、ERC20 DAI、ERC20 USDS余额差并console输出 | 这是程序日志能力，未取得任何实际运行日志。它不自动给出ETH gas、失败费、外部运营成本或完整现金损益账。 |

最低净利判断还没有显式有限值检查：当前分支使用truthiness与toNumber()<threshold；若出现BigNumber NaN，比较语义不等于已明确拒绝。未运行程序或证明输入可达，不把这点宣称为已复现漏洞；它足以限制“任何输入都能保证净利”的表述。

## 闪贷、滑点、收入与风险

已读源码能追到Clipper take的callee回调入口，并列UniswapV2/V3、Curve、1inch等具体实现；**未读取具体callee及其合约**，所以不能把这条入口称为已核完整闪贷/flash-swap策略，不能确认借贷费用、DEX费用、amountOutMin/滑点、净利回滚保护、MEV/重排风险和全部执行步骤。bot阈值没有直接作为独立参数传入已读take入口；更深calldata/合约可能包含约束，本轮UNKNOWN，不能断言完全没有。

经济假设是以拍卖价格取得抵押品、通过选定市场兑换后足够支付拍卖成本并留差额，再覆盖估计链上费。它不是协议固定发放的无条件利息，真正正收益仍取决于报价是否可执行、成交/退出资产、实时gas、竞争与失败成本。不能拿市场报价减拍卖价等同实际利润；本轮不运行模型/策略或人为造价差。

bot README含Goerli上重启拍卖并检查日志的测试步骤，这是开发说明，不能当实盘获利记录。已读文件没有固定运营地址、可绑定本版本的历史实际tx、完整持仓/费用数据包或审计利润下载入口；console打印tx hash能力不等于已经有记录。真实账由根另核，不在此扩查。

## 比auction-keeper多公开了什么

这里已经有可阅读的市场选择与减费阈值程序，而非只提供外部model接口；个人可依法复用这部分报价/候选选择、估费、授权后重评和交易编排结构。仍需确认实际参数、callee合约/费用与滑点保护、历史代码版本对真实tx的绑定，及真实收支原件。缺这些不能称现成稳定获利系统，但也不应再将“全部定价程序私人不可见”套给本已公开的范围。

8次公开GET（HEAD、tree、6blob）已收口。无模型、回测、程序/适配器/策略执行、RPC/EVM、依赖安装、账户连接、凭证读取、交易、付款或外发。实际model/effort UNKNOWN，沿用PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4；未改root/reviewer、旧报告及FAILED/封存记录。
