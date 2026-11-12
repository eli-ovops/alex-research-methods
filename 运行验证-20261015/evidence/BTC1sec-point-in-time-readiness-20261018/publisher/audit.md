# BTC_1sec v1：发布者历史生成绑定

**PARTIAL / UNKNOWN：发布者说明能绑定数据来源叙述，不能绑定精确2021生成commit、配置和快照可得时刻。**本轮未证明文件在system_time即可因果使用，也未发现足以判全部数据存在泄漏的证据。

只复读已保存的固定v1官方HTML及其JSONLD元数据。字段路径为 `JSONLD_text[0]` 内 `description`、`version`、`creator`、`dateModified`：发布者Martin Søgaard Nielsen，version1，2021-09-02修改日期；描述为Coinbase websocket原始订单簿消息被聚合为1秒/1分钟/5分钟快照。致谢仅链接未锁定版本的 https://github.com/sadighian/crypto-rl 。这是工具关联，不是该CSV生成版本、命令或配置的指纹；网页修改时间也不是2021实时特征可用时间。

| 问题 | 本轮层级 |
|---|---|
| 发布者指向哪个采集工具 | YES：笼统crypto-rl链接 |
| BTC_1sec实际使用哪个历史commit/config | UNKNOWN：所读原卡没有版本/命令/环境/归档manifest绑定 |
| 原始tick用exchange event还是collector receipt时钟 | UNKNOWN：发布者原说明未给字段定义 |
| 快照网格标签属于开始、截止、结束/延用哪个状态 | UNKNOWN：不能从“1秒聚合”补出 |
| midpoint/spread/静态量与flows在该标签前何时完成 | UNKNOWN：未见available_at/生成时序绑定 |
| 当前固定工具源码的解释 | 由独立code Owner核；不能替代发布者历史绑定，本Owner不重复读或执行 |

使用3次公开精确搜索、2次原生调用后收口：一个搜索只返回2026第三方NanoJev派生分钟集，不能充当作者2021生成说明；另外两个Kaggle限定关键词查询无结果。没有因空结果声称全球不存在原件。第三方片段自行设置60秒availability lag，不是BTC_1sec可得性证据，未跟读或采用。搜索自动出现其派生行情/标签片段是检索范围偏差，未用于计算或存作数据；仅保存脱范围记录，不冒完整原始返回。

最小缺口是**原发布者将固定v1文件身份绑定到实际生成版本/配置与时钟、快照截止/可得规则的原说明或manifest**。不要求私人全部系统或零风险证明，不联系作者、不申请许可、不新增实验；若只能带明示假设研究，应另由根判断，不能写成已核PIT。

读取日期2026-10-18，原生逐次UTC未捕获；本地源当前hash/字节及scope绑定见JSON。没有新ZIP/CSV/行情文件、源码执行、模型、收益、标签或成本空间重算；没有账号、付款、交易。actual model/effort UNKNOWN。完成即停，旧许可/CRC/成本空间结果保持。
