# 正式B核算前独立审阅

**PASS_FOR_SINGLE_FORMAL_UNIT。无必须修正项。**

- **static_hold.py:85–116**：B保留pretrade5000，首行仅复制A同成本post单位/现金及既扣首费；中间原单位现金不变；末次按实际BTC×P扣比例费一次，零量不清仓。普通q为pre到下一pre；最后q为pre到末post，末行空。
- **static_hold.py:118–158**：年度按区间起始日归属，下一Jan1 pre作旧年终；2020-01-01 pre作两半边界，无额外交易；DD使用起点及逐行pre/post；年度单位现金继承，末费只归最后年。
- **static_hold.py:223–262**：A仅加载已封存持仓与收益观测，重新描述统计用于统一口径核对，不生成A持仓路径；25/50分别继承各自首笔。两成本A/B净volratio[.8,1.2]，技术未清仓优先于risk不合格，收益/Sharpe/DD门槛未改；不做bootstrap或择年。
- **static_hold.py:211–232,263–264**：执行前固定auth/doc/输入与完整source集合；exclusive formal锁；配置seal在B路径之前，B25/B50全账seal后才统一评分，结果再封存。
- **supervise.py:11–49**：prepare累计0.121397540999169秒，正式运行继承已有session累计600秒上限；CPU2环境且单stdlib进程无线程池；采样父子RSS512MiB、目录32MiB；绝对UTC07:58:21截止，总work2h；失败保留独占lock不重跑。RSS/磁盘为轮询监督，非瞬时OS硬配额。
- **preflight/health/synthetic/session-001原件**：现有合成收据PASS、prepare exit0、samplepeak70860800B、目录28809B、no_live_worker=true；无formal锁，无市场账或新评分。只读核验15项artifact/input哈希全部匹配；未重新执行预检。

源绑定：
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/annual-vs-static-execution-20261018/static_hold.py`：17631B，SHA256 `27a6678a7e43accaf7cf4d32f9731c92f6d37a503140bfc76db2f5a6e783cd1a`。
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/annual-vs-static-execution-20261018/supervise.py`：3663B，SHA256 `86811c38a011f6e6aa34dca352242bf25af93731a4ad01d321775e6e40cbe0eb`。

固定protocol SHA256 `608007d4003531308ffa7e2aa21d5797446438202491de6d3f2f7e5ca977b3bf`。本审阅未执行来源脚本、市场路径或指标；未重跑preflight。只写review文件。当前通过仅适用于已授权单次正式单元，不冒B已运行、盈利、真正OOS或可成交/容量证明。actual model/effort/speed UNKNOWN。完成后停止。
