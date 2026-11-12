# 明确迁移链增量核验

**迁移链接已实际跟进；当前collector目录不含旧两样本，尚未形成“相同数据blob＋适用许可”的正面授权桥。**这不是停止在旧repo license=null，也不证明其他目录或历史版本从未包含样本。

旧固定README首行真实指向 `https://github.com/nkaz001/hftbacktest/tree/master/collector`。本轮为每源128KiB界限，先读取新repo非递归root tree，再读取实际定位collector子树的完整递归元数据：
- root tree `5f3ec40b2afb764e0fea112f941ed85523ef4e88`，truncated=false，但仅一层；
- collector tree `c12948c32888742ea1f9b6a18789abd37da6a73b`，递归返回21条、truncated=false，包括Cargo.toml与Rust采集源码。没有sample_data、旧两个文件名，亦无blob `38a1e26f10dde12618a2258bf04560476f867ab7` 或 `14030d53c138fa77e07fbdd5e38e9072f4343043`。

这里确认的是当前明确迁移目标路径的内容变化，不是整个仓库递归审计；未扫其他子树或追git历史，不能扩张为“新repo全局不存在旧样本”。tree身份由API当前master解析后固定；未读commit对象，commit及该tree生效日期UNKNOWN，不把当前Rust结构冒旧Python采集版本。

root还实际列出LICENSE blob `28c446419cb8488ff0825fabb0954bc4d6e8fda1`（1079B）。**本轮只有它的文件元数据，没有读取正文，不能称已重新核MIT或例外条款。**既未在明确迁移collector路径找到同一数据blob，另读泛软件许可也不能自动倒授旧样本。若以后实际取得同一blob在明确许可范围内的原件，应正面采纳；不要求出现“ML”魔法词或额外私人合同。

旧audit、README及draft.txt全部原样保留，只作先前阶段范围；草稿未发送。两次新GET均正常，源小于128KiB，HTTP/UTC/hash已保存，无payload/代码执行/模型/回测/账号/付款/交易。actual model/effort UNKNOWN。

结论仍为这两固定旧样本的适用研究/外部评估许可与历史生成参数UNKNOWN。最小缺口仍是适用于这两文件的许可/生成原说明，而非无上限追版本。此轮完成停止。

