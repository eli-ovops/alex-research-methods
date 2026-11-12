# 两份新增派生的独立对照

**限定PASS，material_errors=[]；无需改根的两份派生。** 原审阅保留；本次新增文件记录实际输入指纹，不改root或旧原件。model/effort实际UNKNOWN，0新网络、来源代码/模型/回测/SDK/SQL/EVM/策略/交易执行。

从实际交易calldata按ABI字节布局独立解析：selector0x73e7b48d，第一参数offset64，sourceAmount=14446372699016692000000，3个六字段静态tuple；各exchangeId、targetToken、minTargetAmount、deadline/custom字段均与actual-historical-call-event-decode.json相符。未调用ABI或合约。

独立解析实际ArbitrageExecuted日志：两个动态数组offset160/288，exchangeIds=[2,5,2]，tokenPath=BNT→原生币占位地址→DAI→BNT。sourceAmount、burnAmount=72375688251368841756、rewardAmount=8041743139040982417与原Transfer及原派生相符；indexed caller与From相符。没有把这些重复加为第二笔收入，也没有给实际原生币占位地址另造token事实。

历史身份派生正确保留两事件严格早于目标、目标tx无Upgraded、最后升级receipt及Sourcify平台match来源。未把latest地址、constructor或2025验证记录当2023首公开/全静默写排除证明。相关原件/派生实际SHA和bytes逐项相符。

财务边界准确：路由minTargetAmount/deadline不等caller扣gas盈利检查；分配按全部剩余BNT余额，不必然只含本次新增收益；默认10%/100BNT不是历史状态查询实值。成功执行、接口匹配与实现定位不自动证明完整策略的事前公开或净盈利。已核真实付款和gas金额未变。

本地检查输出字段count曾在写入时被循环变量覆盖，已仅在本子Agent新增JSON纠正为实际3，与解码原量和根原件无关；没有执行或改动来源。原审阅无需追改，等待根报告的限定终审。
