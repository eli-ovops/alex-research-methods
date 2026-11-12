# 当前合并结论：固定一个数据候选，停止扩大供应商搜索

核验日期：2026-10-17；本轮只研究，行情文件下载、模型运行、训练、回测、交易和新增付款均为0。

**下一步优先核 Kaggle `mczielinski/bitcoin-historical-data` 的固定版本文件和时间定义。** 已取得发布者明确的 CC BY-SA 4.0 数据许可声明，商业用途未被 NC 条款排除。这足以支持进入有限数据质量核验；不是数据完整、预测有效或扣费盈利的证据。本轮没有发现新的赚钱模型或改变既有失败结论。

## 已经决定的路径

| 候选 | 原始证据支持什么 | 尚不能声称什么 | 决定 |
|---|---|---|---|
| Kaggle 长历史 BTC 数据，ID1346、v755 | 官方页面内嵌数据集元数据明确 CC BY-SA 4.0；不是从软件代码许可推断 | 未取得 CSV 表头、内容哈希、实际时间范围、匿名下载结果或完整质量统计；上游权利未全面核 | 固定此候选，进入小范围只读质量核验 |
| Binance Public Data | 数据专用条款明确允许纯个人、非生产历史研究；包含 NC 限制及实盘/商业限制 | 不能从免费和 MIT 软件许可推导整条盈利研发或未来实盘许可；当前用户具体访问条件未核齐 | 本轮保留，不再作为下一步默认数据源 |

### Kaggle 的正面许可与实际边界

[官方数据集](https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data)匿名页面读取成功。页面声明发布者 Zielak / `mczielinski`、version755、更新于2026-10-17T02:10:25.14Z；文件名 `btcusd_1-min_data.csv`、1分钟 OHLC 及 BTC 成交量；声明历史为2012年1月至今。ZIP 大小元数据为111,192,280字节，**没有下载此 ZIP，也没有核验未压缩 CSV 大小或实际起止日期**。

页面许可为 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/legalcode.en)。这份许可没有非商业限制；分享时保留适用署名、来源、许可及修改说明，分享改编材料时遵守同类许可条件。不能据此断言私下研究必须公开，或每个模型权重自动都要开源；也不因文本未点名机器学习就增设一律书面许可要求。授权仅覆盖发布者有权授予的权利，上游条款与权利链尚未全面核验。

数据卡称最初来自 Bitcoincharts、现直接来自 Bitstamp API；[作者采集仓库 README](https://github.com/mczielinski/kaggle-bitcoin)称每天补取、合并再上传。只读了 README，未执行采集器，也未将当前生成代码绑定为 v755 的确切生成版本。数据卡承认缺失时间、跳跃可能由交易所或采集故障造成。去重与完整性仍是发布者尽力声明。

`isAccessibleForFree=true` 与 `requiresSubscription=true` 同时出现，不能据此判定付费、必登录或可匿名下载。分钟柱时间戳单位、开收盘边界、最后完整柱和修订机制也未确认。数据许可、访问方式和数据质量分别判断，不相互替代。

### Binance 为什么暂不优先

固定提交 [`d571690eb66760763b0bd6e27e8cd35603c7e244` 的数据条款](https://github.com/binance/binance-public-data/blob/d571690eb66760763b0bd6e27e8cd35603c7e244/TERMS_AND_CONDITIONS.md)标记v1.0、更新2026-08-26：§4.1提供纯个人非生产历史研究的正面范围；§3.4商业用途另需协议，§4.2排除实盘自营执行、商业自动下单和收费信号。长期赚钱目标不自动否定所有当前文献研究，但也不能把所有盈利研发都改称非商业。数据条款纳入主 Terms；尚未完成其对当前中国内地用户 Dataset 访问条件的具体适用核验，不能猜允许或禁止。本轮未取行情样本。

## 唯一下一步及验收

只核 Kaggle v755 的官方文件元数据、实际表头、未压缩体积和时间字段定义；正常访问可取得小样本时，限定检查时间单调性、重复、缺失及 OHLC 关系，保留来源和读取时间。遇到登录或明确访问拒绝，只停受影响步骤并在确有人工必要时告知用户。不自行注册、不绕过访问控制、不下载全量、不运行模型或回测。

能确认固定版本、字段和已结束柱的含义，才值得准备一份固定研究协议。若仍不能取得合格样本，精确记录缺口，不把元数据当行情。后续若进入模型或收益实验，须保留样本外、费用、滑点及回撤验证；数据准入成功本身不证明其中任何一项。

研究的最终目标仍是找到个人可复制的净赚钱环节，并检验可放大的边界。目前只推进了研究基础，距离 Gerko 1% 财富的可行路径尚无证据。

## 本地原件

- [Kaggle 原件与逐项核验](</Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/Kaggle-BTC-long-history-license-20261017/metadata-audit.md>)
- [Binance 原件与逐项核验](</Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/Binance-public-data-rights-20261017/data-audit.md>)
- [Binance 独立审阅](</Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/Binance-public-data-rights-20261017/review/review.md>)
- [Kaggle 独立审阅](</Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/Kaggle-BTC-long-history-license-20261017/review/review.md>)
