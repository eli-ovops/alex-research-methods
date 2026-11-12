# Coin Metrics许可与CHRIS控制流独立审阅

PASS。实质差异、必要修正：无。PASS只指原件与结论一致，**不代表盈利目的数据使用获准**。全部data-audit声明输入指纹匹配，14份主要实读输入完整指纹与定位见review.json。

## A. Coin Metrics

- README:39–43、LICENSE:1明确针对data的CC BY-NC4.0；API-basics:9–11另行明确Community API非商业许可，未从软件许可推断数据权利。保存CC legalcode原文L91、L98–99、L132明确非商业目的边界。个人、本机、尚未交易不能自动改变项目盈利意图。真正符合NC的一般研究有条件许可，与本项目盈利目的模型研发/交易获准是不同判断；后者仍UNKNOWN_NOT_ADMITTED。没有无依据给商业训练绿灯，也未因缺ML专门用语制造一律书面批准条件。
- 保存GET原件与回执相符：HTTP200、439B、2024-01-01至01-05恰5条、asset/time/PriceUSD三字段、无分页链接；只支持这次匿名访问和字段可取得性，不证明许可、全历史或完整质量。官方覆盖说明与实际五行检查分开。
- PriceUSD-definition:13–17、94–96明确UTC日终参考价及与ReferenceRate时间戳约定不同。00时日期标签不等于当时已经发布；精确延迟、历史首次可取得时间和point-in-time修订规则未核。README:20–22和reference-rate-overview:51也不支持无修订承诺。
- 保存terms-of-use读取结果是Talos产品overview跳转，不是条款全文，不能据此放宽许可。下一步只是许可适配问题，不自动取数、训练、交易或改名用户目标。

## B. CHRIS下载器

data__download_quandl_data.py:15–27的`data = quandl.get(...)`只在调用成功后赋值；except BaseException只print，无continue、重置或重新抛出。首次迭代失败可导致后续访问未绑定data。先有成功赋值、后有捕获失败时，若旧data仍通过Settle列和最早日期条件，且写入成功，就可能按当前ticker名保存旧数据。根的条件路径判断准确；本轮未执行或模拟，没有证明任何实际下载发生此事，不能用于解释旧BTC失败或反推论文数据错。

`start_date="1988-01-01"`只是请求参数，不是已测覆盖；data__pull_data.py:11–16的Settle→close只是字段映射，不证明取得行情、可成交价格或实际收益。

本轮仅文本/JSON及哈希，无新联网、账号/凭证读取、下载代码执行、模型导入/构造/权重读取、预测、收益重算、回测、交易、安装或付费。未运行fixture或单元测试。只新增本目录review.json/md，未改原件。实际模型/effort UNKNOWN。完成停止。
