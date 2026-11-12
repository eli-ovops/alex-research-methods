> ## Documentation Index
> Fetch the complete documentation index at: https://docs.gains.trade/llms.txt
> Use this file to discover all available pages before exploring further.

# Staker FAQ

> Answers to common staking questions

## Why can't I immediately withdraw my funds?

For the security of the vault, and to prevent stakers from front-running PnL changes.

## What determines when I can withdraw my funds?

The collateralization ratio of the vault, determined using the snapshotted total PnL from the beginning of the current epoch.

Depending on the ratio, you can withdraw your funds in 1 (ratio > 120%), 2 (> 110%), or 3 epochs.

## Can I withdraw my funds anytime after my withdraw epoch?

**NO!** This is important. You may only withdraw your funds during your designated withdraw epoch. If you miss the window, you need to make a new request. Please note that you manually have to withdraw the tokens during the designated window that is displayed after requesting a withdrawal. (2 transactions in total)

## Do gTokens still accrue value after I have requested a withdrawal?

Yes.

## What's the purpose of the epoch system?

To provide the vault with snapshotted open PnL data, which factors into the collateralization ratio.

As an example, if the vault has 100k DAI deposited, and 20k DAI in negative PnL, the vault appears over-collateralized (120%). It's covering staker deposits + a 20k DAI buffer.

But suppose there is 40K DAI in positive open PnL. This is not captured by the vault, as the PnL is not final. But it should not behave as if it is over collateralized, as it has a potential outstanding liability of 20k (40k positive open PnL - 20k negative PnL), or a collat ratio of 80%.

## What happens if open PnL closes during an epoch?

Because a snapshot of open PnL is used for each epoch, there is a risk that it will close during the 3 day epoch, thus counting towards total PnL twice as much as it should.

To protect agains this, PnL updates during an epoch do not impact price: A snapshot of total PnL is used.

The vault still tracks all closed PnL during an epoch, but it also does not impact the price or collateralization ratio until the next epoch, as a way of synchronizing open and closed PnL data.

## Can I unlock my gTokens anytime after my unlock date?

Yes, you may unlock gTokens for any gNFT you own anytime after the unlock date.

## What happens if I transfer my gNFT to another wallet?

That wallet becomes the new owner and has rights to the gTokens on unlock.

## Why can't I transfer my gTokens?

You have a pending withdraw request open. Withdraw requests lock gTokens to your wallet for the duration. Of course any other gTokens you have can be transferred, only the amount staged for withdraw can't.

This is to prevent gaming the withdraw request system.

## How is "Estimated Earnings" calculated on Vault webpage?

Estimated Earnings is an approximation of how much you've earned.

> *Using gDAI as an example: estimated earnings = gDAI balance (locked and unlocked) market value  + total DAI withdrawn - total DAI deposited*

**Why is it an "estimate"?** Because gDAI is an ERC20, it is transferrable. You can transfer to a separate wallet, swap on a secondary market, stake as collateral. Any transfer out of or into your wallet is considered a market rate swap (same as a withdrawals and deposits). In actuality it is unlikely gDAI is swapped at market rate.

For example, if you purchase 50 gDAI at a rate of 1 gDAI / DAI then transfer 20 gDAI to another wallet when the exchange rate was 1.5 gDAI / DAI you'll have an estimated earnings:

**Estimated earnings** = (30 gDAI balance \* 1.5 gDAI / DAI)  + (20 gDAI transfer \* 1.5 gDAI / DAI) - 50 DAI  = 45 + 30 - 50 = **25 DAI**

The same is true for locked gDAI (gNFT). They are transferrable and the same assumptions are made when doing so.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.