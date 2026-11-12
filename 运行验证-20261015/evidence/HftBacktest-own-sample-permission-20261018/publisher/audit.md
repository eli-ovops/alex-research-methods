# collector 自带样本：README与许可核验

**UNKNOWN：两份样本真实元数据已定位，但未取得适用的数据复用许可或精确生成参数；不把未知判成违法。**已保存最小作者问题草稿，未发送。

首次GET实际读取固定README blob `6e337c5c7c8df3dd5ce3c47ff7b161751eea7284`，1380B，Git blob独立匹配。原文说明项目迁至hftbacktest/collector，采集命令可选Binance spot/USD-M/coin-M；convert可选-f包含mark/funding/bookTicker、-c修正交换时间单调性、-s使用初态snapshot，例子以前日EODsnapshot作为次日初始。README不是样本生成日志，未说明实际两文件使用哪个commit/flags/初态或clock correction，也未给使用许可。教程文件名与样本basename吻合仅是有限关联。

复用上一阶段已保存完整tree `27abefde5d6a42db125c59bd47332db58677ba4b`（truncated=false）：
- `sample_data/btcusdt_20220811.dat`：757648B，blob `38a1e26f10dde12618a2258bf04560476f867ab7`；
- `sample_data/btcusdt_20220811.pkl`：101418B，blob `14030d53c138fa77e07fbdd5e38e9072f4343043`。

这是文件名/体积/身份，不是实际行情覆盖、初态完整性、时钟质量或已下载回执。没有读取任一payload，尤其未反序列化pickle。

第2次GET为同collector repo当前metadata，正常200，license=null；固定树未列LICENSE/COPYING，所读README也未授权。GitHub检测值和有限文件范围不能证明所有授权都不存在，但不能用另一个hftbacktest repo的MIT自动覆盖本collector样本，也不能把public可下载当个人模型/外部AI披露许可。当前metadata只是读取时元数据，不替代固定tree历史身份。

`draft.txt`仅问：两确切文件的个人离线专用统计预测（含盈利目的研究）及外部AI汇总评估复核是否有适用许可；以及生成collector/converter版本、-f/-c/-s与clock说明。没有索取私有策略、账号或强加全面书面ML审批。未开issue、评论、邮件或联系作者；本轮没有外发授权，也未外发。

两次公开小GET后停止，未用满后续读取额度。HTTP含头原件、Base64惰性解码README与UTC回执已保存；GH客户端只是读公开文件，未运行来源程序。0行情payload、模型/转换执行、回测、账号/安装/付费/交易。actual model/effort UNKNOWN。完成即停。

