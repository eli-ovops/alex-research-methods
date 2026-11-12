# 第三方重建源码：时间恢复与初态限定审查

结论：这是使用后续锚点、trade匹配、回填与启发式状态处理的后验历史重建。它提供可复用代码原件，不能证明每条diff当时已可定时、时序唯一正确或初始book完整。是否某个预测实验已经未来泄漏仍为UNKNOWN，须看具体决策截点与数据可用时间，不能仅因使用后续锚点断言所有用途泄漏。

固定第三方仓库 [KimSoo7261/hyperliquid_microstructure](https://github.com/KimSoo7261/hyperliquid_microstructure)，commit `5c1ee3488c9780b98e42f6077dd4d0434d52ce2a`，tree `71243ff443342494911999043ed7e0b7c74b1bfe`。它不是Zenodo原作者规格。完整tree `truncated=false`；两源码的Git blob SHA与tree一致。

| 实际实现与源码行 | 对预测因果可用性的含义 |
|---|---|
| timestamps:33–50要求opens/cancels为每oid首个open/cancel；按seq左连接，new取open时间、remove取cancel时间 | 订单级匹配约定不能证明每条diff事件唯一对应；上游first选择与seq生成未读 |
| timestamps:89–134用forward-fill取prev_anc、backward-fill取next_anc；按oid forward-asof找prev_anc后首笔trade，不晚于next_anc才接纳，否则前锚点fallback | 使用后续anchor约束及可能后到trade；没有available_at或等待延迟证明。无逐diff一一成交匹配保证 |
| timestamps:149–161将缺失ts向后填充，再以cum_max强制非replayed序列单调 | 有后向回填，无线性时间插值；修正一致性不是恢复原始接收时钟的证明 |
| timestamps:55–86以默认20个连续倒退anchor识别重发段；162–185整coin-hour按oid检测new+remove且同恢复时间的ephemeral | 长段判别和ephemeral需后续记录；若提前用于改变较早时点book须另证延迟与可用性。book:498–500预期调用前已剔除ephemeral，实际调用层未读 |
| book:466–489空映射/全零数组初始化，无snapshot；257–305遇恢复时间gap>5s清空book，起点/重置后120s gated，倒退时间diff跳过 | 这些是实现假设与暖机政策；120s过后不保证先前仍挂单已全部补齐，无法替代snapshot认证 |
| book:423–456对未知oid update/remove只增加miss统计；90–103输出gated标记，262–267在下一时间出现时emit前一block | 状态可能遗漏；gated是否真被下游剔除未读。block-close状态须在block完成之后才可用于决策，不能无证回用至block内 |

合理用途可以是离线描述、重建候选或在明确等待到所有依赖到齐后的分析；目前没有实际arrival/available_at原件、事件级唯一映射或实时等价复现，故“当时可得”和“唯一正确时序”均未证。没有净利、容量或可交易性结论。

本轮4次公开GET已用尽，均HTTP200。首次HEAD endpoint含大diff，在262,144B触发curl56大小保护，原件明确partial，仅完整前缀用于commit/tree定位；查询LOCAL_BLOCKERS exact error无命中，未重试。随后固定tree为19,130B，两源文件分别8,862B和19,348B，均完整。UTC获取窗口2026-10-18T10:30:28Z至10:30:53Z；逐URL/大小/SHA256/预期与实际Git blob SHA见source-receipts.json。没有伪造精确单请求时间。

未读README全文、LICENSE正文、pipeline调用层、真实行情、fixture/test、运行输出及下游预测样本。因此许可证仍UNKNOWN，不把作者MIT自述或单元测试当原件许可或真实重放证据。若根Owner决定继续，最小下一步应只核固定commit调用层与原始数据审计输出如何标availability和量化时序/初态质量；本轮不追加读取。

路由目标gpt-6.1-sol/medium，实际model/effort/速度UNKNOWN。沿用已读PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4、HANDOFF-2026-10-10-v2及只读范围。0源码/decoder/fixture/test执行、行情包/仓库下载、安装、模型训练/回测、账户/凭证/认证变更、交易或外发。所有产物仅在本third-party-reconstruction目录并为证据保留。
