# eth_call最小对象与官方HTTP demo文档核验

结论：官方当页的内嵌OpenRPC及折叠属性数据足以支持本轮最小对象 **`{to: 固定非空TM地址, input: 已封存getter选择器}`**，并省略 `from`、`gas`、`value`。官方字段为 **`input`**；本页15属性没有 `data`，且 `additionalProperties: false`，不据通用习惯声明其别名兼容。仅完成文档层核验，**0次demo/RPC调用**。

来源为 https://www.alchemy.com/docs/chains/ethereum/ethereum-api-endpoints/eth-call 。2026-10-19T21:01:51.510759Z开始、21:01:52.528868Z结束；默认严格TLS普通GET，HTTP200、完整274394B、0重定向。原文 `01.source.html` SHA256 `bc407e28a65bb08f8557a1253c75e8bfef7fc568cba8044e5c6be1b2ce0ceada`。正文发布日期在本次覆盖中未找到，记UNKNOWN。1/2公开动作后提前止网，无需第二来源。

| 本轮使用项 | 官方约束与定位 | 对本轮请求的含义 |
|---|---|---|
| Transaction | `eth-call-openrpc.yaml` L5–12：外层对象required，schema的properties无子字段required列表，additionalProperties=false | 仅采用已列属性；不能省整个对象 |
| to | 同文件L24–34：20-byte地址string，pattern `^0x[0-9a-fA-F]{40}$`；另一分支null表示contract creation | 固定原TM地址，明确非null，不使用创建分支 |
| input | L50–54：string，`^0x[0-9a-f]*$`，Calldata/hex-encoded bytes | 使用已核无参数getter的确切小写hex选择器；本Owner未重新生成选择器 |
| from | L35–39及`optional-label-excerpts.txt`：20-byte sender/msg.sender，UI明示optional | 省略；省略时提供者具体sender默认值未写，UNKNOWN |
| gas | L40–44及optional原标签：最大执行gas，hex quantity string，UI明示optional | 省略；服务端具体gas默认上限UNKNOWN，不填写估计值 |
| value | L45–49及optional原标签：wei金额hex quantity string，UI明示optional | 省略；不搬用示例`value=0x1`，不对未写的默认值补定义 |
| Block | L115–139：外层可省略、默认latest；明确支持显式hex区块高度 | Root本轮调用显式传既定B，不为四次调用各自取latest；本项不替代getBlockByNumber独立schema |

获取方式是**被动解析**HTML内`self.__next_f.push`的JSON数组/字符串，再抽取其中OpenRPC YAML、JSON Schema与UI的optional标签；未执行网页JS、SDK、示例或任何来源代码。`eth-call-openrpc.yaml`保留完整该方法规范，SHA256 `96e320054d0d70a10a3917668fa3e40b44f2ac360012339f475744f824542ca0`；`transaction-schema.json`保留15属性结构，SHA256 `90975287525d26cf6c4b6c1a2d9752a116929c9b2bba7cd0628db4e6e3c674ff`。其余未使用属性仅做结构提取，不声称全面审计。

HTTP demo意图也由同一官方原文确证：可见`apiKey`属性标`defaults to docs-demo`，更高吞吐建议创建自己的key，并提供明确POST `https://eth-mainnet.g.alchemy.com/v2/docs-demo`的cURL示例（`http-docs-demo-example.txt`，只读未执行）。这支持官方有意公开该HTTP演示路径，并非把WS `/demo`机械换成HTTPS。它**不证明当前端点可用、全部方法可用、无账号限额、限流/稳定性或真实返回类型**。样例返回`0x`不能当作有效uint256零；Root仍需依已核ABI执行返回长度/身份校验，遇拒绝/错误停。

本轮不认证目标合约ABI/历史部署，不读取链上状态、不生成财务数值，也不将节点只读执行叫交易广播。方案是否运行由Root按新v3请求清单与独立审阅处理。actual model/effort/CPU/RSS均UNKNOWN。规则三版本沿用；唯一写入本Owner目录，未改他人或旧原件。
