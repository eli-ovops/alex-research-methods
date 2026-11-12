# BitMEX旧费用入口：有普通用户返佣线索，未完成当前准入审查

2026-10-23。本轮只查本地旧报告/小文本与元数据，不联网、不取instrument或行情、不执行金融代码/模型/策略/交易。唯一写入本cost-entry-catalog目录。actual model / effort UNKNOWN。

**结论：旧档案确有“selected derivatives / OG fee schedule”以及面向所有BitMEX用户的历史USDT maker返佣入口，不能说所有普通个人都必然没有返佣。** 但这些只保存为2026-10-18的官方域搜索抽取；旧研究没有独立打开这些公告，也没有核齐当前有效合约、全部普通账户条件或中国内地常住用户准入。历史入口不构成今天应继续接入的理由。

## 1．已找到但未完整审过的两个准确入口

共同本地来源：
`运行验证-20261015/evidence/BitMEX-native-fee-basis-20261019/official-fee/03-native-search.original.json`。
对象为`{read_utc,result}`；`result`中按以下准确标题定位。读取UTC由同目录`report.json`第45–48行记为2026-10-18 16:17:22UTC。该unit目录名日期20261019不是网络读取日。旧`report.md`第3–7行明确三次皆检索，page open和普通GET均0。

| 旧官方入口 | 保存的有限主张 | 未核部分 |
|---|---|---|
| [Selected derivatives / OG](https://www.bitmex.com/en-gb/blog/special-maker-rebates) | 搜索抽取标2025-12-18；列XPLUSDT、MONUSDT、XMRUSDT、LOTUSDT、BMEXUSDT的maker −2.5bp/taker7.5bp；称费率持续至另行通知 | 没有独立打开正文或检查后续终止/修改；所见段落未写成交量门槛，不等于完整条款没有门槛；不是BTC/ETH或所有合约通用表 |
| [USDT legacy maker rebate](https://www.bitmex.com/blog/maker-rebate-offer-usdt) | 搜索抽取标2023-09-05；自述9月7日起向所有BitMEX用户恢复0.02% legacy maker rebate，并列XBTUSDT等USDT合约 | 这是历史官方主张的搜索层证据，不是用户账户资格、全部KYC/地区/费率条件认证；不能移植成2024 XBTUSD inverse收费基数或2026现行费率 |

“所有用户”的旧公告文字是重要反例线索，应保留。它不等于任何居住地的人都可合法开户或获批；也不推定该活动仍有效。旧研究的反向合约问题与这些USDT/指定合约不同，因此没有采用它们认证XBTUSD inverse的手续费币种、Q/P基数或2024适用性。这不是“已研究并否定所有个人返佣”。

旧搜索还列testnet的2026-05 selected-contract fees更新及生产站equity perps更新；它们是不同产品/环境，不可混成上述特定合约当前费用结论。本轮未展开这些旁支。

## 2．现成当前费表与地区准入状态

- **完整当前通用费表：未在本次限定旧档案定位到已独立全文审过的原件。**
- **指定OG返佣的普通账户完整条件：未核齐。**
- **用户具体账户费率/地区/KYC/权限：UNKNOWN，本轮未接账户。**
- **中国内地常住用户的适用地域条款：本次未定位已核结论。**
- **旧拒绝保留：**`BitMEX-native-fee-basis-20261019/official-fee/report.json`第71行记录support费用页旧404只再次出现在搜索缓存，未重新打开；不能把缓存当正文。该URL是[历史费用帮助页](https://support.bitmex.com/hc/en-gb/articles/5903013223837-What-are-the-Trading-Fees-and-where-can-I-see-what-I-ve-paid)，本轮不访问。
- **条款拒绝：**`BitMEX-official-quote-data-admission-20261018/rights-format/report.md`第10、12、35行及`public-read-log.json`保留production June2025 Terms普通GET403。原研究主核历史数据使用/AnnexD，未核完整地域准入；不能改渠道重取受拒资源。

公开旧静态条款或API可读均不自动证明普通个人可交易或返佣可用。相反，未取得条件也不能推导“普通个人一定无返佣”。本轮没有做地区法律解释或新金融推荐。

## 3．旧关闭线索与Root的新原件分开

旧`BitMEX-official-quote-data-admission-20261018/rights-format/docs-and-terms.native.txt`来源L2（文件第4行）已见重定向后首页自述交易所关闭。旧`rights-format/report.md`第9行严谨限定为“所见声明，不独立认证关闭事实”。所以**旧档不是完全没有关闭线索，但未完成独立终止公告核查**。

Root在本次通讯报告已正常读取三篇生产站公告：
- `https://www.bitmex.com/blog/reduce-only-september/`
- `https://www.bitmex.com/blog/delisting-spot-convert-sept2026/`
- `https://www.bitmex.com/blog/bitmex-closure-live/`：Root报告这是正常点击footer Closure notice取得的完整短正文，标题Exchange Now Closed，发布日期2026-09-23，明确所有交易所运营已停止，trading/deposits/new positions不可用。此为Root本轮的新正文事实，不是旧搜索缓存或本Owner独立读取。

本Owner没有重新请求或独立读到Root的新原件，未将通讯中的时间/结论倒写成旧资料事实。按Root明确steering，**本轮不再推进费表、instrument、旧404或受拒Terms读取**；三篇正文及HTTP原件由Root在本轮归档和验收。历史返佣线索与Root现已取得的业务终止正文须分时点保留：旧公告不能被当成当前可交易入口，当前终止也不抹去旧费率主张。

## 4．有限查重覆盖

先查既有catalog、BitMEX费用/产品/条款紧凑报告；随后对旧evidence小文本做精确OG/selected/special-maker/BitMEX fee网址与地域词查重。最终精确范围9,946份≤256KiB的md/json/txt；排除新goal-next-edge、QC/Bitstamp/private/账户凭证/raw/权重/依赖/执行目录及敏感/QC文件名。精确命中主要落在10/18–19的既有BitMEX来源与报告，未定位OG公告被独立全文审过或地域通过的后续报告。

此前一次较宽的BitMEX名称导航检索还命中了执行/QC元数据文件名；没有打开或分析其中行情/数值。本报告只依据明确列出的费用、产品与条款文本；不把路径命中当金融QC读取。

结论仅限旧本地文本与实际阅读路径，不宣称全历史、原始大包或全球不存在其他记录。本轮未重核Lighter、未给新供应商清单，也没有新的模型/交易或实验许可。整体财富目标未达。

