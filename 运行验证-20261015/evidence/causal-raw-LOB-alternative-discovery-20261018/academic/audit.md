# 学术库候选有限准入

结论：未准入本轮“原始逐事件＋可见时钟”用途。只深入一项学术原发布者候选，开放许可为正面证据；不因免费或论文结果认定数据、预测或盈利通过。

候选：[Dryad / Building trust takes time](https://datadryad.org/dataset/doi:10.5061/dryad.q2bvq83rn)，作者Voigt、Hautsch、Scheuch。发布2023-11-28、更新2024-01-04；该版列orderbook_data.sqlite 27.41GB。宣称2018-01-01至2019-10-31分钟API快照，schema含exchange、ts、side、level、price(USD)、size(BTC)。采集叙述前25档，导出schema写1–20档，两者保留区别。以上是目录声明，未实查覆盖。

[Dryad现行条款](https://datadryad.org/terms)更新2025-05-20：§1为dataset采用CC0，§4给广泛复用依据；网站其他内容CC-BY与数据分开。个人统计预测研究属于合理复用范围，不额外要求专门ML字样。权利保证由提交者作出，平台不保证准确性或适用性；本轮不是完整上游法律审计。

决定性缺口：这是分钟快照，并非原始事件流；ts的单位、时区及request/response/本机可见含义未核。不能拿长历史替代因果时钟。体积亦非小样本，未核可控切片入口。

最后一次点击官方README文件返回工具记录403 Forbidden，未取得独立HTTP头/body；已查本地阻断规则，停止该资源，不换工具、身份或别名重取。landing内嵌说明已可读，拒绝不等于数据不存在或必须登录。

共6动作（3 query＋1 open＋2 click）、5个native调用，已停网。原生返回按顺序保存01–05-native-read.json；各UTC与URL在文件内，实际SHA/bytes见audit.json。未取行情payload、未执行源码或模型、未做统计/回测/交易。

若仍保留此来源，唯一最小缺件是发布者对ts及快照取得/可用边界的原始定义；本轮不发请求，不另改研究问题。没有证明其他来源不存在或方法无效。
