# 六次取得成交记录：支付与费用解释口径

限定PASS，仅静态解释；取得成本及利润仍UNKNOWN。实际model/effort UNKNOWN，规则PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4不变。读取UTC：2026-10-16T16:18:07.760787+00:00。

- **ABI**（official-Events.sol L12–14,27–38,48–59）：Indexed orderHash/maker/taker; seven data words side,tokenId,makerAmountFilled,takerAmountFilled,fee,builder,metadata; builder/metadata bytes32, not money.

- **BUY/SELL cash**（official-Trading.sol L204–251,300–347,355–387,446–475,482–535,610–619,676–681）：For this declared version, BUY maker gives makerAmountFilled collateral plus fee and obtains takerAmountFilled position units; SELL maker gives makerAmountFilled position units and receives takerAmountFilled collateral minus fee. Actual refunds, multi-order paths, asset address, decimals and transfer recipients need reconciliation; event amount is not a complete wallet cash ledger.

- **Actor vs execution taker**（official-Trading.sol L131–143,284–296,335–347,492–535; card L113–119）：maker is order owner even for taker-order summary; taker can be counterparty or Exchange. Holder merely appearing as taker on seller row is not evidence that seller fee was paid by holder. Locate own BUY record and matching position/collateral transfers; do not infer real-world common ownership.

- **Duplicate economic legs**（official-Events.sol L63–75; official-Trading.sol L131–143,284–296,492–535）：Taker OrderFilled plus OrdersMatched repeats summary; multiple opposite maker fills and buyer summary can describe same exchange. Uniqueness by chain/contract/tx/logIndex, not orderHash alone. For holder payment sum holder own eligible order executions once; do not add full seller proceeds and buyer summary again. Partial fills of same order may be distinct, not dedup by orderHash alone.

- **Fee de-duplication**（official-Trading.sol L217–236,312–326,364–382,488–490,513–521,676–681）：OrderFilled.fee, FeeCharged and actual collateral Transfer can describe one payment; do not subtract fee twice from already net SELL proceeds or count FeeCharged as second transfer. Zero fee in one row does not establish all tx fees/gas zero. Missing fields remain UNKNOWN, never reconstructed from a current fee formula.

- **Legacy misnamed fields**（hf-pinned-readme.original.md L217–229; official-Events.sol L36–38,56–58）：V2 mapping maker_fee->fee, taker_fee->builder, protocol_fee->metadata. Large unsigned integers of last two are bytes32 metadata, not fee amounts; no three-column sum. SII-specific upstream relation remains UNKNOWN.

- **Existing first4 sample**（wzsg-fixed-first-four.original.json rows0–3）：Four records from two tx; BUY order-owner fields include 8000000/10000000/115200 and two partial BUY maker lines155100/330000/0,2820000/6000000/0 plus opposite BUY6330000 units. Existing two-tx cash reconciliation illustrates distinct per-actor trades and summary, not new acquisitions evidence or profitability.

- **0.69 incoming**（independent-holdings-and-report-review.json fixed transfer leg block86161968/log1513）：Source address7f95... to holder while operatorE111; cannot label gift/free acquisition. Need relevant fill/payment linkage; same token/quantity alone insufficient.

- **Missing coverage**（hf-pinned-readme.original.md L102–123; current note scope）：OrderFilled-only package lacks complete ERC1155 lifecycle, collateral transfers, failed/status/gas/native receipts. If later exact six tx found, join fixed tx/block/token/actor/raw amount; distinguish no row, incomplete archive, and actual zero. No price, profit or new data-row read here.

固定官方源码commit `ccc0596074f4dfd62c944fbca4de252893b82b4b`，wzsg卡revision `f8782fc0c18a4e32b7bdc348ada114e5007a4367`。这只绑定声明源码/字段，非历史runtime或首次公开证明。所有实际输入绝对路径、SHA256、bytes见同名JSON。

0新增网络、0大文件重验、0新数据行/收益核算。未执行来源源码、SQL、SDK、EVM、模型、回测、策略或交易。公众原账可支持历史现金，不以私人bot完整公开作新增门槛。
