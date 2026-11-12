# 同 hash 只读：标准已明确，Alchemy canonical 对象支持未证

结论：**EIP-1898 明确规定 `eth_call` 的 `{blockHash:H, requireCanonical:true}`；Alchemy 当前 Ethereum 文档明确披露的是32字节 hash字符串，未取得其支持上述对象/canonical检查的官方明确声明。** 本轮不改代码、不调用RPC、不启动A，不把文档或旧测试当作已live通过。

## 规范、供应商与计费分开

| 来源 | 已读事实 | 不能升级的结论 |
|---|---|---|
| [EIP-1898 §Specification](https://eips.ethereum.org/EIPS/eip-1898#specification)，Final、Created2019-04-01；本轮全文102行提取 | `eth_call`属于适用方法。第二参数可用`{blockHash:H,requireCanonical:true}`；默认canonical要求为false。true时非规范链应报错，且应与block-not-found错误区分，后者优先 | 标准不能替Alchemy具体实现/免费档/数据端点可用性作证；canonical检查是服务节点在该次调用时的判断，不是永不重组或finality保证 |
| [Alchemy Ethereum eth_call](https://www.alchemy.com/docs/chains/ethereum/ethereum-api-endpoints/eth-call)，正文L99–107；发布日期UNKNOWN | 明文允许显式number、tag或32-byte hash。正常GET原HTML与被动JSON字符串解析进一步显示Block仅三种string变体；hash正则`^0x[0-9a-f]{64}$` | 裸hash字符串与EIP对象是两种请求形式。当前文档未列`requireCanonical`，不等于证明服务拒绝它，也不能据EIP声称服务必然支持 |
| 同Alchemy页L78 | 方法标价26 CU，未列hash字符串或canonical对象的独立费项 | 不能证明实际账单同价/减免或0成本。若方法计价规则照常，替换参数不减少eth_call个数；仅可能省去原fence请求，其实际支持与费用变化未测 |

最小请求形状仅作说明，未发送：标准形式为`params:[CALL_OBJECT,{"blockHash":"H","requireCanonical":true}]`；本轮Alchemy明确披露形式为`params:[CALL_OBJECT,"H"]`。`H`须是实际32字节块hash，不能把块号编码字符串误当hash。多次读都显式绑定同H，才避免每次独立解析同块号；它不替代完整ID全集、oracle语义、本机到达时钟与错误/重组记录。

## 旧 number + fence 的准确边界

[EIP-1898 §Rationale](https://eips.ethereum.org/EIPS/eip-1898#rationale) L64–69专门讨论逐number读取后再查块hash的额外请求，以及一次出链后又入链的盲点。原文关键短句：

> “reorged out before `eth_call`, and then reorged back in before `eth_getBlockByNumber`.”

按Root所述current v2“两次number读取＋末尾fence”结构，若数据读取期间规范链短暂换为同高度另一块，最终又回到最初H，末尾fence仍可能相符；因此不能证明此前每个state读都来自H。本文未独立审阅v2代码，也未构造/执行模拟。旧fence仍能检测它查询时可见的不匹配，已有测试仍有其覆盖价值；只是未覆盖上述情形。Root确认A尚未live，不能据此报告已发生错误观察。

若未来精确提供者确实支持EIP对象并执行canonical检查，所有必要state查询可直接约束同H，从机制上替代用于防混块的逐number fence；任何notfound/noncanonical/解析错误应保留并丢弃受影响块记录，不换有利状态。即使全部调用成功，后续仍可重组；仍须保留原head/header、H/parent、本地接收/完成时间、重组通知/最终标记及ID全集校验。**本轮不据标准说明直接移除现有fence或声称方案已经实测可用。** 裸hash可消除块身份歧义的文档意图，与强制canonical语义仍须分列。

## 获取覆盖与停止

共4/4公开动作：①EIP原生读取；②Alchemy eth_call原生读取；③官方域精确检索`site:alchemy.com "requireCanonical" "eth_call"`，空结果仅限本次检索；④同一未受拒eth_call文档的正常匿名GET，静态展开折叠Block schema。该第四读HTTP200、274394B、SHA256 `f452de4458fbbe04201058d70938d8c0a6a5e457ca50c90452e34422e5631cbf`；未执行页面JS，仅读41个JSON字符串帧。完整原体以base64及SHA保存在同名JSON，native返回原样另存该JSON，其HTTP/raw-body身份为UNKNOWN。

本轮窗口从2026-10-20T03:11:55Z起，第四读精确UTC见JSON.action4；native工具未返回逐请求精确UTC，不能把时间窗冒充精确抓取时刻。已核LOCAL_BLOCKERS的newHeads原文403及docs-demo白名单403；均未重取、换身份、代理或调用数据端点。独立文档GET不是解除旧拒绝。4次后停止网络，不追加读取计费页/SDK/另一个提供者；没有实际API、订阅、账号/key或浏览器应用面板读取，没有安装/模型/金融算术/交易。原封存manifest/代码/原件未修改。actual model/effort/CPU/RSS UNKNOWN。
