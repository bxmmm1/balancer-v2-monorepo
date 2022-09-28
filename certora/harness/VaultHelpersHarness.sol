// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;


contract VaultHelpers {
  mapping(bytes32 => address) pools;
  function toPoolAddress(bytes32 poolId) public returns (address) {
    return pools[poolId];
  }
}
