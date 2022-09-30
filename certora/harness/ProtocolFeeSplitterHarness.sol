// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

// import '@balancer-labs/v2-standalone-utils/contracts/ProtocolFeeSplitter.sol';
import '../munged/standalone-utils/contracts/ProtocolFeeSplitter.sol';

contract ProtocolFeeSplitterHarness is ProtocolFeeSplitter {
  constructor(IProtocolFeesCollector _protocolFeesCollector, address _treasury)
    ProtocolFeeSplitter(_protocolFeesCollector, _treasury) {}
 

  function getBpt(bytes32 poolId) public returns (address) {
    return VaultHelpers.toPoolAddress(poolId);
  }

  function getFeeCollectorBptBalance(bytes32 poolId) public returns(uint256) {
        return IERC20(VaultHelpers.toPoolAddress(poolId)).balanceOf(address(protocolFeesCollector));
  }

  function getBptOwner(bytes32 poolId) public returns (address) {
    return Pool(VaultHelpers.toPoolAddress(poolId)).getOwner();
  }

  function getBeneficiary(bytes32 poolId) public returns (address) {
    return poolSettings[poolId].beneficiary;
  }

  function getRevenueSharePercentageOverride(bytes32 poolId) public returns (uint256) {
    return poolSettings[poolId].revenueSharePercentageOverride;
  }

  function getDefaultRevenueSharingFeePercentage() public returns(uint256) {
    return defaultRevenueSharingFeePercentage;
  }

  function getMinRevenueSharingFeePercentage() public returns(uint256) {
    return 1e16; //_MIN_REVENUE_SHARING_FEE_PERCENTAGE;
  }

  function getMaxRevenueSharingFeePercentage() public returns(uint256) {
    return 50e16; // _MAX_REVENUE_SHARING_FEE_PERCENTAGE;
  }

  function getDelegateOwner() public returns(address) {
    return 0xBA1BA1ba1BA1bA1bA1Ba1BA1ba1BA1bA1ba1ba1B; // _DELEGATE_OWNER;
  }

  function toUint96(uint256 u) public returns(uint96) {
    return uint96(u);
  }

  function getBalance(bytes32 poolId, address addr) public returns(uint256) {
    return IERC20(getBpt(poolId)).balanceOf(addr);
  }

  function getTotalSupply(bytes32 poolId) public returns(uint256) {
    return IERC20(getBpt(poolId)).totalSupply();
  }

  function getFeePercentage(bytes32 poolId) public returns(uint256 feePercentage) {
    uint256 poolFeeOverride = poolSettings[poolId].revenueSharePercentageOverride;
    feePercentage = poolFeeOverride != 0 ? poolFeeOverride : defaultRevenueSharingFeePercentage;
  }
}
