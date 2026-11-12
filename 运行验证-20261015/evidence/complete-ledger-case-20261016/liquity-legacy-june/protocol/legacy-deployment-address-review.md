# 旧Liquity V2 registry与三抵押品TM：官方清单核验

结论：官方`liquity/bold`固定ref部署清单明确把旧registry `0xd99de73b95236f69a559117ecd6f519af780f3f7`与以下三组TM/代币绑定。已取得权威清单即停止扩展；不是仅凭DefiLlama标注。真实链上部署时间、当前状态、部署字节码与特定审计版本对应仍UNKNOWN。

| 分支 | 官方清单troveManager | collToken |
|---|---|---|
| WETH | `0x81d78814df42da2cab0e8870c477bc3ed861de66` | `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` |
| wstETH | `0xb47ef60132deabc89580fd40e49c062d93070046` | `0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0` |
| rETH | `0xde026433882a9dded65cac4fff8402fafff40fca` | `0xae78736cd615f374d3085123a210448e74fc6393` |

三组均位于同一JSON的`branches[]`；其顶层`collateralRegistry`为上述d99地址，顶层`boldToken`为`0xb01dd87b29d187f3e3a4bf6cdaebfb97f3d9ab98`。JSON也列各分支addressesRegistry、activePool、gasPool及其他配套地址，已完整保存，未推测或调用链上注册表。

## 可复核版本身份

本次真实读取[官方固定ref API](https://api.github.com/repos/liquity/bold/contents/contracts/addresses/1.json?ref=cc2a420067e47cafc1b1b1309045b341f9ced1b1)，API返回路径`contracts/addresses/1.json`、[固定ref网页](https://github.com/liquity/bold/blob/cc2a420067e47cafc1b1b1309045b341f9ced1b1/contracts/addresses/1.json)以及不可变[Git blob API](https://api.github.com/repos/liquity/bold/git/blobs/6e65bad32e1aa6d22f8eaac195a168f537f3705c)。

- 请求固定ref：`cc2a420067e47cafc1b1b1309045b341f9ced1b1`；不同于仅把旧manifest标签贴给未知tree，本次API确在该ref下返回了该blob身份。
- 返回blob SHA：`6e65bad32e1aa6d22f8eaac195a168f537f3705c`，被动重算Git blob SHA1一致。
- 解码原件5599B；SHA256 `bd7815aecbbe22e2ef929ec959cc637fcf1780889c6ebed780cffc2e52a3f9e3`；与先前保存`contracts__addresses__1.json`逐字节相同。
- **没有混用旧tree**：先前递归tree的同路径blob为`6e5615b93f5549b2bd9ee55dbb45229a69fc5182`，不是本次返回blob，本次没有读取或把它宣称属于该ref。旧tree与所请求commit的关系未经独立证明，两个不同blob不能当同一commit内容冲突，也不能反向证明其版本关系。权威绑定为上面的真实固定ref GET返回。

## 时间与适用范围

部署清单没有创建交易hash、区块、链上部署timestamp、版本上线日期或历史启用/弃用日期。既有`preevent-source-commit.json`记录该commit日期2025-05-13T14:56:19Z，仅作为继承的Git历史元数据保留；本次未新核该元数据，更不能把Git提交时间当链上部署或精确首次公开时间。治理EPOCH_START等业务参数也不能用作部署时间。实际部署日期UNKNOWN，根另负责官方迁移历史，不在本分支重复。

可证明：官方仓库在本次指定固定ref API中发布了一份明确列旧registry和三分支地址的清单，且内容身份可校验。不能证明：链上注册表实际返回值、每份部署实际运行代码与审计版一致、部署时点、2026年6月还可操作或有哪些事件、是否有其他历史部署。之后若按这些地址查日志，应标为该已声明旧部署范围，不能与新TM混为同一清单。

父任务给出的官方俄文技术页`https://docs.liquity.org/ru/v2-documentation/technical-resources`，本次普通GET返回HTTP403，未取得正文；已停该资源，未重试或换路绕过。不能把搜索摘要或页面标题当作本次实读证据。DefiLlama适配器旧registry仅是第三方线索，不充当本报告官方部署身份来源。

新增公开读取：1次官方GitHub固定ref小文件GET成功，1次官方说明页GET403；最多6次预算内收敛。未改认证，静默gh auth检查；未读env/config/凭证。所有实际URL、UTC、原始API回复和hash在同目录回执。仅数据解码/比对，无下载代码执行、模型、回测、适配器、策略、RPC/EVM、交易、安装、账户、付款或外发。实际model/effort UNKNOWN，继承不覆盖；PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4。仅写本Owner目录，未改其他文件。
