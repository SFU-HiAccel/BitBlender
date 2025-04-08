# Code Generation Scripts

## Usage

First, edit `codegen/gen_Makefile.py`. Line 39 contains a definition for `COMMON_REPO`: change this to the top directory of where you cloned this Git repository.

Next, there are two ways to use this directory: generating a single design, or generating several configurations at once (using the SLURM workload manager).

***This folder does NOT internally implement the automation flow.***

## Single-Design Generation

You can generate a BitBlender design using `python3 generate_BVSharing_design.py -htsb ${H}-${P}-${S}-${D}-${L} -dt bitblender -vv 2022.1`, where:
- The `-htsb` flag defines the BitBlender configuration used:
	- H is the number of hash functions
	- P is the number of bit-vector partitions
	- S is the number of parallel query-streams
	- D is the arbiter ratelimiting distance (which is equivalent to the unshuffle buffer size)
	- L is the length of each bit-vector section, in factors of 2^20.
- The `-dt` flag defines the type of design to generate. This should be specified as "bitblender", but it can also specify "naive", for naively-multistreamed design.
- The `-vv` flag defines for which version of Vitis/Vivado to optimize. This has been tested extensively with v2021.2 and v2022.1.

This will generate a folder structure similar to the folder in `BitBlender_samplecode`. See that folder for next steps.

## Generating Several Configurations

To run a manual multi-design sweep, you may modify the file `designs_to_generate.py`.

This file defines a list of BitBlender configurations, of the form `${H}-${P}-${S}-${D}-${L}`, where:
- H is the number of hash functions
- P is the number of bit-vector partitions
- S is the number of parallel query-streams
- D is the arbiter ratelimiting distance (which is equivalent to the unshuffle buffer size)
- L is the length of each bit-vector section, in factors of 2^20.

To begin the hardware place & route, and bitstream generation of all configs, run `sbatch run_build_sweep.sh`.
To test the generated bitstreams on FPGA, run `sbatch run_fpga_tests.sh`.

