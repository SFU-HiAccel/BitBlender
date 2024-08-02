#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include "SW_MurmurHash3.cpp"
#include "MurmurHash3.h"
#include "my_timer.h"
#include <random>
#include <chrono>


bool verify(bool *final_results){
    for (int i = 0; i < NUM_POPULATION_INSERTS; ++i){
        if (final_results[i] != 1){
            printf("FAILED\n");
            return 0;
        }
    }

    return 1;
}


int main(){

    std::mt19937 rng(5353);

    uint32_t *key1 = new uint32_t[NUM_QUERIES];
    uint32_t seed[NUM_HASH] = {0};
    bool    *final_results = new bool[NUM_QUERIES]; 
    bool    *bv = new bool[BV_LENGTH];

    uint32_t tmp_hash = 0;

    for(int i = 0; i < NUM_HASH; i ++){
        seed[i] = i;
    }

    for (size_t i = 0; i < BV_LENGTH; ++i) {
        bv[i] = 0;
    }

    // Fill the input vectors with data
    for (uint32_t i = 0; i < NUM_QUERIES; i++) {
        // Better randomization : https://codeforces.com/blog/entry/61587
        //key1[i] = rand();
        key1[i] = rng();
    }

    // Populate the bit-vector with the first few inputs
    for (uint32_t i = 0; i < NUM_POPULATION_INSERTS; i++) {
        if (i < NUM_POPULATION_INSERTS){
            for (int j = 0; j < NUM_HASH; j++) {
                SW_MurmurHash3_x86_32(key1 + i, key_width, seed[j], &tmp_hash);
                bv[tmp_hash%BV_LENGTH] = 1;
            }
        }
    }

    timespec starttime = tic();

    omp_set_dynamic(0);
    omp_set_num_threads(24);//40, 1.15;36, 1.25

    for(int l=0; l<NUM_ITERATIONS; l++){
        uint32_t i, j, k;
        #pragma omp parallel for private(tmp_hash)
        for (i = 0; i < NUM_QUERIES; i++) {
            for (j = 0; j < NUM_HASH; j++) {
                SW_MurmurHash3_x86_32(key1 + i, key_width, seed[j], &tmp_hash);

                final_results[i] |= bv[ tmp_hash%BV_LENGTH];
            }
        }
    }

    timespec endtime = tic();
    timespec total_time = diff(starttime, endtime);

    verify(final_results);

    printf("NUM_HASH = %d, NUM_QUERIES = %d, BV_LENGTH(Mi) = %d, NUM_INSERTIONS = %d\n", NUM_HASH, NUM_QUERIES, BV_LENGTH/(1024*1024), NUM_POPULATION_INSERTS);
    printf("Total time: %d.%09d\n", (int)total_time.tv_sec, (int)total_time.tv_nsec);
    printf("NUM_ITERATIONS = %d\n", NUM_ITERATIONS);
    printf("\n\n\n");

    return 0;
}
