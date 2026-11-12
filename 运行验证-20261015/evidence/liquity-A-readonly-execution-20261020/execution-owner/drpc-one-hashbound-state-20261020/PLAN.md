# 单次hash-bound小状态验证：PREPARED，未执行

Root审阅后才能用项目.venv/bin/python -B -E -S执行一次，stdin DEVNULL、固定安全env。原main/core/collector/binding/旧锁/旧原件不改，原T0/T1不变。固定https://eth.drpc.org/，系统现有HTTPS loopback IP literal+validport/PAC关闭只读一次；固定同host CONNECT与SNI，默认CA与hostname/CERT_REQUIRED，禁认证/重定向/代理更改/DIRECT回退。一个TLS连接上串行请求；若服务器要求关闭连接，则停止，不自动建第二连接或重发任何方法。

## 精确执行序列

1. id1 eth_getBlockByNumber ["latest",false]。成功完整JSON响应校验非null header及transactions为hash列表，冻结number=B、hash=H（非零）、timestamp。只此步骤用latest。
2. id2 eth_call [TX,{"blockHash":H,"requireCanonical":true}]。
3. id3 同TX，仅blockHash改固定32字节零hash，requireCanonical仍true。此负对照不是正步骤回退。
4. id4 eth_getCode [TM,{"blockHash":H,"requireCanonical":true}]。与固定Sourcify原件onchainBytecode解码后逐字节及SHA比较。
5. id5 eth_getBlockByNumber [B,false]，number=B/hash=H才fence通过。不能据fence推此前所有瞬间全球canonical，只认证本次指定对象/返回身份和末次fence。

TM=0x7bcb64B2c9206a5B699eD43363f6F98D4776Cf5A，TX={to:TM,from:0x0000000000000000000000000000000000000000,gas:0x186a0,data:0x4aff96e1}。固定gas100000，无gasPrice/value/override，不估gas、不广播。ABI原件getTroveIdsCount()为无参view、uint256输出；结果须恰32字节，整数只作库存数量元数据，不是收益核算。采用transaction-first标准形状，不试其它参数次序、bareHash、latest或blockNumber状态调用替代。

## 负对照事前分类（不可执行后扩名单）

JSONRPC error/code=-32001 → RESOURCE_NOT_FOUND。
或code=-32000且message逐字属于["header not found","header for hash not found","block not found","unknown block"] → EXPLICIT_NOT_FOUND_NONPREFERRED_CODE。
其余码/文本/有效result/null/schema异常都不通过并停止，不trim/lower/正则宽配。仅固定分类与整数code落盘；error原体/原message不落盘，只保留bytes/SHA。第二类仅语义可识别，不能称符合EIP推荐notfound错误码。HTTP非200也停止，不当预期负对照。

## 身份来源

既存../liquity-official-deployment-binding-20261020/root/sourcify-record.body，1182544B/SHA002c37f8674d4fef6fb721a70d1ad26af02ee4a678aba0ae4bdd27222265f202。源码记录chain1/精确TM；ABI/signatures原载selector0x4aff96e1。runtimeMatch exact_match，verifiedAt2025-05-21T14:51:43Z是封存服务身份，不认证当前链runtime；本次步骤4才作同H字节绑定。原runtime23779字节，原bytes SHA c46a82f256fb8daa445eeaad42bb0a27e498297b17c5da0d1f7eaaa328dcd371。脚本在任何网络前核source全hash/chain/address/ABI/selector/runtime hash，source不改不复制。

标准只读一页[EIP-1898](https://eips.ethereum.org/EIPS/eip-1898)，Final，L28–52明确eth_call/getCode对象blockHash+requireCanonical及推荐错误语义，L58示例。小摘录为native返回的引用/摘要，不是rawHTTP；HTTPstatus/页面原体hash及本次独立获取UTC UNKNOWN，不倒填。标准证据不替代dRPC实证。

## 资源与安全

一次probe.once独占在source/route/network前创建，旧once不动。每方法逻辑attempt在发送前计数，send_started/send_completed单列；旧方法66，最多5后71。旧Alchemy32734CU不变，dRPC实际CU UNKNOWN。Root最终futureCPU guard7275（含本Owner20/Root10/另Reviewer5，非历史实测）。Owner准备+后续执行都在20预留内不双加。

另按Root在新数据前固定的工程等效影子刻度保留25M硬帽：既有32833，每次attempt前按原表getBlock20/call26/code20扣，5步最多+112=32945；发送前核不超25M。该影子不是Alchemy实际新增，也不是dRPC真实收费/余额，不代替方法数/CPU/免费资格等更严限制。

外层完整进程wall45秒、累计父子CPU5秒采样超限终止、RSS128MiB目标采样监视；脚本本身alarm45+进程RLIMIT_CPU5，各I/O≤5秒，scutil≤3秒。采样有瞬时/短命子进程盲点，不声称macOS kernel RSS硬帽或精确collective CPU硬帽。新目录≤256KiB，单响应body≤64KiB；runtime原始成功体约47.6KiB、count小体，最多两个64KiB block体，连脚本/metadata须仍在目录帽内。外层执行时监视并收尾stat，不为超限扩帽。

成功JSON在ID/jsonrpc及结果专属schema验证后才保存公共body；普通错误/拒绝只留HTTP/code/固定安全分类/body字节hash。不输出动态异常类、str/repr/traceback、URL、header或路由值；网络错误本单止，不依据旧成功自动重试。整请求若在body未读完就失败，仅能说明实际计量范围，不能假称完整error原体hash。

仅语法编译和负对照分类/源路径合成检查一次PASS，原始stdout/stderr/真实wholewall与CPU已留；不运行run()/系统路线/网络。该验证即使全PASS也只支持一次小状态和TM代码身份，不证重型全扫描、2秒预算、持续服务、独立市场样本或利润，更不启动原A。
