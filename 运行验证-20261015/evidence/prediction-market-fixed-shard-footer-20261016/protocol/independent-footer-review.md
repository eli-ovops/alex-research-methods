# 固定Parquet尾部与metadata独审

**限定PASS：固定文件Range和footer metadata有效；未读行数据、取得成本或盈利。** 0新增网络，未读取root正在下载/分析的完整分片。仅用已存在项目`.venv/bin/python -I -B`与PyArrow26.0.0的`read_metadata`被动解码，没有安装、模型、回测、来源源码/SDK/SQL/EVM、策略或交易执行。actual model/effort UNKNOWN；PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4保持。9份实际输入绝对路径、SHA、bytes及UTC在同名JSON。

## 原件与Range

固定HF revision=`6de5f2a7fc9ff4b42ced990f47c556fa448933c6`，路径：

```text
raw_chain_logs/block_group=043080/part-b086160001-b086162000-1dd5745bbf06.parquet
```

它确实逐项存在于既存HF metadata.siblings；原metadata SHA与事前计划相符。两次回执原URL是该固定revision同一文件，没有替换其他分片或请求SQD。

| 原件 | 独立核得 |
|---|---|
| 末8 bytes | HTTP206，Content-Range `20329646-20329653/20329654`；前4 bytes little-endian=3250，末4 bytes=`PAR1` |
| footer＋尾8 bytes | HTTP206，Content-Range `20326396-20329653/20329654`；实际3258 bytes，其中metadata3250 bytes＋尾8 bytes |
| 版本与字节 | 两回执同ETag，第二请求If-Range相同；各原件SHA/bytes匹配回执，footer最后8 bytes与原tail完全相同 |

几何关系`20329654 - 8 - 3250 = 20326396`精确。原件返回body共3266 bytes，而不是下载20MB。Content-Range声明的整个文件长度为20,329,654 bytes；ETag是对象一致性标识，不当作已核完整文件SHA。

## 独立metadata解码

内存中仅在原footer前加结构性`PAR1`头让Parquet metadata reader读取；没有补造缺失页或观测记录，也没有调用read_table/read_row_group。读取结果：

- 644307行、1个row group、12列，serialized metadata=3250 bytes，与root结果相同。
- chain_id min=max=137；block_number min=86160001、max=86162000，null_count均0。
- scan_from_block min/max=86160001/86161901；scan_to_block min/max=86160100/86162000。
- schema实际含原日志12字段，topics是列表；所有列ZSTD。12个压缩column chunk的原文件offset从4起逐项连续，最后恰止于metadata开始20326396，没有将memory wrapper的offset当原行页已读取。

完整字段和统计由本子任务重新解码保存在JSON，不只沿用root的摘要。

## 通过与未通过层

这补强了“实际指定Parquet文件支持小Range，其footer可解析”，并把纯文件名范围升级为该文件metadata的min/max声明。它在数值上覆盖固定1800块及已知merge块；**尚不证明每个区块/事件或目标holder/token确实存在，更不是原链无漏/全协议完备性证明**。单row group也不自动证明可便宜地按钱包物理读取或返回顺序。

本次没有读取数据页/完整文件SHA、校验每一行或匹配已知10logs，没有判断历史成本、利润、许可或交易资格。root后续唯一完整分片读取和经济分析属于另一项证据，不混成本审阅的已核事实。原既有正负结果及财富目标状态保持。
