# Kaggle v755：文件身份、十行前缀与时间语义

**有限通过：可以准备固定日频研究协议。** 官方固定版本文件metadata和实际CSV表头/前十行已取得；不是全历史质量通过，也没有模型或盈利结果。早期未取得表头的审阅保存在before-metadata-supplement.snapshot，不作为当前状态。

## 实际文件证据
官方历史KaggleSwagger在commit `8c3066490a9393a7261be05c105614594974f7ae`明确DatasetsListFiles、单文件下载及datasetVersionNumber参数。当前Swagger路径404原件保留、没有重试。旧规范不冒当前成功，实际回执另核：

- [文件metadata](https://www.kaggle.com/api/v1/datasets/list/mczielinski/bitcoin-historical-data?datasetVersionNumber=755)：2026-10-17T08:14:33.603094Z—08:14:34.149088Z，HTTP200/application-json，448B；SHA256 `81745066e0eb91d6a41f890225ab0c142e5649e28cc336b6fe6dbfe2a9d25961`。唯一文件 **btcusd_1-min_data.csv**，totalBytes **394775342**、creationDate **2026-10-17T02:10:34.591Z**、columns为空、nextPageToken空。请求明确v755，响应无独立版本回显。
- 单次公开单文件GET带Range bytes=0-65535，**206**、实收65536B、Content-Range总长394775342，与metadata一致。是CSV前缀，不是ZIP；没有取完整文件。前缀hash不是完整CSVhash。回执保留请求URL，响应服务器session字段脱敏且没复用，未发送认证/Cookie。
- 实际只解析表头及**10行**：Timestamp/Open/High/Low/Close/Volume；各行六字段。Timestamp1325376060—1325376600，按Unix秒为2012-01-01T00:01—00:10 UTC，九个间隔均60秒。
- 用stdlib Decimal/csv检查同10行：解析错误、NaN/Inf、非正价格、负Volume、High/Low约束违例、重复/非递增时间戳，全部0。**仅覆盖最前十行**，不覆盖后来追加块的列序、全历史、尾柱、分钟开收端或精确发布延迟。

版本HTML页之前工具返回Internal Error/is not accessible via this tool，仍只属工具读取失败，不是登录/403或账号必要性证据。实际匿名metadata和有界前缀已可访问，不需因此再索账户；不保证任何未来全量访问。

## 当前生成器的条件解释
[作者固定代码](https://github.com/mczielinski/kaggle-bitcoin/blob/3fc058a4fab9ba2c291b61900e60cb59e8aa681b/kaggle_bitcoin/kaggle_update_bitcoin.py)，Git作者/提交者日期2026-10-01T23:15:59Z，未绑定为v755实际运行版本：
- L30–36、99–109、160–176：Bitstamp OHLC、step60；Timestamp按Unix秒和UTC处理。
- L105–107：截止nowUTC减10分钟，是缓冲，不证明全部柱完整或精确到达时刻。
- L164–176按列位置重命名，若API键序不同可能错列；**未证明已发生**。十行初期数据与六列表头相容不验证所有后续追加。
- L139–140、191–202：从已有最大时间戳补尾部、重复Timestamp保留first再排序。此路径不主动审计早期内部缺口，也不证明历史修订已吸收。

[Bitstamp当前官方文档](https://www.bitstamp.net/api/)L1197–1269确认时间框秒数、Unix查询边界及可排除当前未收柱参数；生成器未传exclude_current_candle。精确CSV时间戳代表开端还是收端，本轮仍UNKNOWN。文档数值示例没有当作实际取数。

## 许可及范围
发布者上轮CC BY-SA4.0的商业复用正面证据保留。此次Bitstamp文档L169–173另述企业商业数据协议；具体个人经Kaggle取得后的离线研究适用UNKNOWN，不自动否定CC许可，也不新增一律书面ML批准。文档版本/发布日期未标明，取当前快照。

累计12逻辑公开动作：5 GitHub GET、2 native open、1 native find、2 native query、1 metadata GET、1 Range GET；3次native调用。完整CSV/ZIP下载0，原CSV前缀65536B、实际解析10行；训练/预测/回测/交易/安装/付费0，全部源码惰性阅读。网络已停止，旧FAILED/现金/状态不改。

唯一下一提案：**只形成固定日频研究协议**，明确Timestamp开收端/可用延迟假设、日内完整性和未来数据质量验收条件、固定日期及比较目标；不静默假设1440柱齐全，不自动下载全量或运行实验。完整输入hash、字节、来源和回执见audit.json。

