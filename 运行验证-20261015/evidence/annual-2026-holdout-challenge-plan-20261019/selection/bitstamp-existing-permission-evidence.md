# Bitstamp既有许可证据定位：公共OHLC个人离线自动评估

**证据等级：找到一般单机个人复制/查看依据；在本轮3份已保存记录中，未找到已明确覆盖“官方公共OHLC自动取得、留存及个人离线自动评估”的特别许可或API专用许可全文。** 这是限定材料的定位结果，不证明该许可不存在，不是禁止结论，也不是法律意见。不能仅以没有“AI/Kronos”字样否定一般许可。

## 找到的条文与来源身份

1. **通用单机许可——不是本次自动评估的特别许可。** 2026-10-15保存的正常浏览器记录显示，旧入口`https://www.bitstamp.net/terms-of-use/`跳转到[Bitstamp Ltd Terms of Use](https://www.bitstamp.net/legal/terms-of-use/ltd/)，页面标last updated **2025-05-30**。记录的“Limited Right of Use”允许在单台电脑查看、打印或下载一份副本，用于个人、信息及/或非商业用途，保留版权/专有权利通知。相邻段同时涉及data/prices/trades/charts的复制、修改、采集、抓取、分发及网络使用限制；旧记录自身要求与一般例外/API机制合读，未据这些段落确认自动预测/评价全流程。定位：browser-source-update.json L6–15；许可补核报告L13–20。
2. **公共API存在及commercial/DLA安排——保留已存文本，不冒称完整官网原句。** [license-findings记录](</Volumes/EXTERNAL/亚力克斯 /公开预测资料-20261014/bitstamp-official-20261015__license-findings.json:11>) L7–13将来源定位为[官方API入口](https://www.bitstamp.net/api/)，L11保存的最短必要原样文字是：

   > companies seeking own commercial use directed to receive and sign a commercial use Data License Agreement

   **引文是该本地研究记录的原文，字段名为facts，不能冒称已验证的官网逐字条款。** 本轮3份文件没有保存/标注该API许可段的逐字全文，因此不能在不扩读的情况下补出官网完整原句。该记录明确含`own commercial use`，所述范围涉及companies的**自用商业使用**，不能缩成“仅再分发才需DLA”；而这3份记录并未保存API关于incorporation/redistribution的许可原句，不能替它补写授权。许可段发布日期UNKNOWN，changelog日期不能充作生效日。它也未解决个人内部离线自动评估的用途归类、专用授权、API例外及数据许可报价；公共接口可请求与用途覆盖是不同证据，不反推个人用途被禁止或一律获准。
3. **实体与日期限制。** 实际保存的是Ltd条款的浏览器研究记录，用户适用实体未定；法律目录列多实体，目录中没找到专门个人AI许可不证明其他文件没有。报告/回执读取日只有2026-10-15（Asia/Shanghai），没有精确UTC；2025-05-30是正文自述更新日，并非当年存档真实性证明，也不代表本轮已刷新当前条款。定位：browser-source-update.json L2、9、15、18–29。

## 已解决、避免重复核查的旧问题

较早license-findings.json L16–25记录普通HTTP只取到212B防护脚本。**随后同日的正常浏览器补核已读到条款、法律目录及费用页，明确取代“正文不可读”的旧结论。** 不应再把那份旧失败当成所有工具/当前路径都不能读，或重复为它排障。定位：许可补核报告L3–9、browser-source-update.json L3、41。

费用页记录“2026-10-15起有效”仅是交易/资金/服务费表日期，未定位个人自动评估的数据许可价；交易费不能替代数据授权，公共OHLC旧观察的取得支出0也不是任意用途许可。Kronos/MIT属于模型或代码许可，不套给Bitstamp数据。定位：许可补核报告L24–26；browser-source-update.json L32–38；license-findings.json L28–51。

## 本轮仍未建立的具体项

尚未在这3份记录中建立：适用实体下，官方API对自动收集/保留/离线分析或评价的专门许可、条款例外与通用网页限制的适用关系，以及对本次个人内部非分发账户评估的具体覆盖。旧文档研究目标多为本机预测模型评价；不能不加核对就把其UNKNOWN移植成非模型会计评估的禁止，也不能把一般下载依据扩成该全流程已确认许可。是否还有其他已保存特别条款，本轮未查，不能据未发现断言没有。

## 实际覆盖与未读路径

入口目录仅做文件名筛选，安全小文本3/3完整读取：
- `公开预测资料-20261014/Bitstamp-公开页面加载与授权补核-20261015.md`，L1–34，3750B。
- 同目录`bitstamp-browser-source-update-20261015.json`，L1–57，2825B。
- 同目录`bitstamp-official-20261015__license-findings.json`，L1–64，2271B。

以上是已保存报告/DOM观察摘要，本轮没有重开原官方网页、浏览器或原HTML，未把它们冒充新的官方全文核验。名称为`bitstamp-primary__*.json`、`bitstamp-official-*__gap*.json`、`*latest_exclude*.json`及其他疑似行情响应均未打开；`terms.receipt.json/legal.receipt.json`等其余文件也未扩读。本次没有扫目录内容、行情、CSV、私有Tardis、rollout或preflight，没有网络、代码/模型/回测/账户/交易执行，只新增本文件。实际model/effort UNKNOWN。

