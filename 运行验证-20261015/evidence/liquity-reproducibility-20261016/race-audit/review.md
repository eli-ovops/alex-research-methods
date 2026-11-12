# Liquity V2同一trove先成功清算、后失败调用：独立静态审阅

审阅UTC：2026-10-16T03:07:45.481552+00:00。沿用PERMISSIONS-2026-10-14-v1及ROUTING-2026-10-13-v4授权边界；继承请求模型/effort，实际运行态无法独立见证，标UNKNOWN。未联网，未执行下载/仓库代码、模型、回测、策略或交易。原件只读，所有输出限本race-audit目录。

## 结论

**五对逐项成立。** 失败calldata中的原始uint256 troveID，与更早成功交易同一WETH分支TroveManager的TroveOperation（op=5，liquidate）及同一TroveNFT的burn tokenId逐位相同。成功status及Liquidation事件也对应。因此可确认：这些ID在失败交易上链之前已经完成过清算；不是仅凭区块相邻猜测竞争。

失败上链状态为NothingToLiquidate。公开区块时间只能给出纳入顺序，不能证明失败方何时发现、广播、送达或是否延迟，也不识别其程序、网络或竞争策略的其他根因。第六次wstETH失败另branch，本轮未展开同ID历史。

## 五对精确核验

|失败block|此前成功block|相差block|UTC纳入时间差|原uint troveID完整相同|同分支op5+NFT burn+Liquidation|
|---:|---:|---:|---:|---|---|
|25239392|25239386|6|72秒|是，1个ID|通过|
|25240956|25240926|30|360秒|是，1个ID|通过|
|25251626|25251623|3|36秒|是，1个ID|通过|
|25253137|25253132|5|60秒|是，1个ID|通过|
|25256010|25256005|5|60秒|是，1个ID|通过|

全部原uint、失败raw input/ABI offset32/count1、成功发射者地址、操作和NFT ID、完整txhash与UTC在derived.json逐项保存。既有verified source的Operation枚举从0开始，第5项为liquidate；不是自行赋义。原始success HTML有NFT burn至0地址，并有同branch op5及Liquidation，因此与普通关闭/赎回操作区分。

失败To为WETH TroveManager `0x7bcb64b2c9206a5b699ed43363f6f98d4776cf5a`；先前成功外层To多数是不同bot/wrapper，**不能写成outer To相同**。一致性来自成功TroveOperation和Liquidation的emitter正是上述TroveManager，NFT burn emitter为该分支 `0x1a0fc0b843afd9140267d25d4e575cb37a838013`。

证据支持“同一仓位已经在此前成功交易中清算，而此后该失败调用上链时没有可清算对象”。不证明当前失败交易原本一定能盈利、不证明在它广播前就已清算，也不证明其他4个地址或任何bot应有相同检测/发送延迟。

## 九笔成功只列gross补偿，不能作为赢家完整利润

样本为本轮Latest25 Liquidation事件入口选出的8笔成功，加旧六月5日成功1笔。不是完整协议机会总数，不计算成功率、机会集中率、参与者能力或容量。

|成功block|tx|gross补偿WETH|实际收到WETH地址|
|---:|---|---:|---|
|25239386|[0x7eb25721e4…](https://etherscan.io/tx/0x7eb25721e4b043a4ef2fe92ad70014a56dfa0b088b55dc1dec18ffe6cc03f185)|0.056824292559467443|0x492d255234c83f2ddc5aa904d8a9db6743e9f046|
|25240926|[0x6ec3e9691f…](https://etherscan.io/tx/0x6ec3e9691fba6b899153ba4d5bc083a02c0cecd7bf65d3d434f3a9eb3ef550ca)|0.050483936521858444|0x88b33607d841f9f3892e2ec067a64ad43656e9c2|
|25249192|[0x6a970153f2…](https://etherscan.io/tx/0x6a970153f2760cba022021d740bebb9f5959ebe06ba2fa0851c219f4d9bc80ee)|0.044|0x94d456a424758162298d3b70be68ed9d18659fb9|
|25249375|[0x2f7f282bae…](https://etherscan.io/tx/0x2f7f282bae9388e4b4f3ebf36d09725a39eb221efe59445bbea7b2a73e35d4c3)|0.0475|0x000000000004fbf65b56ae13b507556c2c06bff5|
|25249615|[0xace0ff16c0…](https://etherscan.io/tx/0xace0ff16c0cb85f870ad388d987c2596680ef3cd1955518653355f90e2272625)|0.044451263731969109|0x80bf7db69556d9521c03461978b8fc731dbbd4e4|
|25251623|[0x79575e6db8…](https://etherscan.io/tx/0x79575e6db82e63b3e36921691e3c4bcdcee3bcd8c000a3052e6093883e17abdf)|0.085043731559576748|0x339c0db4a0030c88b4a48aafe56cdba23c8d4338|
|25252291|[0x26353be7b8…](https://etherscan.io/tx/0x26353be7b8570b453daff4c4784dc993ab7b2b742116d953edbe263d85c08ca9)|0.360848784148759889|0x9b29f107d97ccb564c346eb0e41be0dd0727336e|
|25253132|[0xa739926d80…](https://etherscan.io/tx/0xa739926d806048c1d6e59ece74d91c53b32ff73e58facfc8a7366d96c249d436)|0.045|0x492d255234c83f2ddc5aa904d8a9db6743e9f046|
|25256005|[0xb4c3c4ac35…](https://etherscan.io/tx/0xb4c3c4ac35cbb7298d228d3c8954a8d4285ffb7076d33a01519f29c9850b5473)|0.0475|0x9b29f107d97ccb564c346eb0e41be0dd0727336e|

9笔gross合计0.781652008521631633 WETH，进入7个不同实际WETH收款地址；不等于7个人。9笔Liquidation的两个补偿原uint均与WETH Transfer金额/收款地址匹配。历史event字段_boldGasCompensation虽名称带bold，本轮按真实WETH Transfer确认资产，未当BOLD收入。

多个成功者随后unwrap并把ETH转往浏览器标注的builder地址。gross补偿尚未扣这些直接支付、gas或其他失败尝试。收款地址可能是wrapper，From可能是另一地址；不能把它们合并为一人，也不能只因协议付过补偿就称操作者最终赚到全部gross。

## 竞争成本的完整单笔例：0xb4c3…05473

这一新增成功的完整HTML与State已独立静态核算：

|动作|精确金额|
|---|---:|
|协议向wrapper支付WETH|0.0475|
|WETH Withdrawal / WETH合约向wrapper转ETH|0.0475 ETH|
|wrapper→浏览器标Titan Builder地址的直接支付|0.045585735056956094 ETH|
|wrapper→From返回|0.001914264943043906 ETH|
|From实付gas|0.000427703441331096 ETH|
|From本笔ETH净增|0.001486561501712810 ETH|

三条实际nonzero internal ETH转移精确为unwrap、给builder、返From，wrapper可见原生ETH流量净0；两笔WETH补偿合计与Withdrawal亦精确相等。sender State从0.150959031153659515到0.152445592655372325 ETH，差额=返回减实付gas=+0.001486561501712810 ETH。gasUsed517482×effectiveGasPrice精确等实付gas。

该direct builder支付约占gross的95.97%。State中builder增加0.045585735574438094 ETH，等于direct支付0.045585735056956094加正常gas内已含priority的0.000000000517482 ETH。**direct支付在gas之外另扣，priority已包含在gas内不得再扣。** 此例说明gross补偿远大于本笔From留存收益，仍不代表其全运营利润。

State未单列wrapper自身ETH before/after行，不能以缺行当余额未变的独立证明；只称三条已显示内部ETH流量净0、WETH receipts/withdraw闭合。From正增量有State直接支持，不需要假定From与wrapper同一所有人。浏览器标签Titan Builder及转账存在，不证明通过Flashbots路由、private bundle、某个独占协议或具体竞价方式。

## 未闭合及不得扩大的边界

- 区块纳入时间差不是广播/网络/策略反应延迟；未取mempool/private submission记录，不能写“发现晚/发送慢”。
- NothingToLiquidate加先前相同ID清算，能够证明本轮确定事实，不排除其他未观察的根因；wstETH第六失败仍为未检分支，不能照推。
- 只有Latest25筛选入口中的局部成功集合，无全部私人失败、资金流/提现、部署、节点、链下费用。不能据9笔gross算每位赢家净利润、长期成功率或个人可复制收益。
- 本轮原HTML与State来自相同explorer，不冒充独立归档节点字节认证；公共协议事件不替代私有bot源码/真实执行身份。

输入文件SHA256、大小与只读位置在hashmanifest.json；derived.json保存5对原始uint及9成功gross，competition-payment-derived.json保存竞争成本单笔细项。未改根原件或其他工作者文件。
