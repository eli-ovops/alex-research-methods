# DBMF年度审计原件准入：本轮未取得完整财报

2026-10-19 UTC。**本轮不能认证DBMF完整年度损益或正净利润：当前官方基金页被拒；最新定位的2025监管年报因工具大小界限未读成全文，随后唯一严格TLS普通GET也收到403。4/4公开动作后停止，无别名、身份、代理或后续重试。** 不换基金/年份、不拿半年报、摘要或NAV代替财报；这不是基金无利润、财报不存在或永久不可读的证据。

## 选择先后与身份限制

只选DBMF（iMGP DBi Managed Futures Strategy ETF）。官方检索定位候选监管N-CSR：CIK1020425、申报路径000119312526100256、期间2025-01-01至2025-12-31，随后在打开完整监管财报前保存`selection-before-financials.json`。按最新定位的已结束年度固定，而非按金额换年。

**搜索返回意外含正NAV表现/部分资产表摘录，已在选择回执披露，不能称全程盈利盲选。** 未读取Statements ofOperations/Changes原列金额；未取得封面、审计意见/签署日的完整原件核验。故2025只是最新定位候选，不称已确认“最新可公开取得的完整审计报告”，实体/期间最终绑定和auditor仍UNKNOWN。搜索摘要不完成这一步。

## 四个动作与停止回执

|动作|原URL/请求|结果与证据层|
|---|---|---|
|1|公开检索DBMF official annual audited statements|只用官方issuer/SEC结果定位；第三方/Reddit命中未作为证据或访问。原工具返回`01-official-search.tool-return.json`，不是完整报告。|
|2|https://www.imgp.com/us/fund/US53700T8273-imgp-dbi-managed-futures-strategy-etf/|web工具明确返回403 Forbidden。`02-fundpage.tool-return.json`；无HTTP原始正文，停止此对象。|
|3|https://www.sec.gov/Archives/edgar/data/1020425/000119312526100256/d102920dncsr.htm|web工具返回400、Content length too large4194305+；是工具正文大小限制，不把它当来源403。`03-sec-annual.tool-return.json`；没有获得完整财报。|
|4|同一已定位SEC原URL，一次普通GET|在既有LOCAL_BLOCKERS公开大文档支持路径下，严格TLS、无重定向/重试，10MiB读取上限；实际HTTP403，4818字节拒绝体，SHA256 `62d2a999798ae23565390b1d7c8226ffa73435d0e454d5f76cdeefe91d75991a`。`04-sec-original.acquisition.json`及`04-sec-original.failure-body.txt`。收到真实拒绝后停止，未再换渠道。|

动作4 UTC2026-10-19T21:24:22.050285至21:24:22.437321。动作1–3工具状态/正文提取不冒充HTTP raw；动作4所存原字节是**拒绝体而非财报HTML**。没有PDF可供渲染、页图或相关表视觉验收；没有执行PDF创作标记或安装工具。

## 财务覆盖：全部未验，不填零

|必需原件/字段|本轮状态|
|---|---|
|完整年度封面、DBMF series/期间、独立审计意见和日期|UNKNOWN；只有搜索身份/候选日期|
|Statements ofOperations的净投资收入、期货/投资已实现及未实现收益|NOT_OBTAINED|
|expenses、waiver/reimbursement、交易成本及附注口径|NOT_OBTAINED|
|Statements ofChanges、share capital、distributions，资本流与经营结果分离|NOT_OBTAINED|
|完整Notes、衍生工具计量/合并边界及成本包含范围|NOT_OBTAINED|
|PDF页面/表头/列/相关附注视觉核验|NOT_AVAILABLE；无PDF原件|

未抄NAV收益、净资产规模或申购赎回金额来制造盈利；没有新组合回报/费用运算。缺完整报表不能判正或负，也不能由机制解释填补会计原件。

## 收口

来源验收为`FAIL_ORIGINAL_RECORD_COMPLETENESS_THIS_UNIT`；本轮没有新增可认证的完整年度经济盈利证据，不能把仅定位年报或403回执报作财富目标进展。保留具体已定位监管原件及拒绝，不自动再取或换来源/年份。本任务公开动作耗尽，后续由Root决定；本Owner不追加权限提问、模型或新候选。

只写本source-owner；零账号/凭证/API-RPC/模型/回测/新金融运算/交易/外发/私有行情QC读取。实际model/effort/CPU/RSS无平台回执，UNKNOWN。来源/哈希/预算与未读项见manifest.json、coverage.json、receipt.json。
