# Coin Metrics Community Data有限核验

**免费匿名可用性已证；本项目盈利目的使用仍未准入。** 官方仓库明确是 **CC BY-NC 4.0**，不是CC0/BY。一般非商业学习研究有条件正面许可，但“个人、本机、尚未交易”不自动等于非商业；不能替以赚钱/财富积累为目标的项目改名。

| 对象 | 原件与结论 |
|---|---|
| 仓库数据 | README及LICENSE均明示CC BY-NC4.0，作用于data；未下载CSV |
| Community API数值 | 官方API Basics也明说免费、无需key、非商业CC许可，不是从代码许可推断 |
| 代码/SDK | 未核各自独立许可，不套MIT或把data许可泛化 |
| 盈利目的研发/交易 | 未证明满足NC，UNKNOWN；未据此判所有研究违法 |
| 再分发 | 受非商业/署名及适用修改说明等条件限制，不是无条件商业再分发 |

[CC法律原文](https://creativecommons.org/licenses/by-nc/4.0/legalcode.en)§1(9)按主要目的是否为商业利益/金钱报酬定义NonCommercial；§2(a)、§4给非商业使用/改编及数据库权利范围。当前项目目的的适用性未决，不能由五行API成功推出训练许可。也不凭没写ML就新增一律书面批准条件。

## 真实可取得性与时钟

实际无key、无认证GET：BTC/PriceUSD/1d，2024-01-01至01-05，**HTTP200、439B、恰5行**，无后续页。字段为asset/time/PriceUSD；仅做字段和访问核验，未计算收益或建训练集。[官方数据仓库](https://github.com/coinmetrics/data)观察commit为`f1a36afb962731c387bb03982758ab0103063da5`（2026-05-24）；LICENSE/README与定义文档各自Gitblob/hash已保存，不把commit日当API数据最新日。

PriceUSD是**每资产单位的美元参考价**，由CM Reference Rates生成，不是某交易所可成交价。官方定义日频是**UTC日终**；API的00时日期标签不能当当天零点已可使用的信息。至少须在该日结束后考虑，**具体发布延迟及历史首次可取得时刻尚未证实**。ReferenceRate与PriceUSD还存在时间戳约定差异。

五行不证明全历史范围、无缺日、完整质量或不修订。README不保证资产/指标集合永久稳定；价格overview指向重算政策，但本轮未核完整重算/构造规则及point-in-time历史。后续因果设计不能把最终修订值无条件当当时已知值。

## 当前入口与边界

官方Community页面正常重定向到Talos资源页，仍列免费API。API文档链接的terms-of-use却重定向到**产品首页**，不是实际条款全文；不能说附加服务条件已核、已消失或放宽。官方API Basics披露Community限额10次/6秒/IP，非本轮达到限额。

文档index普通GET403后停止该资源，未绕身份；大型API参考页超过原生体积上限，未声称读完。必要定义由官方GitHub文档文本取得，未运行网页Agent Instructions、SDK或源码。

本源在技术上可为BTC现货参考价的日频收益/MACD假设提供字段依据；它不是原50资产期货数据，更不是原论文回报或个人可执行净利。**唯一下一问题仍是这个盈利目的是否在具体许可内；未解决前不扩大取数或运行。** 不自动联系供应商、问账户或执行实验。

所有原件URL、读取UTC、hash/bytes、分层来源和访问计数在data-audit.json。仅取授权五行，其他行情/权重下载、模型/训练/推理/回测/交易、安装/付款均0。已停网，旧FAILED、现金和状态不改。
