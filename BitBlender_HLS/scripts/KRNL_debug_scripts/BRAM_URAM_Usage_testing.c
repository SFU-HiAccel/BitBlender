#include <stdio.h>

//#define NUM_HASH                        (3)
//#define BV_NUM_PARTITIONS               (10)
//#define BV_DESIRED_LENGTH_PER_SECTION   (25)
#define BV_DESIRED_LENGTH ((1024*1024*BV_DESIRED_LENGTH_PER_SECTION)*NUM_HASH)

#define CEIL_DIVISION(X, Y)     ( (X-1)/Y + 1 )
#define ROUND_DIVISION(X, Y)    ( ( (X) + ((Y) / 2)) / (Y) )
#define BV_BRAM_PACKED_BITWIDTH (32)
#define BV_URAM_PACKED_BITWIDTH (64)

//// Method #1 - The ORIGINAL implementation, which is sub-optimal.
// #define BV_NUM_BRAM_PARTITIONS  CEIL_DIVISION(BV_NUM_PARTITIONS, 4)
// #define BV_NUM_URAM_PARTITIONS  (BV_NUM_PARTITIONS - BV_NUM_BRAM_PARTITIONS)

//// Method #2 - favoring URAM usage.
//#define BV_NUM_URAM_PARTITIONS  CEIL_DIVISION(4*BV_NUM_PARTITIONS, 5)
//#define BV_NUM_BRAM_PARTITIONS  (BV_NUM_PARTITIONS - BV_NUM_URAM_PARTITIONS)

//// Method #3 - favoring BRAM usage.
// #define BV_NUM_BRAM_PARTITIONS  CEIL_DIVISION(BV_NUM_PARTITIONS, 5)
// #define BV_NUM_URAM_PARTITIONS  (BV_NUM_PARTITIONS - BV_NUM_BRAM_PARTITIONS)

// Method #4 - Rounding fairly.
#define BV_NUM_BRAM_PARTITIONS  ROUND_DIVISION(BV_NUM_PARTITIONS, 5)
#define BV_NUM_URAM_PARTITIONS  (BV_NUM_PARTITIONS - BV_NUM_BRAM_PARTITIONS)

#define _BV_RF                  (NUM_HASH * BV_URAM_PACKED_BITWIDTH * BV_NUM_PARTITIONS)
#define BV_LENGTH               (CEIL_DIVISION(BV_DESIRED_LENGTH, _BV_RF) * _BV_RF)
#define BV_SECTION_LENGTH       CEIL_DIVISION(BV_LENGTH, NUM_HASH)
#define BV_PARTITION_LENGTH     CEIL_DIVISION(BV_LENGTH, (NUM_HASH * BV_NUM_PARTITIONS))
#define BV_PARTITION_LENGTH_IN_BRAM_PACKED_ELEMS    CEIL_DIVISION(BV_LENGTH, (NUM_HASH*BV_BRAM_PACKED_BITWIDTH*BV_NUM_PARTITIONS))
#define BV_PARTITION_LENGTH_IN_URAM_PACKED_ELEMS    CEIL_DIVISION(BV_LENGTH, (NUM_HASH*BV_URAM_PACKED_BITWIDTH*BV_NUM_PARTITIONS))

/********************************************************************
README README README README README README README README README README
README README README README README README README README README README
README README README README README README README README README README
README README README README README README README README README README
README README README README README README README README README README
README README README README README README README README README README

The purpose of this program is to test the optimal bit-vector partitioning scheme,
in terms of how to split partitions between BRAMs and URAMs.

The preliminary analysis for BitBlender goes as follows:

    - A URAM block holds 4096 words, each word is 72 bits.
        (in BitBlender, we use 64 bits per word).
    - A BRAM block holds 1024 words if each word is 36 bits.
        (in BitBlender, we use 32 bits per word).

    So we see that URAMS can hold 4x more words than a BRAM, and each word is 2x the size.
        => One URAM can hold 8x more data than one BRAM.

    - On the U280, there are 960 URAMs and 2016 BRAMs.
        => There are approximately 2x more BRAM blocks than URAM blocks.

    Therefore, the total URAM storage capacity on the U280 is 4x higher than the total BRAM storage.

From this analysis, we know that we want an approximate 1/5 - 4/5 usage split.

And, from testing, we see that rounding the usage gives the best usage split, on average. Which makes sense.
*/

int main() {
    for (int NUM_HASH = 8; NUM_HASH < 9; ++NUM_HASH){
        for (int BV_NUM_PARTITIONS = 3; BV_NUM_PARTITIONS < 16; ++BV_NUM_PARTITIONS){
            for (int BV_DESIRED_LENGTH_PER_SECTION = 8; BV_DESIRED_LENGTH_PER_SECTION <= 20; BV_DESIRED_LENGTH_PER_SECTION += 4){
                printf("\n\n");
                printf("NUM_HASH = %d\n", NUM_HASH);
                printf("BV_NUM_PARTITIONS = %d\n", BV_NUM_PARTITIONS);
                printf("BV_LEN = %d\n", BV_DESIRED_LENGTH_PER_SECTION);
                int BRAM_USAGE_ESTIMATE = BV_NUM_BRAM_PARTITIONS * BV_PARTITION_LENGTH_IN_BRAM_PACKED_ELEMS/1024;
                int URAM_USAGE_ESTIMATE = BV_NUM_URAM_PARTITIONS * BV_PARTITION_LENGTH_IN_URAM_PACKED_ELEMS/4096;
                //printf("BRAM estimate per query module: %d\n", BRAM_USAGE_ESTIMATE);
                //printf("URAM estimate per query module: %d\n", URAM_USAGE_ESTIMATE);
                printf("Total BRAM estimate: %lf %\n", BRAM_USAGE_ESTIMATE*NUM_HASH/2016.0);
                printf("Total URAM estimate: %lf %\n", URAM_USAGE_ESTIMATE*NUM_HASH/960.0);
                printf("Usage ratio: %d\n", BRAM_USAGE_ESTIMATE/2/URAM_USAGE_ESTIMATE);
            }
        }
    }
}
