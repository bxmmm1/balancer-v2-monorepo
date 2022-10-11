import "../helpers/erc20.spec"

methods{
    setRevenueSharingFeePercentage(bytes32,uint256)
    setDefaultRevenueSharingFeePercentage(uint256)
    setPoolBeneficiary(bytes32, address)
    collectFees(bytes32)
    treasury() returns(address) envfree    
    toPoolAddress(bytes32) returns(address) => DISPATCHER(true)
    getBpt(bytes32) returns(address) envfree
    getBptOwner(bytes32) returns(address) envfree
    getOwner() returns(address) => PER_CALLEE_CONSTANT 
    getBeneficiary(bytes32) returns(address) envfree
    getRevenueSharePercentageOverride(bytes32) returns(uint256) envfree
    protocolFeesCollector() returns(address) envfree
    defaultRevenueSharingFeePercentage() returns(uint256) envfree
    getMinRevenueSharingFeePercentage() returns(uint256) envfree
    getMaxRevenueSharingFeePercentage() returns(uint256) envfree
    canPerform(bytes32 actionId, address account) returns (bool)
    getDelegateOwner() returns(address) envfree
    toUint96(uint256) returns(uint96) envfree
    getBalance(bytes32,address) returns(uint256) envfree
    getTotalSupply(bytes32) returns(uint256) envfree
    getFeeCollectorBptBalance(bytes32) returns(uint256) envfree
    getFeePercentage(bytes32) returns(uint256) envfree
    getActionId(uint32) returns(bytes32) envfree

    withdrawCollectedFees(address[],uint256[],address) => DISPATCHER(true)
}

/// @title: `RevenueSharingFeePercentageInRange`
/// @notice: `RevenueSharingFeePercentageInRange(bytes32 poolId)` checks `revenueSharePercentageOverride` of the given `poolId` is always between `_MIN_REVENUE_SHARING_FEE_PERCENTAGE` and `_MAX_REVENUE_SHARING_FEE_PERCENTAGE`.
/// @notice: SUCCESS
invariant RevenueSharingFeePercentageInRange(bytes32 poolId)
    getRevenueSharePercentageOverride(poolId) == 0 || 
    (getRevenueSharePercentageOverride(poolId) >= getMinRevenueSharingFeePercentage() &&
    getRevenueSharePercentageOverride(poolId) <= getMaxRevenueSharingFeePercentage())

/// @title: `DefaultRevenueSharingFeePercentageInRange`
/// @notice: `DefaultRevenueSharingFeePercentageInRange()` checks `DefaultRevenueSharingFeePercentageInRange` is always between `0` and `_MAX_REVENUE_SHARING_FEE_PERCENTAGE`. 
/// @notice: SUCCESS
invariant DefaultRevenueSharingFeePercentageInRange()
    defaultRevenueSharingFeePercentage() >= 0 && 
    defaultRevenueSharingFeePercentage() <= getMaxRevenueSharingFeePercentage()

/// @title: `SetRevenueSharingFeePercentageCorrectly`
/// @notice: `setRevenueSharingFeePercentage(bytes32 poolId, uint256 newSwapFeePercentage)` reverts if the caller is not authenticated or `newSwapFeePercentage` is out-of-range,  otherwise it set `revenueSharePercentageOverride` for the given `poolId`. 
/// @notice: SUCCESS
rule SetRevenueSharingFeePercentageCorrectly() {
    env e;
    bytes32 poolId;
    uint256 newSwapFeePercentage; 

    setRevenueSharingFeePercentage@withrevert(e, poolId, newSwapFeePercentage);
    bool successful = !lastReverted;
  
    assert canPerform(e, getActionId(setRevenueSharingFeePercentage(bytes32,uint256).selector), e.msg.sender)==false => !successful;    
    assert(successful => toUint96(newSwapFeePercentage)==getRevenueSharePercentageOverride(poolId));
}

/// @title: `SetDefaultRevenueSharingFeePercentageCorrectly`
/// @notice: `setDefaultRevenueSharingFeePercentage(uint256 feePercentage)` revers if the caller is not authenticated or input is out-of-range. Otherwise it sets `defaultRevenueSharingFeePercentage`.
/// @notice: SUCCESS
rule SetDefaultRevenueSharingFeePercentageCorrectly() {
    env e;
    uint256 defaultSwapFeePercentage; 

    setDefaultRevenueSharingFeePercentage@withrevert(e, defaultSwapFeePercentage);
    bool successful = !lastReverted;

    assert canPerform(e, getActionId(setDefaultRevenueSharingFeePercentage(uint256).selector), e.msg.sender)==false => !successful;    
    assert(successful => toUint96(defaultSwapFeePercentage)==defaultRevenueSharingFeePercentage());
}

/// @title: `SetPoolBeneficiaryCorrectly`
/// @notice: `setPoolBeneficiary(bytes32 poolId, address newBeneficiary)` reverts if the `msg.sender` is not the pool owner for the specified `poolId`, otherwise it sets `beneficiary` for the `poolId`. 
/// @notice: SUCCESS
rule SetPoolBeneficiaryCorrectly() {
    env e;
    bytes32 poolId;
    address newBeneficiary;

    uint256 newSwapFeePercentage; 
    setPoolBeneficiary@withrevert(e, poolId, newBeneficiary);
    bool successful = !lastReverted;

    assert(e.msg.sender!=getBptOwner(poolId) => !successful);
    assert(successful => newBeneficiary==getBeneficiary(poolId));
}

function setup(bytes32 poolId, address treasury, address beneficiary) {
    require treasury != beneficiary;
    require treasury != protocolFeesCollector();
    require beneficiary != protocolFeesCollector();
    requireInvariant RevenueSharingFeePercentageInRange(poolId); 
    requireInvariant DefaultRevenueSharingFeePercentageInRange(); 
}

/// @title: `CollectFeesRevertCondition`
/// @notice: `collectFees(bytes32 poolId)` reverts when there are no fees to be collected.
/// @notice: SUCCESS
rule CollectFeesRevertCondition() {
    env e;    
    bytes32 poolId;
                
    uint256 feeCollectorBptBalance = getFeeCollectorBptBalance(poolId);
    address treasuryAddr = treasury();
    address beneficiaryAddr = getBeneficiary(poolId);

    setup(poolId, treasuryAddr, beneficiaryAddr);

    collectFees@withrevert(e, poolId);
    bool successful = !lastReverted;

    assert feeCollectorBptBalance ==0 => !successful;
}


/// @title: `CollectFeesIntegrity`
/// @notice: `collectFees(bytes32 poolId)` splits `feeCollectorBptBalance` between the `beneficiary` of the pool and the `treasury`. If `beneficiary` is not set, all fees go to `treasury`. Collecting fees does not change the total supply of the pool token.
/// @notice: SUCCESS
rule CollectFeesIntegrity() {
    env e;    
    bytes32 poolId;
                
    uint256 feeCollectorBptBalance = getFeeCollectorBptBalance(poolId);
    uint256 feePercentage = getFeePercentage(poolId);
    address treasuryAddr = treasury();
    address beneficiaryAddr = getBeneficiary(poolId);
    uint256 _treasuryBalance = getBalance(poolId, treasuryAddr);
    uint256 _beneficiaryBalance = getBalance(poolId, beneficiaryAddr);
    uint256 _totalSupply = getTotalSupply(poolId);

    setup(poolId, treasuryAddr, beneficiaryAddr);

    collectFees(e, poolId);

    uint256 treasuryBalance_ = getBalance(poolId, treasuryAddr);
    uint256 beneficiaryBalance_ = getBalance(poolId, beneficiaryAddr);
    uint256 totalSupply_ = getTotalSupply(poolId);
    uint256 feeCollectorBptBalance_ = getFeeCollectorBptBalance(poolId);

    // In case of no beneficiary for a pool and no fee percentage defined, everything should go to treasury
    assert getBeneficiary(poolId) == 0 => _beneficiaryBalance == beneficiaryBalance_ && treasuryBalance_ == _treasuryBalance + feeCollectorBptBalance;    
    assert feePercentage == 0 => beneficiaryBalance_ == _beneficiaryBalance && treasuryBalance_ == _treasuryBalance + feeCollectorBptBalance;
    // If fee percentage, beneficiary and treasury are defined and fee collector has at least 1 token, both treasury and beneficiary should get some tokens
    assert feePercentage > getMinRevenueSharingFeePercentage() && feePercentage <= getMaxRevenueSharingFeePercentage() && getBeneficiary(poolId) != 0 && feeCollectorBptBalance > 1000000000000000000 => beneficiaryBalance_ > _beneficiaryBalance && treasuryBalance_ > _treasuryBalance;
    assert feeCollectorBptBalance == (treasuryBalance_ - _treasuryBalance) + (beneficiaryBalance_ - _beneficiaryBalance);
    assert totalSupply_ == _totalSupply;
}

/// @title: `ZeroFeeCollectorBptBalanceAfterCollectFee`
/// @notice: `collectFees(bytes32 poolId)` is called successfully, there are be no fees balance remaining.
/// @notice: SUCCESS
rule ZeroFeeCollectorBptBalanceAfterCollectFee() {
    env e;    
    bytes32 poolId;

    setup(poolId, treasury(), getBeneficiary(poolId));
    collectFees(e, poolId);
    
    uint256 feeCollectorBptBalance = getFeeCollectorBptBalance(poolId);
    assert feeCollectorBptBalance == 0;
}

/// @title: `FeeCollectorBptBalanceShouldNotChange`
/// @notice: No functions other than `collectFees(bytes32 poolId)` change the fees balance.
/// @notice: SUCCESS
rule FeeCollectorBptBalanceShouldNotChange(method f) filtered { f -> 
    f.selector !=  collectFees(bytes32).selector
} {
    env e;    
    calldataarg args;
    bytes32 poolId;
    uint256 _feeCollectorBptBalance = getFeeCollectorBptBalance(poolId);
    f(e, args);
    uint256 feeCollectorBptBalance_ = getFeeCollectorBptBalance(poolId);
    assert _feeCollectorBptBalance == feeCollectorBptBalance_;
}