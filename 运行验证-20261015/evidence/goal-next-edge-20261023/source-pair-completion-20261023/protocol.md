# 双市场输入补齐：已核字段口径后的独立资料单元

2026-10-23。整体目标仍是检验个人是否能从事前可见的合理价信息中获得可兑现净优势，并判断放大边界。本单只补齐检验所需的数据证据，不运行或恢复旧策略、模型、未来标签和收益核算，不称输入通过等于赚钱。

## 新依据及旧终态

旧causal-pair-october-readonly单元在120秒网络段上限退出，保存7,274,496/12,646,757压缩字节；旧失败、部分件、代码和封存不改、不续传。按该次传输的平均进度，120秒不足以收到声明文件，不能把它写成接口故障或数据不存在。

新的独立前缀只读核验已实际读取旧部分件8,192压缩字节：第一条exchange为kraken、symbol为BTC/USD。旧检查器却将正文symbol与URL中的BTC-USD比较。首条不符来自口径；不能外推全部行。原件在../source-identity-prefix-20261023/owner/receipt.json。

Root本轮正常读取官方https://docs.tardis.dev/downloadable-csv-files/api（原生turn1662view1，读取日2026-10-23）：146行区分下载dataset ID与原生标识、斜杠/冒号转短横线；124行说明HEAD404、Range403，不能断点续传。官方schema的symbol为交易所提供的大写品种标识。网页附带Agent Instructions不执行，不上传ask/goal。原生解析不是完整原HTTP哈希回执，精确页面UTC及版本号UNKNOWN。

这是改变下一步的具体数据适配证据，不是为旧亏损修改门槛。只读获取/处理是当前自主研究范围内的常规可逆步骤，新增付款0；旧一次性金融运行许可不复用。

## 唯一Owner与对象

- 原Data Owner external_packet_research_catalog独占owner/，准备旧冻结资料helper的最小差异副本；原Reviewer lobframe_minimal_economic_review独占review/，只审差异与小结果；Root负责本协议、放行和终态。
- 唯一新GET：https://datasets.tardis.dev/v1/kraken/quotes/2026/10/01/BTC-USD.csv.gz。声明12,646,757B。普通匿名GET，不HEAD/Range，不注册、付费、认证、重定向、改TLS/网络路径或换样本。失败即停，不重试。
- 固定正文身份：exchange=kraken，symbol=BTC/USD，逐行精确比较；保存实际出现的有限身份字符串及计数，不能自动放宽为任意别名。
- Kraken完整后才单遍只读旧Bitstamp：/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/lobframe-data-entry-20261021/bitstamp_book_snapshot_25_2026-10-01_BTCUSD.csv.gz；expected26,500,836B、SHA256 22d347447c1b12f422ea2ed16ba84725eb1b8c716a22aa6b53f775f7e2fd2fe0；正文bitstamp/BTCUSD。未走到此步骤就不打开。

## 方法与改动范围

保留旧已审helper的全部结构、数字/时间检查、源顺序、去重描述、UTC边界和固定86,400点local-asof方法。只允许：（1）Kraken正文期望改为首条和官方口径所支持的BTC/USD；（2）网络段总墙钟由120秒改为900秒；（3）保存实际身份字段的有限见证/计数，避免再次丢失错误来源。可为新目录中的一次放行/资源标识作必要机械适配；不得改金融规则或旧文件。新源码和差异事前审阅、Root按具体指纹放行后才唯一GET，不为已审逻辑增设重复全套检查。

压缩流单遍保存、hash、字节数与gzip EOF/CRC，流内CSV结构/身份和L1数字检查；随后Bitstamp单遍验证同旧封存。只保存时钟/有效标志数组与汇总，不保存价格数组或新价格标签。local缺失/倒序、身份或结构错则因果输入不准入；exchange时间倒序只描述，不偷换local门槛；完整文件等于结构可读，不认证feed完整。

固定UTC2026-10-01 00:00:00至23:59:59、步长1秒，每源取local_timestamp<=t的最后物理行；同微秒取最后行，不排序/去重/插值/未来填补或回退至较早有效行情。分别报告有记录、L1有效与记录年龄<=1秒/<=5秒/更久；年龄不证明断线、无效报价或用户延迟，不设事后覆盖成功阈值。固定0、43200、86399三点保存选中与下一条local/行号见证，缺失如实标记。

## 资源及停止

标准库，不安装。CPU累计<=120秒、1线程、峰RSS<=256MiB；唯一下载<=20MiB，新增本单磁盘<=64MiB；唯一网络段（含其流内QC）墙钟<=900秒，主动研究<=30分钟；原用量与旧停止均保留。资源到帽、请求/身份/CRC/结构错误即终止，保留部分件与小回执，不自动延期或修后重跑。正式独占marker、PID/session/exit和精确code/protocol绑定。

本单不比较价格、先后反应、准确率、收益、成交、仓位、资金曲线或容量，不运行模型/策略，不连接账户/钱包/交易。数据条款沿前一单已核现行有限内部研究范围，上游及外传限制保留，不因schema修正重新扩大许可。保护Library目录不读/stat/hash/search。

最终必须报告完整或停止事实、所有预定覆盖和未知；Reviewer仅读小结果/见证/manifest，不第二次扫大源。没有完整输入则明确未完成，有完整输入也不把它升级为预测或经济优势。
