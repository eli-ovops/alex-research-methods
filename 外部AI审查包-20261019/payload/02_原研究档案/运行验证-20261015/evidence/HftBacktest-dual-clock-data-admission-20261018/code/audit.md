# 官方collector双clock与旧转换脚本限定核验

结论：**已核一种官方采集实现的两个clock来源与旧converter修改规则，但不能认证实际样本的原始接收时刻或current HftBacktest完整因果转换。** 正常WS路径记录handler处理起点；序列缺口/初始化缓冲路径会改用稍后的drain时刻。此差异可能是保守的延后可用时间，不能自动称未来泄漏，也不能把所有raw prefix称原始网络接收时间。

读取官方 `nkaz001/collect-binancefutures` HEAD的完整Git tree，固定tree `27abefde5d6a42db125c59bd47332db58677ba4b`、truncated=false；三个源文件均按该tree提供的blob URL读取并独立计算Git blob相符。未获取commit对象，**commit SHA UNKNOWN**；固定身份是tree/blob，不把HEAD当历史样本生成版本。4次公开GET均200，31,127B原响应；3份惰性源码共18,758B。逐URL/UTC/HTTP/SHA256见source-receipts.json。

简称C=`collect/binancefutures.py`，W=`collect/main.py`，V=`convert/convert.py`，对应本目录inert文本。

| 已证代码逻辑 | 对clock与可用性的有限解释 |
|---|---|
| C:23–25在WS handler一开始time.time()，在JSON解析前；C:167–169由异步WS文本消息处理调用 | 本机wall-clock的应用处理起点；不是内核网卡时间、交易所时间、writer落盘时间。队列/进程/写盘延迟未量化，时钟同步/回拨未验 |
| C:35–43序列不连续时仅存(message,raw_message)，丢弃本次timestamp；C:195–217先REST snapshot入队，再为pending drain重新time.time()，同一轮pending共用它 | 缓冲depth行prefix不是初次handler接收时间，而是较晚的重放/初始化处理时间。它可表达更保守的处理可用性，不能拿来精确估网络延迟；snapshot与stream的因果完整性仍须数据检验 |
| W:25–36独立writer从queue取timestamp，写int(timestamp×1,000,000)、空格、message；文件日期由本机fromtimestamp(timestamp)决定 | 此实现prefix是微秒epoch整数，落盘时不重新打戳；文件日期时区依赖主机，而非已核UTC配置。实际样本是否由此tree生成未证 |
| V:51–77读取首16位local_timestamp；trade/depthUpdate用data.T×1000作为exch_timestamp，明确不采用注释中的E | 这套旧路径统一微秒单位；exchange字段是交易时间T的映射，不自动等于事件派发E/撮合内部序号 |
| V:14、32、63–75等仅在--correct启用且exch小于prev时把它钳至prev；local仍用prefix值 | 是人工单调化exchange clock，而非保留原始交易所乱序。该脚本未修改local、未调用fixlocalts或双时序合并；不能将其结论推广给HftBacktest当前独立converter |
| V:90–99可选full的mark/index/funding行使用prev_exch_timestamp而非其刚读的T；V:144–150末尾全book snapshot用最后时戳生成 | 部分输出exchange clock是派生标签；末尾合成snapshot也不是每个档位原始事件时间，需与原事件流区分 |

**版本分区：** 本次实际源码是collect-binancefutures内的微秒`.dat→pkl`旧脚本。publisher Owner读取current `hftbacktest.readthedocs.io/en/latest`资料，其示例local receive为纳秒，提及reorder/latency_offset；这仅作为独立文档线索，未把其代码绑定为本tree或实际样本。旧`hft.readthedocs.io` v1与current命名/单位/处理不可互换。本代码Owner未取得current/v1 HftBacktest validator、fixlocalts、correct_event_order的固定源码，因此其是否/如何平移local、按双clock合并、保留原值及对应版本均UNKNOWN。不能凭搜索摘要把处理后local称原始接收。

能建立的有限时序：在固定源码路径下可区分交易所T、本地正常handler处理、缓冲drain、writer落盘四层；有望以local处理/drain时刻约束策略可见时间。但双字段存在不自动证明可因果重放。最低还需实际样本的collector revision与writer单位、原值/处理后值并列、明确转换参数与固定validator源码、clock校准/乱序/断线初始化审计，以及本地/交易所两套顺序各自推进、策略仅用本地已到事件的规则。本轮只做原件审查，不进行数据QC、运行collector/converter或任何回放。

最小未取原件：**实际发布样本所使用的固定版本转换/验证源码与参数说明**，特别是local correction/latency_offset与双时序合并如何处理；须保留原始local列或可逆映射。实际样本与数据权利由publisher Owner独立判断，代码许可不替代数据许可。本tree列表中的sample文件仅见名字/元数据，未下载/读取payload。

规则沿scope：PERMISSIONS-2026-10-14-v1/ROUTING-2026-10-13-v4/HANDOFF-2026-10-10-v2；actual model/effort/速度UNKNOWN。0来源/fixture/collector/converter执行、模型/回测/标签/成本计算、市场文件读取或下载、账号凭证/安装付款/交易/外发。4读预算已尽，停止。原件/回执/两报告仅code目录保留，无清理项。
