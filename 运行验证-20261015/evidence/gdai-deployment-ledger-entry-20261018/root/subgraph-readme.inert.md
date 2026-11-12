NOTE: The Graph compiles to WASM. This is AssemblyScript, not TypeScript. Please review the [AssemblyScript documentation](https://www.assemblyscript.org/concepts.html).

Notable limitations: No JSON, deconstruction, closures, global importing.

Please show successful build output when submitting PRs.

# Subgraphs

**Polygon**: https://thegraph.com/hosted-service/subgraph/thebuidler/gtoken-polygon

**Arbitrum**: https://thegraph.com/hosted-service/subgraph/thebuidler/gtoken-arbitrum

**Mumbai**: https://thegraph.com/hosted-service/subgraph/thebuidler/gtoken-mumbai

# Overview

This subgraph has been built specifically to provide lenders with estimated earnings on their lending positions, and track relevant historical events. It will be extended over time.

# Key Entity Overviews

### Account

EOA or contract address that has interacted with the protocol.

### Vault

Lending vaults - currently only gDAI vault.

### AccountVault

Vault specific stats and interactions for an account.

Please note the following:

- `totalAssetsDeposited` - total assets deposited by the account into the vault
- `totalAssetsWithdrawn` - total assets withdrawn by the account from the vault.

For both, transfers in and out of gDAI are included. The market rate of gDAI is used to calculate the value of the assets.

For example, if an account deposits 100 DAI into the vault at a rate of 1 gDAI / DAI, and then transfers 50 gDAI out of the vault at a rate of 1.5 gDAI / DAI, the `totalAssetsDeposited` will be 100 DAI, and the `totalAssetsWithdrawn` will be 75 (50 \* 1.5) DAI. The withdrawn is an approximation as the rate of gDAI is not known at the time of the transfer (if it was a sale at all, might have just been a transfer to another account).

### Locked Deposit

An object representing a locked deposit (gNFT). The entity is owned by the current holder of the NFT as it can be transferred, though it contains a reference to the original transaction.

### Deposit

Transaction record for a deposit.

### Withdraw

Transaction record for a withdraw.

### Transfer

Transaction record for a transfer of gDAI.
