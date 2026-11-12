# Transport增量：只准备，零网络

独立代码transport.py，不导入challenge.py/NumPy，不拟合、不解析CSV价量、不触发评分。仅固定两个Nov1 URL；Nov2/Nov3 UTC12:00之前或其他日期拒绝，Root在原定12:00触发一次。每日期独占STARTED门，Nov3只补Nov2明确404的未发布文件；已完整文件只核旧metadata/路径/字节并复用，不重下、不复扫。非404错误全局HALTED，不重试。404未发布不是成功或市场无数据。

普通匿名GET、默认TLS、显式拒绝redirect、无HEAD/Range/认证/换源。流式压缩文件落盘同时hash，gzip流至EOF校验CRC，解压数据丢弃不解析价量；完整后仅将自己新建的.part原子改名为固定.gz。失败.part保留，无覆盖/删除。各完整文件即时保存transport-complete日期-源.json，避免第二源失败时丢失第一源指纹；最终日期结果列全两源。HTTP错误仅保存小状态，不读取错误正文。

usage-transport-*进入现有全单累计：CPU600秒扣已知旧36.478407+准备保守借记10+全部本单usage，RSS1GiB、新盘192MiB、两文件应用读取压缩下载累计128MiB、网络段累计1800秒。HTTP连接/缓冲实际wire字节无法独立核实，不把应用读取字节冒充传输层精确账单。请求、下载及CRC时间保守合计进network_wait_seconds。守卫失败保留部分件并停，不自动延期。

正式入口 `python3 transport.py --mode formal`，当前不可调用。需 ../root/transport-2026-11-02-release.json 或Nov3对应文件，绑定transport_code_sha256、proposal_sha256、model_seal_sha256；Root在取得时复核新适用数据限制。成功后由Root根据实际小metadata写future-release.json，随后Owner才调用已封存challenge.py --mode future。未来release的inputs键B/K须各有固定绝对path、bytes、sha256；下载helper本身不会调用它。

Root在train-release.json同时加入transport_code_sha256，challenge的MODEL_SEALED绑定train-release自身SHA，令运输适配源码随本次训练传递封存；最终Root封存清单亦绑定两代码。主challenge.py保持8349ace5f64a85f71df0fd6f7f4b5f914dae7173719d1822b5b46b4114219f19不变。

transport-checks.json为无网络合成检查，两个日期/12UTC边界、拒绝redirect及内存gzip EOF/CRC损坏识别通过；没有读取行情、下载、模型执行或新安装。检查后仅补了压缩读取前剩余额度限制和完整单源即时metadata保存，静态可定位，无更改日期/参数/来源。全部现场保留，实际model/effort UNKNOWN。
