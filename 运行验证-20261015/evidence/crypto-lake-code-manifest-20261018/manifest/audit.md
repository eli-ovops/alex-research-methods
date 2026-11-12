# Crypto Lake：固定三日对象元数据

结论：PASS_LIMITED。匿名目录与单对象HEAD实际可读；先前只有官方图的三日样本，现在已有真实对象清单。没有取得任何行情内容，不能称连续历史或因果时钟通过。

来源是已保存固定tree `42f0cc5fcf23a19050285d89cb4be075359f55af` 下main.py：56–74行固定sample bucket与UNSIGNED，391行为eu-west-1；307及456–463行确认分区次序。未执行该源码/SDK。初始即用标准区域S3 path-style，不尝试有点bucket的虚拟host、不改TLS。

三次GET固定 `book/exchange=BINANCE/symbol=BTC-USDT/dt=日期/`，max-keys=20；均200，各KeyCount=1、IsTruncated=false：

| 日期 | 文件 | Size字节 | LastModified |
|---|---|---:|---|
| 2022-10-01 | 1.snappy.parquet | 267304100 | 2022-10-10T10:14:04Z |
| 2022-10-02 | 1.snappy.parquet | 282137927 | 2022-10-10T10:14:16Z |
| 2022-10-03 | 1.snappy.parquet | 328029311 | 2022-10-10T10:15:28Z |

第四次仅HEAD首对象，200；Content-Length、ETag、Last-Modified与目录一致。实际version-id `wsEI9nFSmHryDvoX6arap5z6BRl9uz2v`。另外两对象没有HEAD，version-id未知。ETag分别带-32/-34/-40，不当MD5或内容SHA。

公开动作4/4，UTC 2026-10-18T13:41:56.588675Z至13:42:05.484883Z；完整URL/响应头/XML/UTC与实际hash保存在01–04回执、public-read-summary.json及audit.json。仅小型目录正文；市场对象GET/range为0。

边界：文件名日期不证明该日完整、无断线或逐事件；Last-Modified不等于观察时点或collector arrival；XML指纹不等于Parquet内容指纹。许可继承先前官方样例邀请的有限研究解释，本轮不重新研读条款，也不由匿名访问推任意披露授权、预测优势或盈利。

下一唯一缺口是固定对象内容的schema/双时钟及连续性受限QC，需要另行明确小范围；本轮不取文件、不执行、不扩展。已停止。
