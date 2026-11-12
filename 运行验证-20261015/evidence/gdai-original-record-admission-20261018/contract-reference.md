> ## Documentation Index
> Fetch the complete documentation index at: https://docs.gains.trade/llms.txt
> Use this file to discover all available pages before exploring further.

# GToken

*GToken vault contract, direct counterparty to trades happening on Gains*

## gnsToken

```solidity theme={null}
address gnsToken
```

## lockedDepositNft

```solidity theme={null}
contract IGTokenLockedDepositNft lockedDepositNft
```

## manager

```solidity theme={null}
address manager
```

## admin

```solidity theme={null}
address admin
```

## pnlHandler

```solidity theme={null}
address pnlHandler
```

## openTradesPnlFeed

```solidity theme={null}
contract IGTokenOpenPnlFeed openTradesPnlFeed
```

## gnsPriceProvider

```solidity theme={null}
struct IGToken.GnsPriceProvider gnsPriceProvider
```

## PRECISION\_18

```solidity theme={null}
uint256 PRECISION_18
```

## PRECISION\_10

```solidity theme={null}
uint256 PRECISION_10
```

## MIN\_DAILY\_ACC\_PNL\_DELTA

```solidity theme={null}
uint256 MIN_DAILY_ACC_PNL_DELTA
```

## MAX\_SUPPLY\_INCREASE\_DAILY\_P

```solidity theme={null}
uint256 MAX_SUPPLY_INCREASE_DAILY_P
```

## MAX\_LOSSES\_BURN\_P

```solidity theme={null}
uint256 MAX_LOSSES_BURN_P
```

## MAX\_GNS\_SUPPLY\_MINT\_DAILY\_P

```solidity theme={null}
uint256 MAX_GNS_SUPPLY_MINT_DAILY_P
```

## MAX\_DISCOUNT\_P

```solidity theme={null}
uint256 MAX_DISCOUNT_P
```

## MIN\_LOCK\_DURATION

```solidity theme={null}
uint256 MIN_LOCK_DURATION
```

## MAX\_LOCK\_DURATION

```solidity theme={null}
uint256 MAX_LOCK_DURATION
```

## WITHDRAW\_EPOCHS\_LOCKS

```solidity theme={null}
uint256[] WITHDRAW_EPOCHS_LOCKS
```

## maxAccOpenPnlDelta

```solidity theme={null}
uint256 maxAccOpenPnlDelta
```

## maxDailyAccPnlDelta

```solidity theme={null}
uint256 maxDailyAccPnlDelta
```

## withdrawLockThresholdsP

```solidity theme={null}
uint256[2] withdrawLockThresholdsP
```

## maxSupplyIncreaseDailyP

```solidity theme={null}
uint256 maxSupplyIncreaseDailyP
```

## lossesBurnP

```solidity theme={null}
uint256 lossesBurnP
```

## maxGnsSupplyMintDailyP

```solidity theme={null}
uint256 maxGnsSupplyMintDailyP
```

## maxDiscountP

```solidity theme={null}
uint256 maxDiscountP
```

## maxDiscountThresholdP

```solidity theme={null}
uint256 maxDiscountThresholdP
```

## shareToAssetsPrice

```solidity theme={null}
uint256 shareToAssetsPrice
```

## accPnlPerTokenUsed

```solidity theme={null}
int256 accPnlPerTokenUsed
```

## accPnlPerToken

```solidity theme={null}
int256 accPnlPerToken
```

## accRewardsPerToken

```solidity theme={null}
uint256 accRewardsPerToken
```

## dailyAccPnlDelta

```solidity theme={null}
int256 dailyAccPnlDelta
```

## lastDailyAccPnlDeltaReset

```solidity theme={null}
uint256 lastDailyAccPnlDeltaReset
```

## currentEpoch

```solidity theme={null}
uint256 currentEpoch
```

## currentEpochStart

```solidity theme={null}
uint256 currentEpochStart
```

## currentEpochPositiveOpenPnl

```solidity theme={null}
uint256 currentEpochPositiveOpenPnl
```

## currentMaxSupply

```solidity theme={null}
uint256 currentMaxSupply
```

## lastMaxSupplyUpdate

```solidity theme={null}
uint256 lastMaxSupplyUpdate
```

## withdrawRequests

```solidity theme={null}
mapping(address => mapping(uint256 => uint256)) withdrawRequests
```

## lockedDepositsCount

```solidity theme={null}
uint256 lockedDepositsCount
```

## lockedDeposits

```solidity theme={null}
mapping(uint256 => struct IGToken.LockedDeposit) lockedDeposits
```

## assetsToDeplete

```solidity theme={null}
uint256 assetsToDeplete
```

## dailyMintedGns

```solidity theme={null}
uint256 dailyMintedGns
```

## lastDailyMintedGnsReset

```solidity theme={null}
uint256 lastDailyMintedGnsReset
```

## totalDeposited

```solidity theme={null}
uint256 totalDeposited
```

## totalClosedPnl

```solidity theme={null}
int256 totalClosedPnl
```

## totalRewards

```solidity theme={null}
uint256 totalRewards
```

## totalLiability

```solidity theme={null}
int256 totalLiability
```

## totalLockedDiscounts

```solidity theme={null}
uint256 totalLockedDiscounts
```

## totalDiscounts

```solidity theme={null}
uint256 totalDiscounts
```

## totalDepleted

```solidity theme={null}
uint256 totalDepleted
```

## totalDepletedGns

```solidity theme={null}
uint256 totalDepletedGns
```

## totalRefilled

```solidity theme={null}
uint256 totalRefilled
```

## totalRefilledGns

```solidity theme={null}
uint256 totalRefilledGns
```

## accBlockWeightedMarketCap

```solidity theme={null}
uint256 accBlockWeightedMarketCap
```

## accBlockWeightedMarketCapLastStored

```solidity theme={null}
uint256 accBlockWeightedMarketCapLastStored
```

## collateralConfig

```solidity theme={null}
struct CollateralUtils.CollateralConfig collateralConfig
```

## initialize

```solidity theme={null}
function initialize(struct IGToken.Meta _meta, struct IGToken.ContractAddresses _contractAddresses, uint256 _MIN_LOCK_DURATION, uint256 _maxAccOpenPnlDelta, uint256 _maxDailyAccPnlDelta, uint256[2] _withdrawLockThresholdsP, uint256 _maxSupplyIncreaseDailyP, uint256 _lossesBurnP, uint256 _maxGnsSupplyMintDailyP, uint256 _maxDiscountP, uint256 _maxDiscountThresholdP) external
```

## initializeV3

```solidity theme={null}
function initializeV3() external
```

## onlyManager

```solidity theme={null}
modifier onlyManager()
```

## checks

```solidity theme={null}
modifier checks(uint256 assetsOrShares)
```

## validDiscount

```solidity theme={null}
modifier validDiscount(uint256 lockDuration)
```

## transferOwnership

```solidity theme={null}
function transferOwnership(address newOwner) public
```

*Transfers ownership of the contract to a new account (`newOwner`). Can only be called by the current owner.*

## updateManager

```solidity theme={null}
function updateManager(address newValue) external
```

## updateAdmin

```solidity theme={null}
function updateAdmin(address newValue) external
```

## updatePnlHandler

```solidity theme={null}
function updatePnlHandler(address newValue) external
```

## updateGnsPriceProvider

```solidity theme={null}
function updateGnsPriceProvider(struct IGToken.GnsPriceProvider newValue) external
```

## updateOpenTradesPnlFeed

```solidity theme={null}
function updateOpenTradesPnlFeed(address newValue) external
```

## updateDelegatee

```solidity theme={null}
function updateDelegatee(address _delegatee) external
```

## updateMaxAccOpenPnlDelta

```solidity theme={null}
function updateMaxAccOpenPnlDelta(uint256 newValue) external
```

## updateMaxDailyAccPnlDelta

```solidity theme={null}
function updateMaxDailyAccPnlDelta(uint256 newValue) external
```

## updateWithdrawLockThresholdsP

```solidity theme={null}
function updateWithdrawLockThresholdsP(uint256[2] newValue) external
```

## updateMaxSupplyIncreaseDailyP

```solidity theme={null}
function updateMaxSupplyIncreaseDailyP(uint256 newValue) external
```

## updateLossesBurnP

```solidity theme={null}
function updateLossesBurnP(uint256 newValue) external
```

## updateMaxGnsSupplyMintDailyP

```solidity theme={null}
function updateMaxGnsSupplyMintDailyP(uint256 newValue) external
```

## updateMaxDiscountP

```solidity theme={null}
function updateMaxDiscountP(uint256 newValue) external
```

## updateMaxDiscountThresholdP

```solidity theme={null}
function updateMaxDiscountThresholdP(uint256 newValue) external
```

## maxAccPnlPerToken

```solidity theme={null}
function maxAccPnlPerToken() public view returns (uint256)
```

## collateralizationP

```solidity theme={null}
function collateralizationP() public view returns (uint256)
```

## gnsTokenToAssetsPrice

```solidity theme={null}
function gnsTokenToAssetsPrice() public view returns (uint256 price)
```

## withdrawEpochsTimelock

```solidity theme={null}
function withdrawEpochsTimelock() public view returns (uint256)
```

## lockDiscountP

```solidity theme={null}
function lockDiscountP(uint256 collatP, uint256 lockDuration) public view returns (uint256)
```

## totalSharesBeingWithdrawn

```solidity theme={null}
function totalSharesBeingWithdrawn(address owner) public view returns (uint256 shares)
```

## tryUpdateCurrentMaxSupply

```solidity theme={null}
function tryUpdateCurrentMaxSupply() public
```

## tryResetDailyAccPnlDelta

```solidity theme={null}
function tryResetDailyAccPnlDelta() public
```

## tryNewOpenPnlRequestOrEpoch

```solidity theme={null}
function tryNewOpenPnlRequestOrEpoch() public
```

## transfer

```solidity theme={null}
function transfer(address to, uint256 amount) public returns (bool)
```

## transferFrom

```solidity theme={null}
function transferFrom(address from, address to, uint256 amount) public returns (bool)
```

## decimals

```solidity theme={null}
function decimals() public view returns (uint8)
```

## \_convertToShares

```solidity theme={null}
function _convertToShares(uint256 assets, enum MathUpgradeable.Rounding rounding) internal view returns (uint256 shares)
```

*Internal conversion function (from assets to shares) with support for rounding direction.*

## \_convertToAssets

```solidity theme={null}
function _convertToAssets(uint256 shares, enum MathUpgradeable.Rounding rounding) internal view returns (uint256 assets)
```

*Internal conversion function (from shares to assets) with support for rounding direction.*

## maxMint

```solidity theme={null}
function maxMint(address) public view returns (uint256)
```

*See \{IERC4626-maxMint}.*

## maxDeposit

```solidity theme={null}
function maxDeposit(address owner) public view returns (uint256)
```

## maxRedeem

```solidity theme={null}
function maxRedeem(address owner) public view returns (uint256)
```

*See \{IERC4626-maxRedeem}.*

## maxWithdraw

```solidity theme={null}
function maxWithdraw(address owner) public view returns (uint256)
```

*See \{IERC4626-maxWithdraw}.*

## deposit

```solidity theme={null}
function deposit(uint256 assets, address receiver) public returns (uint256)
```

*See \{IERC4626-deposit}.*

## mint

```solidity theme={null}
function mint(uint256 shares, address receiver) public returns (uint256)
```

\_See \{IERC4626-mint}.

As opposed to \{deposit}, minting is allowed even if the vault is in a state where the price of a share is zero. In this case, the shares will be minted without requiring any assets to be deposited.\_

## withdraw

```solidity theme={null}
function withdraw(uint256 assets, address receiver, address owner) public returns (uint256)
```

*See \{IERC4626-withdraw}.*

## redeem

```solidity theme={null}
function redeem(uint256 shares, address receiver, address owner) public returns (uint256)
```

*See \{IERC4626-redeem}.*

## makeWithdrawRequest

```solidity theme={null}
function makeWithdrawRequest(uint256 shares, address owner) external
```

## cancelWithdrawRequest

```solidity theme={null}
function cancelWithdrawRequest(uint256 shares, address owner, uint256 unlockEpoch) external
```

## depositWithDiscountAndLock

```solidity theme={null}
function depositWithDiscountAndLock(uint256 assets, uint256 lockDuration, address receiver) external returns (uint256)
```

## mintWithDiscountAndLock

```solidity theme={null}
function mintWithDiscountAndLock(uint256 shares, uint256 lockDuration, address receiver) external returns (uint256)
```

## unlockDeposit

```solidity theme={null}
function unlockDeposit(uint256 depositId, address receiver) external
```

## distributeReward

```solidity theme={null}
function distributeReward(uint256 assets) external
```

## sendAssets

```solidity theme={null}
function sendAssets(uint256 assets, address receiver) external
```

## receiveAssets

```solidity theme={null}
function receiveAssets(uint256 assets, address user) external
```

## deplete

```solidity theme={null}
function deplete(uint256 assets) external
```

## refill

```solidity theme={null}
function refill(uint256 assets) external
```

## updateAccPnlPerTokenUsed

```solidity theme={null}
function updateAccPnlPerTokenUsed(uint256 prevPositiveOpenPnl, uint256 newPositiveOpenPnl) external returns (uint256)
```

## getLockedDeposit

```solidity theme={null}
function getLockedDeposit(uint256 depositId) external view returns (struct IGToken.LockedDeposit)
```

## tvl

```solidity theme={null}
function tvl() public view returns (uint256)
```

## availableAssets

```solidity theme={null}
function availableAssets() public view returns (uint256)
```

## marketCap

```solidity theme={null}
function marketCap() public view returns (uint256)
```


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.