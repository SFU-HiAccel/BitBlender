
from codegen.normal_krnl.krnl_gen_toplevel  import TopLevelCodeGenerator as NORMAL_TopLevelCodeGenerator
from codegen.naive_krnl.krnl_NAIVE_gen_toplevel import TopLevelCodeGenerator as NAIVE_TopLevelCodeGenerator
from codegen.types import DesignType

class HostCodeGenerator:
    def __init__(self, config):
        self.config = config





    def _generate_common_includes(self):
        codeArr = []

        codeArr.append("""
#include <algorithm>
#include <cstring>
#include <iostream>
#include <string>
#include <unistd.h>
#include <vector>
#include <cmath>
#include <stdio.h>
#include <set>
#include <math.h>
// This file is required for OpenCL C++ wrapper APIs
//#include "xcl2.hpp"

#include "BitBlender.h"
#include "SW_MurmurHash3.cpp"
#include "hostside_aurorahelpers.cpp"
#include "hostside_bitblender_dataprep.cpp"


int actual_population_inputs=0;    // Modified later

        """)
        codeArr.append('' + "\n")
        return codeArr






    def _generate_krnl_declaration(self):
        codeArr = []

        if (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            topLevel = NAIVE_TopLevelCodeGenerator(self.config)
        elif (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            topLevel = NORMAL_TopLevelCodeGenerator(self.config)

        codeArr.extend(topLevel.generate_func_declaration())
        codeArr.append(';' + "\n")

        return codeArr








    def _generate_bitblender_helper_funcs(self):
        codeArr = []
        codeArr.append("""
#include "BitBlender.h"

extern int actual_population_inputs;

// https://stackoverflow.com/questions/9907160/how-to-convert-enum-names-to-string-in-c
//// WARNING: Probably do not change the INPUT_GEN_MODE_ prefix. That is used by the datacollection script.
////        Changes made here will require changes to the datacollection script.
#define __PREPROC__(FUNC) \\
    FUNC(INPUT_GEN_MODE_RANDOM), \\
    FUNC(INPUT_GEN_MODE_NO_CLASH), \\
    FUNC(INPUT_GEN_MODE_CYCLIC_CLASH), \\
    FUNC(INPUT_GEN_MODE_ALL_CLASH)

#define GENERATE_ENUM(ENUM) ENUM
#define GENERATE_STRING(STRING) #STRING

typedef enum {
    __PREPROC__(GENERATE_ENUM)
} INPUT_GEN_MODE_ENUM;
static const char *INPUT_GEN_MODE_STRINGS[] = {
    __PREPROC__(GENERATE_STRING)
};



bool operator==(const LOAD_DTYPE& lhs, const LOAD_DTYPE& rhs)
{
    bool match = true;

    if (lhs.s0_k0 != rhs.s0_k0) {
        match = false;
    } else if (lhs.s0_k1 != rhs.s0_k1) {
        match = false;
    }
    else if (lhs.s1_k0 != rhs.s1_k0) {
        match = false;
    } else if (lhs.s1_k1 != rhs.s1_k1) {
        match = false;
    }
    else if (lhs.s2_k0 != rhs.s2_k0) {
        match = false;
    } else if (lhs.s2_k1 != rhs.s2_k1) {
        match = false;
    }
    else if (lhs.s3_k0 != rhs.s3_k0) {
        match = false;
    } else if (lhs.s3_k1 != rhs.s3_k1) {
        match = false;
    }
    else if (lhs.s4_k0 != rhs.s4_k0) {
        match = false;
    } else if (lhs.s4_k1 != rhs.s4_k1) {
        match = false;
    }
    else if (lhs.s5_k0 != rhs.s5_k0) {
        match = false;
    } else if (lhs.s5_k1 != rhs.s5_k1) {
        match = false;
    }
    else if (lhs.s6_k0 != rhs.s6_k0) {
        match = false;
    } else if (lhs.s6_k1 != rhs.s6_k1) {
        match = false;
    }
    else if (lhs.s7_k0 != rhs.s7_k0) {
        match = false;
    } else if (lhs.s7_k1 != rhs.s7_k1) {
        match = false;
    }

    return match;
}

bool operator!=(const LOAD_DTYPE& lhs, const LOAD_DTYPE& rhs)
{
    return (!(lhs == rhs));
}


std::ostream& operator<<(std::ostream& os, const LOAD_DTYPE& loadval) {
    os  << loadval.s0_k0.to_int() << " " << loadval.s0_k1.to_int() << "\\n"
        << loadval.s1_k0.to_int() << " " << loadval.s1_k1.to_int() << "\\n"
        << loadval.s2_k0.to_int() << " " << loadval.s2_k1.to_int() << "\\n"
        << loadval.s3_k0.to_int() << " " << loadval.s3_k1.to_int() << "\\n"
        << loadval.s4_k0.to_int() << " " << loadval.s4_k1.to_int() << "\\n"
        << loadval.s5_k0.to_int() << " " << loadval.s5_k1.to_int() << "\\n"
        << loadval.s6_k0.to_int() << " " << loadval.s6_k1.to_int() << "\\n"
        << loadval.s7_k0.to_int() << " " << loadval.s7_k1.to_int();

    return os;
}








bool operator==(const STORE_DTYPE& lhs, const STORE_DTYPE& rhs)
{
    bool match = true;

    if (lhs.s0_k0 != rhs.s0_k0) {
        match = false;
    } else if (lhs.s0_k1 != rhs.s0_k1) {
        match = false;
    }
    else if (lhs.s1_k0 != rhs.s1_k0) {
        match = false;
    } else if (lhs.s1_k1 != rhs.s1_k1) {
        match = false;
    }
    else if (lhs.s2_k0 != rhs.s2_k0) {
        match = false;
    } else if (lhs.s2_k1 != rhs.s2_k1) {
        match = false;
    }
    else if (lhs.s3_k0 != rhs.s3_k0) {
        match = false;
    } else if (lhs.s3_k1 != rhs.s3_k1) {
        match = false;
    }
    else if (lhs.s4_k0 != rhs.s4_k0) {
        match = false;
    } else if (lhs.s4_k1 != rhs.s4_k1) {
        match = false;
    }
    else if (lhs.s5_k0 != rhs.s5_k0) {
        match = false;
    } else if (lhs.s5_k1 != rhs.s5_k1) {
        match = false;
    }
    else if (lhs.s6_k0 != rhs.s6_k0) {
        match = false;
    } else if (lhs.s6_k1 != rhs.s6_k1) {
        match = false;
    }
    else if (lhs.s7_k0 != rhs.s7_k0) {
        match = false;
    } else if (lhs.s7_k1 != rhs.s7_k1) {
        match = false;
    }

    return match;
}

bool operator!=(const STORE_DTYPE& lhs, const STORE_DTYPE& rhs)
{
    return (!(lhs == rhs));
}


std::ostream& print_bits(std::ostream& os, const OUT_PACKED_DTYPE& val) {
    os << val[31] << val[30] << val[29] << val[28]
       << val[27] << val[26] << val[25] << val[24]
       << val[23] << val[22] << val[21] << val[20]
       << val[19] << val[18] << val[17] << val[16]
       << val[15] << val[14] << val[13] << val[12]
       << val[11] << val[10] << val[9] << val[8]
       << val[7] << val[6] << val[5] << val[4]
       << val[3] << val[2] << val[1] << val[0] << std::endl;
    return os;
}


std::ostream& operator<<(std::ostream& os, const STORE_DTYPE& val) {
    print_bits(os, val.s0_k0);
    print_bits(os, val.s0_k1);
    print_bits(os, val.s1_k0);
    print_bits(os, val.s1_k1);
    print_bits(os, val.s2_k0);
    print_bits(os, val.s2_k1);
    print_bits(os, val.s3_k0);
    print_bits(os, val.s3_k1);
    print_bits(os, val.s4_k0);
    print_bits(os, val.s4_k1);
    print_bits(os, val.s5_k0);
    print_bits(os, val.s5_k1);
    print_bits(os, val.s6_k0);
    print_bits(os, val.s6_k1);
    print_bits(os, val.s7_k0);
    print_bits(os, val.s7_k1);
    return os;
}






int min(int in1, int in2) {
    return (in1 < in2 ? in1 : in2);
}

uint32_t bv_size(float fp, int insert_num){
    //fp: false positive rate, number of insertion to bit vector, the bit vector size m should be: m = -(insert_num) * ln(fp) / ( (ln2)^2 )
    float tmp1 = -(insert_num) * (log(fp)) / (log(2) * log(2) );
    int tmp2 = (int)ceil(tmp1);

    return tmp2;
}


void generate_keys(
    INPUT_GEN_MODE_ENUM     input_generation_mode
    ,KEY_DTYPE              *keys
    ,std::vector<uint32_t>  seed
) {
    const int NOT_TAKEN = -1;

    static bool     computed_unclashing_keys = 0;
    static KEY_DTYPE unclashing_keys[NUM_STM];

    int taken_by_stmidx[NUM_HASH][BV_NUM_PARTITIONS] = {};

    for (int i = 0; i < NUM_HASH; ++i) {
        for (int j = 0; j < BV_NUM_PARTITIONS; ++j) {
            taken_by_stmidx[i][j] = NOT_TAKEN;
        }
    }

    if (!computed_unclashing_keys) {
        /* For each hash function, ensure that different streams will output
         *  to different partitions.
         */
        if (input_generation_mode != INPUT_GEN_MODE_RANDOM)
        {
            if (NUM_STM > BV_NUM_PARTITIONS){
                printf("minor warning: NUM_STM > BV_NUM_PARTITIONS. Generating invalid unclashing keys.\\n");
                for (int stm_idx = 0; stm_idx < NUM_STM; ++stm_idx) {
                    unclashing_keys[stm_idx] = 5;
                }
            }
            else {
                for (int stm_idx = 0; stm_idx < NUM_STM; ++stm_idx)
                {
                    int found = 0;
                    KEY_DTYPE proposed_key = 0;
                    int taken_partition_idces[NUM_HASH] = {};

                    while (!found) {
                        found = 1;
                        proposed_key++;
                        for (int i = 0; i < NUM_HASH; ++i) {
                            taken_partition_idces[i] = 0;
                        }

                        for (int hash_idx = 0; hash_idx < NUM_HASH; ++hash_idx) {
                            uint32_t bv_index = SW_MurmurHash3_x86_32(
                                proposed_key,
                                KEY_SIZE_IN_BYTES,
                                seed[hash_idx]
                            );
                            bv_index %= BV_SECTION_LENGTH;
                            uint32_t bv_partition_idx = bv_index / BV_PARTITION_LENGTH;

                            if (taken_by_stmidx[hash_idx][bv_partition_idx] == NOT_TAKEN) {
                                taken_partition_idces[hash_idx] = bv_partition_idx;
                            }
                            else {
                                // One stream will clash.
                                found = 0;
                            }
                        }
                    }

                    /////////
                    // FOUND.
                    unclashing_keys[stm_idx] = proposed_key;
                    for (int hash_idx = 0; hash_idx < NUM_HASH; ++hash_idx) {
                        taken_by_stmidx[hash_idx][ taken_partition_idces[hash_idx] ] = stm_idx;
                    }

                    #ifdef __DO_THIS_DEBUG_PRINTS__
                    printf("FOUND an unclashing query (%d) for stm %d\\n", proposed_key.to_int(), stm_idx);
                    for (int hash_idx = 0; hash_idx < NUM_HASH; ++hash_idx) {
                        for (int pidx = 0; pidx < BV_NUM_PARTITIONS; ++pidx) {

                            if (taken_by_stmidx[hash_idx][pidx] == NOT_TAKEN) {
                                printf("%5c", '-');
                            }
                            else {
                                printf("%5d", taken_by_stmidx[hash_idx][pidx]);
                            }

                        }
                        printf("\\n");
                    }
                    #endif
                }
            }
        }
        computed_unclashing_keys = 1;
    }


    if (input_generation_mode == INPUT_GEN_MODE_RANDOM) {
        for (uint32_t input_idx = 0; input_idx < TOTAL_NUM_KEYINPUT; ++input_idx) {
            KEY_DTYPE in = static_cast<KEY_DTYPE>(rand());
            keys[input_idx] = in;
        }
    }
    else if (input_generation_mode == INPUT_GEN_MODE_NO_CLASH) {
        /* Each stream sends the exact same data over and over,
         * and each stream basically has it's own dedicated partition.
         */
        for (int i=0; i < KEYPAIRS_PER_STM; ++i) {
            for (int j = 0; j < NUM_STM; ++j) {
                for (int kpidx = 0; kpidx < 2; kpidx++) {
                    keys[i*2*NUM_STM + j*2 + kpidx] = unclashing_keys[j];
                }
            }
        }
    }
    else if (input_generation_mode == INPUT_GEN_MODE_CYCLIC_CLASH) {
        /* Each input index is an N-clash, but the partitions on which
         * they clash is always cycling around.
         */
        for (int i = 0; i < KEYPAIRS_PER_STM; ++i) {
            for (int j = 0; j < NUM_STM; ++j) {
                for (int kpidx = 0; kpidx < 2; kpidx++) {
                    keys[i*2*NUM_STM + j*2 + kpidx] = unclashing_keys[i%NUM_STM];
                }
            }
        }
    }
    else if (input_generation_mode == INPUT_GEN_MODE_ALL_CLASH) {
        /* For each hash function, ensure that each stream will hash to the
         * SAME partition, so it always clashes every single time.
         */
        for (int i = 0; i < KEYPAIRS_PER_STM; ++i) {
            for (int j = 0; j < NUM_STM; ++j) {
                for (int kpidx = 0; kpidx < 2; kpidx++) {
                    keys[i*2*NUM_STM + j*2 + kpidx] = 5;
                }
            }
        }
    }
    else {
        // Crash - unsupported case.
        assert(1 == 2);
    }
}



void populate_bv(
    BIT_DTYPE *bv
    ,std::vector<uint32_t>   seed
    ,KEY_DTYPE *keys
    ,std::set<KEY_DTYPE>     &unique_inserted_keys
) {
    int input_idces_to_add[actual_population_inputs];

    /* Knuth's algorithm for unique random number generation in an integer array.
     *  https://stackoverflow.com/questions/1608181/unique-random-number-generation-in-an-integer-array
     */

    const int N_ = TOTAL_NUM_KEYINPUT;
    for (int in = 0, im = 0;
            in < N_ && im < actual_population_inputs;
            ++in) {
        int rn = N_ - in;
        int rm = actual_population_inputs - im;
        if (rand() % rn < rm){
            input_idces_to_add[im++] = in;
        }
    }

    // Use those input indices to populate the BV.
    for (int i = 0; i < actual_population_inputs; ++i) {
        int         add_idx = input_idces_to_add[i];
        uint32_t    bv_index = 0;

        unique_inserted_keys.insert(keys[add_idx]);

        for(int hash_idx = 0; hash_idx < NUM_HASH; hash_idx ++){
            bv_index = SW_MurmurHash3_x86_32(
                keys[add_idx],
                KEY_SIZE_IN_BYTES,  // length of each key in bytes
                seed[hash_idx]
            );
            bv_index %= BV_SECTION_LENGTH;
            bv_index += (hash_idx*BV_SECTION_LENGTH);

            bv[bv_index] = 1;


            #ifdef __DO_DEBUG_PRINTS__
            printf("HOST: Populating bit vector to have input_idx=%d be a hit. So we set bv[%d]=1.\\n",
                        add_idx, bv_index
            );
            #endif
        }
    }
}


void compute_expected_outputs(
    BIT_DTYPE               *bv
    ,std::vector<uint32_t>  seed
    ,KEY_DTYPE              *keys
    ,std::set<KEY_DTYPE>    &unique_hit_keys
    ,BIT_DTYPE              *sw_results
) {
    for (uint32_t input_idx = 0; input_idx < TOTAL_NUM_KEYINPUT; ++input_idx)
    {
        uint32_t    bv_index = 0;
        BIT_DTYPE   cur_result = 1;

        for(int hash_idx = 0; hash_idx < NUM_HASH; hash_idx ++){
            bv_index = SW_MurmurHash3_x86_32(
                keys[input_idx],
                4,      // length of each key in bytes
                seed[hash_idx]
            );
            bv_index %= BV_SECTION_LENGTH;
            bv_index += (hash_idx*BV_SECTION_LENGTH);
            cur_result &= bv[bv_index];

            #ifdef __DO_DEBUG_PRINTS__
            printf("HOST: For input %d, hash #%d, this looked up BV[%d]=%d\\n",
                    input_idx,
                    hash_idx,
                    bv_index,
                    bv[bv_index].to_int()
            );
            #endif
        }
        if (cur_result) {
            unique_hit_keys.insert(keys[input_idx]);
        }

        sw_results[input_idx] = cur_result;
    }

}






bool verify(
    BIT_DTYPE   *sw_results,
    BIT_DTYPE   *hw_results
) {
    const int MAX_REPORTED_FAILS = 100;
    bool match = true;
    int errcount = 0;
    int failed_indices[MAX_REPORTED_FAILS] = {0};

    for (int i = 0; i < TOTAL_NUM_KEYINPUT; ++i) {
        if (hw_results[i] != sw_results[i]) {
            if (errcount < MAX_REPORTED_FAILS-1) {
                failed_indices[errcount] = i;
            }
            errcount ++;

            match = false;
        }
    }

    std::cout << "TEST " << (match ? "PASSED" : "FAILED") << std::endl;
    if (!match)
    {
        std::cout << "Num failures: " << (errcount) << std::endl;

        std::cout << "(THIS ERR REPORTING IS STILL BUGGY)"<<
                " Failed on the following indices (reporting up to the first " <<
                MAX_REPORTED_FAILS << "):" <<  std::endl;
        for (int i = 0; i < (MAX_REPORTED_FAILS); ++i) {
            std::cout << failed_indices[i] << ", ";
        }
    }

    std::cout << std::endl;

    return match;
}



#if ENABLE_PERF_CTRS
void print_perf_ctrs(PERFCTR_DTYPE* perfctrs) {

    printf("NUM_PERFCTR_MODULES = %d\\n", NUM_PERFCTR_MODULES); // DO NOT CHANGE: This line is used by the datacollection python script.

    for (int i = 0; i < NUM_PERFCTR_MODULES; ++i)
    {
        printf("PERFORMANCE_COUNTER_VALUE[%d] = %25lu\\n",
                i, perfctrs[i]
        ); // DO NOT CHANGE: This line is used by the datacollection python script.
    }

}
#endif




double get_theoretical_fp_rate() {
    double n = (double)actual_population_inputs;
    double m = (double)BV_LENGTH;
    double k = (double)NUM_HASH;

    double result = pow(( 1 - exp(-k * n / m)), k);
    return result;
}



void reset_krnl_inputs(
    INPUT_GEN_MODE_ENUM input_generation_mode
    ,bool       do_verif
    ,KEY_DTYPE *keys
    ,BIT_DTYPE *sw_results
    ,BIT_DTYPE *bv
) {
    /*
        These 3 sets are used to compute the false-pos rate.
        Think about it this way: if our input keys only contain 5 unique
        values but they look like this:
            [1, 2, 3, 4, 5, 5, 5, 5, 5...]
        and we insert (1,2,3). And suppose 4 is NOT a false-positive, but 5 IS.
            - if we don't consider unique entries and only ask "how many indices hit?"
              our false-positive rate would be 99%.
            - If we consider unique entries, then our false-positive rate will be
              50%, which is correct.
     */
    std::set<KEY_DTYPE>     unique_inserted_keys;
    std::set<KEY_DTYPE>     unique_uninserted_keys;
    std::set<KEY_DTYPE>     unique_hit_keys;

    std::vector<uint32_t> seed(NUM_HASH);

    // Populate the seeds, for each hash function.
    for(int hash_idx = 0; hash_idx < NUM_HASH; hash_idx ++){
        seed[hash_idx] = hash_idx;
    }

    // Initialize the bitvector to all zeroes.
    for (uint32_t bv_idx = 0; bv_idx < BV_LENGTH; bv_idx++) {
        bv[bv_idx] = 0;
    }

    // Initialize the input keys
    generate_keys(input_generation_mode, keys, seed);

    if (do_verif)
    {
        // Populate the bitvector
        populate_bv(bv, seed, keys, unique_inserted_keys);

        // Use the populated bitvector to calculate the ACTUAL expected outputs.
        compute_expected_outputs(bv, seed, keys, unique_hit_keys, sw_results);

        for (uint32_t input_idx = 0; input_idx < TOTAL_NUM_KEYINPUT; ++input_idx) {
            KEY_DTYPE k = keys[input_idx];

            if (unique_inserted_keys.count(k) == 0) {
                unique_uninserted_keys.insert(k);
            }
        }

        int unique_hits     = unique_hit_keys.size();
        int unique_inserts  = unique_inserted_keys.size();
        int unique_uninserted = unique_uninserted_keys.size();
        int unique_falsepos = unique_hits - unique_inserts;
        double actual_fp_rate           = (double)unique_falsepos / (double)unique_uninserted;
        double theoretical_fp_rate      = get_theoretical_fp_rate();
        double fp_difference_percent = 0;

        if (actual_fp_rate > 0){
            fp_difference_percent = fabs(theoretical_fp_rate - actual_fp_rate) / actual_fp_rate;
        }

        printf("The number of inserted elements is %d, but the number of HIT elements is %d.\\n",
                unique_inserts,
                unique_hits
        );
        printf("Therefore, we have %d false positives out of %d uninserted.\\n",
                unique_falsepos,
                unique_uninserted
        );

        /*****************************************************************/
        /*** THESE LINES ARE USED BY THE COLLECT_ALL_RESULTS.py SCRIPT ***/

        printf("number of inserted elements = %d \\n",
                actual_population_inputs
        );
        printf("ACTUAL fp rate = %lf \\n",
                actual_fp_rate
        );
        printf("THEORETICAL fp rate = %lf \\n",
                theoretical_fp_rate
        );

        /*** END of lines are used by the collect_all_results.py script ***/
        /*****************************************************************/

        if (fp_difference_percent > 0.05){
            printf("\\n\\n\\nWarning: FP RATES ARE DIFFERENT BY %lf\\n",
                    fp_difference_percent
            );
        }

        printf("\\n\\n\\n");

        if (unique_inserts > unique_hits) {
            printf(" SOMETHING IS WRONG WITH THE FP RATE ANALYSIS.\\n");
            assert(1==2);
        }
    }


    /*********************/
    // DEBUG: print the bv.
    //#ifdef __DO_DEBUG_PRINTS__
    //for (int i = 0; i < BV_LENGTH; ++i) {
    //    printf("HOST: BV[%d] = %d\\n",
    //            i, bv[i].to_int()
    //    );
    //}
    //#endif
    // #ifdef __DO_DEBUG_PRINTS__
    // const int START_DEBUG_PRINTS = 0;
    // const int END_DEBUG_PRINTS = 3;
    // for (int i = START_DEBUG_PRINTS; i < END_DEBUG_PRINTS; ++i) {
    //     printf("HOST: packed_BV[%d] = %x\\n", i, packed_bv_0[i].to_int());
    //     for (int j = 0; j < BV_URAM_PACKED_BITWIDTH; ++j) {
    //         int total_idx = i*BV_URAM_PACKED_BITWIDTH + j;
    //         printf("HOST: BV[%d] = %d\\n", total_idx, bv[total_idx].to_int());
    //     }
    //     printf("\\n");
    // }
    // #endif
}

        """)

        codeArr.append('//////////////////////////////////////////////////////' + "\n")
        codeArr.append('//////////////////////////////////////////////////////' + "\n")
        codeArr.append('//////////////////////////////////////////////////////' + "\n")
        codeArr.append('//////////////////////////////////////////////////////' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('void datapack_bv(' + "\n")
        codeArr.append('    BIT_DTYPE *bv' + "\n")
        codeArr.append('    ,BV_LOAD_DTYPE *packed_bv' + "\n")
        codeArr.append(') {' + "\n")

        for h in range(self.config.num_hash):
            codeArr.append('    std::vector<BV_URAM_PACKED_DTYPE> bv_section{h}(BV_SECTION_LENGTH_IN_URAM_PACKED_ELEMS);'.format(h=h) + "\n")

        codeArr.append('    #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('    crash(compilation)' + "\n")
        codeArr.append('    #endif' + "\n")

        codeArr.append('    // Datapack the bitvector' + "\n")
        codeArr.append('    for (int i = 0; i < BV_LENGTH; ++i) {' + "\n")
        codeArr.append('        int section_idx     = (i/BV_URAM_PACKED_BITWIDTH) / BV_SECTION_LENGTH_IN_URAM_PACKED_ELEMS;' + "\n")
        codeArr.append('        int array_idx       = (i/BV_URAM_PACKED_BITWIDTH) % BV_SECTION_LENGTH_IN_URAM_PACKED_ELEMS;' + "\n")
        codeArr.append('        int bit_idx         = (i%BV_URAM_PACKED_BITWIDTH);' + "\n")
        codeArr.append('' + "\n")

        for h in range(0, self.config.num_hash):
            if (h == 0):
                codeArr.append('        if (section_idx == {h}) {{'.format(h=h) + "\n")
            else:
                codeArr.append('        else if (section_idx == {h}) {{'.format(h=h) + "\n")
            codeArr.append('            bv_section{h}[array_idx].range(bit_idx, bit_idx) = bv[i].range(0, 0);'.format(h=h) + "\n")
            codeArr.append('        }' + "\n")

        codeArr.append('        else {' + "\n")
        codeArr.append('            printf("Something went wrong with the BV datapacking computation...\\n");' + "\n")
        codeArr.append('            exit(-1);' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('        crash();' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    // Pack the sections into the final BV.' + "\n")
        codeArr.append('    for (int i = 0; i < BV_SECTION_LENGTH_IN_URAM_PACKED_ELEMS; ++i) {' + "\n")

        for h in range(0, self.config.num_hash):
            codeArr.append('        packed_bv[i].section{h} = bv_section{h}[i];'.format(h=h) + "\n")

        codeArr.append('        #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('        crash();' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")



        ### TODO: PACKINPUTS

        if (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            codeArr.append('void datapack_keys(' + "\n")
            codeArr.append('    KEY_DTYPE *keys' + "\n")
            for a in range(0, self.config.keys_num_axi_ports):
                codeArr.append('    ,LOAD_DTYPE *krnl_key_in_{a}'.format(a=a) + "\n")
            codeArr.append('    #if NUM_AXI_PORTS != {}'.format(self.config.keys_num_axi_ports) + "\n")
            codeArr.append('    crash(compilation)' + "\n")
            codeArr.append('    #endif' + "\n")
            codeArr.append(') {' + "\n")
            codeArr.append('    // Pack the key inputs for the kernel.' + "\n")
            codeArr.append('    for (int i = 0; i < KEYPAIRS_PER_STM; ++i)' + "\n")
            codeArr.append('    {' + "\n")

            for a in range(0, self.config.keys_num_axi_ports):
                codeArr.append('        LOAD_DTYPE cur_packed_input_axi{a};'.format(a=a) + "\n")

            codeArr.append('' + "\n")
            for sidx in range(0, self.config.num_stm):
                axi_to_write = int(sidx / self.config.KEYS_MAX_AXI_PACK_FACTOR)
                s_to_write = sidx % self.config.KEYS_MAX_AXI_PACK_FACTOR
                codeArr.append('        cur_packed_input_axi{a}.s{sw}_k0 = keys[i*2*NUM_STM + 2*{stotal} + 0];'.format(a=axi_to_write, sw=s_to_write, stotal=sidx) + "\n")
                codeArr.append('        cur_packed_input_axi{a}.s{sw}_k1 = keys[i*2*NUM_STM + 2*{stotal} + 1];'.format(a=axi_to_write, sw=s_to_write, stotal=sidx) + "\n")
                codeArr.append('' + "\n")

            codeArr.append('        #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
            codeArr.append('        crash on purpose(,' + "\n")
            codeArr.append('        #endif' + "\n")
            codeArr.append('' + "\n")

            for a in range(0, self.config.keys_num_axi_ports):
                codeArr.append('        krnl_key_in_{a}[i] = cur_packed_input_axi{a};'.format(a=a) + "\n")

            codeArr.append('' + "\n")
            codeArr.append('        #if NUM_AXI_PORTS != {}'.format(self.config.keys_num_axi_ports) + "\n")
            codeArr.append('        crash(compilation)' + "\n")
            codeArr.append('        #endif' + "\n")

            codeArr.append('' + "\n")
            codeArr.append('    }' + "\n")
            codeArr.append('}' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('' + "\n")







        if (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            codeArr.append('void datapack_krnl_inputs(' + "\n")
            codeArr.append('    bool            do_verif' + "\n")
            codeArr.append('    ,KEY_DTYPE      *keys' + "\n")

            for a in range(0, self.config.keys_num_axi_ports):
                codeArr.append('    ,LOAD_DTYPE     *krnl_key_in_{a}'.format(a=a) + "\n")

            codeArr.append('' + "\n")
            codeArr.append('    #if NUM_AXI_PORTS != {}'.format(self.config.keys_num_axi_ports) + "\n")
            codeArr.append('    crash(compilation)' + "\n")
            codeArr.append('    #endif' + "\n")
            codeArr.append('' + "\n")

            codeArr.append('    ,BIT_DTYPE      *bv' + "\n")
            codeArr.append('    ,BV_LOAD_DTYPE  *packed_bv' + "\n")
            codeArr.append(') {' + "\n")

            codeArr.append('    datapack_keys(' + "\n")
            codeArr.append('        keys' + "\n")

            for a in range(0, self.config.keys_num_axi_ports):
                codeArr.append('        ,krnl_key_in_{a}'.format(a=a) + "\n")

            codeArr.append('        #if NUM_AXI_PORTS != {}'.format(self.config.keys_num_axi_ports) + "\n")
            codeArr.append('        crash(compilation)' + "\n")
            codeArr.append('        #endif' + "\n")
            codeArr.append('    );' + "\n")
            codeArr.append('' + "\n")

            codeArr.append('    /* Only datapack the BV if were doing verification. Because otherwise we only want to test' + "\n")
            codeArr.append('     * the runtime, and datapacking costs some server CPU time.' + "\n")
            codeArr.append('     */' + "\n")
            codeArr.append('    if (do_verif) {' + "\n")
            codeArr.append('        datapack_bv(bv, packed_bv);' + "\n")
            codeArr.append('    }' + "\n")
            codeArr.append('}' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('' + "\n")



        codeArr.append('' + "\n")
        codeArr.append('//////////////////////////////////////////////////////' + "\n")
        codeArr.append('//////////////////////////////////////////////////////' + "\n")
        codeArr.append('//////////////////////////////////////////////////////' + "\n")
        codeArr.append('//////////////////////////////////////////////////////' + "\n")
        codeArr.append('' + "\n")


        if (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            codeArr.append('void unpack_krnl_outputs(' + "\n")
            for a in range(0, self.config.keys_num_axi_ports):
                codeArr.append('    STORE_DTYPE     *krnl_out_{a},'.format(a=a) + "\n")

            codeArr.append('    #if NUM_AXI_PORTS != {}'.format(self.config.keys_num_axi_ports) + "\n")
            codeArr.append('    crash(compilation)' + "\n")
            codeArr.append('    #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    BIT_DTYPE      *krnl_merged_out' + "\n")
            codeArr.append(') {' + "\n")
            codeArr.append('    int out_bit_idx = 0;' + "\n")
            codeArr.append('    for (int i = 0; i < PACKED_OUTPUTS_PER_STM; ++i)' + "\n")
            codeArr.append('    {' + "\n")
            codeArr.append('        for (int j = 0; j < OUT_PACKED_BITWIDTH; ++j)' + "\n")
            codeArr.append('        {' + "\n")

            for sidx in range(0, self.config.num_stm):
                axi_to_read = int(sidx / self.config.KEYS_MAX_AXI_PACK_FACTOR)
                s_to_read = sidx % self.config.KEYS_MAX_AXI_PACK_FACTOR
                codeArr.append('            krnl_merged_out[out_bit_idx++].range(0, 0) =' + "\n")
                codeArr.append('                krnl_out_{a}[i].s{sr}_k0.range(j, j);'.format(a=axi_to_read, sr=s_to_read) + "\n")
                codeArr.append('            krnl_merged_out[out_bit_idx++].range(0, 0) =' + "\n")
                codeArr.append('                krnl_out_{a}[i].s{sr}_k1.range(j, j);'.format(a=axi_to_read, sr=s_to_read) + "\n")
                codeArr.append('' + "\n")

            codeArr.append('        }' + "\n")
            codeArr.append('    }' + "\n")
            codeArr.append('}' + "\n")





        return codeArr














    def _generate_tapa_host_main_func(self):

        codeArr = []
        codeArr.append('' + "\n")
        codeArr.append('#ifndef NAIVE_MULTISTREAM' + "\n")
        codeArr.append('void crash_compilation(' + "\n")
        codeArr.append('    crash compilation' + "\n")
        codeArr.append('    You need to define NAIVE_MULTISTREAM when compiling!' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append('#endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('DEFINE_string(bitstream, "", "Path to bitstream file. Run SW_EMU if empty.");' + "\n")
        codeArr.append('/**********************************************************/' + "\n")
        codeArr.append('/**********************************************************/' + "\n")
        codeArr.append('/**********************************************************/' + "\n")
        codeArr.append('/**********************************************************/' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('int main(int argc, char **argv) {' + "\n")
        codeArr.append('    gflags::ParseCommandLineFlags(&argc, &argv, /*remove_flags=*/true);' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    setbuf(stdout, NULL);' + "\n")
        codeArr.append('    bool match = 1;' + "\n")
        codeArr.append('    const int NUM_TESTS_TO_RUN = 10;' + "\n")
        codeArr.append('    int test_number = 0;' + "\n")
        codeArr.append('    INPUT_GEN_MODE_ENUM     gen_data_mode;' + "\n")
        codeArr.append('    actual_population_inputs = NUM_POPULATION_INPUTS;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    //gen_data_mode = INPUT_GEN_MODE_RANDOM;' + "\n")
        codeArr.append('    //gen_data_mode = INPUT_GEN_MODE_NO_CLASH;' + "\n")
        codeArr.append('    gen_data_mode = INPUT_GEN_MODE_ALL_CLASH;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    // I/O Data Vectors' + "\n")
        codeArr.append('    std::vector<KEY_DTYPE, tapa::aligned_allocator<KEY_DTYPE>>' + "\n")
        codeArr.append('        keys(TOTAL_NUM_KEYINPUT);' + "\n")
        codeArr.append('    std::vector<BIT_DTYPE, tapa::aligned_allocator<BIT_DTYPE>>' + "\n")
        codeArr.append('        krnl_merged_out(TOTAL_NUM_KEYINPUT);' + "\n")
        codeArr.append('' + "\n")


        codeArr.append('    std::vector<BIT_DTYPE, tapa::aligned_allocator<BIT_DTYPE>>          source_bv(BV_LENGTH);' + "\n")
        codeArr.append('    std::vector<BV_LOAD_DTYPE, tapa::aligned_allocator<BV_LOAD_DTYPE>>  source_PACKED_bv(BV_NUM_LOADS);' + "\n")
        codeArr.append('    std::vector<BIT_DTYPE>                                              sw_results(TOTAL_NUM_KEYINPUT);' + "\n")

        codeArr.append('' + "\n")

        if (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            for s in range(1, self.config.num_stm):
                codeArr.append('    std::vector<BV_LOAD_DTYPE, tapa::aligned_allocator<BV_LOAD_DTYPE>>          source_PACKED_bv_{s}(BV_NUM_LOADS);'.format(s=s) + "\n")
            codeArr.append('    #if NUM_STM!= {}'.format(self.config.num_stm) + "\n")
            codeArr.append('    crash(;' + "\n")
            codeArr.append('    #endif' + "\n")
            codeArr.append('    std::vector<TWOKEY_DTYPE, tapa::aligned_allocator<TWOKEY_DTYPE>>            krnl_key_in[NUM_STM];' + "\n")
            codeArr.append('    std::vector<OUT_PACKED_DTYPE, tapa::aligned_allocator<OUT_PACKED_DTYPE>>    krnl_out[NUM_STM];' + "\n")

        elif (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            for a in range(0, self.config.keys_num_axi_ports):
                codeArr.append('    std::vector<LOAD_DTYPE, tapa::aligned_allocator<LOAD_DTYPE>>        krnl_key_in_{a}(KEYPAIRS_PER_STM);'.format(a=a) + "\n")
                codeArr.append('    std::vector<STORE_DTYPE, tapa::aligned_allocator<STORE_DTYPE>>      krnl_out_{a}(PACKED_OUTPUTS_PER_STM);'.format(a=a) + "\n")
            codeArr.append('    #if NUM_AXI_PORTS != {}'.format(self.config.keys_num_axi_ports) + "\n")
            codeArr.append('    crash(compilation) //Need more krnl arguments.' + "\n")
            codeArr.append('    #endif' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    const int TOTAL_NUM_PERFCTR_OUTPUTS = NUM_PERFCTR_MODULES*NUM_PERFCTR_OUTPUTS_PER_MODULE;' + "\n")
        codeArr.append('    std::vector<PERFCTR_DTYPE, tapa::aligned_allocator<PERFCTR_DTYPE>>    perfctrs(TOTAL_NUM_PERFCTR_OUTPUTS);' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    /**************************************/' + "\n")
        codeArr.append('    /*** Sanity Checks                  ***/' + "\n")
        codeArr.append('    /**************************************/' + "\n")
        codeArr.append('    #if (BV_LENGTH % BV_URAM_PACKED_BITWIDTH != 0)' + "\n")
        codeArr.append('    crash(;' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('    #if ( (KEY_BITWIDTH/8) * MAX_KEYS_IN_ONE_AXI_PORT > (1024*1024*256) )' + "\n")
        codeArr.append('    crash(; // Over 256 MB, it cant fit in one hbm bank.' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('    #if (BV_NUM_BRAM_PARTITIONS + BV_NUM_URAM_PARTITIONS != BV_NUM_PARTITIONS)' + "\n")
        codeArr.append('    crash(;' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('    if (OUT_PACKED_BITWIDTH != 32      &&' + "\n")
        codeArr.append('        OUT_PACKED_BITWIDTH != 64      &&' + "\n")
        codeArr.append('        OUT_PACKED_BITWIDTH != 128     &&' + "\n")
        codeArr.append('        OUT_PACKED_BITWIDTH != 256     &&' + "\n")
        codeArr.append('        OUT_PACKED_BITWIDTH != 512     &&' + "\n")
        codeArr.append('        OUT_PACKED_BITWIDTH != 1024)' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('        printf("ERROR: The OUT_PACKED_BITWIDTH must be a power of 2, between 32 and 1024.\\n");' + "\n")
        codeArr.append('        printf("       Otherwise Vivado will have errors.\\n");' + "\n")
        codeArr.append('        exit(-1);' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('    /**************************************/' + "\n")
        codeArr.append('    /*** END OF Sanity Checks           ***/' + "\n")
        codeArr.append('    /**************************************/' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    while (test_number < NUM_TESTS_TO_RUN)' + "\n")
        codeArr.append('    //while (match && test_number < NUM_TESTS_TO_RUN)' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('        // Seed the random number generator so we have replicatable input vectors.' + "\n")
        codeArr.append('        srand(1+test_number++);' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('        // Only do verif if were using a random input sequence' + "\n")
        codeArr.append('        bool do_verif = 0;' + "\n")
        codeArr.append('' + "\n")

        if (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            codeArr.append('        gen_data_mode = INPUT_GEN_MODE_RANDOM;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        if (test_number == 9) {' + "\n")
            codeArr.append('            do_verif = 1;' + "\n")
            codeArr.append('            actual_population_inputs = NUM_POPULATION_INPUTS;' + "\n")
            codeArr.append('        }' + "\n")
        elif (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            codeArr.append('        if (test_number == 1) {' + "\n")
            codeArr.append('            gen_data_mode = INPUT_GEN_MODE_NO_CLASH;' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('        else if (test_number == 2) {' + "\n")
            codeArr.append('            gen_data_mode = INPUT_GEN_MODE_CYCLIC_CLASH;' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('        else if (test_number == 3) {' + "\n")
            codeArr.append('            gen_data_mode = INPUT_GEN_MODE_ALL_CLASH;' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('        else {' + "\n")
            codeArr.append('            gen_data_mode = INPUT_GEN_MODE_RANDOM;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            if (test_number == 9) {' + "\n")
            codeArr.append('                do_verif = 1;' + "\n")
            codeArr.append('                actual_population_inputs = NUM_POPULATION_INPUTS;' + "\n")
            codeArr.append('            }' + "\n")
            codeArr.append('            //// These take too long to run...' + "\n")
            codeArr.append('            //else if (test_number == 5) {' + "\n")
            codeArr.append('            //    do_verif = 1;' + "\n")
            codeArr.append('            //    actual_population_inputs = (BV_LENGTH/8);' + "\n")
            codeArr.append('            //}' + "\n")
            codeArr.append('            //else if (test_number == 6) {' + "\n")
            codeArr.append('            //    do_verif = 1;' + "\n")
            codeArr.append('            //    actual_population_inputs = (BV_LENGTH/32);' + "\n")
            codeArr.append('            //}' + "\n")
            codeArr.append('            //else if (test_number == 7) {' + "\n")
            codeArr.append('            //    do_verif = 1;' + "\n")
            codeArr.append('            //    actual_population_inputs = (BV_LENGTH/64);' + "\n")
            codeArr.append('            //}' + "\n")
            codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        ///////////////////////////////////' + "\n")
        codeArr.append('        // DEBUG PRINTS:' + "\n")
        codeArr.append('        printf("KDEBUG: TOTAL_NUM_KEYINPUT is %d\\n", TOTAL_NUM_KEYINPUT);' + "\n")
        codeArr.append('        printf("KDEBUG: actual_population_inputs is %d\\n", actual_population_inputs);' + "\n")
        codeArr.append('        printf("KDEBUG: BV_LENGTH is %d\\n", BV_LENGTH);' + "\n")
        codeArr.append('        printf("KDEBUG: BV_SECTION_LENGTH is %d\\n",' + "\n")
        codeArr.append('                    BV_SECTION_LENGTH);' + "\n")
        codeArr.append('        printf("KDEBUG: BV_PARTITION_LENGTH_IN_URAM_PACKED_ELEMS is %d\\n",' + "\n")
        codeArr.append('                    BV_PARTITION_LENGTH_IN_URAM_PACKED_ELEMS);' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        printf("\\n");' + "\n")
        codeArr.append('        printf("KDEBUG: NUM_HASH is %d\\n", NUM_HASH);' + "\n")
        codeArr.append('        printf("KDEBUG: BV_NUM_PARTITIONS is %d\\n", BV_NUM_PARTITIONS);' + "\n")
        codeArr.append('        printf("KDEBUG: NUM_STM is %d\\n", NUM_STM);' + "\n")
        codeArr.append('        printf("KDEBUG: ARB_RATELIM_DISTANCE is %d\\n", ARB_RATELIM_DISTANCE);' + "\n")
        codeArr.append('        printf("\\n");' + "\n")
        codeArr.append('        printf("KDEBUG: STM_DEPTH is %d\\n\\n", STM_DEPTH);' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        printf("WARNING! PERFORMANCE COUNTERS ARE ENABLED! WARNING!\\n");' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('        if (NAIVE_MULTISTREAM) {' + "\n")
        codeArr.append('            printf("WARNING! using NAIVE multistream! WARNING!\\n");' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else {' + "\n")
        codeArr.append('            printf("Using our BV-sharing multistream design.\\n");' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        if (gen_data_mode != INPUT_GEN_MODE_RANDOM) {' + "\n")
        codeArr.append('            printf("WARNING: ");' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        printf("gen_data_mode IS %s\\n\\n", INPUT_GEN_MODE_STRINGS[gen_data_mode]);' + "\n")
        codeArr.append('        ///////////////////////////////////' + "\n")
        codeArr.append('' + "\n")

        if (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            codeArr.append('        for (int i = 0; i < NUM_STM; ++i) {' + "\n")
            codeArr.append('            krnl_key_in[i].clear();' + "\n")
            codeArr.append('            krnl_out[i].clear();' + "\n")
            codeArr.append('        }' + "\n")
        elif (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            pass

        codeArr.append('' + "\n")
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        perfctrs.clear();' + "\n")
        codeArr.append('        for (int i = 0; i < TOTAL_NUM_PERFCTR_OUTPUTS; ++i) {' + "\n")
        codeArr.append('            perfctrs.push_back(987654321);' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        reset_krnl_inputs(' + "\n")
        codeArr.append('            gen_data_mode' + "\n")
        codeArr.append('            ,do_verif' + "\n")
        codeArr.append('            ,keys.data()' + "\n")
        codeArr.append('            ,sw_results.data()' + "\n")
        codeArr.append('            ,source_bv.data()' + "\n")
        codeArr.append('        );' + "\n")
        codeArr.append('' + "\n")

        ################

        if (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            codeArr.append('        datapack_krnl_inputs(' + "\n")
            codeArr.append('            do_verif' + "\n")
            codeArr.append('            ,keys.data()' + "\n")
            codeArr.append('' + "\n")

            for a in range(0, self.config.keys_num_axi_ports):
                codeArr.append('            ,krnl_key_in_{a}.data()'.format(a=a) + "\n")
            codeArr.append('            #if NUM_AXI_PORTS != {}'.format(self.config.keys_num_axi_ports) + "\n")
            codeArr.append('            crash(compilation)' + "\n")
            codeArr.append('            #endif' + "\n")

            codeArr.append('' + "\n")
            codeArr.append('            ,source_bv.data()' + "\n")
            codeArr.append('            ,source_PACKED_bv.data()' + "\n")
            codeArr.append('        );' + "\n")
            codeArr.append('' + "\n")

        elif (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            codeArr.append('        // Only datapack the BV if we need to run verification. Because it costs a long time to do this.' + "\n")
            codeArr.append('        if (do_verif) {' + "\n")
            codeArr.append('            datapack_bv(source_bv.data(), source_PACKED_bv.data());' + "\n")
            codeArr.append('        }' + "\n")

            codeArr.append('        // Duplicate the BV input data, once for each PE.' + "\n")
            for s in range(1, self.config.num_stm):
                codeArr.append('        for (int i = 0; i < BV_NUM_LOADS; ++i) {' + "\n")
                codeArr.append('            source_PACKED_bv_{s}[i] = source_PACKED_bv[i];'.format(s=s) + "\n")
                codeArr.append('        }' + "\n")
            codeArr.append('        #if NUM_STM!= {}'.format(self.config.num_stm) + "\n")
            codeArr.append('        crash(;' + "\n")
            codeArr.append('        #endif' + "\n")

            codeArr.append('        // Pack the key inputs for the kernel.' + "\n")
            codeArr.append('        for (int stm_idx = 0; stm_idx < NUM_STM; ++stm_idx)' + "\n")
            codeArr.append('        {' + "\n")
            codeArr.append('            for (int i = 0; i < KEYPAIRS_PER_STM; ++i)' + "\n")
            codeArr.append('            {' + "\n")
            codeArr.append('                TWOKEY_DTYPE stm_in;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('                stm_in.k0 = keys[stm_idx*KEYS_PER_STM + 2*i + 0];' + "\n")
            codeArr.append('                stm_in.k1 = keys[stm_idx*KEYS_PER_STM + 2*i + 1];' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('                krnl_key_in[stm_idx].push_back(stm_in);' + "\n")
            codeArr.append('            }' + "\n")
            codeArr.append('        }' + "\n")




        #################


        if (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            codeArr.append('        for (int i = 0; i < NUM_STM; ++i) {' + "\n")
            codeArr.append('            for (int j = 0; j < PACKED_OUTPAIRS_PER_STM; ++j) {' + "\n")
            codeArr.append('                // Fill the kernels output bufs with some initial values to help debug.' + "\n")
            codeArr.append('                krnl_out[i].push_back(123123);' + "\n")
            codeArr.append('            }' + "\n")
            codeArr.append('        }' + "\n")
        elif (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            pass

        codeArr.append('' + "\n")


        codeArr.append('        /****************************************/' + "\n")
        codeArr.append('        /***** KERNEL INVOCATION            *****/' + "\n")
        codeArr.append('        /****************************************/' + "\n")
        if (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            codeArr.append('        int64_t kernel_time_ns = tapa::invoke(' + "\n")
            codeArr.append('            workload,' + "\n")
            codeArr.append('            FLAGS_bitstream' + "\n")
            codeArr.append('             ,tapa::read_only_mmap<BV_LOAD_DTYPE>(source_PACKED_bv)' + "\n")
            for s in range(1, self.config.num_stm):
                codeArr.append('             ,tapa::read_only_mmap<BV_LOAD_DTYPE>(source_PACKED_bv_{s})'.format(s=s) + "\n")
            codeArr.append('' + "\n")

            for s in range(0, self.config.num_stm):
                codeArr.append('            ,tapa::read_only_mmap<TWOKEY_DTYPE>(krnl_key_in[{s}])'.format(s=s) + "\n")
                codeArr.append('            ,tapa::write_only_mmap<OUT_PACKED_DTYPE>(krnl_out[{s}])'.format(s=s) + "\n")

            codeArr.append('' + "\n")
            codeArr.append('            #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
            codeArr.append('            , ! //crash on purpose; we need to manually add more streams.' + "\n")
            codeArr.append('            #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            #if ENABLE_PERF_CTRS' + "\n")
            codeArr.append('            ,tapa::write_only_mmap<PERFCTR_DTYPE>(perfctrs)' + "\n")
            codeArr.append('            #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            , KEYPAIRS_PER_STM' + "\n")
            codeArr.append('        );' + "\n")

        elif (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            codeArr.append('        int64_t kernel_time_ns = tapa::invoke(' + "\n")
            codeArr.append('            workload,' + "\n")
            codeArr.append('            FLAGS_bitstream,' + "\n")
            codeArr.append('             tapa::read_only_mmap<BV_LOAD_DTYPE>(source_PACKED_bv)' + "\n")
            codeArr.append('' + "\n")

            for a in range(0, self.config.keys_num_axi_ports):
                codeArr.append('            ,tapa::read_only_mmap<LOAD_DTYPE>(krnl_key_in_{a})'.format(a=a) + "\n")

            for a in range(0, self.config.keys_num_axi_ports):
                codeArr.append('            ,tapa::write_only_mmap<STORE_DTYPE>(krnl_out_{a})'.format(a=a) + "\n")

            codeArr.append('' + "\n")
            codeArr.append('            #if NUM_AXI_PORTS != {}'.format(self.config.keys_num_axi_ports) + "\n")
            codeArr.append('            crash(compilation)' + "\n")
            codeArr.append('            #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            #if ENABLE_PERF_CTRS' + "\n")
            codeArr.append('            ,tapa::write_only_mmap<PERFCTR_DTYPE>(perfctrs)' + "\n")
            codeArr.append('            #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            , KEYPAIRS_PER_STM' + "\n")
            codeArr.append('        );' + "\n")

        codeArr.append('        /****************************************/' + "\n")
        codeArr.append('        /***** END KERNEL INVOCATION        *****/' + "\n")
        codeArr.append('        /****************************************/' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        std::cout << "KERNEL time: " << kernel_time_ns * 1e-9 << " s" << std::endl; // DO NOT CHANGE: This line is used by the datacollection python script.' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")


        codeArr.append('        if (do_verif){' + "\n")
        codeArr.append('            // Merge kernel outputs' + "\n")

        if (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            codeArr.append('            int merged_bit_idx = 0;' + "\n")
            codeArr.append('            for (int i = 0; i < NUM_STM; ++i) {' + "\n")
            codeArr.append('                for (int j = 0; j < PACKED_OUTPAIRS_PER_STM; ++j) {' + "\n")
            codeArr.append('                    for (int bidx = 0; bidx < OUT_PACKED_BITWIDTH; ++bidx) {' + "\n")
            codeArr.append('                        krnl_merged_out[merged_bit_idx++] = krnl_out[i][j].range(bidx, bidx);' + "\n")
            codeArr.append('                    }' + "\n")
            codeArr.append('                }' + "\n")
            codeArr.append('            }' + "\n")
        elif (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            codeArr.append('            unpack_krnl_outputs(' + "\n")
            for a in range(0, self.config.keys_num_axi_ports):
                codeArr.append('                krnl_out_{a}.data(),'.format(a=a) + "\n")
            codeArr.append('                #if NUM_AXI_PORTS != {}'.format(self.config.keys_num_axi_ports) + "\n")
            codeArr.append('                crash(compilation) //Need more krnl args.' + "\n")
            codeArr.append('                #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('                krnl_merged_out.data()' + "\n")
            codeArr.append('            );' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('            match = verify(' + "\n")
        codeArr.append('                sw_results.data(),' + "\n")
        codeArr.append('                krnl_merged_out.data()' + "\n")
        codeArr.append('            );' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        print_perf_ctrs(perfctrs.data());' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        std::cout << "------------------------------------------" << std::endl;' + "\n")
        codeArr.append('        std::cout << "------------------------------------------" << std::endl;' + "\n")
        codeArr.append('        std::cout << "------------------------------------------" << std::endl;' + "\n")
        codeArr.append('        std::cout << "------------------------------------------" << std::endl;' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    printf("\\n\\n\\n\\n\\n\\n\\n\\nHost is now exiting.\\n\\n\\n\\n\\n\\n\\n\\n");' + "\n")
        codeArr.append('    return (match ? EXIT_SUCCESS : EXIT_FAILURE);' + "\n")
        codeArr.append('}' + "\n")

        return codeArr






    def _generate_aurora_host_main_func(self):
        codeArr = []

        codeArr.append("""
/**********************************************************/
/**********************************************************/
/**********************************************************/
/**********************************************************/


int main(int argc, char **argv)
{
    Configuration config(argc, argv);
    setbuf(stdout, NULL);

    printf("\\n\\n\\n\\n STARTING HOST CODE NOW!!! \\n\\n\\n");


    bool match = 1;
    const int NUM_TESTS_TO_RUN = 10;
    int test_number = 0;
    INPUT_GEN_MODE_ENUM     gen_data_mode;
    actual_population_inputs = NUM_POPULATION_INPUTS;

    // I/O Data Vectors
    std::vector<KEY_DTYPE, tapa::aligned_allocator<KEY_DTYPE>>
        keys(TOTAL_NUM_KEYINPUT);
    std::vector<BIT_DTYPE, tapa::aligned_allocator<BIT_DTYPE>>
        krnl_merged_out(TOTAL_NUM_KEYINPUT);

    std::vector<BIT_DTYPE, tapa::aligned_allocator<BIT_DTYPE>>          source_bv(BV_LENGTH);
    std::vector<BV_LOAD_DTYPE, tapa::aligned_allocator<BV_LOAD_DTYPE>>  source_PACKED_bv(BV_NUM_LOADS);
    std::vector<BIT_DTYPE>                                              sw_results(TOTAL_NUM_KEYINPUT);
    """)

        if (self.config.keys_num_axi_ports > 1):
            codeArr.append('crash(compilation); // The Aurora kernel does not work with more than one input port.' + "\n")
        if (self.config.design_type != DesignType.NORMAL_MULTISTREAM):
            codeArr.append('crash(compilation); // The Aurora kernel only supports BitBlender, not naive or singlestream.' + "\n")

        codeArr.append("""
    std::vector<LOAD_DTYPE, tapa::aligned_allocator<LOAD_DTYPE>>        krnl_key_in_0(KEYPAIRS_PER_STM);
    std::vector<STORE_DTYPE, tapa::aligned_allocator<STORE_DTYPE>>      krnl_out_0(PACKED_OUTPUTS_PER_STM);

    #if ENABLE_PERF_CTRS
    const int TOTAL_NUM_PERFCTR_OUTPUTS = NUM_PERFCTR_MODULES*NUM_PERFCTR_OUTPUTS_PER_MODULE;
    std::vector<PERFCTR_DTYPE, tapa::aligned_allocator<PERFCTR_DTYPE>>    perfctrs(TOTAL_NUM_PERFCTR_OUTPUTS);
    #endif

    /**************************************/
    /*** Sanity Checks                  ***/
    /**************************************/
    #if (BV_LENGTH % BV_URAM_PACKED_BITWIDTH != 0)
    crash(;
    #endif
    #if ( (KEY_BITWIDTH/8) * MAX_KEYS_IN_ONE_AXI_PORT > (1024*1024*256) )
    crash(; // Over 256 MB, it cant fit in one hbm bank.
    #endif
    #if (BV_NUM_BRAM_PARTITIONS + BV_NUM_URAM_PARTITIONS != BV_NUM_PARTITIONS)
    crash(;
    #endif
    if (OUT_PACKED_BITWIDTH != 32      &&
        OUT_PACKED_BITWIDTH != 64      &&
        OUT_PACKED_BITWIDTH != 128     &&
        OUT_PACKED_BITWIDTH != 256     &&
        OUT_PACKED_BITWIDTH != 512     &&
        OUT_PACKED_BITWIDTH != 1024)
    {
        printf("ERROR: The OUT_PACKED_BITWIDTH must be a power of 2, between 32 and 1024.\\n");
        printf("       Otherwise Vivado will have errors.\\n");
        exit(-1);
    }
    /**************************************/
    /*** END OF Sanity Checks           ***/
    /**************************************/



    bool emulation = (std::getenv("XCL_EMULATION_MODE") != nullptr);

    uint32_t device_id = emulation ? 0 : (0) %3;

    // NOTE: THESE values depend on the connectivity cfg/ini file.
    uint32_t issue_instance_id = 1;
    uint32_t dump_instance_id = 1;
    uint32_t bloom_bitblender_instance_id = 0;

    xrt::device device = xrt::device(device_id);
    xrt::uuid xclbin_uuid = device.load_xclbin(config.xclbin_file);

    Aurora aurora_0, aurora_1;
    if (!emulation) {
        aurora_0 = Aurora(0, device, xclbin_uuid);
        aurora_1 = Aurora(1, device, xclbin_uuid);

        check_core_status_global(aurora_0, config.timeout_ms);
        check_core_status_global(aurora_1, config.timeout_ms);

        if (aurora_0.has_framing() != aurora_1.has_framing()) {
            printf("ERROR: FRAMING DIFFERENCES.\\n");
            exit(-1);
        }

        if (!aurora_0.has_framing()) {
            config.frame_size = 0;
        }
    }

    double start_time, finish_time;





    while (test_number < NUM_TESTS_TO_RUN)
    //while (match && test_number < NUM_TESTS_TO_RUN)
    {
        // Seed the random number generator so we have replicatable input vectors.
        srand(1+test_number++);

        // Only do verif if were using a random input sequence
        bool do_verif = 0;

        if (test_number == 1) {
            gen_data_mode = INPUT_GEN_MODE_NO_CLASH;
        }
        else if (test_number == 2) {
            gen_data_mode = INPUT_GEN_MODE_CYCLIC_CLASH;
        }
        else if (test_number == 3) {
            gen_data_mode = INPUT_GEN_MODE_ALL_CLASH;
        }
        else {
            gen_data_mode = INPUT_GEN_MODE_RANDOM;

            if (test_number == 9) {
                do_verif = 1;
                actual_population_inputs = NUM_POPULATION_INPUTS;
            }
            //// These take too long to run...
            //else if (test_number == 5) {
            //    do_verif = 1;
            //    actual_population_inputs = (BV_LENGTH/8);
            //}
            //else if (test_number == 6) {
            //    do_verif = 1;
            //    actual_population_inputs = (BV_LENGTH/32);
            //}
            //else if (test_number == 7) {
            //    do_verif = 1;
            //    actual_population_inputs = (BV_LENGTH/64);
            //}
        }


        ///////////////////////////////////
        // DEBUG PRINTS:
        printf("KDEBUG: TOTAL_NUM_KEYINPUT is %d\\n", TOTAL_NUM_KEYINPUT);
        printf("KDEBUG: actual_population_inputs is %d\\n", actual_population_inputs);
        printf("KDEBUG: BV_LENGTH is %d\\n", BV_LENGTH);
        printf("KDEBUG: BV_SECTION_LENGTH is %d\\n",
                    BV_SECTION_LENGTH);
        printf("KDEBUG: BV_PARTITION_LENGTH_IN_URAM_PACKED_ELEMS is %d\\n",
                    BV_PARTITION_LENGTH_IN_URAM_PACKED_ELEMS);

        printf("\\n");
        printf("KDEBUG: NUM_HASH is %d\\n", NUM_HASH);
        printf("KDEBUG: BV_NUM_PARTITIONS is %d\\n", BV_NUM_PARTITIONS);
        printf("KDEBUG: NUM_STM is %d\\n", NUM_STM);
        printf("KDEBUG: ARB_RATELIM_DISTANCE is %d\\n", ARB_RATELIM_DISTANCE);
        printf("\\n");
        printf("KDEBUG: STM_DEPTH is %d\\n\\n", STM_DEPTH);

        printf("KDEBUG: KEYPAIRS_PER_STM is %d\\n", KEYPAIRS_PER_STM);
        printf("KDEBUG: NUM_PACKED_OUTPUTS is %d\\n", NUM_PACKED_OUTPUTS);

        #if ENABLE_PERF_CTRS
        printf("WARNING! PERFORMANCE COUNTERS ARE ENABLED! WARNING!\\n");
        #endif
        if (NAIVE_MULTISTREAM) {
            printf("WARNING! using NAIVE multistream! WARNING!\\n");
        }
        else {
            printf("Using our BV-sharing multistream design.\\n");
        }

        if (gen_data_mode != INPUT_GEN_MODE_RANDOM) {
            printf("WARNING: ");
        }
        printf("gen_data_mode IS %s\\n\\n", INPUT_GEN_MODE_STRINGS[gen_data_mode]);
        ///////////////////////////////////


        #if ENABLE_PERF_CTRS
        perfctrs.clear();
        for (int i = 0; i < TOTAL_NUM_PERFCTR_OUTPUTS; ++i) {
            perfctrs.push_back(987654321);
        }
        #endif

        reset_krnl_inputs(
            gen_data_mode
            ,do_verif
            ,keys.data()
            ,sw_results.data()
            ,source_bv.data()
        );

        datapack_krnl_inputs(
            do_verif
            ,keys.data()
            ,krnl_key_in_0.data()
            ,source_bv.data()
            ,source_PACKED_bv.data()
        );

        /**********************************************************************/
        /**********************************************************************/
        /***        RUN THE KERNEL                                          ***/
        /**********************************************************************/
        /**********************************************************************/

        IssueKernel bloom_issue(issue_instance_id, device, xclbin_uuid, config);
        DumpKernel bloom_dump(dump_instance_id, device, xclbin_uuid, config);
        BitBlenderKernel bloom_bitblender(
                bloom_bitblender_instance_id
                ,device
                ,xclbin_uuid
                ,config
                ,KEYPAIRS_PER_STM           // packed keys num entries
                ,source_PACKED_bv.size()    // bv num entries
    #if ENABLE_PERF_CTRS
                ,TOTAL_NUM_PERFCTR_OUTPUTS    // perfctrs num entries
    #endif
                ,source_PACKED_bv
        );

        bloom_bitblender.start();
        bloom_dump.start();


        bloom_issue.prepare_bitblender_inputs(krnl_key_in_0);
        start_time = aurora_get_wtime();
        bloom_issue.start();


        if (bloom_issue.timeout()) {
            printf("ERROR: Issue timeout. Something is terribly wrong!\\n");
        }

        if (bloom_bitblender.timeout()) {
            printf("ERROR: BITBLENDER timeout...\\n");

            aurora_0.print_core_status();
            aurora_1.print_core_status();
            exit(-1);
        }
        else {
            printf("BITBLENDER KERNEL FINISHED!!!!\\n");
            finish_time = aurora_get_wtime();
        }

        double runtime = finish_time - start_time;
        std::cout << std::endl << std::endl;
        std::cout << "KERNEL time: " << runtime << " s" << std::endl; // DO NOT CHANGE: This line is used by the datacollection python script.


        /**********************************************************************/
        /**********************************************************************/
        /***        DO VERIFICATION                                         ***/
        /**********************************************************************/
        /**********************************************************************/


        if (do_verif){
            krnl_out_0 = bloom_dump.get_output_data();

            unpack_krnl_outputs(
                krnl_out_0.data(),
                krnl_merged_out.data()
            );

            match = verify(
                sw_results.data(),
                krnl_merged_out.data()
            );
        }

        #if ENABLE_PERF_CTRS
        perfctrs = bloom_bitblender.get_perfctrs_data();
        print_perf_ctrs(perfctrs.data());
        #endif

        std::cout << "------------------------------------------" << std::endl;
        std::cout << "------------------------------------------" << std::endl;
        std::cout << "------------------------------------------" << std::endl;
        std::cout << "------------------------------------------" << std::endl;

    }

    printf("\\n\\n\\n\\n\\n\\n\\n\\nHost is now exiting.\\n\\n\\n\\n\\n\\n\\n\\n");
    return (match ? EXIT_SUCCESS : EXIT_FAILURE);

}
        """)

        return codeArr





    def _generate_aurora_helper_funcs(self):
        codeArr = []
        codeArr.append("""
/*
 * Copyright 2023-2024 Gerrit Pape (papeg@mail.upb.de)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "Aurora.hpp"
#include <fstream>
#include <unistd.h>
#include <vector>
#include "BitBlender.h"
#include <getopt.h>

class Configuration
{
public:
    const char *optstring = "";

    // Defaults
    uint32_t device_id_offset = 0;

    std::string xclbin_file = "";

    uint32_t iterations = 1;
    uint32_t frame_size = 1;
    bool use_ack = false;
    uint32_t timeout_ms = 10000; // 10 seconds

    uint32_t BITBLD_key_loads_num_bytes = 0;
    uint32_t BITBLD_keys_num_loads      = 0;

    uint32_t BITBLD_bv_loads_num_bytes  = 0;
    uint32_t BITBLD_bv_num_loads        = 0;

    uint32_t BITBLD_stores_num_bytes    = 0;
    uint32_t BITBLD_num_stores          = 0;

    Configuration(int argc, char **argv)
    {
        int opt;

        struct option long_options[2] = {};
        long_options[0].name = "bitstream";
        long_options[0].has_arg = 1;
        long_options[0].flag = NULL;
        long_options[0].val = 0;

        while ((opt = getopt_long(argc, argv, optstring, long_options, NULL)) != -1) {
            if (opt == 0 && optarg) {
                xclbin_file = std::string(optarg);
            }
        }

        if (xclbin_file == "") {
            std::cerr << "Error: no bitstream file passed" << std::endl;
            exit(1);
        }

        BITBLD_keys_num_loads       = KEYPAIRS_PER_STM;
        BITBLD_num_stores           = PACKED_OUTPUTS_PER_STM;
        BITBLD_bv_num_loads         = BV_NUM_LOADS;

        BITBLD_bv_loads_num_bytes   = BITBLD_bv_num_loads * sizeof(BV_LOAD_DTYPE);
        BITBLD_key_loads_num_bytes  = BITBLD_keys_num_loads * sizeof(LOAD_DTYPE);
        BITBLD_stores_num_bytes     = BITBLD_num_stores * sizeof(STORE_DTYPE);
    }

    void print()
    {
        std::cout << std::endl;
        std::cout << "------------------------ aurora test ------------------------" << std::endl;
        std::cout << "Number of bytes: " << BITBLD_key_loads_num_bytes << std::endl;
        std::cout << "Selected bitstream: " << xclbin_file << std::endl;
        std::cout << "Frame size: " << frame_size << std::endl;
        //std::cout << "Random data" << std::endl;
        std::cout << "Using ack: " << use_ack << std::endl;
        std::cout << iterations << " iterations" << std::endl;
        std::cout << "Issue/Dump timeout: " << timeout_ms << " ms" << std::endl;
    }

    void write_results(double transmission_time)
    {
        char* hostname;
        hostname = new char[100];
        gethostname(hostname, 100);

        std::ofstream of;
        of.open("results.csv", std::ios_base::app);
        of << "hostname, frame_size, msg_size (B),"
            << " transmission time, used_acks" << std::endl;
        of << hostname
            << "," << frame_size
            << "," << BITBLD_key_loads_num_bytes
            << "," << transmission_time
            << "," << use_ack << std::endl;


        of.close();
    }
};










class IssueKernel
{
public:
    IssueKernel(uint32_t instance, xrt::device &device, xrt::uuid &xclbin_uuid, Configuration &config) : instance(instance), config(config)
    {
        char name[100];
        snprintf(name, 100, "issue:{issue_%u}", instance);
        kernel = xrt::kernel(device, xclbin_uuid, name);

        run = xrt::run(kernel);
        this->device = device;
   }

    void prepare_bitblender_inputs(
        std::vector<LOAD_DTYPE, tapa::aligned_allocator<LOAD_DTYPE>>    & key_input
    )
    {
        if (this->instance == 1) {
            uint64_t num_input_bytes = key_input.size() * sizeof(key_input[0]);
            assert(config.BITBLD_key_loads_num_bytes == num_input_bytes);

            int frame_size = 0;
            int iterations = 1;
            int use_ack = 0;

            data_bo = xrt::bo(device, config.BITBLD_key_loads_num_bytes, xrt::bo::flags::normal, kernel.group_id(1));
            data_bo.write(key_input.data());
            data_bo.sync(XCL_BO_SYNC_BO_TO_DEVICE);

            run.set_arg(1, data_bo);
            run.set_arg(2, config.BITBLD_key_loads_num_bytes);    // Message size
            run.set_arg(3, frame_size);
            run.set_arg(4, iterations);
            run.set_arg(5, use_ack);

            //printf("\\nPREPARE BITBLD INPUTS:\\n");
            //printf("sizeof key_input[0] = %lu\\n", sizeof(key_input[0]));
            //printf("ARG key_input.size() = %lu\\n", key_input.size());
            //printf("ARG num_input_bytes = %lu\\n", num_input_bytes);
            //printf("CFG num_input_bytes = %lu\\n", config.BITBLD_key_loads_num_bytes);
        }
        else {
            printf("ERROR: You're trying to prepare Bitblender inputs for the dump-connected issue?\\n");
        }
    }

    void start()
    {
        run.start();
    }

    bool timeout()
    {
        return run.wait(std::chrono::milliseconds(config.timeout_ms)) == ERT_CMD_STATE_TIMEOUT;
    }

private:
    xrt::device device;
    xrt::bo data_bo;
    xrt::kernel kernel;
    xrt::run run;
    uint32_t instance;
    Configuration &config;
};






class DumpKernel
{
public:

    DumpKernel(uint32_t instance, xrt::device &device, xrt::uuid &xclbin_uuid, Configuration &config) : instance(instance), config(config)
    {
        char name[100];
        snprintf(name, 100, "dump:{dump_%u}", instance);
        kernel = xrt::kernel(device, xclbin_uuid, name);

        run = xrt::run(kernel);

        data_bo = xrt::bo(  device,
                            config.BITBLD_stores_num_bytes,
                            xrt::bo::flags::normal,
                            kernel.group_id(1)
        );

        output_packed_data.resize(config.BITBLD_num_stores);

        run.set_arg(1, data_bo);
        run.set_arg(2, config.BITBLD_stores_num_bytes);
        run.set_arg(3, config.iterations);
        run.set_arg(4, config.use_ack);

        //printf("\\nDUMP KERNEL:\\n");
        //printf("CFG store bytes = %lu\\n",   config.BITBLD_stores_num_bytes);
        //printf("CFG num_stores = %lu\\n",    config.BITBLD_num_stores);
        //printf("output_packed_data.size() = %lu\\n", output_packed_data.size());
    }

    void start()
    {
        run.start();
    }

    bool timeout()
    {
        return run.wait(std::chrono::milliseconds(config.timeout_ms)) == ERT_CMD_STATE_TIMEOUT;
    }

    std::vector<STORE_DTYPE, tapa::aligned_allocator<STORE_DTYPE>>  get_output_data()
    {
        data_bo.sync(XCL_BO_SYNC_BO_FROM_DEVICE);
        data_bo.read(output_packed_data.data());
        return output_packed_data;
    }


    std::vector<STORE_DTYPE,    tapa::aligned_allocator<STORE_DTYPE>>       output_packed_data;

private:
    xrt::bo data_bo;
    xrt::kernel kernel;
    xrt::run run;
    uint32_t instance;
    Configuration &config;
};








class BitBlenderKernel
{
public:

    BitBlenderKernel(uint32_t instance
                    ,xrt::device &device
                    ,xrt::uuid &xclbin_uuid
                    ,Configuration &config
                    ,uint32_t packed_inputs_num_entries
                    ,uint32_t bv_num_entries
#if ENABLE_PERF_CTRS
                    ,int perfctr_entries
#endif
                    ,std::vector<BV_LOAD_DTYPE, tapa::aligned_allocator<BV_LOAD_DTYPE>>  packed_bv_data
    ) : instance(instance), config(config)
    {
        char name[100];
        snprintf(name, 100, "workload:{workload_%u}", instance);
        kernel = xrt::kernel(device, xclbin_uuid, name);

        run = xrt::run(kernel);

        bv_bo = xrt::bo(    device
                            ,bv_num_entries * sizeof(BV_LOAD_DTYPE)
                            ,xrt::bo::flags::normal
                            ,kernel.group_id(0)
        );
        bv_bo.write(packed_bv_data.data());
        bv_bo.sync(XCL_BO_SYNC_BO_TO_DEVICE);
        /**********************************************/

#if ENABLE_PERF_CTRS
        perfctrs_data.resize(perfctr_entries);
        perfctrs_bo = xrt::bo(  device
                                ,perfctr_entries * sizeof(PERFCTR_DTYPE)
                                ,xrt::bo::flags::normal
                                ,kernel.group_id(3)
        );
#endif

        run.set_arg(0, bv_bo);
#if ENABLE_PERF_CTRS
        run.set_arg(3, perfctrs_bo);
        run.set_arg(4, packed_inputs_num_entries);
#else
        run.set_arg(3, packed_inputs_num_entries);
#endif

        //printf("\\nBITBLENDER KERNEL:\\n");
        //printf("CFG BV entries = %lu\\n",    config.BITBLD_bv_num_loads);
        //printf("ARG BV entries = %lu\\n",    bv_num_entries);
        //printf("sizeof(BV_LOAD_DTYPE) = %lu\\n", sizeof(BV_LOAD_DTYPE));

        //printf("CFG packed keyinputs = %lu\\n",  config.BITBLD_keys_num_loads);
        //printf("ARG packed keyinputs= %lu\\n",   packed_inputs_num_entries);
        //printf("sizeof(LOAD_DTYPE) = %lu\\n",        sizeof(LOAD_DTYPE));
    }

    void start()
    {
        run.start();
    }

    bool timeout()
    {
        return run.wait(std::chrono::milliseconds(config.timeout_ms)) == ERT_CMD_STATE_TIMEOUT;
    }


    std::vector<LOAD_DTYPE, tapa::aligned_allocator<LOAD_DTYPE>>  get_debug_in_data()
    {
        debug_in_bo.sync(XCL_BO_SYNC_BO_FROM_DEVICE);
        debug_in_bo.read(DEBUG_input_data.data());
        return DEBUG_input_data;
    }


    std::vector<STORE_DTYPE, tapa::aligned_allocator<STORE_DTYPE>>  get_debug_out_data()
    {
        debug_out_bo.sync(XCL_BO_SYNC_BO_FROM_DEVICE);
        debug_out_bo.read(DEBUG_output_packed_data.data());
        return DEBUG_output_packed_data;
    }


    std::vector<PERFCTR_DTYPE, tapa::aligned_allocator<PERFCTR_DTYPE>>  get_perfctrs_data()
    {
#if ENABLE_PERF_CTRS
        perfctrs_bo.sync(XCL_BO_SYNC_BO_FROM_DEVICE);
        perfctrs_bo.read(perfctrs_data.data());
#endif
        return perfctrs_data;
    }

    std::vector<LOAD_DTYPE,     tapa::aligned_allocator<LOAD_DTYPE>>        DEBUG_input_data;
    std::vector<STORE_DTYPE,    tapa::aligned_allocator<STORE_DTYPE>>       DEBUG_output_packed_data;
    std::vector<PERFCTR_DTYPE,  tapa::aligned_allocator<PERFCTR_DTYPE>>     perfctrs_data;

private:
    xrt::bo bv_bo;
    xrt::bo debug_out_bo;
    xrt::bo debug_in_bo;
    xrt::kernel kernel;
    xrt::run run;
    uint32_t instance;
    Configuration &config;

#if ENABLE_PERF_CTRS
    xrt::bo perfctrs_bo;
#endif
};






void check_core_status_global(Aurora &aurora, size_t timeout_ms)
{
    bool local_core_ok;
    local_core_ok = aurora.core_status_ok(3000);

    if (!local_core_ok) {
        std::cout << "problem with one of the aurora cores... #" << aurora.aurora_number << std::endl;
        //exit(-1);
    }
}
        """)
        return codeArr










####################
####################
####################
####################
####################
####################
####################
####################
####################






    def generate_tapa_host(self):
        codeArr = []
        codeArr.extend(self._generate_common_includes())
        codeArr.extend(self._generate_krnl_declaration())
        codeArr.extend(self._generate_tapa_host_main_func())
        return codeArr




    def generate_aurora_host(self):
        codeArr = []
        codeArr.extend(self._generate_common_includes())
        codeArr.extend(self._generate_aurora_host_main_func())
        return codeArr



    def generate_aurorahelpers_file(self):
        codeArr = []
        codeArr.extend(self._generate_aurora_helper_funcs())
        return codeArr




    def generate_bitblender_dataprep_file(self):
        codeArr = []
        codeArr.extend(self._generate_bitblender_helper_funcs())
        return codeArr












    def generate_aurora_hpp_file(self):
        codeArr = []
        codeArr.append("""/*
 * Copyright 2023-2024 Gerrit Pape (papeg@mail.upb.de)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef __AURORA_HPP__
#define __AURORA_HPP__

#include "experimental/xrt_kernel.h"
#include "experimental/xrt_ip.h"
#include <cmath>
#include <bitset>

double aurora_get_wtime()
{
    struct timespec time;
    clock_gettime(CLOCK_REALTIME, &time);
    return time.tv_sec + (double)time.tv_nsec / 1e9;
}

// control s axi addresses
static const uint32_t CORE_STATUS_ADDRESS        = 0x00000010;
static const uint32_t FIFO_STATUS_ADDRESS        = 0x00000014;
static const uint32_t CONFIGURATION_ADDRESS      = 0x00000018;
static const uint32_t FIFO_THRESHOLDS_ADDRESS    = 0x0000001c;
static const uint32_t FRAMES_RECEIVED_ADDRESS    = 0x00000020;
static const uint32_t FRAMES_WITH_ERRORS_ADDRESS = 0x00000024;

// masks for core status bits
static const uint32_t GT_POWERGOOD        = 0x0000000f;
static const uint32_t LINE_UP             = 0x000000f0;
static const uint32_t GT_PLL_LOCK         = 0x00000100;
static const uint32_t MMCM_NOT_LOCKED_OUT = 0x00000200;
static const uint32_t HARD_ERR            = 0x00000400;
static const uint32_t SOFT_ERR            = 0x00000800;
static const uint32_t CHANNEL_UP          = 0x00001000;

static const uint32_t CORE_STATUS_OK = GT_POWERGOOD | LINE_UP | GT_PLL_LOCK | CHANNEL_UP;

// masks for fifo status bits
static const uint32_t FIFO_TX_PROG_EMPTY   = 0x00000001;
static const uint32_t FIFO_TX_ALMOST_EMPTY = 0x00000002;
static const uint32_t FIFO_TX_PROG_FULL    = 0x00000004;
static const uint32_t FIFO_TX_ALMOST_FULL  = 0x00000008;
static const uint32_t FIFO_RX_PROG_EMPTY   = 0x00000010;
static const uint32_t FIFO_RX_ALMOST_EMPTY = 0x00000020;
static const uint32_t FIFO_RX_PROG_FULL    = 0x00000040;
static const uint32_t FIFO_RX_ALMOST_FULL  = 0x00000080;
static const char *fifo_status_name[8] = {
    "FIFO tx prog empty",
    "FIFO tx almost empty",
    "FIFO tx prog full",
    "FIFO tx almost full",
    "FIFO rx prog empty",
    "FIFO rx almost empty",
    "FIFO rx prog full",
    "FIFO rx almost full",
};

// masks for configuration bits
static const uint32_t HAS_TKEEP         = 0x000001;
static const uint32_t HAS_TLAST         = 0x000002;
static const uint32_t FIFO_WIDTH        = 0x0007fc;
static const uint32_t FIFO_DEPTH        = 0x007800;
static const uint32_t RX_EQ_MODE_BINARY = 0x018000;
static const uint32_t INS_LOSS_NYQ      = 0x3e0000;
static const char *rx_eq_mode_names[4] = {
    "AUTO",
    "LPM",
    "DFE",
    ""
};

class Aurora
{
public:
    Aurora(xrt::ip ip) : ip(ip)
    {
        // read constant configuration information
        uint32_t configuration = ip.read_register(CONFIGURATION_ADDRESS);

        has_tkeep = (configuration & HAS_TKEEP);
        has_tlast = (configuration & HAS_TLAST) >> 1;
        fifo_width = (configuration & FIFO_WIDTH) >> 2;
        fifo_depth = pow(2, (configuration & FIFO_DEPTH) >> 11);
        rx_eq_mode = (configuration & RX_EQ_MODE_BINARY) >> 15;
        ins_loss_nyq = (configuration & INS_LOSS_NYQ) >> 17;

        uint32_t fifo_thresholds = ip.read_register(FIFO_THRESHOLDS_ADDRESS);

        fifo_prog_full_threshold = (fifo_thresholds & 0xffff0000) >> 16;
        fifo_prog_empty_threshold = (fifo_thresholds & 0x0000ffff);
    }

    Aurora(std::string name, xrt::device &device, xrt::uuid &xclbin_uuid)
        : Aurora(xrt::ip(device, xclbin_uuid, name)) {}

    std::string create_name_from_instance(uint32_t instance)
    {
        char name[100];
        snprintf(name, 100, "aurora_hls_%u:{aurora_hls_%u}", instance, instance);
        return std::string(name);
    }

    Aurora(uint32_t instance, xrt::device &device, xrt::uuid &xclbin_uuid)
        : Aurora(create_name_from_instance(instance), device, xclbin_uuid)
    {
        aurora_number = instance;
    }

    Aurora() {}

    bool has_framing()
    {
        return has_tlast;
    }

    const char *get_rx_eq_mode_name()
    {
        return rx_eq_mode_names[rx_eq_mode];
    }

    void print_configuration()
    {
        std::cout << "Aurora configuration: " << std::endl;
        std::cout << "has tlast: " << has_tlast << std::endl;
        std::cout << "has tkeep: " << has_tkeep << std::endl;
        std::cout << "FIFO width: " << fifo_width << std::endl;
        std::cout << "FIFO depth: " << fifo_depth << std::endl;
        std::cout << "FIFO full threshold: " << fifo_prog_full_threshold << std::endl;
        std::cout << "FIFO empty threshold: " << fifo_prog_empty_threshold << std::endl;
        std::cout << "Equalization mode: " << rx_eq_mode_names[rx_eq_mode] << std::endl;
        std::cout << "Nyquist loss: " << (uint16_t)ins_loss_nyq << std::endl;
    }

    uint32_t get_core_status()
    {
        return ip.read_register(CORE_STATUS_ADDRESS);
    }

    uint8_t gt_powergood()
    {
        return (get_core_status() & GT_POWERGOOD);
    }

    uint8_t line_up()
    {
        return (get_core_status() & LINE_UP) >> 4;
    }

    bool gt_pll_lock()
    {
        return (get_core_status() & GT_PLL_LOCK);
    }

    bool mmcm_not_locked_out()
    {
        return (get_core_status() & MMCM_NOT_LOCKED_OUT);
    }

    bool hard_err()
    {
        return (get_core_status() & HARD_ERR);
    }

    bool soft_err()
    {
        return (get_core_status() & SOFT_ERR);
    }

    bool channel_up()
    {
        return (get_core_status() & CHANNEL_UP);
    }

    void print_core_status()
    {
        uint32_t reg_read_data = get_core_status();
        std::cout << "GT Power good: " << std::bitset<4>(reg_read_data & GT_POWERGOOD) << std::endl;
        std::cout << "Lines up: " << std::bitset<4>((reg_read_data & LINE_UP) >> 4) << std::endl;
        if (reg_read_data & GT_PLL_LOCK)
        {
            std::cout << "GT PLL Lock" << std::endl;
        }
        if (reg_read_data & MMCM_NOT_LOCKED_OUT)
        {
            std::cout << "MMCM not locked out" << std::endl;
        }
        if (reg_read_data & HARD_ERR)
        {
            std::cout << "Hard error detected" << std::endl;
        }
        if (reg_read_data & SOFT_ERR)
        {
            std::cout << "Soft error detected" << std::endl;
        }
        if (reg_read_data & CHANNEL_UP)
        {
            std::cout << "Channel up" << std::endl;
        }
    }

    bool core_status_ok(size_t timeout_ms)
    {
        double timeout_start, timeout_finish;
        timeout_start = aurora_get_wtime();
        while (1) {
            uint32_t reg_read_data = get_core_status();
            if (reg_read_data == CORE_STATUS_OK) {
                return true;
            } else {
                timeout_finish = aurora_get_wtime();
                if (((timeout_finish - timeout_start) * 1000) > timeout_ms) {
                    printf("reg_read_data = %x\\n", reg_read_data);
                    return false;
                }
            }
        }
    }

    uint32_t get_fifo_status()
    {
        return ip.read_register(FIFO_STATUS_ADDRESS);
    }

    bool fifo_tx_is_prog_empty()
    {
        return (get_fifo_status() & FIFO_TX_PROG_EMPTY);
    }

    bool fifo_tx_is_almost_empty()
    {
        return (get_fifo_status() & FIFO_TX_ALMOST_EMPTY);
    }

    bool fifo_tx_is_prog_full()
    {
        return (get_fifo_status() & FIFO_TX_PROG_FULL);
    }

    bool fifo_tx_is_almost_full()
    {
        return (get_fifo_status() & FIFO_TX_ALMOST_FULL);
    }

    bool fifo_rx_is_prog_empty()
    {
        return (get_fifo_status() & FIFO_RX_PROG_EMPTY);
    }

    bool fifo_rx_is_almost_empty()
    {
        return (get_fifo_status() & FIFO_RX_ALMOST_EMPTY);
    }

    bool fifo_rx_is_prog_full()
    {
        return (get_fifo_status() & FIFO_RX_PROG_FULL);
    }

    bool fifo_rx_is_almost_full()
    {
        return (get_fifo_status() & FIFO_RX_ALMOST_FULL);
    }

    void print_fifo_status()
    {
        uint32_t fifo_status = get_fifo_status();
        for (uint32_t bit = 0; bit < 8; bit++) {
            if (fifo_status & (1 << bit)) {
                std::cout << fifo_status_name[bit] << std::endl;
            }
        }
    }

    uint32_t get_frames_received()
    {
        if (has_tlast) {
            return ip.read_register(FRAMES_RECEIVED_ADDRESS);
        } else {
            return -1;
        }
    }

    uint32_t get_frames_with_errors()
    {
        if (has_tlast) {
            return ip.read_register(FRAMES_WITH_ERRORS_ADDRESS);
        } else {
            return -1;
        }
    }

    bool has_tkeep;
    bool has_tlast;
    uint16_t fifo_width;
    uint16_t fifo_depth;
    uint8_t rx_eq_mode;
    uint8_t ins_loss_nyq;
    uint16_t fifo_prog_full_threshold;
    uint16_t fifo_prog_empty_threshold;

    int aurora_number;

private:
    xrt::ip ip;
};


#endif // __AURORA_HPP__
        """)
        return codeArr















####################
####################
####################
####################
####################
####################
####################
####################
####################







    def generate_all_host_files(self):
        fname = "Aurora.hpp"
        with open(fname, 'w') as f:
            f.writelines(self.generate_aurora_hpp_file())

        fname = "host_QSFP_aurora.cpp"
        with open(fname, 'w') as f:
            f.writelines(self.generate_aurora_host())

        fname = "hostside_bitblender_dataprep.cpp"
        with open(fname, 'w') as f:
            f.writelines(self.generate_bitblender_dataprep_file())

        fname = "hostside_aurorahelpers.cpp"
        with open(fname, 'w') as f:
            f.writelines(self.generate_aurorahelpers_file())

        fname = "host_HBM.cpp"
        with open(fname, 'w') as f:
            f.writelines(self.generate_tapa_host())










