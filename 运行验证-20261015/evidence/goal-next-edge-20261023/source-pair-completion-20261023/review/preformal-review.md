# 独立资料补齐单元：最小副本预审

PREP_READY；must_fix=[]。UTC日期2026-10-23，精确起止UNKNOWN。actual model/effort/speed UNKNOWN。正式尚未由Reviewer执行；Root按具体当前指纹放行后唯一GET。

完整静态读helper-minimal-change.diff、METHOD_READY及preparation-checks原件，并用惰性文本diff核实际旧/新源码差异与完整提交diff逐字一致。旧baseline为已审c7b5115f…b72252；未重开旧asof/CRC/数字检查，不运行测试或读行情。源hash与protocol核合，见preformal-receipt.json。

## 变更核验

- 正文身份精确期望kraken/BTC/USD，URL仍是BTC-USD dataset ID；没有别名兜底。有限identity witness先记录再精确比较，不符立即RuntimeError，异常分支保留partial stats。最多8组、每字段128字符且标截断，截断仅影响展示，不参与判定；计数不外推未读全日。该适配由首条实际前缀与官方字段口径支持，不认证所有行。
- WALL_CAP900仅原网络段含Kraken流内QC，socket timeout/alarm沿相同常量；CPU120/RSS256MiB/一线程/20MiB单GET/64MiB新盘未改。旧部分件不续传、不删除，失败继续保留并不重试。
- 新formal先算自身文件和新protocol SHA，核root-release.json顶层code_sha256/protocol_sha256相等，未匹配/缺release即在源读取前停止；exclusive marker及result保存code/protocol/release hash。新目录并不解除旧金融STOP。只机械版本绑定，没有新增市场或金融运行。
- preparation-selftest只核上述身份精确值、URL保持、有限计数/不符见证先保存再停、900秒常量；回执报告通过。未以其替代原已审方法，无需为本局部再跑完整fixture或独立执行。

固定local-asof86400秒、同戳末物理行、三固定无价格见证、exchange倒序仅报告、local异常拒配对、源顺序/字节hashCRC/显式禁redirect等无额外变更，沿旧结论复用。结构完整也不认证feed完整、预测或经济优势。

当前代码SHA256 ca94f831fee881bd2dcff3f3bd6e3dc292b29ddd9edac9e25398500c5979cb61；protocol949855868a98419c11c6dc50f07f0c7595024ef9ff15482cb50051691756f4c3。其余具体指纹见receipt。只写新review，不改Owner/Root/旧件；零网络、GET、原行情/partial、模型/策略/金融核算。
