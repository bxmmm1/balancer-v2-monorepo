// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

// import '@balancer-labs/v2-standalone-utils/contracts/ProtocolFeeSplitter.sol';
import "../munged/standalone-utils/contracts/ProtocolFeeSplitter.sol";

contract ProtocolFeeSplitterHarness is ProtocolFeeSplitter {
    constructor(IProtocolFeesWithdrawer _protocolFeesWithdrawer, address _treasury)
        ProtocolFeeSplitter(_protocolFeesWithdrawer, _treasury)
    {}

    function getBpt(bytes32 poolId) public view returns (address) {
        (address pool, ) = this.getVault().getPool(poolId);
        return pool;
    }

    function getFeeCollectorBptBalance(bytes32 poolId) public view returns (uint256) {
        (address pool, ) = this.getVault().getPool(poolId);
        IProtocolFeesCollector collector = this.getVault().getProtocolFeesCollector();
        return IERC20(pool).balanceOf(address(collector));
    }

    function getProtocolFeesCollectorOnHarness() public view returns(address) {
        IProtocolFeesCollector collector = this.getVault().getProtocolFeesCollector();
        return address(collector);
    }

    function getBptOwner(bytes32 poolId) public view returns (address) {
        (address pool, ) = this.getVault().getPool(poolId);
        return Pool(pool).getOwner();
    }

    function getBeneficiary(bytes32 poolId) public view returns (address) {
        RevenueShareSettings memory s = this.getPoolSettings(poolId);
        return s.beneficiary;
    }

    function getRevenueSharePercentageOverride(bytes32 poolId) public view returns (uint256) {
        RevenueShareSettings memory s = this.getPoolSettings(poolId);
        return s.revenueSharePercentageOverride;
    }

    function getMaxRevenueSharingFeePercentage() public view returns (uint256) {
        return 50e16; // _MAX_REVENUE_SHARING_FEE_PERCENTAGE;
    }

    function toUint96(uint256 u) public view returns (uint96) {
        return uint96(u);
    }

    function getBalance(bytes32 poolId, address addr) public view returns (uint256) {
        return IERC20(getBpt(poolId)).balanceOf(addr);
    }

    function getTotalSupply(bytes32 poolId) public view returns (uint256) {
        return IERC20(getBpt(poolId)).totalSupply();
    }

    function getFeePercentage(bytes32 poolId) public view returns (uint256 feePercentage) {
        uint256 poolFeeOverride = this.getPoolSettings(poolId).revenueSharePercentageOverride;
        feePercentage = poolFeeOverride != 0 ? poolFeeOverride : this.getDefaultRevenueSharingFeePercentage();
    }

    function getActionId(uint32 selector) public view returns (bytes32) {
        return getActionId(bytes4(selector));
    }

    mapping(bytes32 => mapping(address => bool)) public canPerformMapping;

    function _canPerform(bytes32 actionId, address account) internal view override returns (bool) {
        return canPerformMapping[actionId][account];
    }

    function canPerform(bytes32 actionId, address account) public view returns (bool) {
        return _canPerform(actionId, account);
    }
}
