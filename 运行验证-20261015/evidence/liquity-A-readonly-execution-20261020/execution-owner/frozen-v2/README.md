# A 只读本机入口（工程准备，尚未 live）

唯一目录为本文件所在 `execution-owner/`。没有钱包、签名、广播、交易或 B 入口。未安装依赖；使用系统 Python 标准库。

用户本机入口：双击 `start-A-local.command`，或在 Terminal 运行 `/bin/zsh` 后将这个 `.command` 文件拖入终端并回车。**不要将 RPC URL 放在终端命令、聊天、文件或环境变量中。** 静态来源、费用和独立代码审查尚未通过时，入口会先停止，尚不会询问密钥。

非秘密前提完成后，终端出现 `Alchemy HTTPS RPC URL (hidden, memory only):` 时，本地粘贴完整 HTTPS RPC URL 并回车；不会显示输入内容。仅接受 `https://eth-mainnet.g.alchemy.com/v2/...`，拒绝 query、fragment、账号密码、别的 host/port。代码不访问浏览器或凭证文件，不复制密钥到 argv/env/磁盘。免费 CU、剩余方法数由 Root 已封的 usage 回执和本单累账提供，无需用户再输入。不要输入付款资料。

预检用同 B/hash 验证 code 字节、全 ID（含 zombie）、latest/status、Registry/SP、feed 的真实取价调用路径和预算。feed.fetchPrice 是最后一项非持久化 `eth_call` 模拟；其临时写入不当作 B 上真实状态。原件对照失败、缺字段、拒绝、预算/耗时不够均停，不更换分支或降采样。独立审阅尚未通过；不得以离线 fixture 成功代替上述 live 预检。

只有预检完成、真实 newHeads 三头验证及免费预算通过后，同一活进程才固定**下一 UTC 零点** T0 和 T0+14日，并打印 `ARMED_ACTIVE_PROCESS`。配置存在不等于 armed；看不到此行和活动 PID 就未武装。保持终端和电脑联网醒着；关闭或睡眠会导致中断/UNKNOWN，程序不自动重启、不补成之前已知。

T0 之后首个完整、因果可用的协议 ETH/USD 快照先冻结 USD 锚，再评价候选。日簇仅首次合格、same episode 不重选。每100块日志是事后结果审计，不是当时信号。人工记录在 `operating-costs.json`，UNKNOWN 不填0；任何观察情景都不是实际成交/个人利润。

断网测试：在本目录执行 `/usr/bin/python3 -B -m unittest -v test_readonly_collector.py`。合成头/状态/响应只验证工程；另有已存真实 TM ABI 与提供者 selector 映射核对。测试不联网，不会读取真实密钥。

当前已绑定官方计费/usage、五个部署ABI/runtime与A fee policy；未完成：独立静态release、live 通知字节/N/吞吐/剩余额度、只读聚合实测、14日采集及终态经济验收。所有 live 依赖必须逐项满足；`--live` 不会越过它们。

预检/密钥等待均受2026-10-20 04:10 UTC硬截止的SIGALRM约束；只有预检成功进入ARMED才清除此预检闹钟，不会取消14日终点。第一个技术步骤用3条真实通知按字节投影最低CU；若已超帽即停，不继续展开全扫。

精确响应以gzip成员的不可变byte-range artifact保存（path/offset/bytes/SHA256）；eth_call可使用每64字节差分及最多63层、周期全量基准。`readonly_core.read_artifact_range()`和`reconstruct_rpc_body()`可离线重建原响应文本并核hash。派生快照省略重复latest十字段，字段本身完整保留在RPC原响应中。压缩和差分是证据存储，不是删掉候选/降采样。

Root release格式：`root/live-preflight-release.json`的status=RELEASED_READONLY_A_PREFLIGHT、bindings_sha256、reviewed_code_sha256（core/collector/launcher文件名到hash）、prior_CPU_upper_bound_seconds。任何hash不符在getpass前停止。

V2工程守卫：GetPassWarning在明文回退前停止；服务错误体不落盘。应用读到的头距header时间最多30秒、未来最多2秒；扫描与本轮处理须小于12秒，扫描后socket积压即UNKNOWN停止。应用read不等于wire/provider到达。预检样本仅不同且向前连续的3头。最终资源投影含完整每头实测CU/方法/通知与证据CPU/盘、已用及T0等待，并为日志/最多1000条详情保留192MiB与120CPU秒；额度耗尽停止，不遗漏后继续。runtime-stage.jsonl仅记录无秘密PID/UTC阶段，WAITING不等于ARMED或OBSERVING。
