# 0x095c0c6f 独立静态审阅

结论：现有 runtime 指令支持 owner 访问控制、六字段动态 tuple、批量清算后 WETH 转 ETH、分成前估算净额门槛及 COINBASE 分配逻辑。两笔真实付款与公式在 wei 整数取整上相容。创建交易携带的返回代码逐字节等于当前 runtime，已显著补强历史身份链；这仍是同一 Etherscan 来源的静态证据，不是独立节点重放，也没有恢复完整私有 bot 源码、寻单模型、ABI 函数名或许可。

仅读取本地原 HTML/hex/指令表；未联网、未执行 EVM、constructor、下载源码、模型、策略、回测或交易。实际 model/effort：UNKNOWN。输入 SHA256/UTC 见 hashmanifest.json；精确 uint/金额见 static-derived.json。

## 指令与栈

- dispatcher 0x004f–0x0058 将 0x095c0c6f 跳到 0x0089，CALLVALUE 非零即 revert，ABI decoder 0x1076 取最外层 offset，0x1058 检查 tuple 至少 0xc0 字节（6 word）。不替 selector 猜原函数名。
- 0x01b9–0x023d 读取 slot0 低160位，与 CALLER 比较，不等则 revert；0x8da5cb5b getter 0x0852 也返回该 slot 地址。创建 init 中 CALLER 写入 slot0，支持 owner 解释。它是该函数入口的权限限制，不是普通用户任意调用此已部署 helper 的许可。
- tuple+0xa0 在 0x023f–0x024c 检查 <=0x2710（10000）；tuple+0x80 在 0x027f–0x0289 检查非零。没有从这个上界检查推断其他 selector 的权限或安全。
- 0x02bd 的 GAS 留作 startGas。tuple+0 是外部 target 地址，tuple+0x60 是动态 uint256[] offset；0x1293 decoder 读取数组长度、32字节元素跨度及 calldata 边界。0x02e8 调用 selector 0xef49a6b4，目标为 tuple[0]，数组为参数。仅凭 selector 不宣称恢复原 ABI 名；实际事件确认两笔 target 清算发生。
- tuple+0x20 是 collateral，tuple+0x40 是动态 bytes path。0x0b08 比较 collateral 与 WETH；非 WETH 路径使用 token balanceOf、router 0xe592... 的 0xc04b8d59 调用并带 path（完整路径策略语义未恢复）。WETH 分支绕过此交换。
- 0x0ce2–0x0e29 对 WETH 0xc02a... 调 balanceOf(address(this))，余额为0则 revert，随后 0x2e1a7d4d 调用提取全部 WETH 余额。该数值是余额而非严格本次增量；预有余额也可能计入，不能由代码门槛直接推出本次独立经济利润。

0x0372 调用 helper 0x0e2a 的参数顺序为 startGas、tuple[4]、tuple[5]。按 helper 手工栈追踪：

```
B = SELFBALANCE                    // 转换后 helper 的 ETH 总余额
E = (startGas - gasleft_at_0xe34 + 50000) * GASPRICE
N = B > E ? B - E : 0
require N >= tuple[4]
P = floor(N * tuple[5] / 10000)
if P > 0: CALL(COINBASE, value=P), require success
CALL(slot0_address, value=SELFBALANCE), require success
```

相应地址：0x0e30 GASPRICE、0x0e31 PUSH2 0xc350、0x0e34 GAS；0x0e3b checked SUB；0x0e45 checked ADD；0x0e4f checked MUL；0x0e56–0x0e72 计算 max；0x0e73–0x0eab 门槛；0x0eac–0x0ec8 checked MUL/DIV；0x0ed2 COINBASE 与 0x0f01 CALL；0x0f7b–0x0fcb slot0 地址收余款。0x1713/0x1746/0x1779 分别为 checked SUB/ADD/MUL，溢出/下溢走 Panic(0x11)；0x17e7 checked DIV，零分母走 Panic(0x12)。父任务线性表中的 OP_0xa 实际为 EXP、OP_0x12/13 为 SLT/SGT；未将这些标记当未知执行行为。

feehelper 0x0e2c 明确使用 SELFBALANCE 总余额，未读取调用前余额也未做前后增量相减；预存 ETH 可计入 B 与门槛。这是所审路径的衡量口径，不将它称作安全漏洞。实际两例正增量来自 From State 与资金流核账，不依赖 guard。

因此 1e15 是**分成前估算净额的下限**，不是最终 From 扣完实际 gas 保证赚 .001 ETH。估算含固定50000、时点 gas 及有效 GASPRICE，区别于最终 receipt gasUsed（包括 refund 的最终计费）。未有逐指令 trace，两个 GAS 读数差无法独立实测。

## 两笔已发生 calldata 与金额

两笔 selector 均 0x095c0c6f，外层 offset=32；target=0x7bcb64b2c9206a5b699ed43363f6f98d4776cf5a；collateral=WETH；path offset192 且长度0；trove array offset224、长度1（原 uint 见 JSON）；threshold=1000000000000000，rate=9700。

|交易|WETH unwrap / B (ETH)|COINBASE付款 (ETH)|退回 From (ETH)|实际 gas (ETH)|From净增(ETH)|
|---|---:|---:|---:|---:|---:|
|b4c3…5473|0.0475|0.045585735056956094|0.001914264943043906|0.000427703441331096|0.001486561501712810|
|2635…ca9|0.360848784148759889|0.347506156161122510|0.013342627987637379|0.002219915189772975|0.011122712797864404|

各笔均3条非零内部 ETH 流，B=付款+退回；gasUsed×effectiveGasPrice 与精确 gasfee 相等。付款均满足 floor((B−E)×9700/10000)：分别唯一对应估算 gas 单位610274、527492，E=504396848498872、2595014910489260 wei。这是从实际付款反推的整数一致性，**不能把拟合的 gas 单位当独立 trace 证据**。对应 N 均超过1e15。rate9700是估算净额97%，与付款占 gross 的比例不同。

较大成功 State 原 HTML 中 From 为0.048264218992807530→0.059386931790671934 ETH，差0.011122712797864404，恰好等于退回−实际 gas；较小笔前轮已有 State 核验同样闭合。State 页面同属 Etherscan，不是独立节点。COINBASE direct payment 要作为额外支出；gas 中已有 priority fee 不重复扣。上述账不预设 wrapper 与 From 的真实受益人为同一人。

## 创建身份与四笔明确范围

创建交易原 HTML 状态 Success，input6520字节，前91字节 init，其结尾为 PUSH2 0x191d / DUP1 / PUSH2 0x005b / PUSH0 / CODECOPY / PUSH0 / RETURN / INVALID。标准栈含义是复制并返回从 offset91 开始的6429字节。该切片无尾随额外字节，与当前6429字节 runtime **逐字节相同**，SHA256=1663a8c8f88f5b27ab2363e7584f213a6122dadafefe0c28641b3257053dbbd8。未执行 constructor。此创建原件比“当前代码当然等于六月”更有力，支持同一部署代码身份；没有独立节点的历史 eth_getCode/完整执行 trace，避免宣称跨来源链状态完全复核。

两笔成功 From 净增合计0.012609274299577214 ETH；再扣此 helper 部署 gas0.0004380195及初始化 gas0.000025391572493664，**这四笔明确操作范围为+0.012145863227083550 ETH**。部署/初始化原 HTML 均 Success，精确 fee 来自各原件。此范围不是 From 完整钱包、所有私有尝试、所有 internal/代币流、offchain/基础设施费用或长期经营利润；不作 ROI、美元收益、普通人可复现或许可保证。代码页列出的3笔 normal 与另列 creation 的集合范围也不扩展为 From 全历史。

## 保留项

未获得完整验证源码/签名ABI/反编译；Panoramix fallback4行不证明恢复成功。owner 入口与已发生收益只能说明这两次部署调用的事实和静态计算一致，不能恢复寻单、广播、竞争策略及失败集。这里没有模型/策略执行结果，也不为任何未来机会、最终门槛利润、容量或全成本作保证。
