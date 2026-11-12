# 单一live候选：Taoshi Vanta Network，原账链未闭合

本轮只核一个新候选Vanta Network（Taoshi/Bittensor SN8），3/4公开动作后收口。**没有取得满足“具体事前预测策略→完整后续持仓成交→实际全费用”的合格案例。** 这是本轮有限结果，不是断言其他地方不存在，也不因文档/入口缺口否定项目。

## 真实取得与版本

1. 一次精准公开检索，实际命中维护方GitHub README、miner说明及官方docs。保存 `01-search-official-candidate-excerpts.native.txt` 为与本候选相关官方结果的原生摘录（未保留无关第三方/学术结果，不称完整检索原文）。检索缓存只当线索，不把其中交易收益/透明度宣传当事实。
2. [维护方miner说明](https://github.com/taoshidev/vanta-network/blob/main/docs/miner.md) 的正常公开[raw文本](https://raw.githubusercontent.com/taoshidev/vanta-network/main/docs/miner.md)实际GET200，2026-10-19T04:01:00.961197Z，44982B，SHA256 `4a121a56ff00ea6a7a2fcf33a46b73d25f40f63c6dc9d6f3600da963a522b293`。保存 `02-miner.md.inert.txt`；计算Gitblob为 `3da8ff1df6a059541b8521ed488264cc8805c8ab`。这是mutable main文档的本次固定内容指纹，未取得commit/tree，不冒充独立tree校验或全部策略实现。绝对发布日期/此文档revision UNKNOWN。
3. 文档实际给出的mainnet [dashboard](https://dashboard.taoshi.io/) 原生open返回 `(404) Not Found`，2026-10-19 04:01:00–04:01:09 UTC窗口，精确秒/底层HTTP状态未独立捕获。保存 `03-dashboard.native.txt`。按LOCAL_BLOCKERS作定向查询后不重试、不换身份/host。不是已证登录后可见或永久下线。

## 是否满足要求

| 环节 | 本轮官方原文证据 | 限度 |
|---|---|---|
| 真正方向预测而非纯借贷/清算 | miner L5–7把LONG/SHORT仓位明确解释为对未来价格上/下行的预期 | 网络接收各miner信号，不是本轮已识别的一套可复制预测算法或具体个人strategy |
| 事前记录 | L521–532描述提交信号→validators建仓/跟踪→FLAT结束的流程 | 规则流程不是实际带时间戳的接受回执；未取得一位miner事前信号与不可变发布证明 |
| 持仓/成交原账 | L316–325列Emissions/Performance/Penalty/Debt ledgers；L532提到含open和closed positions的评分 | 只取得字段类别/规则说明，没有实际匿名原始positions/orders、交易ID、数量价格和费用manifest |
| 实际可见性 | L776–793给dashboard入口，并称自己的private positions/orders须钱包认证 | 本轮未登录；这不证明所有其他公开数据都不可得。实际入口404，未取得公共原账清单 |
| 成本 | L404–440描述carry、slippage、spread，明确模拟现实成本；Hyperliquid-sourced pairs使用live funding rates作计费依据 | 模拟费用或使用真实市场费率，不等于实际经纪商/链上fill和实付费用。未核全部数据/API/模型、算力、注册/抵押成本账 |
| 开放损失 | L329称持续观察当天风险，L532按open与closed位置评估；L93–101又说明部分时段估值限制 | 有未平仓风险的规则意识，不等于取得当时全部浮亏、标记价格与完整清算账 |
| 固定源码/公开权利 | 有维护方公开代码仓库与文档，当前文档内容已hash | 没有固定miner策略源码/参数/权重、代码LICENSE正文或信号数据再用许可。文档L806起禁止违反原provider条款的第三方策略，不是对所有信号/数据/服务的开放授权 |

## 谁为什么付钱

L316–325、L482–485描述按此前表现/惩罚计算所需payout，并由ALPHA/TAO/USD计价emissions账衡量实际奖励与剩余欠款。这是为网络信号表现配置的协议激励机制，不是已核的市场交易对手支付的投资净利润。文档称目标是让信号对平台外更有价值（L406），但本轮未取得真实付费客户的signal采购/复制成交/净利账，也不能从token奖励直接推出预测alpha。未计算任何token价值、收益或经济持续性。

## 研究裁决与停止

Vanta比只有排行榜的候选多出方向预测与记账规则线索，仍未通过本轮要求的完整原账验收。最小关键缺口是：某一具体预测策略/账户可公开绑定的事前接受信号，以及同一身份后续真实成交、开放风险和实付费用原件清单。网络模拟仓位/费用、协议奖励或透明度宣称不能替代。未启动注册、钱包、miner、订阅或交易，不把额外付费/身份动作当默认下一步，也不写执行提案。

本轮未读任何已关闭项目，不开第二候选或论文分支。没有下载数据/权重包、反序列化、导入/执行来源代码、模型训练/回测/新收益计算、登录/凭证/APIkey、付费、安装、外发或交易。只写live/；actual model/effort UNKNOWN，PERMISSIONS-2026-10-14-v1/ROUTING-2026-10-13-v4沿用。预算未耗尽不强行增加读取，终态停止。
