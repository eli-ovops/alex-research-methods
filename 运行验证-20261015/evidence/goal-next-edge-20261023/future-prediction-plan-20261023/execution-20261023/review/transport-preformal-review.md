# Transport局部静态审阅

READY_WITH_LIMITS；must_fix=[]。仅审新增运输入口，复用已审主challenge.py结论，不启动任何阶段；Root统一绑定release后才由唯一Owner执行。

审阅UTC日期2026-10-23；精确起止时分UNKNOWN；实际model/effort/speed UNKNOWN。全文阅读transport.py L1–274、transport-checks.json、TRANSPORT_READY.md、transport-READY-sourcehash.json；核四小件SHA。未运行helper/合成/网络，未读行情，不导入模型或数值包。

- L23–28、82–90固定两个11月1日URL，只有11月2/3日UTC12点后可调用。显式NoRedirect，只有匿名GET，无HEAD/Range/认证或替换来源。时刻门允许当天12点后执行，Root仍须按固定12点安排，不能自行延日。
- L175–207每日期独占marker；Nov3要求Nov2结果，完整件只核固定路径/存在/字节复用，不发GET；未完整件仅Nov2明确404方可第二日期获取，其他错误写HALTED，partial保留。完整件后续内容SHA由既审主代码在独立机械QC中核验，运输复用分支没有第二次hash大源。
- L92–173应用读取前限制剩余下载/盘额，流内压缩SHA与gzip EOF/CRC，完整才将自身新建part改名；每完整单源即时metadata保留，失败不删除。网络报警覆盖每个请求/CRC段，finally累计墙钟入usage；下载128MiB、盘192MiB、网络1800秒、CPU600秒/RSS1GiB共用现有usage。应用读取字节非真实wire字节，方法已披露。
- L179–184逐日期Root release绑定transport源码、方案及MODEL_SEALED自身SHA；运输脚本不调用challenge、不解析CSV价量、不触发拟合/预测/评分。train-release须由Root额外纳入transport_code_sha256，之后随主代码写入的release SHA封存；Root每日期须沿该同一运输源码放行，不能仅凭可重新签release就换版本。当前检查的是这条待执行封存契约，不冒称MODEL_SEALED已产生。

现存合成只是日期边界、拒redirect和内存gzip损坏识别，非真实下载证据；最后两项纯传输保护增量以当前源码静态审为依据，不称合成曾走完整真实下载。真实文件存在/许可变化、网络完整性及最终资源仍待未来原件；404并非数据或模型失败。原金融STOP与非盈利边界不变。

- transport.py: `ae3223913c4f403aea7e790bec12435d474dcd21b6b3311d0aae416788db8b8f`
- transport-checks.json: `d6e9ec5324551cdde5a380d56d7e3c23640338324d54430c093c347d1c29e630`
- TRANSPORT_READY.md: `a5fbbc97bff0e8a1a1fc780d18a6752597246fe932234f2b77a94d59d0b056c8`
- transport-READY-sourcehash.json: `fb61c6a272eb5fcbe6792090b719d1920d0bc02638a535e9c09b02a788febeb9`
