# HftBacktest 官方数据准入：双时钟格式正面，实际样本许可未闭合

**PARTIAL：官方当前格式明确exchange/local双时钟；本轮未取得一份身份、体积及数据许可均可核的免费实际样本，不通过样本准入。**不是证明样本不存在或方法不可行。

只读latest文档，未混旧hft.readthedocs.io v1：
- [主页](https://hftbacktest.readthedocs.io/en/latest/) L60–64将Data/DataPreparation与支持者数据入口列为来源。源码repo链接为nkaz001/hftbacktest；latest页面没有固定commit或明确发布日。
- [Data](https://hftbacktest.readthedocs.io/en/latest/data.html) L11–26为8字段格式；exch_ts是事件在交易所发生时刻，local_ts是本地接收时刻，另有px/qty及L3才用的order_id。L57–62明确两种时钟顺序可能不同、可加base latency/offset修正负延迟；规范能容纳双clock，不证明所有已发布normalized字段未经调整。
- [DataPreparation](https://hftbacktest.readthedocs.io/en/latest/tutorials/Data%20Preparation.html) 实际抽取仅至L60（页面声明292行，不冒全文）。L17例示本地usdm/btcusdt_20240808.gz，L26/28说明首token为本地接收纳秒；L31/L46–48显示转换含排序/延迟修正。文件名是教程引用，不是已取得原始文件身份/日期覆盖或公开download回执。文档展示行情样例不作本轮数据payload或质量核验，未另请求其npz/CSV/gz文件。
- 主页真实支持者链接解析为 https://reach.stratosphere.capital/data/usdm/ ，一次原生读取502 Bad Gateway。查LOCAL_BLOCKERS未见该资源条目，未重试、改身份/认证或另走别名。因此文件清单/大小/历史范围/该方许可均UNKNOWN。

本轮未读取实际数据LICENSE；代码MIT即使由其他分工取得，也不能覆盖支持者、交易所或其他供应商数据。本Owner不依据public链接给个人预测研究/外部复核通用许可。若后续实际样本又来自Tardis，须复用原2026-10-17条款审阅的具体Data/DerivedData和外部披露条件，不以本框架开源许可绕开；本轮没有把Tardis文件确定为已准入样本，也未重研其条款。

唯一最小缺口：**一个可读的实际公开样本说明/清单，将精确文件/日期/体积、双时钟来源及适用数据使用许可绑定到同一对象。**当前只列官方入口，不自动下载、采集或转换。不为因果预测额外要求所有L3，但incremental状态/序列仍由code分工核。

动作4：open1＋click3，共3次原生调用；每来源小文本，逐次UTC未捕获，读取日2026-10-18。已保存完整工具返回及实际读取覆盖，非HTTP原件。没有npz/CSV/行情包GET、源码/转换器/collector执行、模型、回测、账户、安装、付款、交易。actual model/effort UNKNOWN。原件不改，完成即停。

