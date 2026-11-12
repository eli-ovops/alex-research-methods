# 衍生OrderFilled包：字段与官方ABI准入

**限定PASS：字段映射有官方源码支持；不是完整持仓、全费或盈利原账通过。** 6次正常公开GET均200，保存320434 bytes；未下载Parquet，未执行SQL、源码、SDK、EVM、模型、回测或交易。实际model/effort UNKNOWN，沿用PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4。每次URL/UTC/HTTP/bytes/SHA在`read-receipts.json`，本报告JSON绑定11份实际输入的绝对路径与指纹。

## 原件与版本

- HF卡固定版本：[`f8782fc0c18a4e32b7bdc348ada114e5007a4367`](https://huggingface.co/datasets/wzsg/polymarket-orderfilled-v2/blob/f8782fc0c18a4e32b7bdc348ada114e5007a4367/README.md)。首次main原响应的`X-Repo-Commit`也是此值，随后固定版本GET与首次卡逐字节相同。根已存metadata的`lastModified`为2026-08-04T00:10:42Z，不是本轮10月更新证明，也不是独立首次公开时间。
- 卡实际链接的[官方Events.sol页面](https://github.com/Polymarket/ctf-exchange-v2/blob/main/src/exchange/mixins/Events.sol)嵌入`currentOid=ccc0596074f4dfd62c944fbca4de252893b82b4b`；本轮按该commit取得Events.sol、Trading.sol及LICENSE.md。是声明源码身份，未独立编译/比运行时或历史部署源码。
- 卡明确链接wzsg的`polymarket-analytics`及官方Polymarket仓库，但其上游只写“combined V1/V2 archive”，**没有明确链接或点名SII**。根已存SII metadata版本`73bc1adc43b05709d2cde3bf41ef4111eda3f4fc`及文件清单可复用，但仅同列名/清单不足以证明它就是该衍生包的具体上游。具体SII字节来源关系仍UNKNOWN，不能将发布者未注明的出处补写成已证。

## 16列及最重要的重命名

固定卡L100–121列明16物理列：`timestamp, datetime, block_number, transaction_hash, log_index, contract, order_hash, maker, taker, side, token_id, maker_amount_filled, taker_amount_filled, fee, builder, metadata`。`event_month`来自目录分区，不是第17物理列（L123）。

固定卡L217–229声明组合包旧列名的V2映射：

| 组合包旧列 | V2实际语义 |
|---|---|
| `maker_asset_id` | `side` |
| `taker_asset_id` | `token_id` |
| `maker_amount_filled` / `taker_amount_filled` | 两个实际成交原量字段 |
| `maker_fee` | `fee` |
| `taker_fee` | `builder`，bytes32 |
| `protocol_fee` | `metadata`，bytes32 |

**不能把三个名含fee的旧列相加。** 后两列在组合包中即使表现为很大的十进制整数，也按该V2映射解释为32字节值，不是手续费金额。卡声称将其无损恢复为`0x`加64位hex；本轮没读Parquet或运行转换器，因此只能核语义和声明，未独证全包转换正确。

[固定官方Events.sol](https://github.com/Polymarket/ctf-exchange-v2/blob/ccc0596074f4dfd62c944fbca4de252893b82b4b/src/exchange/mixins/Events.sol) L12–14给完整签名：`OrderFilled(bytes32,address,address,uint8,uint256,uint256,uint256,uint256,bytes32,bytes32)`。L27–38定义字段，L48–61实际写入七个非indexed word，顺序正是`side/tokenId/makerAmountFilled/takerAmountFilled/fee/builder/metadata`；`log4`的三个indexed参数为orderHash/maker/taker，data长度224 bytes。卡L95给topic0，但本轮未自行计算Keccak，不把卡的hash当独立哈希核验。

[固定Trading.sol](https://github.com/Polymarket/ctf-exchange-v2/blob/ccc0596074f4dfd62c944fbca4de252893b82b4b/src/exchange/mixins/Trading.sol) L217–251可见SELL收到量扣fee、BUY支付fill加fee，并将feeAmount/builder/metadata分别传入事件；L351–382的taker结算同样区分SELL扣款与BUY另收。L676–681另emit FeeCharged。故`OrderFilled.fee`与同一实际收费的FeeCharged/净Transfer应关联而非重复扣费。本轮未取实际收据，不据源码断言历史每行部署参数、付款币种与到账均已核。

## 完整性与许可边界

卡自述575630861行，时间2026-04-28至2026-08-03，123个Parquet、33617734086 bytes；“daily”标签不证明已包含10月。L233–241的NULL/hex/行数/RPC样本对照，L247–249的去重和原子提交，均是发布者自述，本轮未独立执行。L253–257明确当前月可能不完整、时间戳沿用上游、仅含链上fills、一个tx可能多个OrderFilled及重组风险；不能把行数当独立交易或人数。

按这16列，**没有完整ERC1155 Transfer持仓、merge/split/redemption、期初期末余额、receipt gas/status或失败/native内部付款记录**。有txhash/fee可做后续原件关联，但本包本身不是完整限定账期净现金账。此判断仅限已读衍生卡及列结构，不等于根所查SII整套其他表必定不存在这些字段。

HF卡frontmatter和根metadata未给明确数据许可；L258还声明不授予底层合约、商标或第三方额外权利，故数据个人研究复用范围UNKNOWN，公开/ungated不等于许可完备。官方LICENSE是BUSL-1.1，Additional Use Grant=None，Change Date=2030-03-27，Change License=MIT；现条款授权复制、修改、再分发及非生产用途等，受条件约束，不能称当前整套MIT或商业生产复用已获准。源码许可也不自动覆盖数据包。

## 零网络补读：SII组合包卡

根随后提供固定`73bc1adc43b05709d2cde3bf41ef4111eda3f4fc`的`SII-README.pinned.original.md`；本地复读核SHA256=`04addcffb36d97d7facaa5f544a7f5079dc73861e4d78e3c62659744f4c9dffc`、22755 bytes。其L199–218仍用旧名maker_asset_id/taker_asset_id及三种fee泛义说明，并称金额/fee为32字节little-endian，必须与V2真实ABI区别；不能对V2行照此将builder/metadata除1e6计费用。此处是**文档字段解释不足**，还未读取原行，不能断言全包数据已经算错。

SII L50–54自述10月5日版本补齐此前遗漏V2 sell-side与漏日志、去重并统一hash格式；这反而说明版本不能混用或仅凭“complete”当独证。L59限定CLOB OrderFilled，不含2022年11月前FPMM。L464明确声称MIT商业/研究，L34链GitHub LICENSE；这是SII发布者的许可声明，与没有同等声明的wzsg衍生卡分开。LICENSE正文由根另核，不在本子任务读取预算内。不能反向把SII声明自动授给wzsg数据或BUSL官方源码。

可以继续核固定原件的字段来源与费用；不能从本卡声称已核历史盈利、完整持仓费账或未来容量。认可另有闭合历史现金不要求私人bot全部公开；本轮真正缺的是数据与实际现金/费用的对应，不是私人动机。
