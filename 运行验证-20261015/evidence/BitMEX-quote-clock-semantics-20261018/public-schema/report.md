# 官方 GitHub Quote schema 与时间语义

结论：本次实际可读官方README明确 API 返回的时间戳为 UTC；实际 Quote schema 给出六字段及类型，但没有 timestamp 赋时环节或 size 单位的说明。与2024-01-01归档字段一致，是结构对应证据；不是归档时区、事件时间或当时可得性的明确认证。状态 PARTIAL，3/3公开读已停。

## 实际原件

- [BitMEX/api-connectors swagger.json](https://github.com/BitMEX/api-connectors/blob/master/swagger.json)：按首次官方域搜索中实际出现的repo/文件路径，以公开标准raw URL读取。2026-10-18 15:49:34.238208–15:49:34.918362 UTC，HTTP200，271584B，SHA256 `fed3c4d181f96aa58d67a00fb156a02274c06bcf4866a8b2de867e174dd18525`；原件02-swagger.json.inert.txt。Swagger2.0，API info.version1.2.0；这是API标识，不能作为repo commit或历史生效日期。
- [官方 Python client README](https://github.com/BitMEX/api-connectors/blob/master/official-http/python-swaggerpy/README.md)：同样沿实际搜索命中的文件读取。15:49:34.238607–15:49:34.849937 UTC，HTTP200，7264B，SHA256 `a964d4f5cb468f51c905a6a0f2b721f0b067ddff35c6bc008cbe0a7d80ef7bb9`；原件03-python-readme.inert.txt。L66–67 Date ranges 明确 BitMEX 返回的所有timestamps是UTC；L2–6将该client定位为API与Swagger适配。未执行其中安装、查询、认证或交易示例，示例不当真实行情证据。

两份文件均为本次master正文快照，有完整SHA256/HTTP头/ETag/UTC；未取得固定commit、tree或文件历史日期。Git blob SHA1只作本地计算指纹，没有expected tree独立匹配。首轮01-official-github-search.native.txt单独标为搜索缓存；结论中的UTC与字段来自后续实际HTTP正文，不再依赖该缓存。

## 字段与语义

02-swagger.json.inert.txt L7893–7924：Quote模型描述为最佳买卖报价快照及历史bins；timestamp为string/date-time，symbol为string，bidSize/askSize为integer/int64，bidPrice/askPrice为number/double。required仅timestamp、symbol。timestamp属性没有description、时区或事件/发布/接收解释，size属性也没有单位说明。

因此README提供的是API层UTC声明，不等于接收钟。schema并不证明timestamp来自匹配引擎事件、exchange publication还是其他生成时点；也不证明客户端当时已收到。date-time类型或9位小数均不认证纳秒真实精度。整数size不自动等于张数、lot、BTC币量或美元量；产品经济面值仍不能替代字段序列化定义。

## 2024归档绑定

仅本地读取S/execution/inventory-summary.json的非价格摘要，6056B/SHA256 `486f873af3a2497a20ebc174e07ef5116b35cdfc264c321ede2e1896d3d98090`。其header_exact与schema字段集合及顺序相同：timestamp,symbol,bidSize,bidPrice,askPrice,askSize；535218条XBTUSD的时间格式归类为D分隔/9位小数/无zone。

这是“实际归档结构吻合当前schema”的已证事实；把API的UTC约定解释为归档同样UTC是有依据的条件解释，尚非明确历史绑定。没有在已读schema/README中找到2024-01-01 CSV生成器、历史版本或归档clock契约。无zone的D9字符串不能独自补足该缺口。未读取压缩文件、价格/数量/时间数组或重跑QC。

## 有限用途判断

可明确记录API UTC声明和归档结构对应，并在声明代理时点假设的条件下讨论exchange-time研究；不能称已证明真实接收可用性或净盈利。无需强加精确NTP、本地接收钟、完整L4等作为任何条件研究的统一前提。最小剩余原件是官方对历史quote CSV timestamp来源、时区及其与API Quote的关系说明；不是新增数据运行提案。

scope2195B/SHA256 `0a46b8fd903973fc641c35529713c57c59e3773dbce1547c1f422a6ebec078a5`。本轮1search+2公开文件GET，均未重试已拒绝资源；0市场payload、0来源执行/模型/金融计算/账户/交易/付费。目录大小及原件指纹见report.json，实际assistant model/route UNKNOWN。
