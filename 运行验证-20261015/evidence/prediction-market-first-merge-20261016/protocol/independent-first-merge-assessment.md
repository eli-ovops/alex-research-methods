# 首个固定CTF合并：独立原账核验

**原件与被动会计审阅PASS；净盈利案例未准入。** 本笔观察到既有两种持仓各13110000原单位被合并，原持有人收到13110000 pUSD；没有同笔新买入再合并的闭环证据，不能把13.11回款叫利润。0新增网络，未执行源码、Keccak、SQL、SDK、EVM、模型、回测、策略或交易；actual model/effort UNKNOWN。沿用PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4，财富目标active未达。

## 选择与原件身份

只读已保存的2205条全日志、236笔交易字段及原Gnosis ABI/适配器源码；没有读其他交易的经济结果。15份实际输入绝对路径/SHA/bytes及审阅UTC在同名JSON。

`selected-first-merge-before-cashflows.json`于2026-10-16T15:20:01.391648Z封存tx `0x3ca8e82d43f1f34dd92f7a5de60121005ed7ad4cb1b42f6ed094f8a3a1079bb9`、log1161。按指定CTF地址及registry映射topic复查整个既有块，恰好一个匹配，故它也是最早者；未按盈亏挑选或换样本。

PositionsMerge原registry只有一个严格text_signature匹配；TransferSingle返回4个含近名条目，客户端严格等于规范签名后只有一条，且与已知日志topic相同。两个registry原件hash/bytes与回执相符。此证据配合原Gnosis ABI与事件布局，仅支持registry身份和观察形状；**未独立计算Keccak、未独证历史runtime、registry created_at不是协议首公开时间。**

两份区块原件header逐项相同：86161976，hash `0x3a972bb24150b1bb270679630da749683050ef931e989a49656bb2ca64415629`，timestamp1777443996（2026-04-29 06:26:36 UTC）。全日志原SHA与封存记录一致。本tx共10条日志，1158—1167。

## 合并与资产路径

log1161按原Gnosis ABI独立解码：stakeholder=`0xada100874d00e3331d00f2007a9c336a65009718`；parentCollectionId=0；conditionId=`0x725d49504ebb3d7467baa1b442f14fd1ecf31408aaa55c2d0aee5279b8d28719`；collateralToken=2791…（USDC.e）；partition=`[1,2]`；amount=`13110000`。动态offset和数组长度均有效，不把offset当金额。

| log | 原量动作 |
|---|---|
| 1158 | holder `02fe2a4c…fa6f3`→ada，两个CTF token各13110000 |
| 1159 | ada→zero，销毁同两个token各13110000 |
| 1160 | CTF→ada，13110000 USDC.e |
| 1161 | PositionsMerge业务上下文；不再计一次付款 |
| 1162 | ada→C011，13110000 USDC.e |
| 1163 | zero→原holder，铸13110000 pUSD |
| 1164 | C011→c417…9db1，13110000 USDC.e |

仅canonical Transfer重建后的非零向量：holder的两个CTF ID各−13110000、pUSD＋13110000；CTF的USDC.e−13110000、c417的USDC.e＋13110000。ada/C011的观察中间资产净0。CTF两ID供应各−13110000，pUSD供应＋13110000；逐资产非零地址净变动之和等于对应供应变化。

token IDs为`81551531010483259056364843326824519276425229940219964995020338208054471741828`和`7513960599313508175221406531566208571173568115476583808543905304236680112729`。未贴具体YES/NO文字。按已核6位抵押尺度显示13.11，但保留原量，不推美元兑付价。

本tx未见OrderFilled/FeeCharged，也没有先向holder铸造/转入这些CTF份额、或买入付款后再merge的事件。按已核canonical余额模型，这次消耗holder此前已有库存；其取得成本、对冲或链下权利UNKNOWN。USDC.e释放、pUSD新铸属于同一转换链，不能叠加成两笔利润或将pUSD供应新增当经济价值凭空创造。

## 实际gas与未核部分

唯一顶层交易status1，From=`0x4c917200bda6cb9b2608cc07029f846a66d06395`，To=`0xd216153c06e857cd7f72665e0af1d7d82172f494`，value=0。实际gasUsed338097 × effectiveGasPrice226757011291 wei/gas＝**76665865246453227 wei＝0.076665865246453227 Polygon原生币**。

gas付款地址不是持仓/回款holder；实际控制关系和费用回收UNKNOWN，不直接从13.11 pUSD裸减原生gas。log1167为1010系统事件，未在实际gas上再扣；没有FeeCharged也不证明整个持仓期零费用。log1165非Transfer的C011事件、log1166的d216事件未以未核ABI解释或另计收入，完整内部原生流、旧权利状态及跨期成本不在现有范围内。

当前adapter静态源码能解释合并后wrap路径，但不能自动绑定旧ada历史实现，c417及d216的正式部署角色也未独立验证。上述未知不否定已经核得的数量事实；不另要求完整私人bot或全实体多年账。

本例可确认“既有库存换回抵押计价资产＋另一地址支付实际gas”；不能确认同tx新资本套利、全持有期净利、ROI、样本外优势或容量。按固定样本保留该结果，不寻找替代赢家。
