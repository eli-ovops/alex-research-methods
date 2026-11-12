未发布离线诊断候选，未应用主源码，未签release，未联网/重试/重启。

只对原RPC传输except分支增加固定REQUEST_BUILD/OPEN/READ阶段、固定白名单异常/嵌套原因类别、整数errno/verify_code、timeout/TLS布尔及单调耗时/接收字节整数。未知动态类名为OTHER，reason字符串为TEXT_NOT_SAVED，禁止str/repr/traceback/URL/key/header文本。

7项合成安全测试均PASS；它们以mock opener和socket连接禁用验证伪secret/动态类名不落盘、OPEN/READ/REQUEST_BUILD类别、整数类型/布尔排除、超时/TLS，以及HTTP403仍失败即停无原体、不重试。它们不是旧URLError根因复现或实际网络修复。

任何未来应用/预检须由Root根据有效授权决定并绑定新代码/审阅/累计用量；本目录不提供启动入口，不解除旧once-lock或停止状态，不许可新RPC。候选冻结交静态窄审，原core与八原件不改。
