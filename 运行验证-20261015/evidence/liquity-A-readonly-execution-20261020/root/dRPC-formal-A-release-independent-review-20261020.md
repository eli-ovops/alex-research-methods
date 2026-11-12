# dRPC 正式 A 候选：独立接线审阅

结论：`PASS_STATIC_FORMAL_WIRING_ONLY_NOT_PUBLISHED_NOT_ARMED`，`must_fix=[]`。所审隔离候选满足本轮必要接线验收，可交 Root 按下列精确身份和发布参数完成原已授权的发布；本稿不是实际启动/ARMED/观察完成证明，不增加人工审批层，不把接通当盈利。

审阅开始2026-10-20T13:57:39Z。只读取本冻结候选、原已验预检/观察器的必要相关段和已存原件；不执行入口、测试、模型、策略、收益运算或网络，不读秘密/Terminal/私人行情/QC，不修改执行者、Root其他文件或导航。actual model/effort/route UNKNOWN；原三版规则沿用。本审保守20 CPU秒已由 Root 7440→7460（Root自己20另计至7480），不是实测CPU、不重复借记；旧用量保持。

## 必要发布接线

1. **精确发布门在网络前。** `observer.py:13–32,73–85` 检查真实 binding 的 BOUND 状态、固定 limits/T0/T1、唯一 Root 路径、release 的 RELEASED 状态、binding SHA、四份 code SHA、原量下界及有效启动截止；PENDING模板不能激活。Root完整预检 acceptance/result 的精确哈希及状态被实际核验，再用原Bindings加载源码/ABI/runtime/常量/费用源。独立 formal-start.once 排他创建，旧入口、锁和证据不改。
2. **累计资源承接。** FormalBudget保留25M工程影子/400k方法/18k CPU/10秒3000本地刻度/1GiB RAM；DataEvidence保留8GiB−1MiB项目物理盘口径、完整gzip/delta链。仅删除预检30方法/6MiB临时目录限制。正式WS没有180秒/全局16帧/128KiB永久自锁，而是每消息1MiB/16帧/8控制帧，接收chunk仍检查资源/截止。OS CPU限制按剩余累计量设置，不把等待墙钟当CPU。两线程/零付款/无钱包规则未增路径。
3. **新必要身份与方法检查。** chain/header/五runtime仍同初始 H，以 EIP1898 对象 requireCanonical=true 逐字核绑定 runtime；固定 B 的 logs、首个已列 tx及receipt、number fence 和两条独立 BlockCypher metadata GET 保留。新RPC只放行七个必要公开只读方法，getLogs达到10000条即保存原体后UNKNOWN停，不当完整日志。正常启动19外层方法是预计，不写死为已完成或漏掉失败attempt；两metadata GET另列。
4. **全集/状态/资源刷新。** 新一头initial全扫（额外count）、下一连续头一个稳态全扫。正式Scanner沿已验全ID/status/latest/SP/oracle-last和同H fence，不把105固定成永恒数量；initial padding不得超过旧已准入160。同H count不一致、缺失/重复/越界、依赖/runtime改变、时效或backlog等仍停。forecast将旧三次完整实测和新一次取各项max，连同旧/新wait、通知、最新预算和当前物理盘/实际fs headroom核验；不选择最快样本，不把initial四方法误投稳态。启动全部门通过才取消启动alarm并进入同一进程ARMED_WAIT，启动deadline不能误杀正确14日观察。
5. **真实循环完整。** 全文读取 `observer_loop.py`，与原观察循环的必要差异仅为全部预热头的parent/number连续性检查和首个正式完整snapshot状态证据；qualify、Episodes、同起始资产/费用情景、USD锚、因果日簇/去重/未知gap、100块logs及tx/receipt审计、detail/盘/CPU储备、reorg/迟到/缺失与独立覆盖审查没有被这次接线删除。原固定T0=2026-10-21T00:00Z、T1=2026-11-04T00:00Z；原经济门没有改变，B、真实钱包、签名/广播、模型和收益回测无入口。
6. **WS及失败成本。** FormalWire复制严格帧/fragment/控制验证并移除仅预检寿命帽；严格101/accept、固定host/SNI/defaultCA、同一已配loopback IP路线、无key/环境凭证/回退/失败重发。已recv字节无论成功、partial、保存失败或budget guard，在沿用MF1的结算逻辑中恰一次保留工程影子量；已扣再抛不二扣。内存尾部有界但原始通知/预算/完整HTTP原件仍保存，不能把ring叫漏采。
7. **终态与事实。** prepare、实际startup、ARMED、首个OBSERVING、WINDOW_ENDED_PENDING_INDEPENDENT_REVIEW、STOPPED分开；终态保存异常降STOPPED/固定附因，不能exit0；原失败层保留，旧锁/结果不覆盖。必要结果或stage自身写不成会非正常退出，不能由此前ARMED当完成。后续是否取得完整14日覆盖和A/B经济结论仍须实质验原件。

## Root 精确发布时必须填写的参数（不是候选现在已具备）

- 仅按已声明允许的变更，把 template `publication_status` 从 PENDING 改 BOUND 后保存真实 `binding.json`；其他实质变更须同Owner核差异。独立Root JSON status必须为`RELEASED_FORMAL_A_ANONYMOUS_READONLY`，绑定实际binding SHA、四code SHA、完整limits、原T0/T1及有效`startup_deadline_UTC <= T0`。
- `prior_usage`保留Alchemy32734、当前工程影子至少33850、方法至少93；CPU应填 Root 发布时最新累计保守账，已知本审+Root审后为7480而非回填候选历史floor7440，有后续工作还须保留该新增借记。代码中的7440是最低历史floor，不会替Root自动更新最新账。
- 当前无 binding.json/formal-start.once/evidence/runtime-stage/terminal，候选未发布、未运行、未ARMED。Root确切放行与受控启动仍需真实做出并留回执，不能以本审或离线PASS代替。

## 已验原件、覆盖与非阻断限制

- 完整读 PLAN、正式入口、WS实现、复制循环、模板、8项离线检查源/receipt/stdout；读取adapters相对已验预检的完整差异及必要实现。完整review-package的7新增文件段静态重构后逐一等于实际文件；manifest的13文件+22依赖size/SHA全部匹配。未重新审全repo/全部Solidity，也未重跑原预检或旧suite。
- 离线receipt：8 PASS、exit0、whole wall0.137028167秒、childCPU0.06116秒、stderr0。覆盖寿命临时帽移除、每消息控制限制、七只读方法、日志cap停、PENDING不激活、终态保存失败、原经济/审计正文保留、累计方法不重置。它们是合成接线检查；未做真实新Root正向发布/19方法实际startup/ARMED或长期可靠性测量。无需为形式重复同码检查，实际启动仍须自己过门。
- 模板顶层旧 `status=DIAGNOSTIC_PREFLIGHT_ONLY_NO_OBSERVATION` 是沿用标签，运行门实际检查独立`publication_status`、Root release和真实state；本轮非阻断，不能用旧label推断实际有没有运行。发布时应继续按真实运行回执区分状态，不把PENDING模板叫实际观察。
- RPCbody8MiB、WSmessage1MiB、global lifetime临时帽移除不意味着无限量：原累计帽和接收/请求资源检查仍在。RSS是OS可得peak检查而非macOS精确kernel集体上限；采样/本机UTC误差/共享IP负载/匿名实际CU与月余额 UNKNOWN，不能要求不可能的14日保证，也不能由单次成功宣称无限免费。
- 25M是原Alchemy费表的额外工程等效刻度，绝非dRPC真实余额；Alchemy32734历史不改。服务拒绝/限流/收费要求仍停，不静默转付费或另换路径。backend2秒与完整scan/HTTP往返不是同一计量。
- 必要劳动/基础设施实际成本仍UNKNOWN；技术预算不是劳动实耗，也不是成本0。本A只是完整只读情景观察，不能证明实际抢单获胜、失败费用、个人全成本净利、可复制alpha或容量。没有重开Terms/私人bot/旧模型或旧正账。

## 本轮输入身份

| 隔离候选相对路径 | 字节 | SHA256 |
|---|---:|---|
| `manifest.json` | 12183 | `a977d2964960e106f3aa58126a011bde47e71b6d854477678e1965dc17fb2788` |
| `review-package.diff` | 64140 | `13785d8ebb1793e9179a64bd654b123cb2e9225c60d4a42c4e0eb55f9cf4a011` |
| `source-reuse.diff` | 4544 | `071c5d7d2aae877902901fdd14518d268d253f5bbe6ed82a6a9262babc6e0057` |
| `adapters.py` | 14803 | `e1330a313c7aeb5aac0e66c126cfd7a566943e1df0bb7c7c40729fc13bfee81f` |
| `stream.py` | 13187 | `279e0c1354ac1173a008458776be2657238d68b0a8982d18567dece7068162a6` |
| `observer_loop.py` | 4907 | `de707de821d7413708fa1142bdb397d678b081084e2a9f4dd85cb8be8eb2aa46` |
| `observer.py` | 12578 | `4b583bc326c9cec511d2e42c0bf5ea9f38060b68b103de924cac41842005ea29` |
| `binding.template.json` | 3965 | `fb95c58ced868fce81d6594c9f1fe3bc0c3844712caeed21aa9163ca4a2a1cc1` |
| `PLAN.md` | 9113 | `a8fdc2c186ebc5b1c1f7adcab0433ad6ccb56cd835a12de20d9c697876919c8f` |
| `offline-checks.py` | 4388 | `6239c1c433a6196971da91f71e51c81ef5e97bd5b65c469cc44b1b5a6d524dd1` |
| `offline-checks-receipt.json` | 459 | `33fc615019dd7a5b9fa9b18cd533bc1db079e2005e13e080061ccb9c609cb9d6` |
| `offline-checks.stdout.txt` | 557 | `428a89bfa0a4169687718310ecc75260091a840b525d6d3554a037d5267e0178` |

其他绑定依赖仅按manifest核字节/hash；原完整预检Root实际验收SHA `e9e07e4eade9e296b5b101370f4cb910e4b096033354e183a555952c73ab38cf`已读，其状态严格为本次预检技术层接受。此审稿为唯一新增写入。
