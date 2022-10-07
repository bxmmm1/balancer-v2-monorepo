if [[ "$1" ]]
then
    RULE="--rule $1"
fi

certoraRun certora/harness/ProtocolFeeSplitterHarness.sol \
    certora/helpers/DummyERC20Impl.sol \
    certora/munged/vault/contracts/ProtocolFeesCollector.sol \
    --verify ProtocolFeeSplitterHarness:certora/specs/ProtocolFeeSplitter.spec \
    $RULE \
    --optimistic_loop \
    --send_only \
    --staging eyalf/display-storage-in-calltrace \
    --rule_sanity \
    --packages @balancer-labs=$(pwd)/node_modules/@balancer-labs/ \
    --msg "ProtocolFeeSplitterHarness:setup.spec $1 "
    # --debug
    # --packages_path pkg \
    # --solc solc7.3 \
    # --settings -useBitVectorTheory \
    # certora/munged/vault/contracts/ProtocolFeesCollector.sol \
    # certora/harness/VaultHelpersHarness.sol:VaultHelpers \
    
