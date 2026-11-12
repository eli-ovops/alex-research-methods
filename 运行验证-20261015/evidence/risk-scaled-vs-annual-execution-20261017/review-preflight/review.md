# 运行前独立源码审阅

**PASS_FOR_SINGLE_MARKET_RUN。没有必须修正项。**

- **clock_and_continuous_account**（adapter183-231,94-141）：5402完整日源身份绑定；4383时点/4382区间，2014-01-01至2025-12-31；60收益总体std截至e-2、.40风险预算、1上限；每条成本账初始5000且年度不重置。
- **annual_pending_units**（adapter94-130）：Jan1固定f并替换旧pending；无量保持单位现金及原f，逐日固定时点再试，首次成功清pending；年内不再平衡；terminal先于新年逻辑且只清仓。
- **self_financing_cost**（adapter64-92,131-141）：phi纸面代数符合现金自融资，费用按实际BTC成交额；no-fill不收费，精确结转；q以交易前权益串联，最后q用末交易后权益，首末费用各一次；终点残仓invalid。
- **two_costs**（adapter301-315）：同points意图，两方法各25/50bps独立5000连续现金/BTC路径，不强求数量相同。
- **annual_metrics**（adapter234-274）：按区间起始执行日期归年，年初继承pretrade权益/units/cash；下一Jan1尚未发生交易的pretrade权益作旧年终值，末费只归最后年；非cash零std SharpeNone。
- **risk_and_tests**（adapter276-287,316-342）：两成本净波动比均须[.8,1.2]，终点技术无效优先于risk mismatch；单一25bps配对log差90日循环块10000seed20261017/linear5%下界；50仅固定压力条件，不择年/重配风险。
- **seal_single_use**（adapter289-315,343-344）：fixed身份+preflight9输入+gate完整source集合校验；exclusive market锁；意图seal在4账之前，4账seal在统一metrics/bootstrap之前；独占输出避免覆盖。
- **resources**（supervise15-56;adapter38-49,99-100,279-280）：prepare两次1.1071516659576446秒均计1800累计；CPU线程env2，已知父/子RSS采样512MiB、目录32MiB；UTC12:53:58Z终止与周期内deadline；总work2小时由固定绝对截止实现。采样资源不是瞬时硬内存上限证明。
- **prepare_fixture_fix**（snapshot diff;session001.stderr;session002.receipt;synthetic-fixtures）：首次失败在合成flat-holds传空列表，未进入行情准备/市场账；唯一diff仅三行flat holding夹具，第二次exit0；不是市场重跑。当前无market锁或市场账/指标。

固定proposal SHA `dfff60461de5beef77a98075d7e58837981c5bc08ef6980c08f2bc9743d13e6c`，protocol SHA `984e38b8c28f954a67dafa7eea0388f9bc3c0aa5d6610369b8d22f49467aa343`，authorization SHA `e71934fde63023503722add7720937d1288ddf771556f1598b653c8312909463`均实核。preflight九项身份均匹配（原CSV仅流式hash，没有重扫质量或计算市场收益）。完整指纹见同目录JSON。

供根gate绑定：
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/risk-scaled-vs-annual-execution-20261017/adapter.py`：19452B，SHA256 `4e39474c23c0974a6dc4d911e39935b0b031edebf0498ad82b2d8a51b38383a2`。
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/risk-scaled-vs-annual-execution-20261017/supervise.py`：3728B，SHA256 `706fb4a3b18025f602d0ab22c6029ae8479efa3ea0ed344c21ef976e0015e7a9`。

本轮未执行适配器、夹具、市场账、模型、预测、回测、bootstrap、联网或交易。只新增本审阅文件，未改原件。采样资源收据不冒瞬时硬上限；收益、可成交、容量、真正未来样本外均未由此证明。实际model/effort UNKNOWN。完成后停止。
