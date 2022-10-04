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
    getDelegateOwner() returns(address) envfree
    toUint96(uint256) returns(uint96) envfree
    getBalance(bytes32,address) returns(uint256) envfree
    getTotalSupply(bytes32) returns(uint256) envfree
    getFeeCollectorBptBalance(bytes32) returns(uint256) envfree
    getFeePercentage(bytes32) returns(uint256) envfree

    withdrawCollectedFees(address[],uint256[],address) => DISPATCHER(true)
}

// I think that we don't need to test for this, as this is not our responsibility
// This is part of the Balancer's existing codebase
// invariant UniquePools(bytes32 poolId0, bytes32 poolId1)
//     poolId0 != poolId1 <=> getBpt(poolId0) != getBpt(poolId1)

rule SetRevenueSharingFeePercentageCorrectly() {
    env e;
    bytes32 poolId;
    uint256 newSwapFeePercentage; 
    setRevenueSharingFeePercentage@withrevert(e, poolId, newSwapFeePercentage);
    bool successful = !lastReverted;

    assert(newSwapFeePercentage<getMinRevenueSharingFeePercentage() => !successful);
    assert(newSwapFeePercentage>getMaxRevenueSharingFeePercentage() => !successful);
    assert(successful => toUint96(newSwapFeePercentage)==getRevenueSharePercentageOverride(poolId));
}

rule SetDefaultRevenueSharingFeePercentageCorrectly() {
    env e;
    uint256 newSwapFeePercentage; 
    setDefaultRevenueSharingFeePercentage@withrevert(e, newSwapFeePercentage);
    bool successful = !lastReverted;

    // assert(newSwapFeePercentage<getMinRevenueSharingFeePercentage() => !successful);
    assert(newSwapFeePercentage>getMaxRevenueSharingFeePercentage() => !successful);
    assert(successful => toUint96(newSwapFeePercentage)==defaultRevenueSharingFeePercentage());
}

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

rule CollectFeesTotal() {
    env e;    
    bytes32 poolId;
                
    uint256 feeCollectorBptBalance = getFeeCollectorBptBalance(poolId);
    uint256 feePercentage = getFeePercentage(poolId);
    address treasuryAddr = treasury();
    address beneficiaryAddr = getBeneficiary(poolId);
    uint256 _treasuryBalance = getBalance(poolId, treasuryAddr);
    uint256 _beneficiaryBalance = getBalance(poolId, beneficiaryAddr);
    uint256 _totalSupply = getTotalSupply(poolId);

    require treasuryAddr != beneficiaryAddr;
    require treasuryAddr != protocolFeesCollector();
    require beneficiaryAddr != protocolFeesCollector();

    collectFees@withrevert(e, poolId);
    bool successful = !lastReverted;

    uint256 treasuryBalance_ = getBalance(poolId, treasuryAddr);
    uint256 beneficiaryBalance_ = getBalance(poolId, beneficiaryAddr);
    uint256 totalSupply_ = getTotalSupply(poolId);
    uint256 feeCollectorBptBalance_ = getFeeCollectorBptBalance(poolId);

    assert feeCollectorBptBalance ==0 => !successful;
    if (successful) {
        // In case of no beneficiary for a pool and no fee percentage defined, everything should go to treasury
        assert getBeneficiary(poolId) == 0 => _beneficiaryBalance == beneficiaryBalance_ && treasuryBalance_ == _treasuryBalance + feeCollectorBptBalance;    
        assert feePercentage == 0 => beneficiaryBalance_ == _beneficiaryBalance && treasuryBalance_ == _treasuryBalance + feeCollectorBptBalance;
        // If fee percentage, beneficiary and treasury are defined and fee collector has at least 1 token, both treasury and beneficiary should get some tokens
        assert feePercentage > getMinRevenueSharingFeePercentage() && feePercentage <= getMaxRevenueSharingFeePercentage() && getBeneficiary(poolId) != 0 && feeCollectorBptBalance > 1000000000000000000 => beneficiaryBalance_ > _beneficiaryBalance && treasuryBalance_ > _treasuryBalance;
        assert feeCollectorBptBalance == (treasuryBalance_ - _treasuryBalance) + (beneficiaryBalance_ - _beneficiaryBalance);
        assert totalSupply_ == _totalSupply;
    } else 
        assert true;
}
