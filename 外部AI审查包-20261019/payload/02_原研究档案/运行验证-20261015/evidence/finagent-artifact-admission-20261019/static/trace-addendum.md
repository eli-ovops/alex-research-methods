# 六源报告后的调用追踪补件：参数可达不等于消息已泄漏

本补件保留原evidence.md/receipts.json不变。root在同一固定实现内追加4份依赖，现共10/10小文本GET；全部HTTP200、完整size/Gitblob对既有tree一致，无运行。固定commit仍为17248a0b8b729ee3e093e30bb7bea7f52181f363，不倒授为论文原始实验。

## 新原件

07 finagent/prompt/custom.py（4162B）；08 finagent/prompt/helper.py（17511B）；09 finagent/prompt/trading/decision.py（5626B）；10 finagent/memory/interface.py（9693B）。GET开始UTC分别为2026-10-19T03:31:17.429792Z、03:31:17.430061Z、03:31:17.430164Z、03:31:40.576718Z。四源36992B，每份小于64KiB；原URL/完整SHA/树项见07–10编号receipt及trace-addendum.json。编号文件与初轮相同规则，均惰性文本。未读取.env、数据、权重、DB或结果内容。

## 可以进一步收敛的事实

**1. 不存在“整个params默认倾倒给LLM”的直接路径。** 07 L29–103先调generate_prompt_html，再只从生成HTML的system/user message节点收集p文本和img。08 L58–95只展开模板明确引用的iframe模块，然后将placeholder中的$$key$$替换；L20–41也只替换文本中出现的键，不自动列出全部字典。因此05无条件生成next数值、params残留next数值，不足以证明valid模型已经读到这些数值。03训练模板with_next/04验证无with_next的分流有实际意义。

此结论范围是已读renderer代码；ASSET实际模块内容、decision模板与图表生成仍未读，不升级为“valid实际消息已无未来”。若某模块显式引用next键、某图像含未来，仍可经此renderer发送。训练with_next模块能否在此固定版本展开并填入相应价格文字，也取决于未读模块内容；不能以论文内片段替代当前仓库该文件原件。

**2. 过去反思检索未直接将next数值拼进提示，但可以携带受未来影响的推理。** 08 L323–386先读当前low_level_reflection_reasoning/query，再发type/symbol/query_text检索（L345–351）；对返回项仅拼日期与short/medium/long reasoning（L360–369）。不会在这个函数直接拼raw next_price_movement字段。若训练反思的reasoning实际利用未来，它仍可作为历史推理文本传入后续决策，需判断是否在目标时点成熟。

08这个检索调用没有传当前date、未来到期日或available_at过滤；10 L104–129直接把add/query委托给BasicMemory，没有本层成熟检查。下层DiverseQuery、BasicMemory及FAISS未读，不宣称整个系统绝无任何过滤。已读writer是在低层反思后立即添加，未见按1/7/14行成熟等待；同次train→valid共享memory的条件风险仍保留，但未证实际被选中/发送/影响原论文结果。

**3. 最终决策仍是模板选择的消息，而非完整state或params自动发送。** 09 L23–65复制params并加入info的asset_price/cash/position/profit/return和preference；L102–113经同一to_message后调用provider。该实现asset_price源是06当日adj_close，且01在env.step前决策，故“同日收盘价进入可填参数、同日收盘价模拟成交”静态可达已证。具体decision iframe是否显式显示它、当日输入何时可见、延迟及实盘撮合未核；代码假设本身不等于一定能/不能实盘执行。

**4. 另一条具体时点风险是预制策略统计，而非只看next字段。** 08 L157对计算策略信号的价格切至<=当前date；这一步有历史截断。随后L161–203每次从trained/best_result.json或default/trading_record.json读取ARR/SR/MDD；L206–243又读买入持有best_result并形成trading_record1–4/buy_and_hold_record参数。这里没有按当前日期重新截断静态绩效统计，也未见available_at。结果文件覆盖期、产生时间及decision iframe实际引用未在本10源范围绑定，不能直接判“已把测试全年结果送给当天决策”。这是有明确文件/字段路径的条件式风险，不是已经实证的未来泄漏。

helper L175的best_params wrapper调用之后，L182又无best_params调用并覆盖signals；只能说明当前已读函数最后采用这个调用返回值，不能替代未读StrategyAgents实现或声称所有实验都用错参数。此点不触发修代码或重跑。

## 论文与当前实现边界

初轮02配置L104–135还给出gpt-4-1106-preview与gpt-4-vision-preview API ID。它们是此固定代码的静态配置，不是论文原run实际模型响应、API时刻、训练知识截止或调用账；同时存在CLI/配置覆写，不能凭当前配置认证精确历史部署。

综合裁决：训练with_next、两模式都生成未来变量、共享参数与记忆潜在传播、同日adj_close成交及双边0.001费用，都有当前固定代码依据；**valid直接消息泄漏未证，valid因果安全亦未证**。renderer和检索格式排除了“仅有next键就必然泄漏”的简化论断。还缺实际模块/消息/成熟记忆与原run绑定，现不再追加依赖、行情或运行。数值费率不能代替全部费用，源码模拟成交不能冒充真实fill，论文汇总收益不能冒独立实账或个人优势。

本补件只静态文本审计，0来源执行/import、模型/训练/回测/收益计算、安装、账号凭证/付费、交易或外发。实际model/effort UNKNOWN。静态总10次GET后停止，原六源报告与旧证据均未覆盖。
