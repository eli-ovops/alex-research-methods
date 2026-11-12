# 标题信号replication交付：正式v2身份已核，文件manifest未取得

本轮2/5公开动作后停止受影响资源。实际Mendeley v2正文确认**2026-06-15发布**，不是先前搜索线索的06-14；正式作者、版本DOI、CC BY 4.0与README指引可见。但Files区没有返回文件清单，后续同URL普通GET明确403；未取得ZIP原始入口、实际大小/hash或包内signals/交易费用清单，不能作原始交付完成。

## 正式原件与读取覆盖

[Mendeley正式记录v2](https://data.mendeley.com/datasets/f39x226htv/2)：原生ref turn1065view0，L0–61均返回，保存 `01-v2-record.native.txt`。读取UTC窗口为2026-10-19 04:29:08–04:29:21，逐请求精确秒与源HTTP状态工具未给出，记UNKNOWN；这是已返回原生正文，不是重新搜索摘要或ZIP正文。

- L4–16：题名Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models - Replication Package；contributors为Alejandro Lopez-Lira与Yuehua Tang；description自述该论文replication。
- L6：Published 15 June 2026、Version 2、DOI `10.17632/f39x226htv.2`。
- L18–24：Download All按钮、Files标题、Follow README.md；没有实际文件条目、文件URL或单独README链接。出现按钮/README名称不等于单取README或ZIP已验证可得。
- L34–36：CC BY 4.0。L61页脚对开放内容适用Creative Commons的保留说明，不把通用页脚当覆盖特定开放许可的反证，也不将开放页面许可扩成未读第三方数据的完整授权。

另一次普通GET同URL于2026-10-19T04:29:21.014570Z得到 `HTTP Error 403: Forbidden`，保存 `02-receipt.json`。未捕获该响应头/正文，因此错误响应体hash UNKNOWN，不为补回执再请求。查LOCAL_BLOCKERS中同类明确403规则后停止：不换身份、host、代理、浏览器、缓存或另一个API端点重取受拒页面/文件内容。

## 交付层状态

| 项目 | 状态 |
|---|---|
| 正式v2作者/题名/记录DOI/发布日期 | 已核上述原生正文 |
| 对应论文精确版本/实际实验run | 由paper Owner另核；Mendeley题名关联不认证具体原run |
| 文件数量、ZIP名及约500MB说法 | UNKNOWN；不把发现时搜索线索升级实际manifest |
| 实际公开download URL、文件bytes、checksum | 未取得 |
| 单独README/code/license可读性 | 未取得，页面只有指引；不能断言确实只能ZIP |
| signals/逐日预测、positions/trades、费用账 | 未取得实际文件名、schema/日期或manifest，不断言包里不存在 |
| 外部基础行情/新闻/模型payload | 零下载/解压/读取 |

页面有API Docs链接标签（turn1065view0/link7），但未打开或推定其接口格式/权限，也未猜隐藏URI。当前明确拒绝不能通过换接口自行补取同一内容。没有取得公开ZIP直链/size/hash可交给root；这正是本轮的具体缺口，不编造链接或作HEAD请求。

## 权利与结论

正式页面CC BY 4.0是对作者此replication记录开放许可的正面证据，不因为缺少“ML”单词否定一般许可。尚未读README/包内容，故CRSP、RavenPack、TAQ等第三方材料是否包含、如何取得、哪些数据必须自行授权均UNKNOWN，不能由页面CC BY替第三方权利作认证。也不能反向说一切使用都违法；应按实际文件与各权利层判断。

最低可证是作者名义正式replication的v2发布记录，不是独立核账、事前预测封存或可复制净盈利证据。会改变文件可核判断的最小原件是正常公开、实际可读的文件manifest（文件名/bytes/checksum/直链）或单独README；当前停止受拒资源，不以运行模型/重新回测替代作者原件，不为填预算扩其他case。

无登录注册/凭证/APIkey、安装付款、对外发送或交易；无来源执行/import、模型训练/回测/新金融计算、ZIP/市场新闻模型权重下载或解压。只写artifacts/，actualmodel/effort UNKNOWN，PERMISSIONS/ROUTING沿已核版本。终态PARTIAL，原件缺口保留。
