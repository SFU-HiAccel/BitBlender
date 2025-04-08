# Config Selector Scripts

## Usage

This folder takes in a Bloom filter algorithmic configuration, to generate high-performance BitBlender hardware configurations.

Run `python config_sel.py -s 0 -n ${N} -f ${FPR} -a ${aurora} -dt bitblender -vv 2022.1`, where:
- `-n` defines the desired number of insertions
- `-f` defines the desired false-positive rate
- `-a` defines whether or not to enable QSFP integration, with the aurora IP
- `-dt` defines the type of design to generate. This should be specified as "bitblender", but it can also specify "naive", for naively-multistreamed design.
- `-vv` defines for which version of Vitis/Vivado to optimize. This has been tested extensively with v2021.2 and v2022.1.

This script takes ~20 seconds to suggest 5 BitBlender configurations.
These configurations are automatically populated into the sweep-generation scripts in `../codegen_scripts/designs_to_generate.py`. See that folder for more info.
