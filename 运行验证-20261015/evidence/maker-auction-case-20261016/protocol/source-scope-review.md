# Maker auction-keeper：公开程序、外部定价与许可

结论：官方auction-keeper公开了发现拍卖、筛选不安全仓位、将model报价转成竞标/Clipper购买、余额管理及交易替换的参考实现，主源码为**AGPL-3.0-or-later**。但它主动把估值、何时/多高出价交给外部model；没有实现独立的全成本净利保护。当前材料不能单独支持“完整盈利规则已事前固定并与真实盈利账户绑定”。

## 固定来源

本次官方HEAD返回commit `f052830953d675612b69a2a5b871c7954de8c110`，committer日期2021-09-24T13:16:26Z。[官方README](https://github.com/makerdao/auction-keeper/blob/f052830953d675612b69a2a5b871c7954de8c110/README.md)、[COPYING](https://github.com/makerdao/auction-keeper/blob/f052830953d675612b69a2a5b871c7954de8c110/COPYING)、[main.py](https://github.com/makerdao/auction-keeper/blob/f052830953d675612b69a2a5b871c7954de8c110/auction_keeper/main.py)、[model.py](https://github.com/makerdao/auction-keeper/blob/f052830953d675612b69a2a5b871c7954de8c110/auction_keeper/model.py)、[strategy.py](https://github.com/makerdao/auction-keeper/blob/f052830953d675612b69a2a5b871c7954de8c110/auction_keeper/strategy.py)已按该次tree的不可变blob实际读取并校验内容身份，真实GET、UTC、SHA256与blob SHA见`source-receipts.json`。

Git日期只支持所读取历史版本的元数据，不独自证明首次公开、实际部署、某笔交易所用版本或策略事前锁定；这些对应关系UNKNOWN。未执行代码、安装依赖或审计整套外部pymaker等依赖。当前运行兼容性亦UNKNOWN。

## 程序负责什么

| 环节 | 静态公开规则及位置 | 留给运营者/model的部分 |
|---|---|---|
| 发现与启动拍卖 | README40—48，main402—513：循环扫描拍卖/仓位，判断不安全、Dog总/抵押品容量和dust条件；可按配置bark/bite等启动拍卖 | 选择链、ilk、起始块、是否只kick/只bid、数据源及运行频率。资格满足不等于存在净利。 |
| 拍卖状态与model接口 | main633—760、model156—238：管理每拍卖一个外部进程，经stdin/stdout传JSON状态，解析price及可选gasPrice；进程退出会重启，保留最近输出stance | 外部model的市场价、折价、有效期、费用风险及机会选择。model接口公开不等于实际model已公开。 |
| Clipper购买 | strategy99—157：状态可用且拍卖价≤model上限才尝试take；按DAI可负担数量、min_lot、chost约束决定数量，validate_take后构造take | 出价上限由model提供。没有从可执行退出市场报价扣gas/滑点再检验净利的公开流程。 |
| 旧式flip/flap/flop | strategy199—228、272等按model报价、最小加价/减量、tab等转换tend/dent；main690—742处理过期、redo/tick/deal | 接受什么经济价格、执行成本及赢得资产后如何处置，仍需外部规则。不能将不同拍卖类型规则混用。 |
| 余额、发单与替换 | main665—687、760—835：余额reservoir、成本可负担检查、异步发单，报价或gas策略变化时替换挂单；README198—219描述gas初始值、倍率与上限 | Gas配置、余额、发单账户及实际交易结果；账户能负担DAI成本不是净利检验。gas helper/pymaker内部实现本轮未读，不能宣称完整失败处理已审计。 |

README114—115明确提示不会阻止不盈利价格。README145—154也说明授权、调整余额、启动拍卖等可能无竞标仍产生gas，且未显式处理全局结算。main的实际clip扫描也有无DAI时跳过的局部保护，不能把README宽泛描述替代具体分支代码，但两者都未提供全成本利润门槛。

## 公开报价示例不是盈利证据

README117—133的固定723价格脚本只演示接口和更新间隔，不是市场价、实际拍卖成交或利润记录；不得为它造市场价差后声称真实盈利。README提供的flapper/guy地址是JSON通讯示例，没有运营身份、实际交易hash或完整账期绑定。

README明确链接banteg的[Python boilerplate gist](https://gist.github.com/banteg/93808e6c0f1b9b6b470beaba5a140813)。本次最后一次GET已在收到父任务停止扩读消息前完成，随后停止新增请求；不是新扩仓库。API返回固定gist版本`3d5aefc3e9192d502a99c5e03a47379fcdf897de`，public=true；created_at2020-03-26，updated_at2022-07-31。这些日期不证明当前具体内容在2020已经公开，也不能让2022快照自动成为2021官方版本的一部分。

该单文件`model_flip_eth_a.py`逐输入调用CoinGecko ETH/USD，跳过当前账户已最高出价的拍卖，输出USD报价×0.85。它只实现报价折价，无gas/失败费/滑点、DAI与美元偏离、可执行卖出价或现金损益核算；这是假设折价足以覆盖成本的报价示例，不是实际15%净收益。其API原件只有该文件，未附独立许可；不能把主repo AGPL自动扩展给第三方gist，个人复制授权仍UNKNOWN。本轮未读README另链的NodeJS模型源码，也未推断其许可。

已读README没有明确flash-swap示例链接；已读核心Clipper路径使用可用DAI并直接take，不能把它称作已经核清的无本金flash套利路径。任何其他flash实现、许可、定价规则和真实交易对应仍UNKNOWN，不猜仓库。

## 经济来源、个人复用及实际记录

抵押拍卖购买者付出DAI获得抵押品；可能的收益来自成交折价与之后可执行卖出/持有价值之差，承担价格变化、竞争、未成交、库存、gas及退出费用风险。源码只展示支付和购买动作，不证明该差额为正。启动拍卖补偿、flash借贷、DEX费用等协议经济若要用于特定事件，须由对应合约/交易原件另核，本轮没有用通用叙述代替。

个人研究可按主repo的AGPL-3.0-or-later复用其监控、状态接口、拍卖到交易转换和余额/交易管理代码，需遵守许可条款；允许复制不等于低成本可获利。外部model、依赖许可、部署配置、账户与签名、实时定价/退出路径及完整费用，尚需明确；本轮不提出运行/交易方案。

已读官方README给出2019社区会议视频链接、系统/示例合约与测试说明，但没有与该keeper固定版本绑定的真实运营地址、实际盈利tx或连续完整持仓/费用账下载。真实成交分支由根负责，本报告不重复查账，也不宣称官方其他地方不存在记录。

本轮8次公开GET（HEAD、tree、5个blob、1个明确链接gist）收口；无模型、回测、适配器/策略执行、RPC/EVM、安装、账户连接、凭证读取、交易、付款或外发。实际model/effort UNKNOWN，继承不覆盖；规则PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4。未改原FAILED、封存、root/reviewer或其他Owner文件。
