# Crypto Lake固定客户端源码审查

结论：**匿名sample选择与客户端字段变换路径已核；不等于sample实际可读、其服务器采集时钟真实或已通过因果QC。** 所读读取路径未见按received/origin时间补值、前移或自动时间排序，但存在通用Arrow/pandas类型与时区处理；不能将未审服务器生成过程补成无修正原始接收数据。

身份固定为完整tree `42f0cc5fcf23a19050285d89cb4be075359f55af`，不是commit SHA。复用root既有`lakeapi-main.py.txt`全文，不重取。新增5源码均按固定tree中的blob URL取，HTTP200，Git blob独立计算全匹配；原响应137,608B，惰性源码98,734B，每源小于128KiB。URL、精确UTC、SHA256见source-receipts.json；main/tree等既有输入指纹见audit.json。

简称M=既有main.py；P/U/R/D/T分别为本目录_read_parquet.py/_utils.py/_read.py/_describe.py/_data_types.py惰性文本。

| 审查项 | 代码逻辑已证 | 不能升级的结论 |
|---|---|---|
| sample与匿名 | M:56–77选`sample.crypto.lake`；True把U.default_botocore_config包装为botocore.UNSIGNED。M:116–119默认session region=`eu-west-1` | True是明确匿名配置意图，但不证明执行SDK完全不查询凭证或不调用其他服务 |
| 文件/manifest定位 | M:163–174 S3表路径；M:304–306、456–463为table/exchange=.../symbol=.../dt=.../filename顺序。D:159–176用ListObjectsV2、Bucket/Prefix、可选Delimiter，默认页1000 | 可以定位metadata请求；实际对象存在性、大小及访问状态由manifest Owner独立核；本Owner不访问行情 |
| sample目录缓存 | M:443–454的contents helper需bucket.split('/',1)得prefix，再取prefix/table/contents.json.gz；异常回退。sample bucket无slash，因此该分支先本地解构失败，回到M:417–437列表路径 | 不能把推导的sample/table/contents.json.gz当已证manifest接口；SDK列表会先列整表，再本地按分区筛选，不是目标日期的最小请求 |
| 分区边界 | M:127–138、393–404按日期筛start含/end不含，与symbol/exchange；不在此按每行时间截断 | 传入小时/分钟不是已证网络或行级上限；M:206–207 row_slice在数据读回后才iloc，不能用它保证小下载 |
| 重命名/时间 | M:209–224 amount→quantity、receipt_timestamp→received_time、timestamp→origin_time，两旧时间列用unit=ns的pd.to_datetime；trade id→trade_id；funding时间先s失败再ns | 若输入已叫received_time/origin_time，此分支不必再cast。没有以名称证明采集时钟真实；缺失origin原值未在这里插补 |
| 时间/索引通用处理 | P:82–128恢复pandas index元数据；时区列若naive先tz_localize(UTC)，再转metadata timezone；P:131–172由Arrow转pandas并加分区列；T:438起为类型映射 | 这是表示/metadata假设，不等于服务器没有调整时间。未见对这两个时间字段按未来锚点补齐、offset或clamp；仅对所读路径作有限阴性发现 |
| 行序 | P:576–620按文件路径读取；R:123–152线程map按输入paths收集，R:107–120 concat(sort=False) | sort=False是列拼接参数，不证明按时间排列；未自动按received/origin排序或验证单调、去重。不能把文件/concat顺序当原始接收顺序 |
| 凭证/付费路线 | M:120无条件_login；M:231–252尝试Lambda登录并调用session.get_credentials，异常退unknown/s3；M:323起CloudFront分支会取冻结凭证并签名；R:145/U:39–49多文件线程前序列化session也调用get_credentials | 匿名sample函数不构成“绝无凭证读取”的端到端证明。未见购买/扣费代码；订阅提示及带凭证分支不等于实际扣费，本轮均未运行/读取凭证 |

未见疑似硬编码共享凭证值；以上只讨论程序引用的凭证方法，不读取或复述任何真实凭证。sample bucket与region为公开位置常量，已及时发manifest Owner。没有执行Lambda、S3列表/数据读取、CloudFront或SDK。

最小后续要求（不实施）：将实际取得对象身份/hash、parquet原字段单位与上述变换版本绑定，保留raw时间及稳定顺序；独立检查received_time缺失/单调/重复、exchange clock缺失与相对顺序，再定义预测可用时间。客户端只把服务器提供的时间列转表示；服务器采集/处理/校正日志、其received_time是否为处理完可用时刻，仍需原发布者定义/原件。不能以此代码审查认证真实样本时序或利润。

明确未读：_fs.py、_cache.py、_config.py、服务器采集/写文件源码、依赖库具体运行行为及任何行情文件；不声称全SDK所有路径审完。正文参考与5源哈希均已保存，5读用尽即停。

规则沿scope且未变；actual model/effort/速度UNKNOWN。0来源import/执行、SDK/示例、凭证/账号/注册、安装付款、行情GET/range/解析、模型/统计/回测/交易。仅code目录保留证据与报告，无清理项。
