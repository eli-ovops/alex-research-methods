# Open Book v1.0 reader限定审查（2026-10-18）

结论：reader可确定格式与本地文件行读取方式，不能证明任意一小时能独立重建准确L4 book，也不能替每条bookdiff建立无歧义事件时间。保留该数据源作为候选，不准入时序依赖的后续实验。本审查不改变旧FAILED或数据研究Owner。

| 问题 | 已核原件 | 仍为UNKNOWN及影响 |
|---|---|---|
| diff顺序 | reader 418–479按小时0..23、每文件文本行append，未排序 | 撮合/区块内/采集接收顺序与批次边界；文件行序不是已核接收顺序 |
| 时间/序号 | schema 357–382与reader 403–405、435–461无此字段；order status另有ts | 未取真实diff，不能排除原始JSON额外字段被reader丢弃；无法逐diff定时 |
| oid一对多 | schema 142–147明确订单生命周期多行；reader无join | oid订单唯一不等于事件唯一；缺匹配键/tie-break，不可任选first/last时间 |
| 初始book | schema381宣称从空book重建；reader没有snapshot/book状态处理 | 未说明空book起点、每小时snapshot、月初边界；744小时无缺口不能证明初态充分 |
| 最小独立子集 | 最小可读事件文件为日期/exH.gz，3币混排、可筛币；读取不依赖mapdir | 精确book重建所需实际最小子集未知；条件上须完整起点snapshot+连续diff+边界规则，不能冒称已提供 |
| 编码/单位 | schema79–132与reader95–120给出固定点及signed规则；bookdiff十进制字符串；trade sz明确base units | order/bookdiff size基础单位、quote/settlement、合约乘数等未明确；美元示例不证明经济约定 |

reader的二进制解码返回float32；bookdiff/trade转pd.to_numeric。后续若获准实施，须保留原始整数/十进制字符串再按审定规格处理。schema153对full-fill sz保留“0或filled quantity”的语义歧义。本轮未运行decoder、导入源码或读取行情包；文档示例只按示例处理。

最小下一原件仅一项：发布者针对v1.0的采集/重建规格，明确原事件顺序/时间与statuses事件关联、某小时起点snapshot及月初边界、价格/数量经济单位。当前材料无此原件实际入口，停止泛搜，不猜路径、不联系他人。

获取：实际HTML JSON-LD链接 `https://zenodo.org/api/records/18184441/files/read_data.py/content`，1次普通公开GET，HTTP200，24,427B，完成时间上界2026-10-18T10:24:44Z（精确请求开始未记录，HTTP Date见headers）。SHA256 `a9c2f825400a44e7d5f2d5ad066c006f6ecabccb2533d53704df28003cb4c107`；MD5 `03ccb90a9042880ef7360a54f49c9a6b`与发布页相符。README/SCHEMA原URL、UTC、hash与逐项证据详见reader-audit.json和read_data.receipt.json。

规则：PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4 / HANDOFF-2026-10-10-v2，已读§2/3/4；LOCAL_BLOCKERS定向检索无直接命中。目标gpt-6.1-sol/medium；实际model/effort/速度UNKNOWN。限于已给入口，使用agent-reach网页路由参考并遵从本任务普通GET限制。0行情包/压缩包/来源或decoder执行/模型训练回测/账户交易/安装/认证变更/外发消息。所有新增文件在本reader目录，供交接保留，无清理项。
