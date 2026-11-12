# KMLM运行后原账可得性：PARTIAL，完整净利链未闭合

本轮4/4公开读取已用完并停止。已核基金官方身份和当前快照/基金NAV披露；未取得连续完整历史持仓、逐笔成交及逐笔成本，不能作个人可复用净盈利或预测alpha验收。未取得不等于从未公开。

## 实际已读与缓存分层

- 两次公开检索，查询分别为 `site.kraneshares.com KMLM holdings annual report audited financial statements`、`site:kfafunds.com KMLM holdings annual report`。仅采用返回的官方基金/SEC线索，合并原件为 `01-02-official-searches.native.txt`。查询首项原样保留，未误称带冒号的域过滤器。检索结果不是本轮实际年报/SEC正文读取。
- [官网](https://kraneshares.com/kmlm/)实际正常重定向至 [产品页](https://kraneshares.com/etf/kmlm/)，原件 `03-04-official-page-and-pdf.native.txt` 中turn1021view0，原生L0–405全返回。读取时间窗口2026-10-19 03:10:05–03:10:16 UTC；逐请求精确UTC/源HTTP状态未由工具给出，记UNKNOWN。页面数据日期为2026-10-16/绩效2026-09-30，非文档发布日期；页面固定版本UNKNOWN。
- 检索实际给出的 [2024年度报告PDF](https://kraneshares.com/resources/compliance/2024_03_31_kraneshares_annual.report.pdf) 本轮open返回404，原件同文件turn1021view1；查LOCAL_BLOCKERS相关PDF404后不重试/换路径。缓存摘录可见年度披露线索，但不能当已取得PDF或审计意见。
- 当前主页L381实际可见Annual Financials And Other Information链接（turn1021view0/link54，显示域www.kraneshares.com），仅链接未读。保存的原生输出没有展开其精确href，记UNKNOWN；未取HTML、未为解析再联网，故与上述404旧PDF是否相同也UNKNOWN，不猜文件路径。

## 身份与记录链结论

官网L85–128确认现名KraneShares Mount Lucas Managed Futures Index Strategy ETF、ticker KMLM、ISIN US5007676522，成立2020-12-01，Mount Lucas为sub-adviser，基准KFA MLM Index。旧称KFA与2024-08-01改名仅见SEC检索命中摘要，未另读SEC正文。不能将指数早期历史当本ETF实际运行历史。

| 待核环节 | 本轮可证 | 未闭合项 |
|---|---|---|
| 完整历史持仓 | 官网L293–378为单个当前日期的期货敞口、抵押品/货币、持仓；L347有Full Holdings CSV，L381–383链接年度/半年度及2024-06/12投资明细 | 未跟CSV/季度文件；快照及定期报告链接不证明逐日全历史、盘中变动或缺失可补 |
| 逐笔成交 | 当前持仓行有合约、方向、数量/名义敞口等快照字段 | 已读页面未提供逐笔成交时间、数量、成交价、order/fill标识账；不得用持仓差分冒充fill |
| 逐笔及基金层成本 | 官网L125、L390–392披露总年度运营费用率；L113说明投资者买卖ETF可能有经纪佣金；L329–344另示抵押品/现金 | 费用率不是逐笔佣金/价差/融资/期货滚动清单；现金收益与期货盈亏、展期贡献的完整核账未取得 |
| 净值、审计与基准 | 官网L182–197有Fund NAV/Closing Price/Underlying Index分列；L291–292说明growth图扣管理费及其他基金费用、再投资且基于NAV | 图中假设$10k投资不是“基金全为模拟”的证据；审计报告原件本轮未取得，最新净值未独立复核；KFA MLM Index比较不等于匹配风险后的alpha归因 |

官网当前快照已经包含期货与现金/国债抵押品，因此不能只看期货方向就把全部基金回报归因于预测能力。基准为同一相关策略指数，指数不可直接视为个人可交易、同费率或同风险预算的反事实。没有计算收益、风险暴露或alpha。

## 原件缺口与停止

现有官方信息足以把它识别为真实运行ETF的披露候选，而非仅看一条回测曲线；**仍不足以闭合完整可复制原账净利链**。需要能绑定同期规则/信号、连续持仓、逐笔成交/费用和审计基金账的原件，才会改变这项判断。当前仅观察到报告链接，未取得这些完整文件；不宣称其不存在或不公开。

依派单条件在缺口处收口，不继续供应商、目录或第四以外网页，不自动运行实验。规则PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4沿用；实际model/effort UNKNOWN。未注册、登录、使用凭证/API key、付费、安装、下载行情大包、执行来源代码、模型/回测、财务计算、交易或对外发送。
