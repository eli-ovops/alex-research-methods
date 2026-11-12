# Limited independent single-fee binding review

PASS_LIMITED_SAVED_UI_AND_RPC_SINGLE_FEE_BINDING_REVIEW. Material findings:none. Actualmodel/effortUNKNOWN.

Fixed sample selection verified against saved responseid23: earliest(blockNumber,transactionIndex,logIndex) in inclusive50661501..51242185 window equals frozen selected event; no replacement/sum or per-holder attribution.

Saved transaction observation statesSuccess, hash a2e287..e07e, block50661898. OldRPC eventlog6 matches UI transcription emitter,topic,sender,rawdata,block and tx; oldRPC does not independently supply status or other newUI logs.

Saved UI log3 DAI S(cfa6..33c)->callback6c612..28f46 and log4 callback->vaultd85e..91b both14684219999999999999; log6Reward and log7DaiVaultFeeCharged same raw amount, ordered in same transaction. These are one fee flow, not four incomes. S actual configured storageT identity is not independently bound by transfer addresses alone.

Fee log7 trader6e48..2e66 agrees with log18 LimitExecuted t.trader; orderType2 matches StorageInterfaceV5.sol L18 enum {TP,SL,LIQ,OPEN}, under obtained source interpretation. Compound tuple, historical runtime and full trade/account closure remain unverified.101 leverage is a displayed trade field, not holder return.

Logs12/13 transfers558000360000000000000 match log14AssetsReceived, separate from fee path. AssetsReceived is not another trading fee/personal dividend. Zero trader transfer/log18daiSentToTrader0 does not establish complete trader loss or holder net profit.

GToken L721-729 and callback L772-805/L902-905 are consistent with observed fee and separatePnL segments; source-level support does not replace complete operative historical implementation binding.

Exact Decimal display14.684219999999999999DAI and558.00036DAI matches saved raw quantities using earlier accepted DAI18precision; no payout/return/net-profit calculation.

Alignment-review preserves research-only scope and does not claim this new receipt independently read or a price-prediction breakthrough. No material contradiction found.

Evidence limits:

- Reviewer independent currentUI field read UNKNOWN: exactly one cua.getTab(7,browser2) returned Browser is not available:2. No retry,inventory,newtab or alternative route. This is reviewer-context unavailability, not evidence root page unavailable.
- All nonlog6 transfer/fee/limit fields andSuccess are inherited from root saved actual UI transcription, not reviewer refreshedUI or original complete rawreceipt.
- Underlying source version through transaction, configuredstorageT/vault, pair parameters and complete upgrade history remain limited.
- One local fee payment only; no500/933 generalization, personal distribution/fullcostprofit, prediction model edge, repetition or capacity proof.
- Displayed transaction fee belongs to this oracle execution, not automatically fixedholder personal cost; fee event/asset movement/PnL labels must not be double-added.

Browser blocker checked in LOCAL_BLOCKERS.md277/821; no retry or route change. Full input bytes/SHA in review.json. Only assigned review outputs written, old artifacts unchanged.
