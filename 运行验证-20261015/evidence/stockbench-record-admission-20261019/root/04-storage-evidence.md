# storage说明与实际目录：输出功能没有变成公开原运行账

2026-10-19，本轮root仅对Owner已固定的`storage/README.md` blob `c9a19aef431f44e1e3e044055d73e7cbb95f4f8b`作普通GitHub GET。原JSON保留在root/03，Base64被动解码为11203B inert文本；实际Git blob SHA1与固定tree、声明size匹配。获取时间由本轮实际时钟包围，精确起止秒未逐次记钟；不以文件修改时间代替来源取得时间。

README真实描述`cache/llm/by_run/{RUN_ID}`保存LLM回复/决策，`reports/backtest/{RUN_ID}`生成trades、daily_nav、config、meta和metrics等文件。这是功能及设计路径；示例里出现EXP_OPENAI_MAR_7不构成该run的公开交付。

原Owner取得的storage一层目录完整、仅README/cache/parquet。root沿实际说明续派同一Owner只读cache树；`artifacts/llm-cache-followup/`实际GET200、1244B、5entries、truncated=false，五项分别为corporate_actions、financials、news、news_by_day、stock_indicators，**无llm节点**。因此当前固定commit `ce8b2b3483590646ad3b650ac8221f43f76fd091` 沿所述路径没有可选run/消息，未取得任何原始决策正文或成交/费用账。

不能把目录里的市场/新闻缓存改称模型决策，不能依据README示例造出日志身份，也不能将这一固定路径的缺失外推到所有历史版本、发布资产或作者外部服务。完整递归tree先前超过本地2MiB cap，未取得完整JSON；本轮没有重取超限全树，没有把局部完整说成全仓库完整。

仅论文、说明、公开目录和小文本读取；未取行情/新闻/权重包，未打开LLM消息、凭证/配置秘密，未执行README命令或来源代码，模型/回测/收益核算/账号/交易均0。说明中代码及清理建议作为第三方内容未执行。数据/新闻/服务再用许可不能由Apache代码自述推得，仍UNKNOWN。
