# Mantle/Lendle指定历史交易：原件有限准入

**通过：精确交易的explorer原HTML已取得，身份、成功状态、时间及清算事件得到页面原件支持。未验证完整净利润或公开参与者身份。**

- URL：<https://mantlescan.xyz/tx/0x5165cdcf3363042ec3f6c4c04e64df1a6378dfeb47acfce978560433722e1507>。两次公开动作：原生工具HTTP未知；查LOCAL_BLOCKERS B019后，同URL一次普通HTTPS GET为HTTP200、659930B、0重定向、TLS校验通过。原HTML SHA256：`b0174b9a078a8957d32aaf4f81441a38f4e1e331cc5c9b13d3dcc0d59a80ca06`。首次开始2026-10-19 15:18:11 UTC；普通GET开始15:18:59 UTC，精确完成时刻未单采，15:20:18 UTC前已观察正常结束。没有重试或遇403后换路。
- 静态正文第99—121行显示指定完整hash、sender `0x57D8718f0d24DB1F3F6445337c8A0C24948d77c2`、Success、block101326324及2026-09-30 15:42:40 UTC。顶层成功同时伴随页面的内部revert提示，不能说每个子调用均成功。
- 第460—502行保留gas used `1,749,787`、gas limit `2,500,000`、gas price `50.25 Gwei`及页面L1/L2/总费字段，逐项原样提取；没有费用乘加、美元换算或重算看板reward/gas/profit。未取RPC JSON，因此不能声称独立节点receipt字段已经勾稽。
- 第1506—1566行的Receipt Event Logs条目26含`LiquidationCall`、原topic/data，发出地址`0xCFa5aE7c2CE8Fadc6426C1ff872cA45378Fb7cF3`由explorer标为Lendle Lending Pool；解码liquidator与本交易to一致，`receiveAToken=True`。这支持实际发生清算，强于仅有看板盈利标签。地址/topic/data与explorer解码标签分开保存；标签不是本Owner另取Lendle官方注册表的绑定，页面事件表也不是独立节点回执。本Owner未另验ABI/Keccak或部署身份，不运行合约。
- 默认首屏选取方式与看板估算来自Root，本Owner没有重现看板选择或独立核算利润。取得这笔成功交易不能证明全历史成功失败/成本完整、净运营盈利、该执行者是否API3伙伴、是否用公开延迟路径、可持续个人优势或容量。

原件、headers、被动HTML文本及解析层已保存；URL/UTC/HTTP/哈希在`acquisition-receipt.json`，字段在`transaction-static-fields.json`。原HTML第1578—1698行的gas价格/限额/用量片段另存`gas-fields.raw-fragment.html`；第2340—2343行含LiquidationCall地址/topic/data的原片段另存`liquidation-event.raw-fragment.html`，均保存精确字节SHA。仅运行自有stdlib被动HTML提取器及本地切片/哈希，未执行来源JS/策略代码，无RPC/eth_call/trace/estimateGas/logs范围请求、模型/回测/交易、安装付费登录、凭证或排除目录访问。2/4公开动作已足够本项有限准入，不消耗剩余预算。实际model/effort UNKNOWN。
