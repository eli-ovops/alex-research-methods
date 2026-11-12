# Independent implementation supplement review

PASS_LIMITED_IMPLEMENTATION_MECHANISM_SUPPLEMENT_REVIEW; no material findings. Actual model/effort UNKNOWN.

Saved root normal-browser observation records creator tx0c45..d604 at block49275558, emitter fixed caller, Upgraded topic1ae31..6121 and vault approval. This reviewer did not independently reopen UI; saved UI observation is not raw receipt or complete upgrade-history proof.

Observed logic address matches independent Sourcify address; creation/runtime exact_match provider assertions, deployment block49275550 before proxy UI block49275558 and fixed case deposit50661501. No local recompilation/runtime validation.

Archive receipt bytes/hash and extracted30898B source match exactly. SPDX MIT for obtained callback source, not whole data/participation rights;2024verifiedAt does not prove pre-case publication.

L739-760 private unregisterTrade passes closingFeeDai+nftFeeDai to pairInfos.getTradeValue. Exact internal fee arithmetic and actual historic parameters outside inspected file are not independently established.

L772-780 conditional trade.positionSizeDai>0 branch computes closingFeeDai*daiVaultFeeP/100, transfers storageT DAI to callback then calls storageT.vault().distributeReward and emits DaiVaultFeeCharged. This is an explicit source-level trading closing-fee-to-vault mechanism.

L789-805 compares trader settlement to remaining collateral, sends shortfall from vault or routes surplus to vault; L902-905 sendToVault transfers DAI then receiveAssets. PnL settlement is distinct from reward-fee distribution and does not guarantee holder profit.

L156-182 onlyGov matches storageT.gov and may change fee fractions summing100; comment eg40 is not a historic parameter. Source callback restrictions and private scope do not establish actual historical governance/state values.

Owner final supplement retains branch condition, UI/source distinctions, fee-ratio and upgrade gaps. No material correction required. Previous proxy-only review preserved as historical;933 event audit and prior cost arithmetic not repeated.

Still unproved:

- No original raw creator receipt or complete intermediary upgrade timeline. Same initial/current UI address does not rule out changes in between.
- No proof all933 reward events used this implementation or followed this fee route; no per-event actual receipt/DAI transfer matching in supplement.
- Historical fee shares, actual pair parameters and storageT.vault endpoint across window UNKNOWN.
- No original trained prediction model, personal forecast edge, full holder net profit, borrowing/collateral/full-cost profit, repeatability, capacity or wealth-goal proof.

No new network, source/EVM/model/backtest execution or profit calculation. Previous reviews unchanged. Full source fingerprints in companion JSON.
