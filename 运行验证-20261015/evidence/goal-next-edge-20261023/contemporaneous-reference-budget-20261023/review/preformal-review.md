# 同时点报价距离统计：预正式独立审阅

结论：PREP_READY；must_fix=[]。这是静态方法/实现准备验收，不是统计执行许可或结果验收；Root仍须绑定当前版本放行。

审阅UTC日期：2026-10-23；精确起止时分UNKNOWN。继承实际model/effort/speed UNKNOWN。规则沿用PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4、HANDOFF-2026-10-10-v2。

## 实际覆盖

完整阅读新reference_distance.py、helper-change.diff、METHOD_READY.md、preparation-checks-final.json；既有Source/asof仅按完整diff审实际改变，复用此前已审方法。纯文本比较确认该diff恰为旧已审helper至当前源码的完整差异。核对当前协议与宽度增量。未运行helper、合成检查或Notebook；未打开行情源、执行统计、金融核算、模型或策略；未联网。

## 实质结论

- Source返回并保存包含bid/ask的观测tuple；at(t)只返回local_timestamp≤t的最后物理行，正式L439从b[3:5]/k[3:5]计算。后继pending可用于顺读QC和时钟见证，但未被当成当前报价。相同时间戳规则未改。
- L303–314五式分母分别为Bitstamp mid、mid、mid、bid、ask；absD取D绝对值。严格阈值用Decimal交叉乘法比较，未先转浮点判断等号；S_B>2c为同一时点共同参考价满足双侧距离的必要宽度条件，未替换成动态利润判断。
- L326–376全部有效层与三个互斥年龄层分别保留计数、固定nearest-rank（偶数中位数取较低中项）及空层UNKNOWN；阈值、年龄1s/5s边界已有受影响小合成原件。浮点只用于分位展示，不用于严格阈值。未选择较有利层作为主结果。
- L378起入口校验Root release中源码/协议SHA并独占创建正式marker；全部源顺读完、EOF/CRC/哈希/旧QC分母核合后才发布统计。8MiB输出、120CPU秒、256MiB与错误停止检查可见；不存在网络下载入口或信号/仓位/收益路径。

## 限制

本验收不独立执行已有合成检查，不证明真实源必通过。正式结果仍须核小终态原件、固定见证和分母；不再次全扫源。二进制浮点分位展示存在通常舍入，Decimal阈值口径独立。报价年龄不是断流/个人时延；同时点Kraken mid不是已知未来公平价，网格数不是可交易机会。30/40bp仅当前标准费表条件参照，非历史或本人费率。当前距离或宽度不足不能否定未来预测能力，不解除旧金融STOP。

## 身份绑定

- `protocol.md`：`bfa7731e607cefaa03d0bc29b6dd9605f6eb2b8f19d33bf129caa4687f1ea333`
- `owner/reference_distance.py`：`7dc8a1017efc8aa6beb2cad1284ddd1ba383f1c84b33e926519677e795a8cf84`
- `owner/METHOD_READY.md`：`f30442d600d4b101355c43d2d5c1f6acd4c39e6b22588349075837980a3d890d`
- `owner/helper-change.diff`：`943b234bf53849e537fb1cb33f646ba96e71fb963eef2379847c1c66386737e1`
- `owner/preparation-checks-final.json`：`62d71e4525194604302da5553ccc751023fe86d54c00cf65dc7e6cfd997ffd8e`
