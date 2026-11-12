# 迁移完整树增量：同repo真实样本与MIT

**结论：当前新repo确有可定位的小型真实行情示例，根MIT为这些随项目分发的示例用于个人本机研究、改编及汇总评估复核提供有限正面许可依据；旧两blob未迁入当前固定树，不能自动倒授旧repo文件。**没有下载样本、核质量或运行模型。

本轮第1次GET读取固定root tree `5f3ec40b2afb764e0fea112f941ed85523ef4e88?recursive=1`，282条元数据、truncated=false、HTTP含头69799B，未用512KiB放宽。完整当前树逐项比对旧 `38a1e26f10dde12618a2258bf04560476f867ab7` 与 `14030d53c138fa77e07fbdd5e38e9072f4343043`，匹配均0。这只界定当前树，不追或否认历史存在。

完整树包含15个examples/*.gz数据文件（全清单及blob/字节见JSON），包括：
- `examples/usdm/btcusdt_20240808.gz`：3637062B，blob `a786c69d99a77be6060af5f7714db7393c9a4f5d`；与当前官方DataPreparation教程引用同名，形成比未定义本地路径更具体的公开对象。
- 同目录次日BTC及两日ETH、cm/spot两日BTC/ETH等；这是文件名日期标签，不是已扫描的起止/完整日。
- 最小对象 `examples/hyperliquid/btcusd_20250126.gz`：7484B，blob `6626834e8150e1baa17c1f9d7fe78c18c0e48907`；小并不证明适合任意预测或足量样本，未按表现选择它。
- Bybit与MEXC也有文件元数据，不扩为其他策略或多源研究。

第2次GET实际取得根LICENSE（1079B），blob `28c446419cb8488ff0825fabb0954bc4d6e8fda1` 独立匹配。原文MIT，版权2022 nkaz001；允许软件及关联文档的使用、修改、分发、再许可和商业复制，保留版权/许可通知，无担保。tree另有py-hftbacktest/LICENSE，未读；examples/未见单独LICENSE/NOTICE路径。

**许可层级**：根MIT与同一固定树内作为项目示例分发的数据构成合理的仓库许可适用推断，不再一概停在“publicdownload非许可”。个人专用统计研究、向AI助手披露不重构原始数据的汇总评估有这层正面依据，不需特定“ML/AI”许可字样。但MIT字面对象是Software及关联文档，没有逐文件独立数据授权段；本轮未读取所有文档内嵌例外，且不保证发布者拥有所有交易所权利或用户获准实盘。故标有限依据，不当全司法或上游权利审计通过。没有将这些样本说成Tardis重分发，亦未借框架MIT豁免另源条款。

本轮改变：已有一个精确到blob/大小、与官方教程匹配的当前repo样本入口，可继续其格式/时钟/初态和实际内容的有限准入核验；这并非下载或实验授权。生成collector/convert精确commit及参数仍须按当前样本分别绑定，不能沿旧Python两文件生成假设套新gz。

旧audit/migration partial与draft原hash保留为历史阶段；草稿只针对旧两文件，未发，不用于宣称新样本无许可。两GET正常，URI/UTC/含头响应与解码许可原件已保存。0行情payload/pickle读取、代码执行、模型、回测、账户、付款、交易；actual model/effort UNKNOWN。完成停止，不再查历史。

