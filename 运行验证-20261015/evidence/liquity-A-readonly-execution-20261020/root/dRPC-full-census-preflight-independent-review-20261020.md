# 最终同轮差异复核：受限静态通过

`decision = PASS_STATIC_BOUNDED_PREFLIGHT_CANDIDATE_ONLY_NOT_EXECUTED`；`must_fix = []`。MF1 与 MF2 均已 ADDRESSSED。仅允许将此结论用于 Root 对本隔离完整预检冻结包的发布判断，不是实际预检 PASS、ARMED、14 日观察完成、盈利或长期服务承诺。以下旧版审阅保留为历史问题及范围证据，其 CHANGES_REQUIRED 状态已由本段覆盖。

本次只复核精确局部 diff、必要 fake-wire 检查源/回执/stdout 与冻结哈希，没有重跑旧 6 项或新 8 项，没有导入/运行候选、网络、日志扫描、金融计算或额外调查。原总 CPU 保守借记 10 秒已含 7365，本同轮差异复核不另加；actual model/effort/route UNKNOWN。此前等待不计主动工作。

- MF1：每次 receive 尝试以独立 before-byte 值和 settlement_started 确保恰一次结算；partial EOF/timeout/验证或归档错误的 finally 亦更新已知字节、解析帧尝试与安全结算字段。Budget.delivered 在资源检查前抛时，已到字节的工程影子欠量补入 cu/window，同时仍抛停机；若已加 cu 再触发 CU/peak 帽则不二扣。没有添加重试/重连或存储异常原文。WS_received_bytes 明示包含 upgrade，单次 receive delta 与通知/工程账继续分列；未知未 recv 字节和 dRPC 实际账单不被补数。
- MF2：finalize_terminal 捕获终态保存异常，固定降级 STOPPED_INCONCLUSIVE / TERMINAL_ARCHIVE_SAVE_FAILED；原固定失败原因另存，最终 return 非 PASS / 非零。结果文件自己写不成仍是未完整结果，不能由 wrapper exit 或局部层冒通过。
- 已读原始局部检查：8 PASS，exit0，whole wall 0.165456084 秒、child CPU 0.066119 秒、stderr0，覆盖成功/partial EOF/timeout/前后保存失败/扣前资源 guard/扣后 cap/终态降级。它们是 fake-wire 局部检查，没有模拟完整新供应商扫描、真实网络或经济优势。最后仅计数 scope 标签及文档变更，无需重复同码测试。
- v2 manifest 31 文件及 18 个旧依赖 size/SHA 全匹配；旧包冻结副本和旧 6 项原始回执保留，adapters/config/原 core、collector、binding 及经济/覆盖/资源/日期逻辑未变。原 manifest 的 old_review SHA 是下方旧版正文历史身份，不是本最终文件的新哈希，不能误当漂移。
- 实际执行前仍由 Root 核精确 v2 身份并给本有界预检唯一指令/外层资源监督；本稿不新增人工审批层，不为匿名余额 UNKNOWN 另造不可能保证，也不将候选当已准入长期数据通道。

| 修订输入 | 字节 | SHA256 |
|---|---:|---|
| `manifest-v2.json` | 16824 | `1026182372831c2ca748000545813f5105598f281be40de1d2df45869dc7fbff` |
| `preflight.py` | 19154 | `d39dde2562da777e8940e40f7d4ca515ef46a891650a009db1102e353c150f9b` |
| `mf1-mf2-v1-to-v2.diff` | 8416 | `71e9f3aa2c242e366d33d057d237680965763c77cc4b6d403fefe9e8a24315c7` |
| `review-package-v2.diff` | 52715 | `a914a92aa74d75342838a806c876225e60f167be7380317e0310519c685b0eaa` |
| `offline-settlement-checks.py` | 3483 | `231d133351bacb595991e3a373c4a0c44e95cb2d37f555fec7a497ee1da441e3` |
| `offline-settlement-checks-receipt.json` | 441 | `96cdb87ba5c8821ba2f51d951db256f95d1144afee435f2df01cb2db4d0b6033` |
| `offline-settlement-checks.stdout.txt` | 536 | `61f49c7758339545fa3ae828ada35473b3ea3cd7a3cdf63bfe6c2317b3450221` |
| `PLAN.md` | 8383 | `733d3bcc4a485458f72181b7002620cd41bdf611ed6de2485b10484d34f4f99c` |

---

以下为修订前完整审阅正文，原字节 SHA256 `a055ad4d8141dcee8e34c5553f493ca6327fe3039c4c6853eef3fb7f4d1c8927`，保留两项问题及已核层；现行结论以上述最终差异复核为准。

# dRPC 完整全集预检独立静态审阅

结论：`CHANGES_REQUIRED_BEFORE_PREFLIGHT`。本版有两项必须修正；尚未执行候选、发出请求或产生完整预检结果。本审阅不放行 ARMED 或正式观察。

审阅日期：2026-10-20 UTC。唯一 Reviewer 沿用原角色与设置，actual model/effort/route `UNKNOWN`。规则版本沿用 `PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4 / HANDOFF-2026-10-10-v2`。只写本文件，不改执行者/Root 其他文件、不派子 agent。本审阅保守 CPU 预算借记 10 秒已含于 7365，不重复追加；不是实测 CPU。候选 READY 后开始实际静态审阅，不将此前等待算作主动工作。

## 必须修正

1. **MF1：WS 接收失败路径不能漏记已接收字节的工程影子用量。** `preflight.py:56–82` 在 `receive_message()` 抛 EOF、控制帧/长度错误、读超时等异常时，可能直接离开；已完整读出的数据若在归档时失败，也可能在 `budget.delivered` 前退出。冻结 `probe.py:96–107,127–170` 的 `Wire.read` 已逐次增加实际 recv 字节，所以这不是纯假想的不可知成本。当前 `WS_received_bytes/frames` 也只在成功末尾更新。最小修订是对每次接收尝试已知 wire delta，在成功与失败终结时都恰一次保留安全计数/固定类别并结算工程等效；若 `delivered` 已扣后因帽而抛出，不得再次扣。不能存错误原文、增加重试或把影子用量叫 dRPC 实际计费；仍未知的字节/供应商费用保持 UNKNOWN。握手原始头与 WS 帧应继续分开。
2. **MF2：必要终态归档失败不能仍返回 PASS。** `preflight.py:202–207` 捕获 `evidence.save('terminal',state)` 的 `Stop` 后仅置 `terminal_archive_save_failed=True`，未改变原 PASS 状态，因此磁盘/证据帽拒绝该保存时，仍可能 exit0。最小修订是保留固定失败类别及原通过层事实，最终状态改 `STOPPED_INCONCLUSIVE`、非零退出；不把缺失归档补成成功，不重跑网络。

请由同一执行 Owner 在隔离包内修正，并只补必要的失败接收计账/终态保存失败离线原件。旧 6 项检查不用重复，也不需要模型、源代码业务执行、真实网络或逐步新增人工批准。修复冻结后只对这些差异复核。

## 已核接线和适用边界

- 已完整读取候选 adapters.py、preflight.py、config、PLAN、offline-checks 与原始检查回执/stdout；读取 reuse-wiring.diff，并逐段对照冻结原 `Bindings/Scanner.snapshot/qualify/forecast/timely/forward_head/ChainTrack` 必要源段、原独立 BlockCypher 函数和冻结 WS Wire。完整 review-package.diff 的 5 个新增文件段已静态重构，与对应文件文本逐一相同；首次工具输出中段曾截断，已通过单独全文读取候选文件补齐，不能将截断输出当全文实读。
- manifest 列 11 个文件及 18 个未改依赖均独立核字节/SHA，全部匹配。依赖的哈希核验不等于本轮重新通读所有 Solidity、ABI、runtime 或依赖安全审计。冻结旧 core `54b09fc1…`、collector `2284076c…`、binding `2b4d1f6b…` 和原锁/账/样本未被本候选改写。
- chainId/header + 5 runtime 同初始 H，以 EIP-1898 `{blockHash:H,requireCanonical:true}` 获取，与封存源码 runtime 字节比较；独立 BlockCypher chainroot + 固定 B 两次 GET 保留。它们是特定提供者返回和有限块身份核对，不证明独立后端、canonical 最终性或未来每个 H 的 runtime 均再次取得。
- 先 3 wait 通知，第 3 个作 initial 完整快照，再 3 measured 完整扫描，共 6 通知/4 扫描头。正常 22 方法与 2 metadata GET 分列。initial 多一 count 不冒充稳态每头方法成本，前两 wait 的 CPU/盘/等待计量仍在。
- Scanner 原全集逻辑未缩减：active+zombie 全 ID、count/padding、缺失/重复/越界、status/latest tuple、注册依赖、SP、oracle 模式和 lastGood；fetchPrice 为最后非持久子调用；同 H 初始 count 与 base count 一致。不同 H 的 N 在固定 padding 内变化正常，不能强制 N 永远为旧 105。
- 原 3 个正向连续 measured 头、age/future/处理时长/backlog/fence 门保留，观察应用读取时间，不冒 NIC 到达/全网最快。资源 measurement 从等待 head 前到扫描/证据落盘后；原 forecast、日志审计储备与磁盘物理分配口径保留。只证明当前工程准入观测，不能保证 14 日永不超帽。
- `DataEvidence` 的 input→data 仅改变缓存键接线；原 gzip/fixed64 delta/base SHA/depth/cache 逻辑保留，已有合成公开字节 roundtrip 支持该接线，不是对新链快照的真实验证。
- Alchemy 历史 32734 CU 保留；本项目工程影子 32945、全供应商方法 71、CPU 保守预算 7365 承接。25M 仅旧费表工程等效硬帽，dRPC 实际计费/月剩余 `UNKNOWN`；官方匿名免费政策、每 IP/方法/响应限制另列，不拿注册账户 210M 或假整数余额作匿名准入。18k CPU、40 万方法、8GiB−1MiB、原线程/RAM/0付款等门未被放宽。
- 原 T0 `2026-10-21T00:00:00Z` / T1 `2026-11-04T00:00:00Z` 固定；本程序只预检，不调用旧 run_live/ARMED/观察。Root 对精确冻结包的单次执行指令及外层 180 秒/资源监督仍是实际执行前条件，不把本静态审阅当网络完成。

## 离线检查证据与未核

原 receipt 为 exit0、6 个 PASS、wall 0.163714667 秒、子 CPU 0.07856 秒、stderr0；Reviewer 只读取未重跑。覆盖 5 绑定/原函数身份、EIP 对象/data 编码、合成 lossless delta、累计方法上限及不调用 live。没有覆盖本次两个失败路径，也未实测 dRPC 全量 snapshot、完整 MC3 大调用响应、180 秒内 6 通知、真实 CPU/盘投影或长期匿名服务余量。后补 metadata attempt counter 仅有静态 syntax，不能冒称已动态覆盖。未知不等于服务不存在或所有免费路径不可行。

完整预检即便后续通过，也不证明个人抢单获胜、失败费、全成本净利或容量；必要主动劳动/资金/费用口径沿原方案，不把技术门代替经济门，也不删除旧历史正账。

## 当前审阅输入身份

| 文件（候选目录相对名） | 字节 | SHA256 |
|---|---:|---|
| `manifest.json` | 10052 | `294a7b6822288e2c3462ec39b397166474217caaa5ec6ea3cff12d28b6a78462` |
| `adapters.py` | 14837 | `406067e55de219a38d8afc156a2ac82a5d754ec8ceb16f59cab765bb3f033385` |
| `preflight.py` | 17294 | `8f55227c1435b27c654db2a97214acc2aeb149dfc3fee55596a7cd48d485cb33` |
| `config.json` | 2649 | `e12c20417b50dc07118248d49c46a9678e7cbdd34963749cb67bda894c58cdf2` |
| `review-package.diff` | 46200 | `d7feb12c151ec12ccf9bbce44c8fc313f5e4bcd2f9585dfa221806059f5d4a7b` |
| `reuse-wiring.diff` | 12594 | `a85273371e953281ee0f7063d8849134e0700a574ef70c5137acb6e3e642dbea` |
| `offline-checks.py` | 3199 | `53839131b22f3c2a9c6c2f1dd8582b1f4b8eb64d752291ca3a552bc864b4ed80` |
| `offline-checks-receipt.json` | 451 | `09036eaa600a19ddf889539ff8df796a2ad3402f565dc8f14d19d617b4c64f16` |
| `offline-checks.stdout.txt` | 427 | `0cb55c5b3c8813f0f3cd2ede51eaba6b4c993c7353330831a69d15f0dbe2376e` |
| `offline-checks.stderr.bin` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `PLAN.md` | 7378 | `79bcc2fb1e933f09afd681217f77022d1175b31b489a4c09f0df9bcdefcf7470` |

输入目录：`/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/drpc-full-census-preflight-20261020/`。其他已核输入及精确依赖身份由上述 manifest 绑定。未读取任何私人行情/QC、秘密、Terminal 或凭证，没有新网络/源码导入执行/测试复跑/金融重算。
