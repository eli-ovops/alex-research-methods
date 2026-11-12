# run05 既有系统HTTPS路线隔离候选：未应用/未启动

只读一次scutil当前HTTPS配置，仅保留内存中的loopback IP literal和有效端口，必须启用且PACfalse；名称/非loopback/无效端口/读取失败即停，无DNS/直连/SOCKS/其他route回退，不认证不重试。RPC和WS共享同一个route对象。CONNECT仅固定官方host443，不含API路径/key；收到200且默认CA+hostname验证的同SNI TLS成功后，才发送原业务。CONNECT响应8KiB封顶；配置3s、route各I/O≤5s及15s剩余阶段检查，原08:10:50总alarm覆盖预检，不冒任意内部操作精确15s硬保证。

route配置子进程CPU实测一次加入prior，阶段另留children_CPU_seconds以备失败账务，不把等待wall当CPU。系统原配置、proxy地址端口、raw CONNECT headers、原异常/凭证均不输出/存档。既有公共独立BlockCypher核对逻辑保持原样；没有新增源/业务/观察。

默认peak100、仅已有补充授权和精确release才300；原extra2h9db20/peak9b6c及全部经济/覆盖/forecast/no-retry规则不变。447CU/20methods/CPUfloor6425并由Rootrelease最终6475借记+live实际承接；原08:10:50、5.5h、25M actualfree更严、400k方法、7200CPU、2线程、1GiB/2GiB/8h/付款0保留。

5项受影响离线检查PASS，socket.create_connection禁网（只mock假对象）；不读真实系统设置/key，不运行模型/完整collector或无关套件。旧run04源副本/锁/原件身份封存，当前主源不改。Root精确review/release后才应用和唯一打开入口；任何一次成功不证明根因/稳定性或完整A通过。
