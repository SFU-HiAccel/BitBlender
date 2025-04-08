# Code Generation Scripts

## Usage

First, edit `codegen/gen_Makefile.py`. Line 48 contains a definition for `COMMON_REPO`: change this to the top directory of where you cloned this Git repository.

Next, there are two ways to use this directory: generating a single design, or generating several configurations at once (using the SLURM workload manager).

## Single-Design Generation

You can generate a BitBlender design using `python3 generate_BVSharing_design.py -htsb ${H}-${P}-${S}-${B}-${L}`, where:
    - H is the number of hash functions
    - P is the number of bit-vector partitions
    - S is the number of parallel query-streams
    - B is the arbiter ratelimiting distance (which is equivalent to the unshuffle buffer size)
    - L is the length of each bit-vector section, in factors of 2^20.

This will generate a folder structure similar to the one in `BitBlender_samplecode`. See that folder for next steps.

## Generating Several Configurations

To run a multi-design sweep, you need to modify the file `designs_to_generate.py`.

This file defines a list of BitBlender configurations, of the form `${H}-${P}-${S}-${B}-${L}`, where:
    - H is the number of hash functions
    - P is the number of bit-vector partitions
    - S is the number of parallel query-streams
    - B is the arbiter ratelimiting distance (which is equivalent to the unshuffle buffer size)
    - L is the length of each bit-vector section, in factors of 2^20.

To begin the hardware place & route, and bitstream generation of all configs, run `sbatch run_build_sweep.sh`.
To test the generated bitstreams on FPGA, run `sbatch run_fpga_tests.sh`.

