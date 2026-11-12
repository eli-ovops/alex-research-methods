# 追加四模块：净利公式、V3报价与上链保护边界

本补充接续最初8 GET报告，新增4个直接引用模块；未改变最初阶段读/未读记录。固定版本仍为`07cfb299b5143595f04a65366ea117ff13d485e6`。结论：公开程序确有报价减预估gas/授权费的阈值，但**用户最低净利T是链下判断，已读UniswapV3 callee参数并没有把T或T加实际gas设为链上最低利润**。

## 公式已核清的部分

`core/src/price.ts`46—56行：估计毛利G=q×M−q×P，其中q为代码计算的拟购抵押量、M为对应数量市场单位报价、P为拍卖approximateUnitPrice。q按auction debt、拍卖价、lot与chost约束计算（59—98行），部分舍入分支加入1.001补偿系数；不是已成交实付数量。`auctions.ts`111—115行：N=G−combinedSwapFeesDAI。

按前阶段已读`fees.ts`，combinedSwapFees由722651个固定swap gas量乘getGasPriceForUI结果，加缺少的0—2项授权估费（每项固定48356 gas量），换算DAI。该表达式没有从实际receipt取得gasUsed/effectiveGasPrice，也未把历史失败尝试、builder支付、RPC服务、运营费或其他不可见成本归入本笔净利。

keeper以N与用户T比较，授权后递归重新计算；README允许T为负。它是完整可读的过滤逻辑，不能读成强制扣所有实付费后盈利。

## UniswapV3的报价、费用与滑点

- `UniswapV3Callee.ts`的非auto-route路径根据抵押数量取得路径报价并除以数量成为M；`helpers/uniswapV3.ts`逐池将地址和`pool.fee`编码进路径，向Quoter的`quoteExactInput(encodedPools, collateralIntegerAmount)`请求给定数量输出。源码不是简单取静态中间价；它明确使用带池费率的数量相关报价接口。
- 从调用范围可知估计希望采用Quoter返回的换出量，不能把它再称完全忽略DEX费用/数量影响。但本轮未读Quoter实现、池状态、routeToPool或实际callee合约，未实测报价；不独立认证DEX费扣除数学或报价必等于成交。Auto-router的totalPriceAdjusted路径亦未深核。
- 没有在这些文件中看到另一次显式“闪贷/借款费”扣项。不能据此声称费用为零，或所有callee都需要/不需要闪贷；是否在具体兑换回调内隐含发生及金额UNKNOWN。
- 已读V3 calldata中没有用户指定的价格滑移比例或独立DEX amountOutMin字段；它有下述minProfit参数。不能把当前报价、29秒缓存或拍卖最大价当作完整DEX滑点保障。

## 上链参数究竟约束什么

`UniswapV3Callee.ts`31—40行把`minProfit`**硬编码为原始整数1**，随后编码`profitAddress, joinAdapterAddress, minProfit, encodedPoolPath, AddressZero`。用户T和预估/实际gas没有进入这个minProfit。不能将其写成用户最低DAI净利的链上保证。callee Solidity不在已读文件内，本轮不确认该1的资产单位、最终比较/回滚方式；尤其不能仅凭变量名保证任何实际利润。

前阶段`auctions.ts`的Clipper take参数含拍卖index、抵押数量、拍卖unitPrice上限、callee及上述data。最大拍卖价控制与DEX兑换后净利是两种不同约束。此调用本身不证明具备原子闪贷还款/最小收益保护，需确切callee部署代码另证。

`core/src/execute.ts`取得当前gas参数后直接调用合同，交tracker；仅对nonce已用错误递归重试。已读发送模块没有再次核N≥T或把T加入参数。tracker、gas参数函数及callee合约未读，因此不承诺最终确认、gas偏差、完整失败处理或执行安全。

## 收口

比“外部model私人不可见”更强的公开环节仍成立：市场选择、估计利润/费用、阈值、授权后重评和发单编排均有公开实现。不能升级的结论是：T获链上完整强制保障、全成本利润已核、历史真实盈利或未来低成本复制已证。成功后的console代币余额差仍未扣ETH费与失败费，亦无真实运行账被本轮取得。

四模块源路径：`core/src/price.ts`、`core/src/calleeFunctions/UniswapV3Callee.ts`、`core/src/calleeFunctions/helpers/uniswapV3.ts`、`core/src/execute.ts`；实际不可变blob GET、UTC、hash见`cost-formula-source-receipts.json`。新增4 GET已停止，不扩部署/性能诊断。仅静态文本阅读，没有执行文件中任何quote/交易调用，也无模型、回测、程序、适配器、策略、RPC/EVM、安装、账户、付款或外发；actualmodel/effort UNKNOWN，规则/路由沿用，未改其他Owner文件。
