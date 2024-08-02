
from enum import Enum

class ArbiterType(Enum):
    HIERARCHICAL            = 1
    SPLIT_MONOLITHIC        = 2
    SINGLE_MONOLITHIC       = 3

class ShuffleType(Enum):
    SPLIT_MONOLITHIC        = 1
    BIFURCATED              = 2

class DesignType(Enum):
    NORMAL_MULTISTREAM      = 1
    NAIVE_MULTISTREAM       = 2
