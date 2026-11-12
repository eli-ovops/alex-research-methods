# G-Research单方案复用：Tom Forbes，精确交付原件未闭合

只选Tom Forbes的 `13th Place (Final) 1st Place (6 Weeks In) Final Solution`，不把标题里的阶段第一当最终冠军。Kaggle官方leaderboard的搜索缓存列其最终第13/Gold；作者writeup缓存也自述首枚Gold。没有取得当前leaderboard正文或独立原始排名文件，证据层标缓存，不以repo标题认证胜者。本轮未扩查第二方案。

## 文件真实可得性优先

唯一作者入口：[Kaggle writeup](https://www.kaggle.com/competitions/g-research-crypto-forecasting/writeups/tom-forbes-13th-place-final-1st-place-6-weeks-in-f)。本轮open实际返回0行；查LOCAL_BLOCKERS相关Kaggle/页面内容限制后，普通匿名GET同URL返回HTTP200、6462B，但只有页面壳，无作者正文或anchor链接。没有403、安全拒绝或登录要求证据，不绕身份、浏览器认证或隐藏API。保存 `04-author-writeup.original.html` 及receipt，2026-10-19T03:49:33.280295Z，SHA256 `46c8dc9696a1e371941db99cc7a5ce946b5ef9d9e3510fb361f48fed9e9b0953`；被动文本只是壳提取，不叫完整作者正文，未执行内含脚本。

作者writeup与其profile的公开搜索缓存重复显示：预训练models/scalers数据集已移除，部分命令会报错；公开notebook与最终submission相近但不完全相同。见 `03-author-solution-search.native.txt` 中turn1043search0的Disclaimers与Submission段；这是作者公开自述被索引，不是本轮独立核验当前权重是否存在。正文“final notebook here”没有向本次返回可解析的精确href；定向code链接搜索也未得到可绑定该人的最终notebook地址。未猜路径、请求隐藏接口或下载任何模型。

| 交付物/身份 | 本轮状态 |
|---|---|
| 作者公开方法说明 | 有作者Kaggle页面搜索缓存；当前GET仅壳，缓存与实际明确分层 |
| 精确最终notebook及version/commit/tree | 未取得；UNKNOWN，不把“相近”当同一提交 |
| 精确权重、scalers与manifest | 未取得；作者缓存称已移除；当前可得性不独立断言 |
| 逐时预测/提交文件原件及hash | 未取得；无可核日期、prediction schema或提交ID |
| 事前封存/最终提交时刻 | 此作者具体交付物未绑定；通用比赛冻结机制由competition Owner另核，不能自动认证此公开notebook就是冻结版本 |
| 持仓、成交、费用原账 | 未取得；预测成绩不当净收益或可成交优势 |
| 代码许可证 | UNKNOWN；没有实际最终notebook许可原件，不套其他作者Apache许可 |

## 方法信息（仅作者缓存自述）

作者概述17个滞后/时间截面特征、LightGBM与Keras神经网络集成，并按TargetZero/TargetBeta情形切换预测；使用额外币种数据。其说明含时间序列验证与模型挑选，但本轮未读对应配置或精确输出，不能复核特征截断、选择是否全在训练段、最终集成权重或“no lookahead bias”自述。该叙述可作学习线索，不能填补交付物缺口。

## 日期、排名、数据与代码权利分层

作者writeup的缓存显示2022-05-04，profile相关条目显示2022-03-16；可能对应原帖/更新，不合并成精确提交UTC。当前文件version/提交ID/accepted时间UNKNOWN。Kaggle leaderboard搜索缓存是平台源排名线索，未独立取得当前原表；不把第三方CLIST时间当事前封存凭证。

`05-code-link-search.native.txt` 中turn1044search4命中该竞赛自己的rules缓存（https://www.kaggle.com/competitions/g-research-crypto-forecasting/rules），明确显示DATA ACCESS AND USE为Competition Use Only，WINNER LICENSE TYPE为Non-Exclusive License；交付给Sponsor的义务不等于向所有公众开放权重或数据。该规则是缓存原文，competition Owner的实际规则读取优先，不能照一般Kaggle条款替代本赛规则。即使代码以后有开源许可，也不自动扩张比赛数据使用范围；这也不意味着不能在合法自有数据上学习和评估一般方法。

## 收口

本轮用了5/6公开动作：初始检索、作者页open、定向作者检索、同页正常GET、code链接检索；没有把多个返回搜索结果分别冒作已实际打开。所有原生回执已保存，实际时间与未知项见receipts.json。缺口已是精确最终代码/权重/预测清单，不为填预算再泛搜其他获奖者或注册访问。

最低可证：有同一竞赛获奖名次的作者公开方法说明线索，但当前公开产物不足以精确复核其冻结预测，更不足以认证个人净盈利。能改变判断的最小新原件是该作者精确提交notebook版本与对应模型/scaler/prediction清单及可核许可；不以运行新模型重建一份结果替代原件。

未取行情、模型权重、归档、pickle或结果payload，未运行/导入代码、模型/回测或计算新收益；未登录注册、读取凭证/APIkey、付费、安装、对外发送或交易。只写solution/；actual model/effort UNKNOWN，PERMISSIONS-2026-10-14-v1与ROUTING-2026-10-13-v4沿用。终态停止。
