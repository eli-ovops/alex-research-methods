# Form4历史分类字段：官方缓存支持部分映射，规范正文尚未取得

结论PARTIAL：本轮未完成当前ownership schema和修订语义的官方正文验收。不可据字段名宣称已经能完整、点时地还原CMP三年分类。4项动作已用完；技术规范PDF正常GET403即停，不换通道。此前已核论文规则不重读、不重算。

## 原件层级

1. [SEC Ownership XML v3（2010）](https://www.sec.gov/info/edgar/ownershipxmltechspec-v3.pdf)的官方搜索抽取给出Appendix C字段映射；本轮实际PDF GET403，无正文/HTTP头/响应体hash。它是历史版本，不冒现行规范。
2. 官方EDGAR Filer Manual v77（2026-03-16）搜索缓存列Form4与4/A、Form3及5对应表；没有打开或保存全文，不把草稿v78搜索结果当生效规范。
3. 搜索还返第三方aff10b5One及transaction结构说明，未读取/不作为官方语义确证。未读取root另核的AAPL申报，不重复采集实例或扫描历史。

## 字段与缺口

| 所需内容 | 本轮证据与界限 |
|---|---|
| 公司/个人身份 | 官方v3搜索映射：issuer/issuerCik属于发行人；reportingOwner/reportingOwnerId/rptOwnerCik属于报告人。ticker/issuer名称不能当个人标识，个人同名也不能自动合并。联合报告、同人跨发行人识别及CIK历史连续性尚未核。 |
| 交易日/公开日 | periodOfReport映射最早交易日；不是每条交易日，更不是SEC接受/首次公众可见时刻。逐行transactionDate、完整accession/acceptance映射仍须原件核实。 |
| 修订 | dateOfOriginalSubmission映射原申报日期，4/A是修订类型（官方手册缓存）。尚无正文证明其逐行替换/补充语义；不可把4/A当另一笔新交易，也不可无证覆盖原件或用后修订内容冒当时已知。 |
| 普通股/交易性质 | 当前官方正文未核。必须区分非衍生/衍生表、securityTitle、交易代码与附注；持股增加不自动是现金买入，行权/授予/税款扣留/赠予/私下交易须分开。P/S能否直接等同公开市场交易，本轮UNKNOWN，不能靠代码字母硬推。 |
| 10b5-1 | 未取得当前官方aff10b5One定义/适用起始日；第三方搜索不能补此缺口。即使有计划标记，也不同于CMP的三年共同月份和routine吸收态，不可相互替代；旧档缺标记不能当false。 |
| 三年覆盖 | 字段存在或一个实例不能证明三年逐人历史无遗漏。缺报、晚报、修订、Form5补报、跨格式历史与身份去重仍需完整性证据，不得将“未见交易”直接当该年无交易。 |

## 最小下一原件与收敛

最小缺口是能正常读取的当前SEC ownership技术说明/官方代码说明（含修订与交易性质），再与root实际申报小样本绑定；不是采集全市场/三年历史。当前可准备字段清单，但不能给出数据READY或交易/模型运行结论。若root已有正常官方字段/说明，可在本轮总验收复用；本Owner不因403改变身份或追加请求。

来源工具回执保留URL、UTC及搜索内容；04-SEC-v3.receipt.json如实记录403及body hash UNKNOWN。0来源程序/XML实体执行、模型、回测、金融计算、市场数据包、账户、安装、付款或交易。actual model/effort/route=UNKNOWN。
