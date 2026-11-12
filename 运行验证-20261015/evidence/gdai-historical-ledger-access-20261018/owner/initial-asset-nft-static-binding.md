# 初始asset与锁仓NFT：构造数据静态绑定

限定通过，仅从两份已有Sourcify原件确定初始Transfer查询对象：

- asset：`0xda10009cbd5d07dd0cecc66161fc93d7c9000da1`。
- lockedDepositNft：`0x673cf5ab7b44caac43c80de5b99a37ed5b3e4cc6`。
- gDAI份额的emitter仍是proxy `0xd85E038593d7A098614721EaE955EC2022B9B91B`，不是以上两个对象。

本轮未使用subgraph配置、读取其他钱包或构造资金账。上述地址只是原件中初始配置，不证明当前状态或任何实际Transfer已发生。

## 字节定位与身份

proxy JSON的`creationBytecode.transformationValues.constructorArguments`首word给logic `0x38827724dd5abac83828151a6636f250ede58093`，匹配第二原件。第三word为`0x60`，即constructor参数起点偏移96处存_data长度964；随后964字节是初始化calldata。

calldata头4字节为`0xaabf8ede`。从初始logic ABI的initialize参数递归展开tuple得到规范签名，以独立纯整数Keccak256计算，前4字节精确匹配；同时核了Keccak256空串已知向量。未用SHA3-256代替、未运行源码／ABI库或EVM。完整规范签名、原始word与offset在JSON。

去掉selector后的args头第3word（偏移64）是`0x220`，指向args偏移544的`ContractAddresses`。前8字段依次是asset、owner、manager、admin、gnsToken、lockedDepositNft、pnlHandler、openTradesPnlFeed，第9项是动态gnsPriceProvider的offset，不得误读为地址。

| 字段 | tuple索引 | args偏移 | calldata偏移 | constructor参数偏移 | 原始word |
|---|---:|---:|---:|---:|---|
| asset | 0 | 544 | 548 | 676 | `000000000000000000000000da10009cbd5d07dd0cecc66161fc93d7c9000da1` |
| lockedDepositNft | 5 | 704 | 708 | 836 | `000000000000000000000000673cf5ab7b44caac43c80de5b99a37ed5b3e4cc6` |

动态字符串还读出name为`Gains Network DAI`、symbol为`gDAI`，仅作布局一致性说明，不据名字判断币种权利或收益。

## 源码赋值及限制

初始`project:/contracts/v6.3/GToken.sol`的struct字段顺序在L154–165，initialize签名L168–181；L203–204将asset交给ERC4626初始化，L207–208把lockedDepositNft转为INft并保存。proxy父构造的初始化路径在TransparentUpgradeableProxy L28–36、ERC1967Proxy L14–24。

两输入原件为上一阶段root的`independent-sourcify-contract.original.json`和`independent-sourcify-initial-logic.original.json`，当前SHA／字节见JSON。匹配初始构造数据不能替代升级史、当前storage、资产decimals、NFT后续实现或具体提现时点版本。这里不证明存赎／NFT转移或获利，也不改变根按时间固定的Withdraw样本。

状态`PASS_LIMITED_INITIAL_ASSET_NFT_STATIC_CONSTRUCTOR_BINDING`。actual model/effort UNKNOWN；新网络、链／ABI／EVM调用、源码编译／执行、钱包选择、持仓／收益计算、模型／回测及交易均0。两文件保存后停止。
