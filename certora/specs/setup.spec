import "../helpers/erc20.spec"

methods{
    setRevenueSharingFeePercentage(bytes32,uint256)
    setDefaultRevenueSharingFeePercentage(uint256)
    setPoolBeneficiary(bytes32, address)
    collectFees(bytes32)
    treasury() envfree
    toPoolAddress(bytes32) returns(address) => NONDET
    getBpt(bytes32) returns(address) envfree
    // getBptOwner(bytes32) returns(address) envfree
    getOwner(bytes32) => PER_CALLEE_CONSTANT 
    getBeneficiary(bytes32) returns(address) envfree
    getRevenueSharePercentageOverride(bytes32) returns(uint256) envfree
    protocolFeesCollector() returns(address) envfree
    defaultRevenueSharingFeePercentage() returns(uint256) envfree
    getMinRevenueSharingFeePercentage() returns(uint256) envfree
    getMaxRevenueSharingFeePercentage() returns(uint256) envfree
    getDelegateOwner() returns(address) envfree
    toUint96(uint256) returns(uint96) envfree
    getBalance(bytes32,address) returns(uint256) envfree
    getFeeCollectorBptBalance(bytes32) returns(uint256) envfree

    withdrawCollectedFees(address[],uint256[],address) => DISPATCHER(true)
}

invariant UniquePools(bytes32 poolId0, bytes32 poolId1)
    poolId0 != poolId1 <=> getBpt(poolId0) != getBpt(poolId1)


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

rule CollectFeesWoBeneficiary() {
    env e;    
    bytes32 poolId;
    
    require getBeneficiary(poolId) == 0;
    uint256 feeCollectorBptBalance = getFeeCollectorBptBalance(poolId);
    address treasuryAddr = treasury();
    uint256 _balance = getBalance(poolId, treasuryAddr);

    collectFees@withrevert(e, poolId);
    bool successful = !lastReverted;

    uint256 balance_ = getBalance(poolId, treasuryAddr);
    assert feeCollectorBptBalance==0 => !successful;
    assert successful => _balance + feeCollectorBptBalance == balance_;
}

rule sanity(method f)
{
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}
