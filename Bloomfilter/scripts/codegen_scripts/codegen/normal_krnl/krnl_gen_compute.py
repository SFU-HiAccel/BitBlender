
class ComputeCodeGenerator:
    def __init__(self, config):
        self.config = config

    def generate_murmurhash(self):
        codeArr = []
        codeArr.append(
"""
uint32_t MurmurHash3_x86_32 (
    KEY_DTYPE key,
    uint32_t seed
){
#pragma HLS inline
    const int nblocks = KEY_SIZE_IN_BYTES / 4;
    uint32_t h1 = seed;
    const uint32_t c1 = 0xcc9e2d51;
    const uint32_t c2 = 0x1b873593;

    //length is limited as this:  KEY_SIZE_IN_BYTES / 4  <= KEY_SIZE_IN_BYTES
    BLOCK_DIVIDING:
    for( int i = 0; i < nblocks; i++){
    #pragma HLS UNROLL
        KEY_DTYPE tmp;
        tmp.range(31,0) = key.range(32*i+31, 32*i);

        uint32_t k1 = tmp;
        k1 *= c1;
        // copy-paste the body of the rotl() function, otherwise it doesn't work.
        //k1 = ROTL32(k1,15);
        k1 = ( (k1 << 15) | (k1 >> (17)) );
        k1 = k1*c2;

        h1 ^= k1;
        // copy-paste the body of the rotl() function, otherwise it doesn't work.
        //h1 = ROTL32(h1,13);
        h1 = ( (h1 << 13) | (h1 >> 19) );
        h1 = h1*5 + 0xe6546b64;

        #if PRINT_HASH_VALUES
        printf("KERNEL DEBUG: key = %d, k = %d, h = %d, i = %d\\n",
                key.to_int(), k1, h1, i
        );
        #endif
        
    }
    //Remainder from block division
    uint32_t tail = key[nblocks];

    //Finalization
    h1 ^= KEY_SIZE_IN_BYTES;
    //h1 = fmix32(h1);
    h1 ^= h1>>16;
    h1 *= 0x85ebca6b;
    h1 ^= h1>>13;
    h1 *= 0xc2b2ae35;
    h1 ^= h1>>16;

    uint32_t retval;
    //retval = (uint32_t)key * (seed+3);
    retval = h1;
    return retval;
}
"""
        )
        codeArr.append("\n\n\n")
        return codeArr


    
    def generate_computeHash_feeder(self):
        codeArr = []
        codeArr.append('void computeHash_Feeder(' + "\n")
        codeArr.append('        int                                 strm_idx,' + "\n")
        codeArr.append('        int                                 keypair_idx,' + "\n")
        codeArr.append('        tapa::istream<KEY_DTYPE>            & key_in_stream,' + "\n")
        codeArr.append('        tapa::ostreams<KEY_DTYPE, NUM_HASH> & key_out_stream' + "\n")
        codeArr.append('){' + "\n")
        codeArr.append('    const int READ_STOP_COUNT =     KEYPAIRS_PER_STM;' + "\n")
        codeArr.append('    const int WRITE_STOP_COUNT =    KEYPAIRS_PER_STM*NUM_HASH;' + "\n")
        codeArr.append('    int total_num_reads = 0;' + "\n")
        codeArr.append('    int total_num_writes = 0;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    int input_idx = 0;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    KEY_DTYPE       key;' + "\n")
        codeArr.append('    bool            key_written[NUM_HASH];' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=key_written dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    INIT_KEY_WRITTEN:' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_HASH; ++i) {' + "\n")
        codeArr.append('        key_written[i] = 1;' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    while (total_num_reads < READ_STOP_COUNT ||' + "\n")
        codeArr.append('            total_num_writes < WRITE_STOP_COUNT' + "\n")
        codeArr.append('    ) {' + "\n")
        codeArr.append('    #pragma HLS PIPELINE II=1' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        bool do_read = 1;' + "\n")
        codeArr.append('        HASH_RD_LOOP:' + "\n")
        codeArr.append('        for(int hash_idx = 0; hash_idx < NUM_HASH; ++hash_idx){' + "\n")
        codeArr.append('            if (key_written[hash_idx] == 0) {' + "\n")
        codeArr.append('                do_read = 0;' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        if (do_read &&' + "\n")
        codeArr.append('            input_idx < KEYPAIRS_PER_STM' + "\n")
        codeArr.append('        ){' + "\n")
        codeArr.append('            ///////////////////////////////////' + "\n")
        codeArr.append('            // READ LOGIC:' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            // NOTE: This blocking read is ok because we only have one input stream' + "\n")
        codeArr.append('            key = key_in_stream.read();' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('            printf("COMPUTEHASH_FEEDER #%d kp%d - Read input #%d, with value %d.\\n",' + "\n")
        codeArr.append('                strm_idx, keypair_idx,' + "\n")
        codeArr.append('                input_idx, key.to_int()' + "\n")
        codeArr.append('            );' + "\n")
        codeArr.append('            #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            total_num_reads++;' + "\n")
        codeArr.append('            input_idx++;' + "\n")
        codeArr.append('            for (int j = 0; j < NUM_HASH; ++j) {' + "\n")
        codeArr.append('                key_written[j] = 0;' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        ///////////////////////////////////' + "\n")
        codeArr.append('        // WRITE LOGIC:' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        for (int hash_idx = 0; hash_idx < NUM_HASH; ++hash_idx) {' + "\n")
        codeArr.append('        #pragma HLS UNROLL' + "\n")
        codeArr.append('            if (key_written[hash_idx] == 0) {' + "\n")
        codeArr.append('                if (key_out_stream[hash_idx].try_write(key)) {' + "\n")
        codeArr.append('                    total_num_writes++;' + "\n")
        codeArr.append('                    key_written[hash_idx] = 1;' + "\n")
        codeArr.append('                }' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    printf("\\n\\nCOMPUTEHASH_FEEDER #%d kp%d - DONE NOW.\\n\\n",' + "\n")
        codeArr.append('            strm_idx, keypair_idx' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('    return;' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append("\n\n\n")

        return codeArr






    def generate_computeHash_computer(self):
        codeArr = []
        codeArr.append('void computeHash_Computer(' + "\n")
        codeArr.append('        int                             stm_idx,' + "\n")
        codeArr.append('        int                             hash_idx,' + "\n")
        codeArr.append('        int                             keypair_idx,' + "\n")
        codeArr.append('        tapa::istream<KEY_DTYPE>        & key_stream,' + "\n")
        codeArr.append('        tapa::ostream<HASHONLY_DTYPE>   & hash_stream' + "\n")
        codeArr.append('){' + "\n")
        codeArr.append('    int module_idx = stm_idx*NUM_HASH + hash_idx;' + "\n")
        codeArr.append('    const int WRITE_STOP_COUNT =    KEYPAIRS_PER_STM;' + "\n")
        codeArr.append('    int total_num_writes = 0;' + "\n")
        codeArr.append('    int input_idx = 0;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    MAIN_LOOP:' + "\n")
        codeArr.append('    while ( total_num_writes < WRITE_STOP_COUNT){' + "\n")
        codeArr.append('    #pragma HLS PIPELINE II=1' + "\n")
        codeArr.append('        KEY_DTYPE key = key_stream.read();' + "\n")
        codeArr.append('        uint32_t hash = MurmurHash3_x86_32(key, hash_idx);' + "\n")
        codeArr.append('        hash %= BV_SECTION_LENGTH;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        hash_stream.write(hash);' + "\n")
        codeArr.append('        total_num_writes++;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('        printf("COMPUTEHASH_COMPUTER #%d kp%d - (STM %d, HASH %d): read input #%d, key %d, computed hash = %d\\n",' + "\n")
        codeArr.append('                module_idx,' + "\n")
        codeArr.append('                keypair_idx,' + "\n")
        codeArr.append('                stm_idx,' + "\n")
        codeArr.append('                hash_idx,' + "\n")
        codeArr.append('                input_idx,' + "\n")
        codeArr.append('                key.to_int(),' + "\n")
        codeArr.append('                hash' + "\n")
        codeArr.append('        );' + "\n")
        codeArr.append('        input_idx++;' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append('' + "\n")
        return codeArr








    def generate_computeHash_wrapper(self):
        codeArr = []

        codeArr.append('#define COMPUTEHASH_STREAM_DECLS_KP(KP_IDX)   \\' + "\n")
        for s in range(0, self.config.num_stm):
            codeArr.append('    tapa::streams<KEY_DTYPE, NUM_HASH>      key_tmp_stream_{s}_kp##KP_IDX;\\'.format(s=s) + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('#define INVOKE_COMPUTERS_FOR_HASH(HASH_IDX, STM_IDX, KP_IDX)\\' + "\n")
        codeArr.append('    .invoke(computeHash_Computer,\\' + "\n")
        codeArr.append('            STM_IDX,\\' + "\n")
        codeArr.append('            HASH_IDX,\\' + "\n")
        codeArr.append('            KP_IDX,\\' + "\n")
        codeArr.append('            key_tmp_stream_##STM_IDX##_kp##KP_IDX[HASH_IDX],\\' + "\n")
        codeArr.append('            hash_stream_h##HASH_IDX##_kp##KP_IDX[STM_IDX]\\' + "\n")
        codeArr.append('    )' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('// CONFIG: need NUM_HASH calls to INVOKE_COMPUTERS_FOR_HASH' + "\n")
        codeArr.append('#define INVOKE_COMPUTERS_FOR_STM(STM_IDX, KP_IDX)\\' + "\n")
        for h in range(0, self.config.num_hash):
            codeArr.append('    INVOKE_COMPUTERS_FOR_HASH({h}, STM_IDX, KP_IDX)\\'.format(h=h) + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")

        #####

        codeArr.append('#define COMPUTEHASH_INVOKES_FOR_KP(KP_IDX)  \\' + "\n")

        for s in range(0, self.config.num_stm):
            codeArr.append('        .invoke(computeHash_Feeder, \\' + "\n")
            codeArr.append('                    {s},  \\'.format(s=s) + "\n")
            codeArr.append('                    KP_IDX,    \\' + "\n")
            codeArr.append('                    key_stream_kp##KP_IDX[{s}],   \\'.format(s=s) + "\n")
            codeArr.append('                    key_tmp_stream_{s}_kp##KP_IDX    \\'.format(s=s) + "\n")
            codeArr.append('        )   \\' + "\n")
        codeArr.append('    /* Need NUM_STM of these^ invokes */ \\' + "\n")

        for s in range(0, self.config.num_stm):
            codeArr.append('    INVOKE_COMPUTERS_FOR_STM({s}, KP_IDX) \\'.format(s=s) + "\n")
        codeArr.append('    /* Need NUM_STM of these^ invokes */' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('#if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('void crash(){ crash compilation' + "\n")
        codeArr.append('#endif' + "\n")

        codeArr.append('' + "\n")

        return codeArr
















    def generate(self):
        codeArr = []
        codeArr.extend(self.generate_murmurhash())
        codeArr.extend(self.generate_computeHash_feeder())
        codeArr.extend(self.generate_computeHash_computer())
        codeArr.extend(self.generate_computeHash_wrapper())

        codeArr.append("\n\n/*************************************************************************************/\n\n")
        return codeArr

