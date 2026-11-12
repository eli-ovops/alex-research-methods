# 冻结源码独立语义审阅

**限定PASS：公开区间构造与调用资格可复核；完整调度及配置历史仍UNKNOWN，不能据此判定真实盈利或完整历史策略已事前固定。** 2026-10-16T08:13:40Z后完成静态审阅；实际model/effort UNKNOWN。源审阅0新增GET、0外来程序/模型/回测/EVM/交易执行。规则PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4未覆盖。

固定commit：774960877e122da12015878ee3a03dfa58536968。root通过公开GitHub仓库HTML currentOid及按commit的raw读取绑定；8项保存原件SHA256均与读取回执吻合，包括7源码/说明/许可及commit网页。各输入URL、源读取UTC、当前输入hash见同名JSON。Git作者2021-10-19T14:44:23+01及提交14:44:31+01只支持元数据日期，不能单独证明首次公开、当时链上部署或2021介绍与此源码完全相同。

| 层 | 静态确认 | 边界 |
|---|---|---|
| PassiveStrategy.sol 104–162 | rebalance先经shouldRebalance，要求msg.sender是keeper、达到lastTimestamp+period、tick移动达minTickMove、偏离TWAP不超maxTwapDeviation、远离价格边界；成功才更新lastTimestamp/lastTick。 | period是最小间隔，不是到时自动发单、必须执行或最长等待时间；首次lastTimestamp默认0，不能当部署时起计。观察调用资格也不证明真实及时性。 |
| PassiveStrategy.sol 104–125及AlphaVault.sol 274–340 | tick按tickSpacing向下取整；base上界额外加一tickSpacing；传入bid/ask区间，vault先放base，再按可部署liquidity较大的一侧放limit；策略传swapAmount=0。 | 是明确的状态依赖区间规则，不是精确50:50保证；不能把文案简式当全部取整规则。vault本身有可选swap路径，不可称所有治理替换策略永不换币。 |
| AlphaStrategy.sol 91–128 | 同为keeper调用、TWAP与边界检查、公开区间公式。 | 本函数没有PassiveStrategy的period/minTickMove条件；不能混称同一实现。 |
| scripts/rebalance.py 24–41 | 单次main遍历3个策略地址，提交rebalance，ValueError时输出并继续，示例gas scaling参数50至1000gwei。 | 没有循环/cron/外部调度器；地址仅为脚本清单，未证实际调用、keeper身份、历史运行频率或全部费用。未读取真实环境变量、密钥或配置。 |
| scripts/deploy_mainnet.py 9–18 | 示例PERIOD=41400秒，即11.5小时；PROTOCOL_FEE=5000。 | 注释约12小时并不等于文案24/48小时。AlphaVault按1e6分母，5000为手续费的0.5%，脚本“5%”注释错误；都不是实际部署配置证明。 |
| AlphaVault.sol 115–150、215–252、559–617 | 存款按当前两币比例铸份额且受cap约束；提现销份额按比例返两币、受min约束；vault重平衡只允许指定strategy；治理可替换strategy/费率/cap并紧急burn；策略治理可改keeper及阈值/period等。 | 不是普通存款者可调用该现存vault的keeper入口；但这不证明个人不能复制公开实现、自部署或选择合法既有参与方式，亦不证明实际keeper具有未公开主观择时。 |
| AlphaVault.sol 352–392 | collect包含本金；先减burned得到fee，再按protocolFee/1e6截取协议份额。 | 不能将全部collect当收入；LP还承担库存变化、无常损失/逆向选择、gas及合约风险。本轮无实际账。 |

## 个人可复用与真正缺口

根LICENSE为Unlicense，三份合约SPDX同为Unlicense，允许个人研究、复制、修改及商业使用其自有代码；依赖OpenZeppelin、Uniswap的具体版本和许可并未在本轮全审，不能推广为整个依赖树无条件无义务。公开规则及单轮调用示例比仅有协议接口更具体，可合法静态研究；没有进行实现、安装或运行。

48h与24h是两页文案；41400是该冻结部署脚本示例。三者应并列保留，不能任选一个当所有实际vault的固定历史规则。当前AlphaProVault permissionless未在这组源码核实，不能归入legacy实现。

本阶段真正缺的是：具体真实vault与此源码版本绑定、研究账期内strategy/阈值/period/keeper/费用配置与变更历史，以及调用调度如何确定/何时发送的公开记录。**这些尚未取得，不等于已证私有择时或不可复制，更不构成新的全实体多年费用门槛。** 如后续限定真实vault账期，可分别证明公开区间逻辑、实际调用与扣费账本，不能因为治理可变就直接否认该段可核的历史结果；也不能从公开逻辑直接宣称完整政策事前锁定或盈利。

本次未核任何收益榜/赢家或真实收益、未核部署字节码，首次公开精确时点UNKNOWN。缺项按证据层保留，未把UNKNOWN写成策略失败。

补读root/source-policy-findings.json九项：实质事实和限定推断与已读源码一致，PASS。可变权限不等于实际更改，用户自行存取不单独否定份额净值评估；评估基金份额需限定账期完整份额/资产流水。未增加全实体、多年费用或未来持续盈利等必需门槛。输入指纹已追加同名JSON。
