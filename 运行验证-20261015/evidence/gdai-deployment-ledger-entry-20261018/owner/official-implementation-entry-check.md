# 官网账户v6.1仓库：GToken入口窄核

结论：在所指定的完整Git树未定位GToken／gDAI专门实现路径，按任务条件立即停止；没有使用第三次读取扩展其他版本。

根已读取官网指向独立的`GainsNetwork`账户，本轮只读其`https://github.com/GainsNetwork/gTrade-v6.1`。不能因此把`GainsNetwork-org`等同该官网账户或宣布关联已核。

2026-10-18 08:13:57—08:14:07 UTC两次公开gh GET均成功，先metadata确认默认分支main，再取recursive tree：`7803cc0a1d62c5b115c38b8e432a7436b51926d3`，`truncated=false`。原件和精确回执保存在本owner目录，指纹见同名JSON。

该树列交易、回调、PairInfos合约及`VaultInterfaceV5.sol`等路径，没有GToken／gDAI命名实现。接口不能替代金库实现；本轮未读具体blob，也不宣称未读源中绝无嵌入实现，更不证明所有其他仓库不存在。

仓库API的license字段为null，tree未定位LICENSE／COPYING。仅能说本轮未取得GToken实现许可，不能推广为全部源文件没有SPDX或所有使用均被禁止；其他SDK／合约的MIT不能移植到未取得的GToken。

仓库created_at为2022-07-12T13:15:06Z、pushed_at为2023-01-13T18:03:20Z；这些是仓库级时间，不是GToken首次公开日期或部署版本证据。没有取得历史实现、合约地址一致性或净盈利。未访问Arbiscan、链上调用或执行源码，模型／回测／收益计算／账户／付款／交易均0，actual model/effort UNKNOWN。完成停止。
