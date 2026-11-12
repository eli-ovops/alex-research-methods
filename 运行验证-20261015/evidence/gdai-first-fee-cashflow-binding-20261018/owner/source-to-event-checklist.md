# 单笔Reward：从源码到交易费实转的判定表

这里只准备判定规则，不宣布目标交易通过。沿用根已固定tx `0xa2e287bac295e81e51c2b0234b447dc4f9500d88e552552f094563847d99e07e`、block `0x3050a0a`、vault logIndex `0x6`，不重新筛选记录或读取浏览器。

| 要核什么 | 最少实际原件 | 只能作为线索的情形 |
|---|---|---|
| 同一成功交易 | 回执字段原件的状态1、chain42161、txhash/blockHash/number、各logIndex和原topics/data；时间另来自块／交易详情 | 正常完整加载网页的实际字段可作UI原件，注明层级及缺字段；不强制另取RPC JSON。仅名称或timestamp0占位不够，不重取被拒资源。 |
| 金库reward | emitter为gDAI proxy；RewardDistributed的indexed sender为callback6c612…28f46，非indexed assets原量A | Reward单独不能认交易费，因为GToken函数无角色限制。 |
| 实际DAI入库 | DAI合约Transfer：callback→gDAI，value=A，与reward同笔、顺序相容 | 同名Transfer但emitter不是DAI，或按汇率给份额转移标值，不是实收DAI。 |
| 费用归属 | callback proxy发DaiVaultFeeCharged，indexed trader=T、valueDai=A，位于对应reward后 | 其他地址同签名或没有匹配A的费用标签不能顶替。trader不是存款者身份。 |
| 上游钱流 | 同段DAI Transfer S→callback，金额A，先于callback→vault；S由实际原件识别，若称storageT资金须另有配置绑定 | 不猜storageT地址；一笔多段相同数额须按log顺序消歧，不能只搜到一个相等数就归因。 |
| 平仓识别 | MarketExecuted应核callback emitter、orderId、trade.trader=T及open=false；或可靠解码的其他平仓路径 | 泛订单事件不等于平仓。复杂Trade tuple布局未在这两文件定义，不猜topic或word位置；缺可靠解码就限定平仓身份未核。 |
| 历史版本 | callback及vault在该交易时点的版本证据，与采用源码／ABI一致 | 初始部署、当前UIImplementation或代码存在不能替完整升级史。 |

两个金额相等的事件不够：应连起**storage来源→callback→vault资产实转、同额Reward、同额DaiVaultFeeCharged**，并保留同交易的平仓识别及版本局限。若只能确认其中部分，就写部分绑定，不以缺完整窗口为由否认已经观察的单笔现金。

## 源码及topic

Callbacks L120定义DaiVaultFeeCharged；L750–760把closingFeeDai+nftFeeDai传入交易者结算函数；L772–780在positionSizeDai>0分支将closingFeeDai的治理比例部分经storageT转到callback，再调用vault.distributeReward及emit fee。GToken L137、L721–729从msg.sender拉asset并emit reward，事件sender不是任意传入标签。

本地两份源码路径／SHA及行号、独立纯Keccak算得的RewardDistributed、DaiVaultFeeCharged和Transfer三个topic0均在JSON。未运行来源程序、ABI或EVM。MarketExecuted／LimitExecuted包含外部定义的Trade tuple，两个输入中不足以确定其完整规范签名，本轮明确不生成未核topic。

此表尚未核实际目标。即使单笔链路通过，也只支持该笔毛交易费进入金库：不是全部500／933次来源验证，不是该持有人直接取得全部奖励，也不是扣除PnL、借款、全费后的净利或个人预测优势；不能将Reward与同一Transfer重复计收入。手续费比例可治理变更，注释示例不是历史值。gas和成本另取receipt定义，本轮不算。

actual model/effort UNKNOWN。仅读两份已有源，新增网络、浏览器、链调用、模型、回测、收益核算、账户、付款及交易均0。状态`SOURCE_TO_EVENT_CHECKLIST_ONLY_TARGET_NOT_YET_ADJUDICATED`，完成停止。
