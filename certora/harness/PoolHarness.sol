// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;
import "../helpers/DummyERC20Impl.sol";

// interface Pool {
//     function getOwner() external returns (address);
// }

contract Pool is DummyERC20Impl {
  address owner;
  function getOwner() public returns (address) {
    return owner;
  }
}
