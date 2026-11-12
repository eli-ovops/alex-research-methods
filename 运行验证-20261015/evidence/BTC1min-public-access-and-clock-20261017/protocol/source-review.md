# Database时钟补证

**PASS_LIMITED：固定源码中原始 `system_time` 是本地记录函数时钟；仍不等于2021 CSV逐行实际可用时点已证。** 唯一GET成功、Git blob匹配，已停网。

`Database.new_tick:55–66`：recording=False直接返回；True时把`index`设为`dt.now(tz=TIMEZONE)`，再把它转为字符串写入`system_time`，积累到BATCH_SIZE才写库。因此记录函数时间、批量落库时间与消息自带`time`不同，不能称精确网络到达时刻。TIMEZONE的实际值未在此文件定义，不能自动填UTC。

`_query_arctic:87–98`：按DateRange读取后，取有load_book的最早日期，再取该日最后一个匹配的索引项并截去此前记录；不是简单“第一个load_book”。返回前没有显式排序/去重，顺序仍依赖底层返回。异常转None也不是市场零活动。`get_tick_history:125`只断言这个查询对象关闭recording，不替所有嵌套对象证明配置。

结合已存Simulator，首次网格锚点来自`last_tick_time`，它在Coinbase路径取消息`time`；后续跨格差值却用原始`system_time`。Simulator再把旧状态重复填入跨越格点后应用当前tick。因此**原始记录时间与导出的网格时间同名但不可直接等同**。warmup记录先重建、未完成前跳过普通特征；仍不证明实际CSV完整无缺口或已披露每条可用时间。

唯一决策影响：新源的一页文档协议可明确记录这层时钟条件，而非继续找私人系统。保留时间、顺序和分箱审计；若实际截止语义仍未绑定，未来结果只称历史下一行基准，不冒可实时执行的60秒优势。固定commit记录日期2021-11-30晚于9月3日作者Notebook，本结论仍是条件解释，不自动绑定旧CSV，也不否定CC0或公开字段。

JSON绑定8个实际输入及HTTP回执；新增GET1，源码/数据库/模型/评分/回测/模拟/交易均未运行，行情/权重下载0。实际model/effort UNKNOWN，停止后续读取，交根节点正常公开入口核验。
