# v.1.24.0发布标签下的规则：四文件历史版本核验

结论：本次真实按`v.1.24.0`读取的四份文件，与此前2026 HEAD读取版本逐字节相同。用户最低净利门槛、授权后重评、固定gas/授权估费、V3回调minProfit=1这些**同类规则存在于当前可读的该历史发布标签内容中**，无需将2026 HEAD文件直接回填给交易时点。但发布标签/元数据和当前tag内容不是当日独立网页存档，也不证明真实交易采用此bot或参数。

## 发布记录与版本身份

复用根已取得的`sidestream-releases-page1.original.json`及其读取回执。匹配release id253251218、tag_name=`v.1.24.0`、draft=false、prerelease=false；created_at2025-10-09T07:28:28Z，published_at2025-10-09T07:35:06Z，[官方release URL](https://github.com/sidestream-tech/unified-auctions-ui/releases/tag/v.1.24.0)。其发布元数据早于父任务所给2026-02-05目标交易日期。target_commitish为`main`，不是本轮独立解析的commit SHA。

新增4次GitHub contents GET均显式`?ref=v.1.24.0`，原始API回复保留html_url/download_url/git_url/sha；解码内容重算Git blob SHA一致。所属resolved commit本轮未另查，记UNKNOWN。不可变内容权威标识如下，真实GET和UTC/SHA256见`source-receipts.json`：

| 源路径 | 本次返回blob SHA | 与此前2026 HEAD同文件 |
|---|---|---|
| bot/README.md | `eb4ca6d1ae0f1e49519fc31ec35eda42490965e1` | 逐字节相同 |
| bot/src/keepers/collateral.ts | `2ac460133c2af5eb80b85ce3ae1e402f22c393f9` | 逐字节相同 |
| core/src/fees.ts | `b497a52059215c8ef7e467714b6e0bcba4894610` | 逐字节相同 |
| core/src/calleeFunctions/UniswapV3Callee.ts | `21a16b81b0bcece9be7f4b7eeab7d12fd61068ad` | 逐字节相同 |

这提供了官方历史release与同类规则的较强来源链索，但本轮没有tag不可移动证明、当日归档或当时下载包hash；不能独自证明四份准确字节自2025-10-09起从未改变或tag从未移动。

## 四份实际规则

- README34—40行：说明刷新默认60秒、用户指定最低净利（可为负）、默认按机会授权及可选预授权。参数定义公开，实际运营值未取得。
- keeper54—92行：检查gross不为负，再按transactionNetProfit与用户阈值比较；96—113行钱包/抵押品新授权后递归重新评估；随后调用bidWithCallee。执行后的DAI/USDS余额差只打印console，不是实际历史账，也不自动扣ETH费用。
- fees9—37、60—102行：swap固定722651 gas量、授权固定48356 gas量乘所取gas价并转换DAI；根据授权状态加相应估费。是预估成本规则，不是已付gas或失败费。
- V3 callee31—40行：`minProfit`仍为硬编码原始整数1，与profitAddress、joinAdapterAddress、编码路径及零地址一起编码；没有把用户最低DAI净利或其gas成本替换进这个值。

本轮没有读取该tag下auctions.ts、price.ts、Quoter/helper、执行模块、LICENSE或callee Solidity。因此此前2026版本中已核的完整gross/net公式、具体报价行为、许可、实际链上最小利润单位与回滚语义，不能仅凭这四文件逐字节相同就全部迁移为该tag的独立历史核验。这里只确认上述实际读到的四模块事实，不声称整个repo及依赖完全相同。

## 对目标交易的边界

父任务目标hash为`0x8c06abcb3a94762501ce7064e08616c1541e63b98f185b217403762f8c88cca4`；其日期、callee地址、付款及后续流量由根另核，本分支未读链账。

即便交易使用相同公开callee、甚至calldata相符，也不自动证明由Sidestream运营、由这个bot发送、由该tag运行，或事前锁定了某个盈利阈值/选择规则。任何人可调用公开入口。不能把release日前后关系升级成该运营者完整样本外策略；也不能把一笔DAI到账当扣全费用利润。

4 GET已收口，无新增metadata/tag解析GET，无运行任何文件内的quote或执行调用；0模型、回测、程序、RPC/EVM、策略、交易、安装、认证变更、账户、付款或外发。实际model/effort UNKNOWN；规则与路由沿用。仅写本Owner新子目录，其他历史报告和原件未改。
