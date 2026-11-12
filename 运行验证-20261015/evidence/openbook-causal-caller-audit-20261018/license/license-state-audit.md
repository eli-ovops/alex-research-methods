# 固定重建工具许可与发布者初态说明

结论：**固定第三方工具代码 MIT 已原文核实；数据 CC BY 4.0 是另一对象。现有发布者说明未明确提供可独立启动任意小时的初始快照或真实 collector-arrival 时钟。**

## 代码许可

唯一 GET 为固定 commit `5c1ee3488c9780b98e42f6077dd4d0434d52ce2a` 的 [LICENSE](https://raw.githubusercontent.com/KimSoo7261/hyperliquid_microstructure/5c1ee3488c9780b98e42f6077dd4d0434d52ce2a/LICENSE)。HTTP200，1065B，Git blob `3f12375da94d67d6a10b3e77c4e8c42321e4e179` 独立匹配，SHA256 `2a2b5dd42321a58131192d17602f1e2a6136a8c706a7bcd6b55e794f1bcfecf1`。版权主体为2026 Zijin Su（L3）。

L5–14允许使用、修改和分发软件及关联文档，含商业使用，须保留版权与许可通知；L16–21为无担保/责任限制。该软件许可不把第三方市场数据改成MIT，不保证重建代码正确、历史数据权利完备或利润。发布者数据README L151–153另标CC BY4.0，保留其署名等条件。

## 仅复读已有发布者 README / SCHEMA

- README L25/L37声明2025年12月有744小时、无缺口；L81–102示范按小时读取。只是文件组织/读取接口及作者完整性声明，不证明每小时自带可用完整簿初态。
- SCHEMA L293–382列book diff字段及变化语义。L381指引从空簿按顺序应用事件，L382用oid与status关联；没有明确初始snapshot文件/记录的身份、任意小时边界重置的正确条件或首个状态覆盖证明。因此“从空簿开始”不能等同“任意小时独立重建已验证”，也不能据缺说明断言一定不可重建。
- SCHEMA L28、L135–138为status的事件时钟；L290说trade时间反映链区块时间。未见真实collector-arrival字段。book diff字段表本身未列timestamp或sequence。
- 小文档足以确认更新级研究潜力，但初态、跨小时承接与可因果时间关联仍需相应证据；不能以真实到达语义未知否认所有事件顺序研究。

未读取数据payload或加载运行代码，未构造模型/回测/收益。1次正常默认TLS GET，无认证/拒绝/重试；UTC与HTTP回执已保存。其他输入只本地只读，actual model/effort UNKNOWN。完成即停。

