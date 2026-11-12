# HftBacktest支持者连续历史目录：一次普通HTTPS结果

**UNKNOWN：仍未取得目录或足够连续历史的文件清单/许可。**本轮正常读取的阻断已具体化为TLS主机名不匹配，不能把失败解释为站点无数据。

目标仅 https://reach.stratosphere.capital/data/usdm/ ，来自官方HftBacktest主页实际链接。先读LOCAL_BLOCKERS该资源条目，旧记录只是原生工具502、底层server status未知；因此按本轮scope用普通urllib、默认TLS、无Cookie/认证/代理身份修改GET一次。

结果：`CERTIFICATE_VERIFY_FAILED`，证书主机名不适用于 `reach.stratosphere.capital`。没有服务器HTTP响应状态或正文；无HTML文件可保存，也没有实际observed terms/license链接。精确UTC、错误及请求参数见supporter-index.read-receipt.json。没有降低TLS校验、改host/身份、换工具或重发，未取任何行情文件或HEAD元数据。

目前无法核：实际文件路径/大小、日期与连续覆盖、下载条件/是否账号、收费与数据许可；文件名/当前仓库MIT也不能填这些未知。不能据访问错误断言全球没有免费历史、数据已消失或所有预测研究不可行。

本轮仅1次GET（30秒/256KiB界内），无第二文档读取，因为没有取得index来观察合法后继链接。0行情payload、collector/converter/模型执行、回测/标签/收益、安装、账户、付款、交易或外发。actual runtime/route UNKNOWN。旧研究和已验小样本不改，完成即停。

最小剩余原件是发布者经正常可验证HTTPS提供的同目录/镜像官方新链接与适用数据说明；本轮不自行寻找别名或绕当前TLS失败，不发邮件/草稿。

