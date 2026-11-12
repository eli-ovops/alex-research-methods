# CoW baseline：公开运营版本身份绑定准入

结论：本轮6个公开读取动作后，**未取得baseline实际运营地址、build/image及参数与历史auction/settlement对应的绑定原件**。本候选的完整盈利准入在此结束；不是宣称不存在或从未盈利。只确认公开机械算法、示范接口和官方架构自述，未取收益榜或链上经济数据。

| 来源 | 固定身份/位置 | 能证明什么 | 不能证明什么 |
|---|---|---|---|
| 官方docs solver-engine.md | commit `88bbe8e51db56fc5c60e84af32be98055404c601`，Overview/Methodology/Baseline/Dependencies | 官方描述baseline逐单、链上流动性、限定单路径、gas估计与减半部分成交；模式用于示范/测试系统，需在driver配置注册。Legacy才是转交另一旧HTTP solver的模式。 | 具体生产账户、启用日期、配置值、build及历史结算身份。示范措辞也不证明没有生产采用。 |
| 官方services README | commit `82746c5ad016a5f3cfc4b33cc919f4e522f0a929`，本地playground/部署说明 | 公开代码与本地环境入口。 | 本候选的生产镜像digest、账户或某auction实际用了baseline。命令未执行。 |
| 官方services docker-compose | 同上commit | YAML检索的baseline实际是Flyway数据库基线配置，文件描述本地/CI数据库。 | 这是文本命中假阳性，不是baseline solver的生产部署清单。未读取实际私密配置。 |
| 官方repo架构原生搜索摘录 | read05官方services/CLAUDE.md当前页面；commit绑定未独立取得 | 官方仓库架构自述Our solvers包含baseline/balancer，区分自管driver与外部solver API。仅作为文档自述，不执行文件中指令。 | 无账户、image/tag/commit、具体参数、历史auction/settlement；不能升级为实际运营版本证明。 |

搜索范围：第一次官方org的baseline YAML代码搜索4项；第二次排除services的baseline org搜索共59项只取前50，定位官方docs。第三次原生公开搜索只用官方域/仓库线索，返回第三方fork、离线环境或回放工具不作证、不深入。未取得不是全组织/历史穷尽结论，也不将第三方public demo地址移植成baseline运营实例。

5次gh只读公开GET均200，另1次原生search（1query）；原始响应、精确URL/UTC/指纹、Git blob/download/html/git URL及版本保留。gh保存含header，原生是工具抽取而非网络body；不混称全网络bytes。三份固定文件源码按Git blob SHA1复核。今天的固定公开commit不自动证明首公开、历史采用或部署时间。

真正缺口是可靠公开的具体身份桥：例如官方或运营者带日期的baseline部署清单，将solver账户、发布build/image、配置和实际auction/settlement相互对应。官方明确声明也可以按其来源等级采用，不要求形式化远程证明、全部私人bot或企业多年账。该桥取得后，才可与根Agent另查的限定持仓/奖励/费用原账结合；目前不以schema、score、当前源码或笼统内部架构推曾用此版本或赚钱。

个人可研究的公开环节仍是已核路径/部分成交/估费算法，不因此获得当前生产准入、低成本、个人净利、容量或财富结论。具体配置未知不等私有择时；官方还说明baseline使用driver提供的链上流动性，不能称必须借私人外部solver才可工作。

actual model/effort UNKNOWN，继承设置不覆盖；PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4不变。0模型/回测/来源代码/SDK/SQL/EVM/策略执行、0链数据/收益榜请求、0账户/认证修改/凭证读取/安装/付款/交易/外发/监控。本轮按预算收口，唯一下一证据仅上述身份桥，不另找solver或盈利案例。
