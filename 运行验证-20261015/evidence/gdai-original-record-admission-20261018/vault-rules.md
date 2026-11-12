> ## Documentation Index
> Fetch the complete documentation index at: https://docs.gains.trade/llms.txt
> Use this file to discover all available pages before exploring further.

# gToken Vaults

> Collateral vaults supporting trading liquidity

**Current gToken Vaults**: gUSDC, gDAI, gETH, gGNS, gBTCUSD

gToken vaults follow ERC-4626, a standard API for tokenized yield-bearing vaults that represent shares of a single underlying ERC-20 asset. For each vault, gToken shares represent the underlying token asset. For example, gDAI represents DAI.

Vaults serve as a counterparty to all trades made on the platform:

* When traders win (positive PnL), their winnings are received from the vault.
* When traders lose (negative PnL), their losses are sent to the vault.

In exchange, the vault receives a portion of trading fees. These fees are proportionally split among gToken shares, incentivizing stakers to stay in the vault.

The vault that earns fees, pays profits, and bears losses is determined by each trade's collateral.

Collateralization of the vault depends on trader PnL. As long as fees earned is greater than PnL payouts, stakers earn a positive return. This has proven to be the case for 2+ years and the protocol has various risk management measures in place to ensure it continues.

Net losses are used to create a buffer, further protecting stakers' funds and the protocol from future PnL abnormalities.

To better approximate real collateralization ratio, and to minimize risks for the protocol (including stakers), the vault follows an epoch system for capturing snapshots of open PnL. Open PnL represents the aggregate PnL of all open trades at the time of the snapshot.

## gToken

gTokens are ERC-20s representing ownership of the underlying token asset. It follows an exchange rate model (similar to Compound's cTokens) where the price of gToken to asset changes in real-time from two variables: accumulated fees and trader PnL (both open and closed).

*`gToken = 1 + accRewardsPerToken — Math.max(0, accPnlPerTokenUsed)`*

`accRewardsPerToken`: accumulator value representing how many fees a single gToken has accrued. This value always increases over time.

`accPnlPerTokenUsed`: a snapshotted accumulator value of trader PnL from all closed trades and a snapshot of open trades from the end of the previous epoch. This value changes every epoch and can move in either direction.

To summarize, the vault consists of two parts:

* The asset staked by stakers, which corresponds 100% collateralization
* The overcollateralization layer, which makes up anything beyond 100%

If the vault is at 110%, its overcollateralization layer is 10%. The overcollateralization layer does not increase the gToken price. See the gToken price formula above.

The overcollateralization layer (OC) acts as a buffer between traders and lenders, and profits and losses are paid out, or paid to, the OC as long as it exists. By design, the vault can be in two states; overcollaterized (>=100%) and undercollaterized (\<100%).

* If the vault is **overcollateralized**, a percentage of trader losses is diverted to a pool where users can sell GNS for the asset, OTC, using the 1-hour TWAP. This enables users to sell GNS without paying any slippage that would occur on an exchange, or affecting the GNS price. This GNS is then burned, to counteract any minting that happens while under-collateralized.
* If the vault is **undercollateralized**, GNS is minted and sold for the asset, OTC. The asset is then used to replenish the vault. A maximum of 0.05% of the total supply of GNS can be minted every 24h (18.25% per year). Again, this creates a secondary market where users can buy GNS without having to pay any slippage. (*Please note that in the case of BtcUSD, \$GNS will not be minted in order to replenish an undercollateralized vault, it instead relies on its partner — Bifrost — to restore the overcollateralization buffer.*)
* Both the mints and burns are entirely decentralized and only happen when someone interacts with the vault. The interface for it is located at [https://gains.trade/otc](https://gains.trade/otc)

<img src="https://mintcdn.com/gains/IoupFIThDEsTzJuI/images/5OlHorCRNboKrsGH1W48-photo_2025-06-18_23-58-01.jpg?fit=max&auto=format&n=IoupFIThDEsTzJuI&q=85&s=feee9dec3a62af2387931e85a6dde302" alt="" width="1280" height="720" data-path="images/5OlHorCRNboKrsGH1W48-photo_2025-06-18_23-58-01.jpg" />

<img src="https://mintcdn.com/gains/IoupFIThDEsTzJuI/images/bpv1tIE5IcFo7cYFnLMo-photo_2025-06-18_23-58-10.jpg?fit=max&auto=format&n=IoupFIThDEsTzJuI&q=85&s=0b8e2b0100f2de14c932a79343dc7dc1" alt="" width="1280" height="720" data-path="images/bpv1tIE5IcFo7cYFnLMo-photo_2025-06-18_23-58-10.jpg" />

## gNFT

gNFT is an ERC-721 representing ownership of locked gToken shares. Locked gToken is purchased at a discount based on the lock duration, and can be unlocked after that duration ends.

Locked gToken accumulates fees like all other shares.

## Epoch system

The epoch system provides open PnL data to the vault in a decentralized manner, so the vault can better estimate its collateralization ratio. Calculating open PnL in real time on-chain would be too computationally expensive.

There are two states the epoch system can be in:

* **Withdraw window** - the period before open PnL values are being received and stakers may make withdraw-related actions (both requests and withdraws).
* **Open PnL window** - the period before the epoch closes where the protocol requests open PnL snapshots from oracles. It makes multiple requests to a network of oracles, taking the median value, finally averaging across the request periods. This PnL value is then used in the succeeding epoch.

## Withdraw locks

For the security of the vault, and to prevent stakers from front-running PnL changes, assets can't be withdrawn immediately. Instead they must go through a withdraw request system.

Depending on the collateralization ratio of the vault, a staker may withdraw either 1, 2, or 3 epochs after making a request. The higher collateralization ratio, the shorter the lock period. It's important to note that the gTokens continue to accrue value even after a withdrawal request has been made.

If a staker misses their withdraw window, they must make a new request.

For a more detailed overview of the vault, please see our Medium post:

[https://medium.com/gains-network/introducing-gtoken-vaults-ea98f10a49d5](https://medium.com/gains-network/introducing-gtoken-vaults-ea98f10a49d5)

## Audit

[Download file](/images/xsZrNA7skYMdwMiPTNi7-gains_trade_smart_contract_security_audit_report_halborn_final.pdf)


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.