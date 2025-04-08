# BitBlender Sample Code

This folder contains a sample, auto-generated BitBlender design, configured as follows:

`H-P-S-D-L`, where:
- H is the number of hash functions
- P is the number of bit-vector partitions
- S is the number of parallel query-streams
- B is the arbiter ratelimiting distance (which is equivalent to the unshuffle buffer size)
- L is the length of each bit-vector section, in factors of 2^20.

So in this folder, the code is for a design with 5 hash functions, 9 bit-vector partitions, 8 streams, a ratelimiting distance of 16, where each bit-vector section is 10,485,760 bits long - for a total bit-vector length of 5\*10\*2^20 = 52,428,800 bits.

## Usage

(Runtime estimates here are approximated for a dual-socket, Intel(R) Xeon(R) Silver 4214 CPU @ 2.20GHz - 48 total cores, with 192 GB DDR4 DRAM)

First, run `cd 5-9-8-16-10`.

Next, run `make check TARGET=sw_emu AURORA=disabled`, to run software emulation.

Note that the host-code runs 10 tests of the BitBlender kernel, where the first 3 tests use special input configurations (to test best-case and worst-case performance), and the remaining 7 tests use randomized inputs.
By default, only the 9th test will run verification against a software implementation.
Each test should take less than a minute.

Alteratively, run `make check TARGET=hw_emu AURORA=disablled`, to run hardware emulation. This is not rigorously tested, but it should spend ~30 minutes running one test, and then crash. This is normal.

Finally, run `make check TARGET=hw AURORA=${aurora}`, to run the full hardware build and test, where:
- The `AURORA` flag defines whether or not to enable QSFP-port integration, by utilizing the Aurora IP.

This may take 12+ hours to build.

After building, the host code execution is as follows. Each test will take ~30 seconds to prepare the inputs, and the kernel execution should be very quick (less than a second).

## Folder Structure

Here we discuss the important files. Some files are not explained here.

`5-9-8-16-10/src/multistream_BitBlender.cpp` contains the HLS code for the BitBlender design.

`5-9-8-16-10/src/`, `host_HBM.cpp` and `host_QSFP_aurora.cpp` contains the host code, which prepares inputs and runs verification for the BitBlender design.

`5-9-8-16-10/collect_resource_usages.py` is a python script. It is used after hardware builds to summarize some build statistics such as resource usages, frequency, and the initiation intervals of each module.
