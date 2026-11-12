# Liquity V1直接调用：6请求内未取得确定清算hash

2026-10-16。只读公开检索，6次请求（5 search query、1合约页读取）。未运行仓库、模型、回测或交易，没有连接钱包、注册、付款或发消息。

结论：没有取得能确认EOA直接调用V1 liquidate/batchLiquidateTroves且成功支付ETH+200LUSD补偿的实际txhash，按限定停止。不将地址或ABI列表充当净利事件。

定位到Etherscan标为Liquity: Trove Manager的V1地址：
0xA39739EF8b0231DbFA0DcdA07d7e29faAbCf4bb2
https://etherscan.io/address/0xA39739EF8b0231DbFA0DcdA07d7e29faAbCf4bb2

搜索正文可读ABI，含liquidate(address)、liquidateTroves(uint256)、batchLiquidateTroves(address[])，Liquidation事件含_collGasCompensation、_LUSDGasCompensation；这些仅表明合约接口，不能证明某笔交易已经成功或补偿足以覆盖gas。合约页直接工具读取一次403，查询LOCAL_BLOCKERS后未重试、换代理或API绕过。

首轮批量清算搜索主要命中Liquity V2，包括0xb2346116f3437c1227243e90c361900f8035284f9911f12e602a5af38691e3fe、0x9c06addedd2b7f86a7e69271712c54fb74a0f7a73163f045aa6897ee49a2643c等，搜索已明确标签V2，不混为V1，也没有进一步读这些交易。

唯一检索到的V1交易链接：
https://etherscan.io/tx/0x32b3fd58d2391796097e7f4e9f4c3500784fb4da410db613e6ad01b3c732da56
搜索明确为Close Trove，不是本任务所需清算，未将其列为候选净利事件、未再打开。

未确认：EOA直接成功清算hash、ETH补偿、200LUSD实际转入、gas、残留资产、规则首次公开日期、合约精确源码/部署映射及许可。本轮也未独立打开Liquity官方部署registry，Etherscan标签定位不能升级为官方映射核验完成。

此结果只是有界检索未找到，不表示没有普通EOA直接清算。原文搜索与403回执见direct-*.json，hash和落盘UTC见manifest.json；全部保留作续接证据。未修改他人文件。
