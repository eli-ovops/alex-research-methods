# QuantConnect live原账功能层核验

**官方文档支持订单事件、持仓现金与部署代码的查看功能，但未核任何具体盈利记录。** live标签本身不能认证真实资金；公开分享权限由root另核。本轮1查询+2open=3/3，0账户API/登录/数据包/代码或金融执行，实际model/effort UNKNOWN。

## 实际正文与字段边界

[Results](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/results)，native turn1102view0，声明570行，实际保存L0–569：

- L331–343：统计有equity、fees及未实现损益；停止再部署会重置统计。因此一条曲线不自动是跨部署完整账，也非已清仓现金净利润。
- L468–480：持仓显示symbol、平均价、数量、市场价值、未实现损益，cash按CashBook币种数量显示；这是平台状态，不是独立券商对账单或历史逐期资金流水。
- L483–512：订单可展开提交、成交、部分成交、更改单、撤单及期权事件；trade为可配置订单合并后的已平仓记录。GUI为ET，CSV为UTC；order CSV是折叠摘要且只含最近750天，不能冒完整fill事件账或无开放损失。文档另列旧记录查询路径，本轮未调用。
- L524–543：日志及部署所用项目文件可查看，日志跨重新部署保留。未见本轮可认证的commit/hash、不可篡改时间封存或一切依赖配置的完整manifest，代码可见不等于精确可复现部署。

## 真实券商与Paper层

[QuantConnect Paper Trading](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/brokerages/quantconnect-paper-trading)的本轮open turn1102view1虽声明506行，实际只返回L0–31导航，不能称业务正文已读。第1查询官方缓存明确：实时数据live运行也可使用虚拟资金，成交由模型模拟；默认费用按模型，默认不含滑点，并可更换brokerage model。这里只作为官方索引缓存层证据，不当具体run配置或实际扣费。

Results正文“Fees”是平台口径，不能单凭字段名证明真实券商已扣、全费用含融资/借券/换汇/平台费、或与现金流水完整勾稽。查询还见官方文档源码缓存称真实live填价/费用由券商设置，但未打开该源码；具体券商、账户是否纸面、fee来源及修订/对账均UNKNOWN。截图中的actual fill表述也不能把模拟fill变成交易所成交。

## 收口

功能文档准入通过；具体原账/净利准入未通过，原因是本轮没有检查任何策略实例，而非证明平台不提供。后续若有具体公开run，需绑定真实/模拟brokerage身份、各部署代码版本、全部订单fill与费用、持仓现金及跨部署/外部资金变动，再判断覆盖；本报告不启动查run或执行。公开可见哪些tab/代码/下载另依分享配置，不能从拥有者界面说明直接推所有路人可见。

读取窗口2026-10-19T05:24:27–05:24:34Z；各调用精确秒UNKNOWN。保存的是原生工具回执文本，其SHA不是源HTTP body hash；源HTTP状态/headers、页面发布日期/固定revision均UNKNOWN。完整原回执与覆盖见receipts.json。
