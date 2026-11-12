# 固定分片持仓与终稿独审

**限定PASS，material_errors=[]；完整净盈利案例未准入。** 0新网络，使用已有项目PyArrow26.0.0，`python -I -B`、CPU/IO线程设1、batch32768、`use_threads=False`被动读取唯一原Parquet。没有模型、回测、来源源码/SQL/SDK/EVM、策略、交易、账号凭证、安装或付款执行。actual model/effort UNKNOWN；PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4保持。

终稿绑定现版8357 bytes，SHA256=`bd9e371375a8bfde0bab3850087c2d889fccb2751e96761c62388b5ee24cc6f0`。同名JSON记录26份实际输入绝对路径/SHA/bytes、审阅UTC、独立逐项转移与统计。正文末段新增的增量损益澄清已纳入，原数字不变。

## 直接读取原文件核到什么

完整原文件SHA256独立分块计算为`1dd5745bbf06063f6f5e0af3909cb632c1289eda6d9a6ef2590a32a690290401`，大小20329654 bytes；与一次200回执、固定revision/文件URL相符。完整文件末3258 bytes与此前Range footer原件逐字节相同；ETag与旧尾部回执一致，但不是该文件SHA256。没有将文件名短hash或ETag单独当内容验证。

第一遍读取聚焦固定holder两token的前1800块及封存merge正对照；第二遍仅补取刚识别7tx＋封存merge的关联CTF/NegRisk原始行。未研究其他持有人经济，不是运行策略或重新生成交易。

- 实读644307行，623853来自CTF4d97…、20454来自NegRisk d91e…，chain均137、removed均false，块min/max86160001/86162000。20个scan标签及行数与root一致；标签不代替逐块全链完备性。
- 固定holder、两ID、86160176—86161975内独立解得8项transfer腿/7个tx，零重复身份。六项转入，另一次Batch转出两腿。各字段逐项与root结果相同。
- 原封存merge的3条CTF行与旧SQD全日志按txhash/logIndex唯一对应，contract、topics、data、block number/hash精确一致；不是全文件认证或独立共识证明。
- 同8tx共有46条该文件过滤内原始行，与root完整提取集合逐项相同。两次PositionsMerge为block86161965/log1235、amount16880000，以及block86161976/log1161、amount13110000；condition/parent0/partition[1,2]/2791抵押一致。前一次实际pUSD收款不在此两合约归档内，未当成已核现金。

## 数量与会计边界

| token | 前窗口转入raw | 前窗口转出raw | 再扣封存合并13110000后观察delta |
|---|---:|---:|---:|
| A（815515…741828） | 29990000 | 16880000 | 0 |
| B（751396…12729） | 30165000 | 16880000 | ＋175000 |

按六位尺度即A入29.99、B入30.165、各出16.88，加入封存合并后A0/B＋0.175。这是指定观察区间净变化，不是期末余额、免费库存、现金或利润。0.69项的from是7f95…f056，但operator仍为E111；事件不足以称免费赠与。未给市场名称、具体YES/NO标签或现实控制人归属。

终稿现版明确：若所有相关资产/负债/费用净变动闭合，可判断相对保留原库存的增量损益，不必强制追溯全部历史成本、假设期初零或FIFO，也不要求私人bot。**此澄清正确**；当前抵押现金价费缺失，连此增量损益尚不能判断；ROI另需本金和期限。没有把这些未知写成亏损或不可能盈利，也未将部分数量链提升为可持续复制。

## 来源与后续范围

五phase要点与实际回执相符：官方固定存储schema及generated client不足以确认钱包子过滤；后续已知块POST实际403/17 bytes并停止，不否认旧200。HF splits/info revision吻合，topics数组过滤未获原文支持；唯一标量已知tx filter超时无状态/body/revision/partial，不能记空。独立固定Parquet随后实际200成功，不把filter失败扩成原档不可读。

文件只含两合约原日志，没有完整USDC.e/pUSD、Exchange OrderFilled、gas/失败/native费用；许可仍UNKNOWN。公开读取/被动研究与生产商业交易授权分开。前阶段数据和错误原件均保留。

终稿固定HF版本/文件名/来源URL与回执一致；Apache/PyArrow链接为格式/读取方法引用；文末5个本地phase目录与所指原件存在。下一仅六已固定取得tx、3份4月成交文件footer的scope明确未执行，本审阅未开展它。所有历史FAILED及财富goal未改，不新增候选或验收门槛。

无需实质修改或扩大测试。此PASS确认原始持仓数量链及报告口径，不是净盈利、未来优势或财富目标通过。
