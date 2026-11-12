# 官方发布附件与状态归档文档准入

**未取得 ETH-BTC-USDC momentum 的真实历史state快照或独立生产版本绑定。** 本轮取得的是官方发布清单及通用运行/记录文档，不能改变“目标实盘原账尚未取得”的判断；不是目标不存在或没有盈利的证明。

范围：6次现有gh公开GET，均200，25秒/次、1MiB响应上限后停网。逐实际URL/UTC/HTTP捕获bytes/SHA、原响应及两个文档Gitblob指纹见read-receipts.json及同名JSON。只读文档，无来源代码/SDK/SQL/EVM/模型/回测/策略/命令执行，无账户认证/凭证/安装/付款/交易/外发；actual model/effort UNKNOWN，规则版本沿用。没有接触受拒策略索引、executor或目录网页。

## 实际查到什么

1. 官方API `repos/tradingstrategy-ai/trade-executor/releases?per_page=10&page=1` 本次返回3条：v1242（published_at=2026-06-05T20:56:20Z）、v1241（2026-02-24T18:30:57Z）、v1240（2026-02-24T14:54:32Z），三条assets都为空。它们是当前该接口返回的发布记录；未见目标2024快照附件，不能推旧版本/移除附件/别的发布渠道从未存在，更不能用软件release发布时间当数据首公开时间。
2. docs限定`state.json`搜索返回两条；docs中`state backup`返回3条；`state archive`返回8条。保存完整搜索原件，只把结果当路径发现，没有把所有命中当正文已读，也没有搜索或打开别的策略盈利榜。
3. 根据实际命中读取`docs/docker.md`不可变blob **25a36e235b86cf6268ec34ad35aeeab330c2900f**，4569B。说明每策略执行器独立container/domain，参数由环境配置，持久state目录映射且跨实例共享、文件必须按策略区分。Production维护段强调须使用同部署image/env/state volume，权威state路径和备份，并说明特定repair可重写state。示例是hyper-ai，**不是本候选归档下载链接/地址或2024生产证明**。这仅说明文件 provenance 应和具体执行器/部署/备份版本对应；不能据存在repair推目标数据已被改或造假。
4. 读取`docs/strategy-input-recorder.md`不可变blob **6241d204df2c4b61ef24ad243574f2d41e99cce0**，5724B。开头明确该recorder保存live决策输入与计算，**not a state archive or a replay engine**。Stored data表列runs/source reference/策略与executor身份/package版本、parameters及decisions；正文明确正常state仍是portfolio/trade history的权威文件，recorder仅留路径和关联ID，明确排除state-file copies、完整API响应及credentials。没有目标state快照或公开下载地址。其live-only recorder说明不等于任何普通state JSON均为真实实盘，也不回填2024已启用该recorder。

两个blob由当前搜索定位，固定Gitblob指纹已核；本轮未把它们独立绑定到根已核34fc7eb… commit，也不以现行文档证明2024部署同结构/同功能。Git日期、当前文档或source reference字段都不是实际快照的首公开/身份验证原件。

## 可支持与缺口

官方通用文档支持：策略运行有持久state文件、具体执行器关联，状态可作为portfolio/trade history的应用记录；同一部署image/env/文件及备份 provenance 值得核对。字段设计提供关联能力，不是本轮已取得目标数据，也不独立担保成交、Gas、全部资金流或盈利。

尚未取得目标文件确切公开URL、原发布日/版本/大小、实盘vs测试标记、执行器/链地址与历史规则绑定、完整持仓/成交/费用/资金流。许可对实际快照数据是否适用也UNKNOWN；不把上阶段历史代码AGPL自动移给独立账本或第三方数据。没有可交根代理下载的新候选大文件路径。

下一最小证据仍是同一候选的实际公开state/备份发布原件及其运行身份，而不是更多通用功能文档、全部私人bot或多年企业账。根另查同名JSON/fixture，此分支不重复；fixture即使含真实hash也不能单凭此证明完整实盘净利。本轮到6GET收口，不自动扩展。
