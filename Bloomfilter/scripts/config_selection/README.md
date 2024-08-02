# Config Selector Scripts

## Usage

This folder takes in a Bloom filter algorithmic configuration, to generate high-performance BitBlender hardware configurations.

Run `python config_sel.py -s 0 -n ${N} -f ${FPR}`, where:
- $FPR is the desired false-positive rate of the resulting Bloom filter.
- $N is the number of elements that will be inserted into the Bloom filter.

This script takes ~5 seconds to suggest 5 BitBlender configurations, which is automatically populated into the sweep-generation scripts in `../codegen_scripts`. See that folder for more info.
