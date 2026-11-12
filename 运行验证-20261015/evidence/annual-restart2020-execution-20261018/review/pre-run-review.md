# 2020新本金四账：独立预运行审阅

**READY_FOR_ONE_FORMAL_UNIT，无必须修正项。**

- **restart_adapter.py:10–12,170–196**：源仅白名单日期/P/量/冻结f/生成日及核对flags，2020–2025共2192点；两来源字段完全一致。旧单位/财富/fee/收益未作为新状态；旧flags仅核对，不控制新账。
- **restart_adapter.py:45–91**：每账5000cash/0BTC独立入场，目标按post权益与实际交易额自融资；同成本A/B首笔结果断言相同，不复制旧2020首费。A每Jan1设置新pending，B只在未首次完成前跟同一年度pending；成功后B单位现金不变。新年替换未完成目标，terminal优先。
- **restart_adapter.py:85–123**：q普通pre_next/pre-1，末区间post_last/pre_prev-1，终行空；首末fee各一次，净因子与终值勾稽。DD起始5000加逐行pre/post；年界下一Jan1 pre、单位现金继承、六年完整，末费只归最后年。
- **restart_adapter.py:238–267**：首笔与下一非零重配前共同路径逐行assert；两成本risk A/B净vol闭区间[.8,1.2]，分母0则不匹配；terminalinvalid优先；25/50净正/财富/Sharpe/DD原门槛准确，undefined不能通过，无bootstrap。
- **restart_adapter.py:215–250,273–275**：auth与冻结文件身份、preflight全部input/source/reference、rootgate源码集合；exclusive正式锁；配置seal→四账seal→统一metrics→finalseal；输出exclusive避免覆盖，正式失败后不重跑。
- **supervise.py:11–49;fixtures130–168**：CPU2环境、单stdlib进程无线程池；600秒累计session，RSS512MiB/目录32MiB采样监督，绝对UTC08:46:40；prepare0.122323209秒exit0/sampleRSS59080704B、目录313188B、无正式锁。已有合成收据覆盖freshentry、carry、annual/pending、terminal/zero、年界、q，未重跑。资源轮询不是OS瞬时硬限额。

16项输入/产物身份均匹配。preflight points2192/intervals2191，首目标0.7853985165876642、截止2019-12-30，未生成市场账户或评分。已授权完整单元，无需新的人类确认；仍须root内部gate后正式运行一次。

源绑定：
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/annual-restart2020-execution-20261018/restart_adapter.py`，18960B；SHA256 `001a7e1728868824a6adf9f5fa0a6347e43d48d631a34faf712bbcf8bbc5cd7d`。
- `/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/annual-restart2020-execution-20261018/supervise.py`，3650B；SHA256 `6b29e5e936d799fec4d0e70be551b7efc5c7b954fb9a65e7c72bd36ccccab2fc`。

冻结protocol SHA256 `96c0a93af2de1d4d5e9a9bd151b11520dd1e1e56871ef57820013a11e77bdf98`。本轮未import/执行Owner代码、生成新市场路径或指标、运行模型/随机检验/网络/账户/交易。只写review文件。后验独立核验时间须另外计入600秒，不能声称由Owner监督器覆盖。实际model/effort/speed UNKNOWN；本pass不证明真实费用、成交或容量，也不构成科学结果。完成停止。
