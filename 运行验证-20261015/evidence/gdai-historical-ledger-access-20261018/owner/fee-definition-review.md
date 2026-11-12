# Arbitrum One：L1费用是否已含

结论：按Nitro普通交易回执语义，`gasUsed × effectiveGasPrice`是含L1 posting部分的费用；`gasUsedForL1`是其中以L2 gas单位表示的分项，不能另加。这里只核定义，不乘算本样本费用、求和或算PnL。

[Arbitrum官方Gas and fees](https://developer.arbitrum.io/how-arbitrum-works/deep-dives/gas-and-fees)实际正文L66–69说明parent费用由wei转换为child-chain gas；L187–190说明总费把执行与parent部分合并后按gas价格收费；L200–204解释receipt的`gasUsedForL1`单位。因此不能把`(gasUsed + gasUsedForL1) × effectiveGasPrice`当总费，也不能把同一posting部分再按其他字段扣一遍。

本地Withdraw、approval及funding回执确有`gasUsed`、`effectiveGasPrice`、`gasUsedForL1`与status。原始hex逐笔照录在JSON，未算费用。顶层交易gasPrice／maxFeePerGas可与receipt effectiveGasPrice不同，应以实际receipt为费用价，不能用gasLimit或块累计cumulativeGasUsed替代本笔gasUsed。

## 2023适用边界

官方当前Nitro设计说明与早2023普通type0x2回执结构支持上述总项／分项解释；未取得2023归档网页或复核历史ArbOS二进制，不把本次定义核查冒作钱包余额独立对账。当前页面的PGA、collectTips／ArbOS61等更新不能倒套该期。

[Inside Arbitrum Nitro](https://docs.arbitrum.io/how-arbitrum-works/inside-arbitrum-nitro)的官方搜索摘录亦给总费关系；实际open只返回L0–42，不称读完504行。[官方troubleshooting](https://docs.arbitrum.io/build-decentralized-apps/troubleshooting-building)搜索摘录另保留Classic历史价格重建例外，不将不同历史栈混为一致规则。文档发布日期／精确每次读取UTC未显示，标UNKNOWN；保存日及工具层级见JSON。

3个逻辑读取（1query＋2open，2次原生调用）已用完并停网。全部实际native返回保存为`fee-definition-native-captures.json`，不是HTTP原件；只采用官方结果，未用第三方匹配支撑结论。两本地输入和capture的SHA／字节在审阅JSON。

状态`PASS_LIMITED_NITRO_FEE_DEFINITION_L1_COMPONENT_NOT_ADDITIONAL_FEE`。actual model/effort UNKNOWN；未调用链／EVM、执行源码、算收益或换币、安装、连接账户、付款或交易。nonce40由根单独定位，本文件不认定其性质；完整费用覆盖和盈利仍未由本定义核查证明。完成停止。
