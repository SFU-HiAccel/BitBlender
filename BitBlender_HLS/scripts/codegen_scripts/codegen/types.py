
from enum import Enum

class ArbiterType(Enum):
    """
    "SEPARATED" refers to behaviour-separation. I.e. splitting it into (1. T-to-S forwarding) and (2. arbitration).
    "PER_HASH" refers to splitting into multiple modules - one per hash.
    "HIER/MONO" refers to the implementation of the arbitration logic - either tree-based, or all-at-once.
    """
    ### This is the best implementation.
    SEPARATED_HIERARB_PER_HASH      = 1
    ### This is the 2nd most naive, monolithic arbiter-per-hash implementation.
    UNSEPARATED_MONOARB_PER_HASH    = 2
    ### This is the most naive, one single arbiter for everything, implementation.
    SINGLE_MONOLITHIC               = 3
    ### This is the module-split (fwd/arb/ratemon), but with NON-TREE arbitration.
    SEPARATED_MONOARB_PER_HASH      = 4
    ### This HANGS, in general. I was testing this for a while but it doesn't make sense in general.
    SEPARATED_HIERARB_PER_HASH_NORATELIM      = 5
    ### This is the 2nd best implementation, with tree-based, separated arbiter, but without multicycle exit checking.
    SEPARATED_HIERARB_PER_HASH_SINGLECYCLE_EXIT_CHECK = 6

class ShuffleType(Enum):
    SPLIT_MONOLITHIC        = 1
    SEPARATED_BUFFER_BASED  = 2
    SEPARATED_FIFO_BASED    = 3

class DesignType(Enum):
    NORMAL_MULTISTREAM      = 1
    NAIVE_MULTISTREAM       = 2
