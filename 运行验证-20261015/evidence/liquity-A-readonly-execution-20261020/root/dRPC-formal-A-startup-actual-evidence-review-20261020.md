# dRPC 正式 A：实际启动原件独立验收

结论：`PASS_ACTUAL_STARTUP_AND_ARMED_AS_OF_SAVED_EVIDENCE`，`must_fix=[]`。这次正式启动有独立的新原件支撑，不是移植先前预检PASS。保存证据显示唯一PID9735在2026-10-20T14:04:27.316256Z进入ARMED_ACTIVE_PROCESS；固定尾部证据至14:06:37仍是T0前warmup，正式A样本0。此审不宣称此刻重新实测健康、完整14日覆盖、个人盈利或容量。

审阅开始2026-10-20T14:08:29Z；只读指定launch/index/closed admission，以及固定闭合启动前缀和必要成员。活归档累计只读取219478字节（含两份已闭合snapshot的再次窄读），定向输入在384KiB上限内；没有读/hash活归档整档、循环poll或重复health。未请求网络、重跑预检/Scanner/qualify/forecast/策略/测试、读秘密/Terminal、改文件/活进程或重启。仅用stdlib gzip/JSON及已冻结的原件/ABI解码辅助定义，未计算收益。actual model/effort/route UNKNOWN。CPU保守10秒已含7602，不再加；旧原件/预算均保留，原三版规则沿用。

## 本次实际身份与原件

- launch记录固定`.venv/bin/python -B -E -S observer.py`，stdin DEVNULL、无地址/凭证参数；PID9735，单次启动14:03:47.692456Z，独立session。真实binding为BOUND，Root release为RELEASED_FORMAL_A_ANONYMOUS_READONLY，四code SHA与已审候选及当前文件逐一相同。release启动截止14:12:48.151556Z，实际启动及ARMED均在其内；ARMED后的观察不受此启动截止误杀。
- 真实release的prior为Alchemy32734、工程shadow33850、方法93、CPU预算借记7602；固定T0=2026-10-21T00:00Z/T1=2026-11-04T00:00Z及全部原帽未改。7602是保守预算账，不冒历史CPU或劳动实耗。launch时PPID9734和后续Root核到PPID1符合launcher结束后的reparent，不能据此判重启；本审未再次ps或碰进程。
- 固定活归档前缀`[0,170297)`完整解出26个gzip成员，前缀SHA=`c4f9886aca968c344483d49859dc9503aa052413b68b83db0a92770a8f365560`；另按index读闭合区间`[170297,203730)`及最后warmup成员`[231198,232527)`。相关成员的offset/长度/SHA与index一致，zlib gzip完整结束/CRC成立；不是原子整档快照或整个未来archive的最终SHA。未读取两个区间之间未选的warmup成员。
- 所选34个成员含18个HTTP响应，逐一还原full/delta body并核长度/SHA、JSON-RPC id/result、HTTP200/error-null；加一次WS subscribe，实际新增19个Ethereum方法，累计112；两BlockCypher metadata GET另列，不把它们静默写成RPC或供应商账单。

## 新读的实质数据

1. **五runtime新H核回。** 本次chainId0x1，初始B=`0x1904d9f`、H=`0xa5235a084c27f94629afce7d299d6f3927977111a34640089531464516fa2c94`。五getCode的EIP1898对象都固定此H/requireCanonical=true；实际解码长度及SHA匹配已封源绑定的TM23779B、registry3326B、SP8198B、feed1629B、MC3 3808B，不是复用先前预检的live code值。仅认证此初始H，未声称每后续头都重取runtime。
2. **新审计接口。** 固定B的TM getLogs真实返回空数组，只证明该次范围；块transactions第一个hash=`0xc8bc907aa41c6b85364c68e4ddc418ce266c87d8b8c4b5f48bb2e583e1a6bd0e`，新tx/receipt的hash、blockHash、blockNumber均匹配该B/H，receipt status0x1；最后number fence仍同B/H。它是预定首行接口兼容性检查，不是清算利润选样。
3. **独立来源时间。** 两实际BlockCypher HTTP200分别为ETH.main chainroot及固定26234271块。height/hash均与本次初始B/H对应；固定Block.time=`2026-10-20T14:03:47Z`对应header.timestamp。root.time=`14:03:49.906543552Z`是root更新字段，不能替代建块时间、独立后台同步或因果latency；不同provider也不自动证明独立后端节点或最终性。
4. **两新完整扫描。** initial B=`0x1904da1`/H=`8242f8…0ef5b`，steady B=`0x1904da2`/H=`81ddb7…8b237`，逐一parent/number连续。独立机械解请求和响应：initial count+169base/ID+212detail，steady169+212；两次N105/P160、105唯一ID、55个past-count失败，compact ID顺序逐一同原件。两次均95个active(status1)+10个zombie(status4)，210组status及10-word LatestTroveData完整可无损还原。依赖地址/MCR/SP/mode/lastGood/ethUsdOracle与snapshot相同；fetchPrice确为末位非持久子调用，协议价格/新增failure字段与返回原量一致，number fence同B/H。没有把compact未重复保存latest当缺字段，也没有重新计算金融资格或利润。
5. **实际时序。** initial通知应用读14:04:13.056052→formed14:04:15.027383，约1.97134秒；steady14:04:24.950741→formed14:04:27.315451，约2.36470秒（包含后续保存的cycle处理字段2.365114959秒）。formed时本机UTC与块timestamp之差约4.027/4.315秒，在原age/future/12秒处理门内；backlog守卫通过由已hash源码成功控制流支撑，不冒独立NIC遥测。未把应用层时钟当wire arrival、已赢竞价或全球最快；时钟误差界UNKNOWN，整scan与文档backend2秒不同量。

## ARMED 准入与资源核对

closed admission原件与index所存record一致，真实member SHA可核，记录本次新cycle及旧3cycle全部保留。旧3组字段/hash逐项未变，没有择最快替换；新cycle为3方法、147工程CU、物理盘增量65536、processCPU0.038544、处理2.365114959秒。预测取四组各项max，处理max仍为旧4.174784125秒，CPUmax仍旧0.059754秒；initial额外count不冒稳态3方法。

| 门 | 本次实际准入记录 | 原帽 |
|---|---:|---:|
| 工程shadow预测 | 15,141,430未来 + 34,424当前 = 15,175,854 | 25,000,000 |
| 方法预测 | 305,408未来 + 112当前 = 305,520 | 400,000 |
| 项目物理盘预测 | 7,013,863,424 B | 8,588,886,016 B（8GiB−1MiB） |
| CPU保守账预测 | 13,757.03489 s | 18,000 s |

原12秒/块→100800块、至T0等待2978头、完整周期最大值、每100块logs、1000 detail/192MiB/120CPU储备保留；本机可用1699962609664B大于所需新增7003570176B。当前already_disk11341824B单列，不拿活archive逻辑大小替代全部旧占用，也不把65536物理分配max叫理论必需盘量。预测/OS当时计量不是未来实耗保证或完整历史kernel轨迹。

本次原件中的原方法费表借记和ACK/两通知工程字节量共同支持shadow33850→34424、方法93→112；没有重置或将Alchemy32734改成新账。dRPC真实计费/月余额UNKNOWN，25M仅原费表工程刻度；CPU7602.26531包含保守prior和当前进程/配置子CPU口径，不与保守预留或launcher CPU重复加。本审10秒已经在7602中。

launch-stage明确ARMED/PID9735，全部新门成功后同进程等待原T0；index中最后固定成员14:06:37.972605/B0x1904dad的shadow35245、方法112、CPU7602.320274是后续纯warmup新通知，未新增RPC，不能称正式A样本。此处只是固定as-of证据，不声称本审末尾再观测过当前进程。没有停止、重启或再次输入。

## 非阻断限制与后续事实边界

没有本启动层必须补件或修正。当前可以承认正式启动与ARMED的实绩；没有14日覆盖/机会捕获/实际失败费/个人全成本净利/alpha/容量认定，必要劳动/基础设施成本仍UNKNOWN，未知不填0。新服务限流、断链、资源增长/耗尽、漏头/重组和终态保存失败仍沿原门停止/不完整，不能把短样本承诺成未来零风险。采样/本机时间、匿名共享IP与实际账单限制沿原规则；没有为这些UNKNOWN再造不可能的准入保证。

原活archive仍可能追加，本审只有上述固定成员范围的原件验收；Root监测和未来终态须按真实状态，而不是本审覆盖到未来。原T0/T1及经济门/原历史正账均未动。

## 关键输入身份

- `launch-receipt.json`：1845B，SHA `46e78a0e1ace874b0af0395ab295b7af9511e1eda3fb185cf9ce07488a19089a`。
- `startup-evidence-index.json`：20135B，SHA `b8315d405ba9bb1315bbdc71ad0086b43808d69dff488e9a810997be32357081`。
- closed `startup-admission.member.json.gz`：1211B，SHA `0e1389844668e167f842f7fe4b9c13b093e9bc55e16a6de5bad20361f5b8b01e`；同活archive闭合offset202519/1211B成员。
- initial snapshot：offset163057/7240B/SHA `b660be7911f3ae474b2513441831a866a82716e5855ab936e64afde4c6227aae`；steady：offset195340/7179B/SHA `b61405158b7bd0fbf6125c776bc0ef4db76a1a2052b1ae0aeaf5bbfd0315c4de`。
- 本次尾warmup：offset231198/1329B/SHA `551fe009ba826548fcd3aef6f7ca40544f28acc37b3e2381f2ef1501c29ba276`。
- 真实binding：3968B，SHA `eee2dca75dbb9973e23b6e536694e105155fe2fc2de8f3ff26bf3daadc4ea94d`；Root release：3846B，SHA `4275fd9b66443212779cc3b88cd79ada2eaeccb6c372f6b63c5752b2e9b14724`。
- 四code逐一核回：adapters `e1330a313c7aeb5aac0e66c126cfd7a566943e1df0bb7c7c40729fc13bfee81f`；stream `279e0c1354ac1173a008458776be2657238d68b0a8982d18567dece7068162a6`；observer_loop `de707de821d7413708fa1142bdb397d678b081084e2a9f4dd85cb8be8eb2aa46`；observer `4b583bc326c9cec511d2e42c0bf5ea9f38060b68b103de924cac41842005ea29`。

唯一输出为本审稿，未生成平行运行真值、改变原源码或再次获取现场数据。
