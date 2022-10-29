if [[ "$1" ]]
then
    RULE="--rule $1"
fi

certoraRun certora/harness/ProtocolFeeSplitterHarness.sol \
    certora/helpers/DummyERC20Impl.sol \
    certora/munged/standalone-utils/contracts/ProtocolFeesWithdrawer.sol \
    certora/munged/vault/contracts/ProtocolFeesCollector.sol \
    --verify ProtocolFeeSplitterHarness:certora/specs/ProtocolFeeSplitter.spec \
    $RULE \
    --optimistic_loop \
    --send_only \
    --packages @balancer-labs=$(pwd)/node_modules/@balancer-labs/ \
    # --rule_sanity
    # --msg "ProtocolFeeSplitterHarness:setup.spec $1 "
    # --packages_path pkg \
    # --solc solc7.3 \
    # --settings -useBitVectorTheory \
    # certora/munged/standalone-utils/contracts/ProtocolFeesWithdrawer.sol \
    # certora/munged/vault/contracts/ProtocolFeesCollector.sol \
    # certora/harness/VaultHelpersHarness.sol:VaultHelpers \
    
