# dRPC public订阅与同块状态语义核验

结论：官方明确EVM支持newHeads，也列Ethereum匿名WSS地址；但本轮仍未取得“匿名public WSS持续免费newHeads”的明确资格与配额声明。此关键前提为UNKNOWN，不能把通用订阅页的带key示例当匿名资格。当前不足以宣布原A完整14日免费入口准入通过。未发任何RPC、WS或probe，未改collector/binding。

## 已读原件与证据

1. [官方EVM Subscriptions](https://drpc.org/docs/pricing/subscriptions/evm)，本轮原生工具正文摘录01，L2122–2176。L2125–2130区分建立WSS并订阅与接收通知，二者分别20CU；L2135–2136明确newHeads逐新区块推送header。L2142–2163示例为wss://lb.drpc.org/NETWORK-NAME/YOUR-DRPC-KEY。
2. [官方Ethereum eth_call](https://drpc.org/docs/ethereum-api/executingtransactions/eth_call)，本轮正文摘录02，L2118–2300。20CU（L2121）；600M gas cap（L2137）；部分带gas_price或模拟写状态调用有sender余额检查说明（L2135–2136）。
3. 复用前一已封单元的01-ethereum-public-endpoints.native-excerpt.txt：官方Ethereum overview明列https://eth.drpc.org/及wss://eth.drpc.org；复用02-public-rate-limits.native-excerpt.txt L2115–2125：public nodes always free；一般free policy包括每IP通常120000CU/min、区域高需求可降低到50400、最大timeout 2秒、batch最多3项、logs最多10000、filter默认禁用。注册起算210M CU/30日不能直接解释为匿名账户的可核余额。旧任务未重开、未重取。

本轮完整读到的是两页所返回的方法正文，不是全站、法律条款或服务实测。HTTP raw status/原HTTP体及页面发布日期UNKNOWN；文档里的示例200不是本机响应。摘录哈希认证本地保存的native parsed文本，不认证HTTP raw。

## 匿名newHeads关键缺口

通用订阅页没有明确匿名public免费资格、每连接/订阅数量、连接寿命/空闲断开、通知每日额度、消息字节成本或强制超额行为。20CU/订阅与20CU/通知是所列CU计量，不证明匿名资源池额度、收费现金或无限免费。页面“instant/real-time”没有定量延迟、接收时间、连续性/补历史/重组交付保证。其自动重连最佳实践不改变本项目失败即停规则。

因此“public WSS存在”与“通用EVM newHeads支持”均有文档证据，二者合起来仍不是匿名持续14日订阅资格的直接声明。filter不是subscribe，不能用filter禁用证明subscribe被禁。

## 同块调用与free 2秒

eth_call请求参数正文仅说明block number及latest/earliest/pending（L2221–2229）；未载blockHash、EIP1898对象、requireCanonical或裸hash字符串语法。因此hash-bound方法支持UNKNOWN，不等于已证明不支持。标准语法本身不能替代提供者能力证据。

公共eth_call示例用eth.drpc.org，但params次序是blockNumber在前、transaction对象在后、state override第三（L2173–2195）；与现collector的transaction-first结构不同，不能未经核验机械照搬。正文只列data，未明确input别名。此为文档/现实现接线不确定，不是实际服务拒绝。

600M gas cap不能保证重型调用在free 2秒内完成；本轮未见特殊重型调用豁免、执行时间保证或明确Multicall禁止。现A每常规块两次Multicall eth_call及一次header fence，initial另count；JSON-RPC batch≤3不等于Multicall子调用≤3，不据此误拒。N/响应字节/CPU与2秒是否相容仍需将来另授权有界实测，当前不执行。

## 预算与停止

本轮6/6公开动作：3次官方域检索（第3动作零结果），3次页面读取/导航；实际实质覆盖上述两页。最后检索未补得匿名订阅明文。没有访问旧Polygon403对象、其它链数据或任何数据API。原Alchemy CU/方法本地累计32734/63保持，本轮新增数据RPC/WS=0；公共文档动作单列。保守新增本地CPU借记10秒（预算占用，不冒实测），actual model/effort UNKNOWN；无安装/账号/付费/模型/回测/交易。封存UTC 2026-10-20T12:39:00Z；每次公开动作独立起止UTC未记录，UNKNOWN，不倒填。

最小后续证据仅为官方对匿名wss://eth.drpc.org的newHeads可用性、免费通知/连接限额及同块hash语法的明确说明；本轮预算结束，未自动联系支持或追加查询。条款由独立Owner负责，不以本报告代替合法使用准入。
