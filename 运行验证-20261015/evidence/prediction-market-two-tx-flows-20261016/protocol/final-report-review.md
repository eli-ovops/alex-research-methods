# 两笔真实交易资金流终审

**限定PASS，material_errors=[]；盈利案例仍未准入。** 0新网络，只做已有原文、被动JSON/hex、整数与Decimal核算及指纹检查，没有执行来源代码、模型、回测、SQL、SDK、EVM、策略或交易。actual model/effort UNKNOWN；规则PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4保持。

报告SHA256：`4591d8d34009b77902652ba1e790aee81e0388e297b2fa68889f3e8f6ee54904`。21份实际输入的绝对路径/SHA/bytes与UTC保存在同名JSON。

- 实读同块完整日志NDJSON：2205条，header及block hash与旧原文相同；目标两tx为11/23条，共34。旧7/15条日志按完整对象逐项一致，9个新增pUSD Transfer核得。读取前固定scope早于POST；1360418 bytes及SHA与回执相符，没有换时间/钱包/收益排序。
- 从ERC20三topic及CTF Single/Batch动态offset独立重建每币、每ID、每地址变化和zero mint/burn；非零净向量逐项与root结果完全相符，非零地址和等于各资产供应变化，不将铸造再记作免费收入。
- T1买方pUSD−8115200、token＋10000000，卖方pUSD＋8000000、token−10000000，F＋115200。两SELL同卖方、各5000000/4000000；买方汇总与OrdersMatched没有再算一次成交。卖库存回款不是已核利润。
- T2甲pUSD−2975100、B＋6330000，乙pUSD−3402200、A＋6330000，F＋47300；Exchange及ada在所核资产事件中净0。pUSD供应−6330000，A/B供应各＋6330000，c417的USDC.e−6330000、CTF抵押余额事件增＋6330000。按原量独立算得本金单价0.47及0.53，合计1；另加0.0473费用，没有完整组合折价。链址不同未被强推现实控制人不同，未自行贴YES/NO标签。
- F合计162500原单位/0.1625 pUSD，只称本样本毛费用收入。FeeCharged关联实际Transfer，不重复加收入/扣费；1010系统事件不在既有gas上再扣。gas币不与pUSD裸减，付款人和费用接收人不默认为一人。没有整账户、全经营净利、ROI或容量结论。
- 新固定CollateralToken源码L121–124为6位；adapter源码可解释pUSD unwrap后将USDC.e抵押split，但未匹配历史runtime。旧ada地址不同于当前官方表，c417正式角色保持UNKNOWN。原始整数事实与显示单位/源码声明分开。
- Mermaid顺序和金额与事件路径一致，是pUSD转换、抵押、分配持仓；没有画成pUSD直接兑现美元利润或将两子凭证加成双倍财富。具体历史路由身份的UNKNOWN在图后明确披露。
- 两份源码实际9844＋8138 bytes，加一次存储数据POST1360418＝root3HTTP1378400；加既有子3源码GET312516＝6/1690916 bytes。第三方搜索仅定位，未作为部署/盈利证据；本轮终审没有新增读取。
- 重要外链对应已存固定来源；本稿没有本地Markdown链接，文中phase目录/原件实际存在。下一首个merge选择scope明确executed=false/new_data_reads=false，未执行、未评分；没有改变原FAILED或将研究进展当财富完成。

无需实质修改，不追加范围。此PASS确认限定历史资产事件和报告表达，不证明完整持有期现金收益、私人策略事前公开或未来优势。
