# FinAgent固定实现六文件静态审计

结论：**训练with_next与验证无with_next的模板分流已证；验证仍计算并保留真实未来价变，但“验证LLM已经消费这些值”尚未闭合。** 当前代码不是论文原始run绑定，不能由这次审计倒推论文确定泄漏。环境是按当日adj_close模拟成交、双边0.001费率的简化账，不是可执行成交或个人全成本净盈利证据。

## 原件身份与范围

固定公开实现DVampire/FinAgent，root指定commit `17248a0b8b729ee3e093e30bb7bea7f52181f363`。已存 `../root/05-tree-retry.response.json` 的truncated=false、526entries、342blobs。六路径均在该树，各自本轮普通匿名GET一次，2026-10-19 03:29:08 UTC开始，HTTP200；全部完整长度与树size一致，计算Git blob与树SHA一致。每源≤64KiB；六源合计50227B。原URL、精确UTC、SHA256与Gitblob见各编号receipt及receipts.json。没有执行/import任一源码，也未读取被引用数据、权重、结果包或凭证。

本报告引用编号对应惰性文件名：01=tools/main.py；02=configs/exp/trading/AAPL.py；03=train低层反思模板；04=valid低层反思模板；05=finagent/prompt/trading/low_level_reflection.py；06=finagent/environment/trading.py。行号均为这些原文本的物理行。

## 1. 训练/验证模板与调用层

- 02 L14–26设置train 2022-06-01至2023-06-01、valid 2023-06-01至2024-01-01，past/next范围均为1/7/14。L32与L38指向本轮已取两个不同模板。
- 03 L28、L32引用带with_next的price_change_description和prompt iframe；04相同行引用无with_next版本。两者其他结构大体相同，不能把论文展示的训练式模板自动套成所有验证路径。
- 01 L121–147分别以run(mode=train/valid)调用；L229、L294–305依据run的mode选择模板，再运行同一个LowLevelReflection类。02 valid_environment L73虽写mode=train，但06只保存self.mode，已读环境逻辑没有据此选择LLM模板，不能据这个标签声称验证一定用了训练模板。
- 01 L51–52缺省if_train=False、if_valid=True；L65–82允许CLI覆写。因此“先训练再验证”是可选分支，不能冒称本轮或论文已经这样跑。

## 2. Future实际来源、成熟与消费：分三层

**已证生成来源**：06 L117–154在每个当前day取前look_back至未来look_forward的price/news/guidance/sentiment/economic窗口，未按train/valid分别截断，也未按env.end_date裁掉未来窗口。02两环境均传14行look_forward（L56–84）。05 L53–61从state.price取timestamp/adj_close，去空并按timestamp保留首条；L70–89直接计算从当前行向后1/7/14行的百分比变化并形成next文字，不是模型自行预测的字段。L94–109、L175–186在两模式均先算params再to_message。这里的days名称实际按价格行periods计算，不可擅自当日历天。

**已证保留/调用顺序**：05 L211将包括next字段的task_params更新到共享params；L138–154将整份params连同reasoning/query存入low_level_reflection memory。01 L294–321在最终decision前执行低层反思、检索、入库；L376–388随后把state/info/params/memory交decision。上述六文件没有按未来结果成熟时间延迟入库的判断。01 L218–222及05 L218–220有写出按日期命名的记忆/交易/响应文件的代码；这是将生成的路径，未证明实际文件存在或当时封存。

**仍未证消费**：当前train模板明确要求with_next片段，且params具相应字段；但iframe片段文件及Prompt.to_message基类未读，不能把实际消息渲染内容当已核。valid模板没有with_next，故仅“字典中存在next字段”不足以证明该字段被发给valid模型。decision类/模板、prepare_*检索过滤和plots实现也未读；无法认证它们是否过滤未来、是否展示未来K线，亦不据此反向宣称验证因果通过。

训练中的成熟历史未来标签可以是合理的离线反思资料，不能仅因训练可见未来就判预测作弊。这里更具体的条件风险是训练/验证边界：若启用同次train后valid，01 L109–147复用同一memory对象且无中间清空；06的未来窗口不受训练end_date限制，训练末端反思可能使用到验证区间的价变后再带入验证。是否实际发生取决于数据覆盖、运行开关、渲染/记忆检索及原始run，均未核；没有读取行情或结果来实证污染。精确实验运行日志/消息与记忆快照会改变此判断，模板本身不能替代。

## 3. 当日输入、成交价与时点

06 L111–112将current price设为当日adj_close；reset L156–187返回同日state/info。01 L179–206先run_step生成action，再env.step。06 L235–250在day加一前用self.price买卖；不是下一日open成交。state对当日数据及未来窗口的暴露已证，但各模块实际过滤/输入截止未全读，无法认证当日收盘价是否已被模型观察后仍按同一收盘成交。即便无next消费，若用当日完整OHLC/新闻决策却同收盘无时延成交，也需要独立时点/撮合假设；当前六文件没有arrival/available_at或可成交报价原件。

06 L246–271先按当前成交价得post_value，再day++更新date/price；value在这次step返回前未按新price重新估值。因此返回info的日期/price与value存在阶段差异，不能仅看日志日期认定该value已按同日收盘标记。这里只读描述执行顺序，没有算收益、评判数值偏差或修代码。

## 4. 费用数值及覆盖

02 L9–10配置transaction_cost_pct=1e-3；L67、L82传两环境，06 L20为同一缺省。06 L189–213的买入可买数量考虑(1+费率)，现金扣quantity×price×(1+费率)；L215–229卖出现金加quantity×price×(1−费率)。所以此固定配置为成交名义额每边0.001（10bps）模拟交易费；不再把该实现数值说成完全UNKNOWN。

这不能移植成论文原run已采用同一数值。已读交易路径没有独立bid/ask、滑点、订单队列/部分成交、市场冲击、融资利息、数据订阅或LLM调用费用账；也没有交易所/经纪商fill与手续费回执。使用adj_close作为成交单位并非实际原始可成交价的认证。未读数据处理/供应商授权和所有外部费用依赖，不宣称整个仓库绝无其他成本实现。

## 裁决与停止

可以排除“只因论文with_next模板就认定全部valid调用直接读未来”的过强裁判；不能排除未来state/params/记忆经过未读模块进入决策。数值模拟双边费率与同日adj_close成交已从固定实现确认；真实资金、事前封存信号、完整成本与论文实验部署仍UNKNOWN。这些区别不降低完整净利验收标准，也不要求作者身份作为检查公开实现的额外前提。

本轮6/6公开GET已用完，0模型/训练/回测/新收益计算/行情或权重下载/源码执行/账号凭证/安装付款/对外发送/交易。实际model/effort UNKNOWN；规则版本沿已核PERMISSIONS/ROUTING/HANDOFF。只写static目录，未改旧原件、代码或其他Owner成果。停止，不扩大依赖或修bug。
