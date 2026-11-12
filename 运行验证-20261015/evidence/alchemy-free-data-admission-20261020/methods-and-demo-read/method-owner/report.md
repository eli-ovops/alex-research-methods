# Ethereum两方法与官方HTTP demo：参数已补，finalized/null展开仍缺

2026-10-19 UTC，方法Owner文档4动作已收口；**未调用RPC/demo或执行示例。** 本单元读的是`methods-and-demo-read/root/protocol.json`，旧总单元协议只作背景，不能替代本次界限。

## 提供者实际正文

1. [eth_chainId Ethereum方法页](https://www.alchemy.com/docs/chains/ethereum/ethereum-api-endpoints/eth-chain-id?explorer=true)：L78写CU0、Throughput CU5；L80/93定义返回十六进制chain ID。L99完整示例为HTTP POST、Content-Type application/json、JSON-RPC2.0/id/method，**没有params字段**；L105示例result为`0x1`。因此精确可复用的是文档的省略params形式，不能从这里假装取得另一种params对象的完整规范。其他链页面模板不作为Ethereum证据。

2. [eth_getBlockByNumber Ethereum方法页](https://www.alchemy.com/docs/chains/ethereum/ethereum-api-endpoints/eth-get-block-by-number)：L78写20CU；L92–103列必需的区块号/tag string-or-enum，以及必需boolean hydrated transactions；`false`表示只返回交易哈希。L116示例参数为`["0x68b3",false]`；L120示例结果包含`number/hash/parentHash/timestamp`及transactions等字段。区块number/hash应从实际结果保存，不能沿用这份示例的固定值。

两页均在L84–88把apiKey默认列为`docs-demo`，并在完整HTTP示例中使用`https://eth-mainnet.g.alchemy.com/v2/docs-demo`；这是官方主动提供的方法演示路线，不能仅因字段叫apiKey就增设注册前提。它也**不保证本次匿名demo可用、稳定、免费无限额或方法实际成功**。全部“200 Success”均为文档示例，不是实测。

## 必须保留的未读展开

getBlockByNumber的参数enum及response各显示“Show2variants”，但本次web正文未展开它们。可读说明只举latest/earliest/pending；**没有明确展示finalized、安全标签完整枚举、结果null或错误对象/代码**。此前另一eth_call页的finalized说明不能自动证明本方法接受它；不能用通用Ethereum标准替代提供者声明，也不能称未见即不支持。

因此，`finalized_false_exact_provider_support=UNKNOWN`，`null/error_provider_semantics=UNKNOWN`；完整wire schema覆盖仍是PARTIAL。Root协议已规定遇null/畸形/错误停止，这是本次任务策略，不冒充已核提供者错误定义。两方法已明确的number与boolean类型、文档请求/结果字段和官方demo意图，可以用于可审方案；未展开项不能靠发请求猜参。

## 来源、执行与预算

动作=2条官方域限定搜索+2方法URL打开；结果URL未报告显式重定向。工具输出、URL/UTC/hash及覆盖见manifest.json、method-bindings.json和receipt.json。仅保存web工具原返回的搜索摘录/正文提取，**不称HTTP原HTML或完整OpenAPI**；HTTP状态、服务器原体hash/大小未由工具暴露，均UNKNOWN。单件/合计保留量在1MiB/3MiB内不等于已测网络传输原体大小。

已停止公开读取；零RPC、demo试跑、订阅、账号/凭证、第三方代码执行、模型/回测、金融计算、交易或外发。实际model/effort/resources无平台回执，UNKNOWN。执行归Root统一任务，本Owner没有另设权限提问或自行放行。
