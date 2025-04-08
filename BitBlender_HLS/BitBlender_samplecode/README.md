# BitBlender Sample Code

This folder contains a sample, auto-generated BitBlender design, configured as follows:

`H-P-S-B-L`, where:
    - H is the number of hash functions
    - P is the number of bit-vector partitions
    - S is the number of parallel query-streams
    - B is the arbiter ratelimiting distance (which is equivalent to the unshuffle buffer size)
    - L is the length of each bit-vector section, in factors of 2^20.

So in this folder, the code is for a design with 5 hash functions, 8 bit-vector partitions, 4 streams, a ratelimiting distance of 16, where each bit-vector section is 8,388,608 bits long - for a total bit-vector length of 5\*2^20 = 41,943,040 bits.

## Usage

Timing estimates here are approximated for a dual-socket, Intel(R) Xeon(R) Silver 4214 CPU @ 2.20GHz - 48 total cores, with 192 GB DDR4 DRAM.

First, run `cd 5-8-4-16-8`. Note that the host-code runs 10 tests of the BitBlender kernel, where the first 3 tests use special input configurations (to test best-case and worst-case performance), and the remaining 7 tests use randomized inputs. Additionally, by default, only the 4th test will run verification against a software implementation.

Next, run `make check TARGET=sw_emu`, to run software emulation. This should run 10 tests, where each test takes ~3 seconds.

Alteratively, run `make check TARGET=hw_emu`, to run hardware emulation. This is not rigorously tested, but it should spend ~30 minutes running one test, and then crash. This is normal.

Finally, run `make check TARGET=hw`, to run the full hardware build and test. This may take 12+ hours to build. Each test will take ~30 seconds to prepare the inputs, and the verification adds approximately a minute of runtime.

## Folder Structure

Here we discuss the important files. Self-explanatory files are not listed.

`5-8-4-16-8/src/multistream_MurmurHash3.cpp` contains the HLS code for the BitBlender design.

`5-8-4-16-8/src/host.cpp` contains the host code, which prepares inputs and runs verification for the BitBlender design.

`5-8-4-16-8/collect_resource_usages.py` is a python script, used after hardware builds, to summarize some build statistics, such as resource usages, frequency, and the initiation intervals of each module.
