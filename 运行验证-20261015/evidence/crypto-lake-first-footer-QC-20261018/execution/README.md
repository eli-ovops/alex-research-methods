# 首个Parquet footer：上限触发停止

状态：FOOTER_OVERSIZE_LIMIT_STOP。不是schema通过，也没有证明文件损坏。

独立静态gate通过后只运行一次。首Range `267304092–267304099` 返回206，Content-Range总长267304100、ETag及version-id与冻结scope一致，应用正文仅8B。尾部magic为PAR1，little-endian footer长度声明16,043,444B，超过事前1,048,576B上限。因此按冻结规则停止，不追加额度、不换源、不重跑；未请求footer或first4。

helper使用统一错误名INVALID_FOOTER_LENGTH_OR_MAGIC；此次已存8B可区分真实原因是oversize，不是magic错误。声明长度尚未通过完整footer解析验证。未取得schema、types、rows、rowgroups、真实数据时间或内容质量。没有创建metadata-only人工容器、没有数据页解码；完整原文件hash仍UNKNOWN。

PyArrow26.0.0本地依赖预检通过，无安装。正式supervisor PID91533/worker91534，2026-10-18T13:54:43.010916Z–13:54:44.469581Z，exit1，正式1.458643833s，含预检累计2.006267s，采样合并峰RSS84,213,760B。100ms采样不是瞬时硬RSS保证；退出后无活worker。formal-started.lock保留。exec session20193已结束。

本轮1请求/3上限，仅8B正文；未执行vendor SDK、模型、统计、收益账、回测或交易，0新增付款。原始tail、HTTP/UTC/身份回执、stderr、源码/config/seal、gate及资源收据全部保留，身份见completion.json。旧成果不改。

这只改变后续研究资源判断：目标声明footer超过当前单元上限。本轮不取得其余metadata、不修改范围；交独立验收后停止。不能由此推出数据不存在、不可用于研究、可预测或盈利。
