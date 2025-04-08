
from codegen.normal_krnl.krnl_gen_toplevel  import TopLevelCodeGenerator as NORMAL_TopLevelCodeGenerator
from codegen.naive_krnl.krnl_NAIVE_gen_toplevel import TopLevelCodeGenerator as NAIVE_TopLevelCodeGenerator
from codegen.types import DesignType

class HostCodeGenerator:
    def __init__(self, config):
        self.config = config



    def generate_header(self):
        codeArr = []

        codeArr.append(
"""#include <algorithm>
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

#include "MurmurHash3.h"
#include "SW_MurmurHash3.cpp"

#ifndef NAIVE_MULTISTREAM
void crash_compilation(
    crash compilation
    You need to define NAIVE_MULTISTREAM when compiling!
}
#endif

using std::chrono::high_resolution_clock;
DEFINE_string(bitstream, "", "Path to bitstream file. Run SW_EMU if empty.");

int actual_population_inputs;    // Modified later

// https://stackoverflow.com/questions/9907160/how-to-convert-enum-names-to-string-in-c
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

""")
        return codeArr






    def generate_krnl_declaration(self):
        codeArr = []

        if (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            topLevel = NAIVE_TopLevelCodeGenerator(self.config)
        elif (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            topLevel = NORMAL_TopLevelCodeGenerator(self.config)

        codeArr.extend(topLevel.generate_func_declaration())
        codeArr.append(';' + "\n")

        return codeArr



    def generate_datapack_bv(self):
        codeArr = []

        codeArr.append('void datapack_bv(' + "\n")
        codeArr.append('    BIT_DTYPE *bv' + "\n")
        codeArr.append('    ,BV_LOAD_DTYPE *packed_bv' + "\n")
        codeArr.append(') {' + "\n")

        for h in range(self.config.num_hash):
            codeArr.append('    std::vector<BV_URAM_PACKED_DTYPE> bv_section{h}(BV_SECTION_LENGTH_IN_URAM_PACKED_ELEMS);'.format(h=h) + "\n")

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

        return codeArr








    def generate_helper_funcs(self):
        codeArr = []
        codeArr.append("""
bool min(int in1, int in2) {
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
    for (int in = 0, im = 0; 
            in < TOTAL_NUM_KEYINPUT && im < actual_population_inputs; 
            ++in) {
        int rn = TOTAL_NUM_KEYINPUT - in;
        int rm = actual_population_inputs - im;
        if (rand() % rn < rm){
            input_idces_to_add[im++] = in;
        }
    }

    // Use those input indices to populate the BV.
    for (uint32_t i = 0; i < actual_population_inputs; ++i) {
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
    int cur_failed_idx = 0;


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
    for (int i = 0; i < NUM_PERFCTRS; ++i)
    {
        for (int j = 0; j < NUM_PERFCTR_OUTPUTS; ++j)
        {
            printf("perfctr[%5d][%5d] = %25lu\\n",
                    i, j, perfctrs[i*NUM_PERFCTR_OUTPUTS + j]
            );
        }

        // CHECKING TO MAKE SURE THE CYCLES MATCH UP AS EXPECTED:
        int idx = i*NUM_PERFCTR_OUTPUTS;
        PERFCTR_DTYPE sum = perfctrs[idx + 0] + 
                            perfctrs[idx + 1] + 
                            perfctrs[idx + 2] + 
                            perfctrs[idx + 3];

        if ( sum != perfctrs[idx + 4] )
        {
            printf("ERROR: SOMETHING IS WEIRD! My sum = %lu, total cycles = %lu\\n",
                    sum, perfctrs[idx + 4]
            );
        }
        if (perfctrs[idx+0] == 0 ||
            perfctrs[idx+1] == 0 ||
            perfctrs[idx+2] == 0 ||
            perfctrs[idx+3] == 0 ||
            perfctrs[idx+4] == 0)
        {
            printf("ERROR: Why is one or more of the perfcrs zero?\\n");
        }


        printf("\\n");
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



int reset(
    INPUT_GEN_MODE_ENUM input_generation_mode
    ,bool       do_verif
    ,KEY_DTYPE *keys
    ,BIT_DTYPE *sw_results
    ,BIT_DTYPE *bv
    ,BV_LOAD_DTYPE *packed_bv
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
    int num_desired_hits = 0;

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

        // Datapack the bitvector
        datapack_bv(bv, packed_bv);

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
            printf("\\n\\n\\nERROR. FP RATES ARE DIFFERENT BY %lf\\n",
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
    #ifdef __DO_DEBUG_PRINTS__
    const int START_DEBUG_PRINTS = 0;
    const int END_DEBUG_PRINTS = 3;
    for (int i = START_DEBUG_PRINTS; i < END_DEBUG_PRINTS; ++i) {
        printf("HOST: packed_BV[%d] = %x\\n", i, packed_bv_0[i].to_int());
        for (int j = 0; j < BV_URAM_PACKED_BITWIDTH; ++j) {
            int total_idx = i*BV_URAM_PACKED_BITWIDTH + j;
            printf("HOST: BV[%d] = %d\\n", total_idx, bv[total_idx].to_int());
        }
        printf("\\n");
    }
    #endif

    return 0;
}

"""
        )

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



    def generate_main_func(self):

        codeArr = []
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('int main(int argc, char **argv) {' + "\n")
        codeArr.append('    gflags::ParseCommandLineFlags(&argc, &argv, /*remove_flags=*/true);' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    bool match = 1;' + "\n")
        codeArr.append('    const int NUM_TESTS_TO_RUN = 10;' + "\n")
        codeArr.append('    int test_number = 0;' + "\n")
        codeArr.append('    INPUT_GEN_MODE_ENUM     gen_data_mode;' + "\n")
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
            codeArr.append('    std::vector<LOAD_DTYPE, tapa::aligned_allocator<LOAD_DTYPE>>        krnl_key_in;' + "\n")
            codeArr.append('    std::vector<STORE_DTYPE, tapa::aligned_allocator<STORE_DTYPE>>      krnl_out;' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    const int TOTAL_NUM_PERFCTR_OUTPUTS = NUM_PERFCTRS * NUM_PERFCTR_OUTPUTS;' + "\n")
        codeArr.append('    std::vector<PERFCTR_DTYPE, tapa::aligned_allocator<PERFCTR_DTYPE>>    perfctrs(TOTAL_NUM_PERFCTR_OUTPUTS);' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    // SANITY CHECKS:' + "\n")
        codeArr.append('    #if (BV_LENGTH % BV_URAM_PACKED_BITWIDTH != 0)' + "\n")
        codeArr.append('    crash(;' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('    #if ( (KEY_BITWIDTH/8) * TOTAL_NUM_KEYINPUT > (1024*1024*256) )' + "\n")
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
            codeArr.append('        if (test_number == 4) {' + "\n")
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
            codeArr.append('            if (test_number == 4) {' + "\n")
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
        codeArr.append('        printf("KDEBUG: SHUFFLEBUF_SZ is %d\\n", SHUFFLEBUF_SZ);' + "\n")
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
        codeArr.append('' + "\n")
        codeArr.append('        ///////////////////////////////////' + "\n")
        codeArr.append('' + "\n")

        if (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            codeArr.append('        for (int i = 0; i < NUM_STM; ++i) {' + "\n")
            codeArr.append('            krnl_key_in[i].clear();' + "\n")
            codeArr.append('            krnl_out[i].clear();' + "\n")
            codeArr.append('        }' + "\n")
        elif (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            codeArr.append('        krnl_key_in.clear();' + "\n")
            codeArr.append('        krnl_out.clear();' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        perfctrs.clear();' + "\n")
        codeArr.append('        for (int i = 0; i < TOTAL_NUM_PERFCTR_OUTPUTS; ++i) {' + "\n")
        codeArr.append('            perfctrs.push_back(987654321);' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        reset(' + "\n")
        codeArr.append('            gen_data_mode' + "\n")
        codeArr.append('            ,do_verif' + "\n")
        codeArr.append('            ,keys.data()' + "\n")
        codeArr.append('            ,sw_results.data()' + "\n")
        codeArr.append('            ,source_bv.data()' + "\n")
        codeArr.append('            ,source_PACKED_bv.data()' + "\n")
        codeArr.append('        );' + "\n")
        codeArr.append('' + "\n")

        ################

        if (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            codeArr.append('        // Pack the key inputs for the kernel.' + "\n")
            codeArr.append('        for (int i = 0; i < KEYPAIRS_PER_STM; ++i)' + "\n")
            codeArr.append('        {' + "\n")
            codeArr.append('            LOAD_DTYPE cur_packed_input;' + "\n")
            codeArr.append('' + "\n")

            for s in range(0, self.config.num_stm):
                codeArr.append('            cur_packed_input.s{s}_k0 = keys[i*2*NUM_STM + 2*{s} + 0];'.format(s=s) + "\n")
                codeArr.append('            cur_packed_input.s{s}_k1 = keys[i*2*NUM_STM + 2*{s} + 1];'.format(s=s) + "\n")
                codeArr.append('' + "\n")
            codeArr.append('            #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
            codeArr.append('            crash on purpose(,' + "\n")
            codeArr.append('            #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            krnl_key_in.push_back(cur_packed_input);' + "\n")
            codeArr.append('        }' + "\n")

        elif (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
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
            codeArr.append('        for (int j = 0; j < PACKED_OUTPUTS_PER_STM; ++j) {' + "\n")
            codeArr.append('            // Fill the kernels output bufs with some initial values to help debug.' + "\n")
            codeArr.append('            STORE_DTYPE dummy;' + "\n")

            for s in range(0, self.config.keys_axi_port_pack_factor):
                if (s < self.config.num_stm):
                    codeArr.append('            dummy.s{s}_k0 = 123123;'.format(s=s) + "\n")
                    codeArr.append('            dummy.s{s}_k1 = 123123;'.format(s=s) + "\n")
                else:
                    codeArr.append('            dummy.padding_{s}_k0 = 123123;'.format(s=s) + "\n")
                    codeArr.append('            dummy.padding_{s}_k1 = 123123;'.format(s=s) + "\n")

            codeArr.append('            krnl_out.push_back(dummy);' + "\n")
            codeArr.append('        }' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('        auto start = high_resolution_clock::now();' + "\n")


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
            codeArr.append('            , 12345' + "\n")
            codeArr.append('        );' + "\n")

        elif (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            codeArr.append('        int64_t kernel_time_ns = tapa::invoke(' + "\n")
            codeArr.append('            workload,' + "\n")
            codeArr.append('            FLAGS_bitstream,' + "\n")
            codeArr.append('             tapa::read_only_mmap<BV_LOAD_DTYPE>(source_PACKED_bv)' + "\n")
            codeArr.append('' + "\n")

            codeArr.append('            ,tapa::read_only_mmap<LOAD_DTYPE>(krnl_key_in)' + "\n")
            codeArr.append('            ,tapa::write_only_mmap<STORE_DTYPE>(krnl_out)' + "\n")

            codeArr.append('' + "\n")
            codeArr.append('            #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
            codeArr.append('            , ! //crash on purpose; we need to manually add more streams.' + "\n")
            codeArr.append('            #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            #if ENABLE_PERF_CTRS' + "\n")
            codeArr.append('            ,tapa::write_only_mmap<PERFCTR_DTYPE>(perfctrs)' + "\n")
            codeArr.append('            #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            , 12345' + "\n")
            codeArr.append('        );' + "\n")



        codeArr.append('' + "\n")
        codeArr.append('        std::cout << "KERNEL time: " << kernel_time_ns * 1e-9 << " s" << std::endl;' + "\n")
        codeArr.append('        ' + "\n")

        codeArr.append('        if (do_verif){' + "\n")
        codeArr.append('            // Merge the kernel outputs into one big array.' + "\n")
        if (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            codeArr.append('            int merged_bit_idx = 0;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            for (int i = 0; i < NUM_STM; ++i) {' + "\n")
            codeArr.append('                for (int j = 0; j < PACKED_OUTPAIRS_PER_STM; ++j) {' + "\n")
            codeArr.append('                    for (int bidx = 0; bidx < OUT_PACKED_BITWIDTH; ++bidx) {' + "\n")
            codeArr.append('                        krnl_merged_out[merged_bit_idx++] = krnl_out[i][j].range(bidx, bidx);' + "\n")
            codeArr.append('                    }' + "\n")
            codeArr.append('                }' + "\n")
            codeArr.append('            }' + "\n")

        elif (self.config.design_type == DesignType.NORMAL_MULTISTREAM):
            codeArr.append('            int out_bit_idx = 0;' + "\n")
            codeArr.append('            for (int i = 0; i < PACKED_OUTPUTS_PER_STM; ++i)' + "\n")
            codeArr.append('            {' + "\n")
            codeArr.append('                for (int j = 0; j < OUT_PACKED_BITWIDTH; ++j)' + "\n")
            codeArr.append('                {' + "\n")

            for s in range(0, self.config.keys_axi_port_pack_factor):
                if (s < self.config.num_stm):
                    codeArr.append('                        krnl_merged_out[out_bit_idx++].range(0, 0) =' + "\n")
                    codeArr.append('                            krnl_out[i].s{s}_k0.range(j, j);'.format(s=s) + "\n")
                    codeArr.append('                        krnl_merged_out[out_bit_idx++].range(0, 0) =' + "\n")
                    codeArr.append('                            krnl_out[i].s{s}_k1.range(j, j);'.format(s=s) + "\n")
                    codeArr.append('' + "\n")

            codeArr.append('                }' + "\n")
            codeArr.append('            }' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('            match = verify(' + "\n")
        codeArr.append('                sw_results.data(),' + "\n")
        codeArr.append('                krnl_merged_out.data()' + "\n")
        codeArr.append('            );' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        std::cout << "------------------------------------------" << std::endl;' + "\n")
        codeArr.append('        std::cout << "------------------------------------------" << std::endl;' + "\n")
        codeArr.append('        std::cout << "------------------------------------------" << std::endl;' + "\n")
        codeArr.append('        std::cout << "------------------------------------------" << std::endl;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        print_perf_ctrs(perfctrs.data());' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    printf("\\n\\n\\n\\n\\n\\n\\n\\nHost is now exiting.\\n\\n\\n\\n\\n\\n\\n\\n");' + "\n")
        codeArr.append('    return (match ? EXIT_SUCCESS : EXIT_FAILURE);' + "\n")
        codeArr.append('}' + "\n")

        return codeArr





    def generate(self):
        codeArr = []
        codeArr.extend(self.generate_header())
        codeArr.extend(self.generate_krnl_declaration())
        codeArr.extend(self.generate_datapack_bv())
        codeArr.extend(self.generate_helper_funcs())

        codeArr.extend(self.generate_main_func())
        return codeArr





















