# BitBlender

BitBlender is a highly configurable, highly scalable Bloom filter accelerator framework for FPGAs. It is implemented in HLS. It achieves high performance by leveraging dynamic (data-dependent) scheduling. For more information, please see our paper published in FPL 2024, titled "BitBlender: Scalable Bloom Filter Acceleration on FPGAs with Dynamic Scheduling".

See `BitBlender-Multistream-Architecture.png` for an architecture diagram.

## System Requirements

BitBlender has been tested extensively on an Alveo U280 FPGA, built using [TAPA](https://github.com/UCLA-VAST/tapa), version 0.0.20221113.1.
See [here](https://tapa.readthedocs.io/en/release/installation.html) for installation instructions.

TAPA relies on AMD/Xilinx Vitis and Vivado, so you will also need a valid version of these tools. BitBlender has been tested to work on v2021.2. It can also work on v2022.2, but it achieves worse performance. Please contact the author if you wish to try this.

To use the automated DSE tool, you will need scikit-learn (preferably version 1.4.2), pandas, and numpy. It most seamlessly integrates with the SLURM task-manager, but it is possible to work around this requirement.

## Usage

To see a sample BitBlender design, look in `Bloomfilter/BitBlender_samplecode`.

In order to generate your own BitBlender designs, see the `Bloomfilter/scripts` directory.

## Known Issues

*** BitBlender designs synthesized using Vitis v2023.2 and v2024.1 do not schedule properly, and deadlock. ***

