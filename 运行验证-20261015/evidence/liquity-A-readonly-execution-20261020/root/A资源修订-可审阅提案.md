# A资源修订提案：使用现有免费余量，保留完整核对

2026-10-20。**仅提案，尚未批准、应用或运行。旧A配置仍停止，没有live release、密钥输入、RPC或观察。**

建议只修订一项用量和一项时间条件：本单A+B累计CU帽由1000万调整为2500万；适配与预检累计上限由2小时调整为3小时（包含此前，不清零），且收到新批准后的新增窗口仍最多1小时，先到即停。其他资源、数据覆盖、市场、选择、费用和经济标准不变。先实测原方案能否成立，不先开发复杂的增量状态维护去节省目前尚未产生美元账单的额度。这是研究效率判断，不是盈利结论。

## 已完成的依据

- 10M项目帽、账户页面30M免费余量、现金新增付款0是三种约束。原预算准入失败不是个人净优势的经济反证。
- 当前v2每块固定两次aggregate加一次fence，即3个外层RPC/72CU，无按仓位数增加的分页RPC；仓位增多影响内部计算、响应和本机资源。Root先前“分页”措辞需更正。
- 即使假定能删fence，按原newHeads完整14字段文档与最短JSON结构，固定投影仍为10,140,480CU>10M。这是条件性文档算式，不是实际通知或账单。
- EIP-1898明确hash及requireCanonical语义；Alchemy目前明确披露裸32字节hash字符串，但对象requireCanonical支持UNKNOWN。最小正确性适配是：**两次状态读取都绑定同一H的已披露hash格式，保留最后按区块号核对H**。不依赖未证的canonical对象，不删fence，不把number加末尾fence当作所有读同H的保证。

## 待一次批准的完整单元

批准修订后，复用同一执行Owner完成最小参数/请求适配、必要离线错误边界检查和独立定向复审。之后才由用户在本机隐藏提示中输入自己的Alchemy HTTPS RPC URL；key不进聊天、argv、env、文件或日志，不读取浏览器key面板或凭证文件。全单连续推进，不逐步重新问批准。

运行前只读复核实际免费余额，以项目新帽和实际余额中更严者为准；不加卡、升级或购买资源。预检核chain、当前代码/依赖、同H完整ID（含zombie）、协议取价、池余额、实际通知字节、完整扫描方法/CU、本机时钟/CPU/内存/磁盘、独立块身份、错误及陈旧/积压。先投影14日资源；超任何帽、状态不完整、来源拒绝或时序失败，保存原件即停，不改规则择优再跑。

只有预检满足原要求，才固定下一UTC零点为T0，结束T0+14个完整UTC日。原市场/分支、全额池覆盖、单仓位/每日风险簇、补偿及费用选择、USD锚、UNKNOWN、经济验收均保留。原唯一一次观察尚未启动；本修订不增加观察次数，不自动延长或进入B。

## 资源与停止条件

| 项目 | 拟修订或保留 |
|---|---|
| CU总帽 | A+B累计25,000,000，包含此前实际使用；实际免费余额更严时从严 |
| 适配/预检 | 累计上限拟由2小时改为3小时（含此前，不清零）；新明确批准收到后新增窗口≤1小时，与累计帽先到即停。只有新批准生效后，才记录新UTC截止并替换旧04:10UTC条件；未批准前不延长 |
| 人工 | 原全单8小时总帽保留，包含此前必要新增工作，不重置；实际个人劳动UNKNOWN不填0，不用AI时间冒充 |
| 本机 | 原2线程、累计CPU2小时、内存1GiB、累计新增磁盘2GiB保留；既有使用及保守借记不清零 |
| RPC/吞吐 | A+B共40万方法、峰值100CU/s保留，服从平台更严限制；批量与订阅计费照计 |
| 金融与付款 | 新增平台付款0；不运行模型/训练/收益回测，不连接钱包、签名、广播、交易或B |
| 失败/超限 | 立即停受影响阶段，不缩短窗口、漏仓位、降采样、换分支、换身份绕拒绝、改指标或补跑 |

25M不保证足够，也不保证其他帽能通过。当前没有实际N/通知/扫描资源测量，没有市场结果可供择优；本修订只放宽资源用量，经济门槛不变。未经明确批准，不能提高任何帽、恢复采集或启动替代配置。

## 必需交付与证据

最终分开交付：①最小改动、离线检查和独立复审；②真实预检通过或具体停止原件；③若通过，实际活进程、固定T0/T1，结束后完整覆盖/候选/已错过/UNKNOWN及必要成本情景。①不能冒充②或③；A不证明个人抢单成功、全成本净利润、稳定优势、资金容量或财富目标。

- 原批准范围：[authorization.json](</Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/root/authorization.json>)。
- 请求布局：[static-request-economics.json](</Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/static-request-economics.json>)。
- 规范/提供者：[hash-bound-read-feasibility.md](</Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/source-owner/hash-bound-read-feasibility.md>)。
- 经济解释：[budget-vs-economic-stop-scope.md](</Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/method-review-owner/budget-vs-economic-stop-scope.md>)。
- 删除fence仍超帽：[no-fence-schema-bound-review.json](</Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/method-review-owner/no-fence-schema-bound-review.json>)。

本提案没有改变现有停止状态，没有产生新的盈利证据。
