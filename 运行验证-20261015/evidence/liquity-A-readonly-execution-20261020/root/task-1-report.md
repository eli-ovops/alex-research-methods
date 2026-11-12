# Task 1 报告：DONE（隔离候选与必要检查可审）

仅完成brief授权的离线准备；未应用、未启动、未恢复观察。旧run06终态保留，T0前停止，正式14日样本仍为零。

已完整读取task-1-brief、run06-provider-throughput-boundary与run06-terminal-acceptance-review。基线core SHA `a2f7d56b1f90c2ee535679d3d48c461a30f2ec2e92001227887312c5b3508436`、collector SHA `4dd5774bf4d5fea066bb55714907615c208009065582db70e80f824f843a6e74`前后均匹配。唯一候选在`execution-owner/offline-throughput-window-candidate/readonly_core.py`，SHA `54b09fc1d32186dfca56c0a8eb15b6172b335693824489676ba47c627c7af5bc`；完整文件仅Budget局部有差异，其余字节相同。

本地守卫改为10.0秒滚动、容量peak*10；peak名义上限300及原默认100不改。到达旧记录年龄>=10.0才过期；RPC与WS继续同一deque。已收到的WS仍按原到达时间立即加累计CU再判断；没有睡眠、改时间戳、移窗或丢消息。原请求预发送节流保留，等待公式对应10秒，不延迟已收WS。累计CU/方法/CPU/磁盘、WS字节/帧头保守口径和整数取整、原请求成本及429停机不变。它不是提供者token bucket或共享账户状态的复制，不能由局部通过证明真实免费余额/服务可用性。

`check_window.py`只AST抽取Budget，注入虚拟单调/进程时钟和资源读取适配，容器为真实deque。未导入/执行整份客户端，没有网络、TLS、市场/归档读取、模型或真实入口。`check-results.json`逐项保存输入/预期/实得：两155在0/.004秒累计310通过；20笔第20笔3100停止且费用保留；9.999保留/10.0过期但累计310不清零；总额310边界后已收1费用保留311并停，未发送请求超总额则保持310；2000请求+1100通知共窗3100停止。7项全PASS，单次检查退出0，stderr0，全部测试sleep_calls为空。

审查包为`review-package.diff`（含上下文、基线/候选hash、全部局部改动）；manifest列所有输入/输出身份。`checks-receipt.json`及原stdout/stderr给真实命令/退出/CPU，`check-results.json`给确定性实得。仅为预算逻辑局部工程检查，不冒充原客户端或真实服务验证。未派Reviewer/子agent，由Root按brief派原Reviewer只读审同包，不重跑已通过同码检查。

资源：Owner新独立准备CPU保守借记5秒，检查child CPU实测0.037297秒包含其中；child maxRSS27,131,904B，最多父子2个本机进程；新增文件远低于1MiB，最终逻辑/分配字节随`output-size-receipt.json`封存。Owner主动工作保守占用240秒（小于10分钟）；首读UTC未记录，不编造精确起点或实际人工劳动账。检查UTC09:48:03.932–09:48:04.006Z。此预算独立于已结束的旧跟进，旧观察CPU/盘/CU帽和用量不改、不清零。

未做：独立方法审阅、主源应用、启动器/绑定/配置变化、任何新输入/账号/API/TLS连接、采集/观察恢复、付费/安装/交易/模型或经济门槛改变。个人净优势、长期稳定性、容量、实际共享余额均UNKNOWN。actual model/effort UNKNOWN，未声称模型切换。完成仅表示Task1离线候选可审；后续无真实采集授权。新文件均为候选/检查/审查证据用途；旧文件没有清理或覆盖。
