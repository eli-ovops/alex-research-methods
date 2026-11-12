# 免费样本包 README 核验

结论：一次匿名 GET 已取得官方 GOOG 一层样本包，仅读其中 README；**未找到具体使用许可，个人盈利目的预测研究及未来交易用途仍 UNKNOWN**。不因此判违法，也不把免费访问当任意授权。

选择在下载前保存：从既有官方样本HTML提取一层候选，以标称MB最小、同大小文件名字母序选择。GOOG 为0.5MB，实际URL：
https://php.lobsterdata.com/info/sample/LOBSTER_SampleFile_GOOG_2012-06-21_1.zip

实际 ZIP 636670B，SHA256 `34ec126261ac19831972f47edd8ab874d52d93b54a9ab623ee4ce89d3f90f5cc`。目录3项：message CSV、orderbook CSV、README。没有读取或解压任何CSV，也未执行代码。原始ZIP含数据字节已保存，不能称本子步骤“数据包获取0”；其CSV记录读取为0。

README 为4790B，标记版本2013-09-01；正文是格式说明，没有许可段。它说明 message 的事件时钟为午夜后秒、size为股数、price为美元价乘10000，以及orderbook最佳ask/bid价格和数量。文件名的34200000/57600000按说明代表理论起止毫秒，即09:30/16:00；这不是实际CSV首末事件核验，也未在此README确定时区。目录元数据不能替代payload质量/逐行对齐检查。

原GET默认TLS、无认证/Cookie；1次请求，无重试，未越过8MiB/30秒限制。HTTP状态、原URL、UTC、响应头和hash见回执。只存一份README惰性文本；旧owner报告不改。实际model/effort UNKNOWN；模型、训练、回测、账户、付款、交易均0，无活进程。

唯一剩余原件：明确适用于该免费样本的实际许可/使用说明；本轮没有这项原文，不自动邮件、注册、取其他包或启动实验。

