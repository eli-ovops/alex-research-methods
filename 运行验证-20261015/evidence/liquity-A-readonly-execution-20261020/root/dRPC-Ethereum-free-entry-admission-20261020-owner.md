# dRPC Ethereum公开免费入口：有限文档准入

**有官方无key形态的公开HTTP/WSS候选，尚不足认定原A可直接运行；不是整体目标blocked。** 最大实际适配风险为免费请求2秒timeout与完整聚合扫描是否兼容；决定持续观察资格的订阅/计量与hash指定仍UNKNOWN。此轮没有数据探针，不能把文档可读当端点可达或14日可靠。

## 已读官方支持与限制

[官方Ethereum概览](https://drpc.org/docs/ethereum-api) 正文L2143–2155明确提供“账户或public”的选择，列`https://eth.drpc.org/`和`wss://eth.drpc.org`。因此存在不以注册取得key为前提的公开入口依据；同页其余教程使用带key Premium示例，不能混成匿名公共配额。未访问这些RPC/WSS地址。

[限流正文](https://drpc.org/docs/howitworks/ratelimiting) L2115–2125称public nodes免费；一般规则：每IP通常120000CU/min，高需求可降至50400，部分网络可另定；限流时每方法至少按10CU；请求最大timeout2秒、日志最多10000条、JSON batch最多3项、filter方法默认禁。210M CU/30日条款以注册日重置，匿名如何对应这份额度没有说明，不能据此给自己分配210M。没有把文中eth_call近似RPS例子当所有方法RPS保证，也不把dRPC CU与Alchemy CU直接换算。

## 原A必需项：覆盖与UNKNOWN

| 项 | 本轮能证明什么/仍缺什么 |
|---|---|
| 无账户/无key | 正文public替代账户且列固定无key URL，支持候选存在；真实匿名权限/可达未测。 |
| eth_subscribe/newHeads | Ethereum导航列eth_subscribe/unsubscribe，概览检索索引描述新块等WS事件；**本轮未读参数/持续订阅正文**，精确newHeads、公有节点许可及是否收费/保活/消息字节计量UNKNOWN。不能由WSS URL或营销free自动通过。 |
| eth_call、eth_getLogs、块方法 | Ethereum导航列这些方法及getBlockByHash。详细schema、公有方法白名单/重型调用限制、bare blockhash eth_call或EIP1898 requireCanonical支持UNKNOWN；不是用通用Ethereum标准替代dRPC承诺。 |
| batch与完整扫描 | JSON-RPC batch≤3。原A内部Multicall3聚合不是JSON-RPC batch，不能据此单项否决；但每个完整eth_call能否满足2秒服务timeout/体积与执行gas帽UNKNOWN。 |
| 订阅/并发/每日 | 公共WSS并发、每连接订阅数、日/月匿名额度、消息/断线/重组/丢失补历史语义、保证新鲜度或通知到达上界均UNKNOWN。filter禁用不自动等于WS订阅禁用。 |
| SLA/时间语义 | 未取得适用于匿名free的SLA/连续14日保证，不能声称有或没有SLA。marketing可靠/高性能不可作因果到达证据。 |
| 个人研究/地区/未来经营交易/收费 | **条款/隐私/地区限制和商业许可正文未读**，本轮UNKNOWN；未公开写不等于已允许或已禁止。public免费声明不覆盖未来Premium、商业或交易用途/任何方法免费。0付款当前边界保持，不能自动切付费。 |

前两份是实际正文，方法覆盖第三份仅导航，检索snippet未冒充方法/条款全文。有限6动作（2检索+4页面读，含两次导航过长后的正文定位）已耗尽，因此Terms、EVM Subscriptions、eth_call方法页未展开；这是本轮覆盖缺口，不宣称这些事实永远不存在。只采用dRPC官方资料；搜索返回的其它供应商/社区材料未采用，也未打开其页面。未读Polygon方法正文或调用旧Polygon拒绝资源。

## 对原A的取舍

保留为可继续核验的**独立数据入口候选**，不更换collector/provider/binding。原A固定Ethereum同一合约、同T0/T1、逐块完整状态/同hash/fence/时效/资源/经济门均不降低。原40万方法/18kCPU/8GiB/免费总帽不是dRPC的服务配额；现有Alchemy式订阅CU公式与预算守卫不能直接作为dRPC计费。只有具体公共方法/订阅文档与可用额度明确后，才能制定一次有界技术验证，不能立即恢复14日或因换provider把既有经济结果当新增独立样本。

最小下一原件：已在官方docs导航定位的Pricing→WS Subscriptions→EVM Subscriptions，先解决公共newHeads资格/通知计量与持续限制；其余hash eth_call与Terms仍是后续准入缺口，当前不自行追加读数或任何RPC。没有已证“所有免费方案无法做A”的结论。

原件索引：`/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/drpc-Ethereum-free-entry-20261020/manifest.json` SHA `46677648bbf4b03e9f369ee3c6610428a705495197a834eb561e65549adf486d`；保留URL/native行号/hash与实际覆盖。均是原生web解析摘录而非HTTPraw；取源精确UTC未单独记录UNKNOWN，封存UTC 2026-10-20T12:33:50.352724+00:00，不伪造HTTPDate。来源摘录无需保存大量共享导航。

本轮CPU保守新增10秒、主动≤15分钟，旧32734CU/63RPCmethods保留、0新数据方法/注册/登录/安装/付费/模型/交易，主源/旧锁/自动化未变。本Owner预算到停止，交Root决定下一有限行动，不把局部工具问题当整体经济目标阻断。
