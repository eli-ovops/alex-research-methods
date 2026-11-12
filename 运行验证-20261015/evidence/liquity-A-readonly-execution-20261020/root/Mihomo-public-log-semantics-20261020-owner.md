# Mihomo公开日志语义：有条件结论

**能做不披露名字的标签分类，不能由`match/using`证明应用层TLS成功；当前binary逐字版本仍UNKNOWN。** 本轮只核官方源码，未读私有日志、未写/运行logreader或core，无代理/API探测。

固定tag [v1.19.10 tunnel.go](https://raw.githubusercontent.com/MetaCubeX/mihomo/v1.19.10/tunnel/tunnel.go) 的web原件L464–520：先选adapter，调用DialContext；含可选握手/peek数据写入，err非nil返回，之后才logMetadata，最后转发socket。因此它是adapter报告无错误后的INFO，不是单纯拨号前规则命中，仍不保证远端业务TLS/证书/HTTP成功（REJECT有特殊处理）。L532–554区分拨号错误WARN和INFO；有规则的INFO用Chains.String打印`using`。这也是条件性代码推理，不能追认实际那一行已完整匹配此模板。

[adapters.go](https://raw.githubusercontent.com/MetaCubeX/mihomo/v1.19.10/constant/adapters.go) webL63–81：空链空字串；单链打印名字；多链打印外层名字及方括号内首链名字。它是name，不是adapter.Type或完整拓扑。不能只看包含DIRECT子串，也不能把GLOBAL当具体出站。

建议未来若另行允许**只在内存**分析，须先确认完整TCP INFO模板、固定目标/时窗且using后缀不歧义，再只输出四枚举：

| 输出 | 可支持的严格口径 |
|---|---|
| DIRECT | 已确认内置终端链标签为精确DIRECT；只描述该标签，不认证实际IP路线/TLS。 |
| REJECT | 已确认内置终端链标签为精确REJECT；不从INFO推出网络成功。 |
| NON_DIRECT_NAMED | 最多表示using呈现其它具名链标签，绝不输出该名字；**不能单凭名字证明实际非直连**。若分类要求真实adapter类型，此项须退UNKNOWN。 |
| UNKNOWN | 模板不符、GLOBAL/SpecialProxy、未知/空链、嵌套或歧义括号、名称与内置类型无法绑定、实际版本无法满足所需语义。 |

命名可自定义，组名也可能包装DIRECT，故上述为保守标签提案，不是已实现或已对真日志得出分类。不要输出using原串、rule payload、节点/IP/URL/key，也不能因某词面缺失判无错误。本轮不授权新读取。

版本边界：Root提供本机Go嵌入声明revision4b60ed144e28d44e2abc87986a62367a3d1b1650、time2026-09-09T03:08:39Z、modified=true，binary SHA44c67a97bbd3a5fbfe3470cb120961bbd49cd1107fc6cd0836bcac73688ab494（这些是Root已核转述，本Owner未另读binary）。第三公开动作读取[该commit同文件](https://raw.githubusercontent.com/MetaCubeX/mihomo/4b60ed144e28d44e2abc87986a62367a3d1b1650/tunnel/tunnel.go)得到工具404，无源码，不改URL/重试；不能确定404原因，也不能将tag视为本机原样代码。Go声明非签名/可复现证明且modified=true，实际日志版本联结仍有条件。

原件均为原生web工具返回文本（保留完整公开代码/行标签），不是HTTP raw；URL/tag/nativehash见 `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-A-readonly-execution-20261020/execution-owner/mihomo-public-log-semantics-20261020/manifest.json` SHA `0afe9103ea2652ec8adb96292714dcdbb8eecef3bef11e8d0e826d1443fc58df`。封存UTC 2026-10-20T12:11:07.536956+00:00；每次取源精确UTC未另计，UNKNOWN，不伪造为封存时刻。公开动作3/3，停止网络。source1/2阅读全文相关控制流及Chain实现，source3仅404；无仓库广扫/下载执行。

本轮新增保守CPU10秒（非实耗），旧32734CU/63RPCmethods/7100floor保留由Root去重追加；无新数据API/付款/模型/输入/采集/配置变化。全部输出<256KiB。结论不支持重启旧A或直接改网络路线，当前Owner停止。
