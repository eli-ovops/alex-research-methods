# SEC公开披露：免费复用有依据，接收时刻不等于公开可见时刻

读取日2026-10-19，root实际公开请求6项：两项定向搜索、FAQ与Form4 PDF两项open、从FAQ实际链接指向的研究指南/访问说明两项click。只保存工具文本回执，没有获取或执行申报/交易数据、账户、爬虫代码、API或模型。

## 免费、再用与访问条件

[SEC Webmaster FAQ](https://www.sec.gov/about/webmaster-frequently-asked-questions)，页面标2021-05-19，Last Reviewed/Updated 2024-08-23；本轮实际返回444行。L77–83明确政府内容及EDGAR公开申报可免费访问和复用。不是仅能在线看，也不需要从“没有ML字样”推定不可研究。

[Accessing EDGAR Data](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)，页面标2021-03-23，本轮实际返回206行。公开查询/下载、索引路径有说明；自动访问须遵守声明及当前10请求/秒上限，避免额外负载。本轮没有启动任何批量采集，也没有伪造访问身份。免费披露不自动包含第三方证券行情、退市回报、公司行动或论文数据清洗服务。

## 最少必须分开的时钟

1. **内部人士成交日**：交易本人何时买入，外部跟随者当时未必知道。
2. **申报/SEC接收时刻**：官方研究指南说明Form4通常在交易后两个工作日内披露；这是一般规则，不认证任何实际一条记录及时申报。
3. **公开页面首次可取得时刻**：FAQ L332–372称通常比系统时间晚1–3分钟，高负载可更久且不保证；SEC没有标记页面首次公开可见的时间戳。因此不能将acceptance timestamp直接当零延迟可成交时间。
4. **外部研究者真正收到信息、形成判断和入场时刻**：本轮未采集这些记录，亦未成交；后续如有授权检验，必须另作保守可用性假设或保存实时取得凭证，不用内部人士原价冒充外部成交。

[Using EDGAR to Research Investments](https://www.sec.gov/oiea/Article/edgarguide.html)，2018-09-04、更新2018-09-05，本轮实际返回194行；L59–66说明officers/directors及10%以上持有人披露，Form4为持股变化申报。它不是“违法内幕交易名单”，也不是公开披露之前获取私人消息。

官方访问说明另标明部分受理/传播跨日、夜间索引生成，以及受理后修订/删除可能重建季度索引。历史上最终状态的文件不自动等于当时可用快照。FAQ中的时间说明采用其原文EST表述；本轮未核任何记录的夏令时转换，不随意把无时区字段当UTC。

## 失败与覆盖

`https://www.sec.gov/about/forms/form4data.pdf` 的原生open本轮返回Internal Error，HTTP状态/正文UNKNOWN；不据此称403、表格不存在或需要账号。查询LOCAL_BLOCKERS后没有重试，也没有下载该PDF；上述一般申报规则来自独立可读的官方投资研究指南。没有用其他入口重取被明确拒绝的内容。

保存文件：01-sec-discovery.native.json为发现线索；02-sec-faq-form4.native.json含实际FAQ与PDF错误；03-sec-research-access.native.json含实际指南/访问说明。未获得源HTTP头、精确逐请求UTC或原始HTML字节，源HTTP状态UNKNOWN；原生文本内容与hash可核。实际读取窗口为2026-10-19 04:42–04:45 UTC。

结论：**披露这一信息层有正常免费、可复用的官方路径**；完整历史预测效果、市场数据权利、可交易时序、净费用及容量仍由不同证据证明，不能因为免费就说盈利，也不把尚未核的行情条件写成一定要买机构数据库。
