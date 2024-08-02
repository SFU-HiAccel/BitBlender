

class ModuleCodeGenerator:
    def __init__(self, config):
        self.config = config


    def generate_modules(self):
        codeArr = []

        codeArr.append("""
#include "MurmurHash3.h"

#if NAIVE_MULTISTREAM != 1
void crash_compilation(
crash compilation.
}
#endif


uint32_t rotl32(uint32_t x, int8_t r){
#pragma HLS inline
    return (x << r)|( x >> (32 - r));
}

#define ROTL32(x,y)    rotl32(x,y)
#define BIG_CONSTANT(x)    (x)

//For avalanche test
uint32_t fmix32( uint32_t h){
    //inline as well
    h ^= h>>16;
    h *= 0x85ebca6b;
    h ^= h>>13;
    h *= 0xc2b2ae35;
    h ^= h>>16;
    return h;
}

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






void loadBV(
    int strm_idx
    ,tapa::async_mmap<BV_LOAD_DTYPE>    & input_bv
""")
        for h in range(self.config.num_hash):
            codeArr.append('    ,tapa::ostream<BV_URAM_PACKED_DTYPE>    & bv_load_stream_{}'.format(h) + "\n")
        codeArr.append('    #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('    ,crash,' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append("""

    #if ENABLE_PERF_CTRS
    ,tapa::ostreams<PERFCTR_DTYPE, 1>                   & perfctr_out
    #endif
){

    #if BV_LOAD_BITWIDTH > 1024
    crash(); on purpose();
    // We need more sophisticated loading logic. AXI bitwidth shouldnt be higher than 1024.
    #endif

    int section_idx = 0;
    BV_LOAD_DTYPE  cur_bv_val;

    #if ENABLE_PERF_CTRS
    PERFCTR_DTYPE   load_cycles = 0;
    #endif

    for (int i_req = 0, i_resp = 0;
            i_resp < BV_NUM_LOADS; )
    {
        #pragma HLS PIPELINE II=1

        #if ENABLE_PERF_CTRS
        load_cycles += 1;
        #endif
        
        if (i_req < BV_NUM_LOADS && input_bv.read_addr.try_write(i_req)) {
            ++i_req;
        }
        if (!input_bv.read_data.empty()) {
            cur_bv_val = input_bv.read_data.read(nullptr);
""")
        for h in range(self.config.num_hash):
            codeArr.append('            bv_load_stream_{h}.write(cur_bv_val.section{h});'.format(h=h) + "\n")
            
        codeArr.append('            #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('            ,crash,' + "\n")
        codeArr.append('            #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('            for (int i = 0; i < BV_URAM_PACKED_BITWIDTH; ++i)' + "\n")
        codeArr.append('            {' + "\n")
        codeArr.append('                int total_idx = i_resp*BV_URAM_PACKED_BITWIDTH + i;' + "\n")
        codeArr.append('                BIT_DTYPE cur_bit;' + "\n")
        codeArr.append('                cur_bit.range(0,0) = cur_bv_val.section0.range(i, i);' + "\n")
        codeArr.append('                printf("KDEBUG: LOADBV - The %dth packed BV value of section 0 is %d\\n",' + "\n")
        codeArr.append('                        total_idx, cur_bit.to_int());' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('            #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            ++i_resp;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append("""


    #if ENABLE_PERF_CTRS
    WRITE_PERF_CTRS:
    for (int i = 0; i < NUM_PERFCTR_OUTPUTS; ++i) {
    #pragma HLS PIPELINE II=1
        if (i == 0){
            perfctr_out[0].write(load_cycles);
        }
        else{
            perfctr_out[0].write(55555);
        }
    }
    #endif  // ENABLE_PERF_CTRS

    #ifdef __DO_DEBUG_PRINTS__
    printf("\\n\\nLOADBV %d - DONE NOW.\\n\\n", strm_idx);
    #endif
    return;
}












/**********************************/

void loadKey(
        int strm_idx
        ,tapa::async_mmap<TWOKEY_DTYPE>  & key_in
        ,tapa::ostream<KEY_DTYPE>        & key_stream_0
        ,tapa::ostream<KEY_DTYPE>        & key_stream_1
){
    TWOKEY_DTYPE cur_load;

    for (int i_req = 0, i_resp = 0;
            i_resp < KEYPAIRS_PER_STM; )
    {
        #pragma HLS PIPELINE II=1
        
        if (i_req < KEYPAIRS_PER_STM && key_in.read_addr.try_write(i_req)) {
            ++i_req;
        }
        if (!key_in.read_data.empty()) {
            cur_load = key_in.read_data.read(nullptr);
            
            #ifdef __DO_DEBUG_PRINTS__
            printf("LOADKEY %d - Writing %d and %d to the key streams\\n",
                    strm_idx,
                    cur_load.k0.to_int(),
                    cur_load.k1.to_int()
            );
            #endif

            key_stream_0.write(cur_load.k0);
            key_stream_1.write(cur_load.k1);
            ++i_resp;
        }
    }

    #ifdef __DO_DEBUG_PRINTS__
    printf("LOADKEY %d - DONE NOW\\n", strm_idx);
    #endif
    return;
}


void DEBUG_loadKey_sink(
        int strm_idx
        ,tapa::istream<KEY_DTYPE>&               key_stream
){
    for(int input_idx = 0; input_idx < KEYPAIRS_PER_STM; ++input_idx){
    #pragma HLS pipeline II=1
        KEY_DTYPE tmp_key = key_stream.read();
        #ifdef __DO_DEBUG_PRINTS__
        printf("DEBUG_loadKey_sink #%d - read input #%d\\n", 
                strm_idx,
                input_idx
        );
        #endif
    }
    return;
}

void computeHash(
        int strm_idx
        ,tapa::istream<KEY_DTYPE>&               key_stream
        ,tapa::ostreams<HASHONLY_DTYPE, NUM_HASH>&   hash_stream
){
    for(int input_idx = 0; input_idx < KEYPAIRS_PER_STM; ++input_idx){
    #pragma HLS pipeline II=1
        KEY_DTYPE tmp_key = key_stream.read();
        for(int hash_idx = 0; hash_idx < NUM_HASH; ++hash_idx){
            uint32_t hash_val = MurmurHash3_x86_32(
                                                    tmp_key,
                                                    hash_idx
            );

            hash_val = hash_val % BV_SECTION_LENGTH;

            #ifdef __DO_DEBUG_PRINTS__
            printf("COMPUTEHASH_COMPUTER %d - For input %d, our %d'th hash value AFTER modulo is %d\\n", 
                    strm_idx,
                    input_idx, hash_idx, hash_val
            );
            #endif

            hash_stream[hash_idx].write(hash_val);
        }
    }

    #ifdef __DO_DEBUG_PRINTS__
    printf("COMPUTEHASH_COMPUTER %d - DONE NOW\\n", strm_idx);
    #endif
    return;
}


void DEBUG_compute_sink(
        int strm_idx
        ,tapa::istreams<HASHONLY_DTYPE, NUM_HASH>    &  hash_stream_0
        ,tapa::istreams<HASHONLY_DTYPE, NUM_HASH>    &  hash_stream_1
){
    PROCESS_QUERIES:
    for (int i = 0; i < KEYPAIRS_PER_STM; ++i)
    {
        #pragma HLS PIPELINE II=1
        for (int j = 0; j < NUM_HASH; ++j)
        {
            #pragma HLS UNROLL
            HASHONLY_DTYPE cur_hash_0 = hash_stream_0[j].read();
            HASHONLY_DTYPE cur_hash_1 = hash_stream_1[j].read();

            #ifdef __DO_DEBUG_PRINTS__
            printf("DEBUG_compute_sink %d - Read input #%d, hash #%d\\n",
                    strm_idx, i, j
            );
            printf("DEBUG_compute_sink %d - Read input #%d, hash #%d\\n",
                    strm_idx, i+1, j
            );
            #endif
        }
    }
    return;
}


void queryResult_per_hash(
        int strm_idx
        ,int hash_idx
        ,tapa::istream<HASHONLY_DTYPE>         &  hash_stream_0
        ,tapa::istream<HASHONLY_DTYPE>         &  hash_stream_1
        ,tapa::istream<BV_URAM_PACKED_DTYPE>   &  bv_load_stream
        ,tapa::ostream<BIT_DTYPE>              &  query_bv_stream_0
        ,tapa::ostream<BIT_DTYPE>              &  query_bv_stream_1
){

    BV_BRAM_PACKED_DTYPE     bv_buf_BRAMS[BV_NUM_BRAM_PARTITIONS][BV_PARTITION_LENGTH_IN_BRAM_PACKED_ELEMS];
    #pragma HLS BIND_STORAGE variable=bv_buf_BRAMS type=RAM_T2P impl=bram
    #pragma HLS ARRAY_PARTITION variable=bv_buf_BRAMS dim=1 complete

    BV_URAM_PACKED_DTYPE     bv_buf_URAMS[BV_NUM_URAM_PARTITIONS][BV_PARTITION_LENGTH_IN_URAM_PACKED_ELEMS];
    #pragma HLS BIND_STORAGE variable=bv_buf_URAMS type=RAM_T2P impl=uram
    #pragma HLS ARRAY_PARTITION variable=bv_buf_URAMS dim=1 complete

    BV_URAM_PACKED_DTYPE cur_bv_val_uram;
    BV_BRAM_PACKED_DTYPE cur_bv_val_bram0;
    BV_BRAM_PACKED_DTYPE cur_bv_val_bram1;

    LOAD_BV_VALUES:
    for (int i = 0; i < BV_SECTION_LENGTH_IN_URAM_PACKED_ELEMS; ++i) {
        #pragma HLS PIPELINE II=1
        cur_bv_val_uram = bv_load_stream.read();

        int partition_idx = i/BV_PARTITION_LENGTH_IN_URAM_PACKED_ELEMS;
        int uram_element_idx = i%BV_PARTITION_LENGTH_IN_URAM_PACKED_ELEMS;
        int bram_element_idx = (uram_element_idx*2);

        if (partition_idx < BV_NUM_BRAM_PARTITIONS) {
            cur_bv_val_bram0.range(BV_BRAM_PACKED_BITWIDTH-1,0) =
                cur_bv_val_uram.range(BV_BRAM_PACKED_BITWIDTH-1,0);
            cur_bv_val_bram1.range(BV_BRAM_PACKED_BITWIDTH-1,0) =
                cur_bv_val_uram.range(BV_URAM_PACKED_BITWIDTH-1,BV_BRAM_PACKED_BITWIDTH);

            #if (BV_URAM_PACKED_BITWIDTH != 2*BV_BRAM_PACKED_BITWIDTH)
            crash(; // We need to have URAM_PACKED_BITWIDTH=64, BRAM_PACKED_BITWIDTH=32.
            #endif

            bv_buf_BRAMS[partition_idx][bram_element_idx+0] = cur_bv_val_bram0;
            bv_buf_BRAMS[partition_idx][bram_element_idx+1] = cur_bv_val_bram1;

            #ifdef __DO_DEBUG_PRINTS__
            printf("QUERY UNIT %d %d - %d, bram%d\\n",
                    strm_idx, hash_idx, partition_idx, bram_element_idx);
            for (int j = 0; j < BV_BRAM_PACKED_BITWIDTH; ++j) {
                BIT_DTYPE tmp;
                tmp.range(0,0) = bv_buf_BRAMS[partition_idx][bram_element_idx+0].range(j,j);
                printf("QUERY UNIT %d %d - bv[%d] = %d\\n",
                        strm_idx,
                        hash_idx,

                        hash_idx*BV_NUM_LOADS*BV_URAM_PACKED_BITWIDTH +
                        partition_idx*BV_PARTITION_LENGTH +
                            (bram_element_idx+0)*BV_BRAM_PACKED_BITWIDTH+j,

                        tmp.to_int()
                );
            }
            for (int j = 0; j < BV_BRAM_PACKED_BITWIDTH; ++j) {
                BIT_DTYPE tmp;
                tmp.range(0,0) = bv_buf_BRAMS[partition_idx][bram_element_idx+1].range(j,j);
                printf("QUERY UNIT %d %d - bv[%d] = %d\\n",
                        strm_idx,
                        hash_idx,

                        hash_idx*BV_NUM_LOADS*BV_URAM_PACKED_BITWIDTH +
                        partition_idx*BV_PARTITION_LENGTH +
                            (bram_element_idx+1)*BV_BRAM_PACKED_BITWIDTH+j,

                        tmp.to_int()
                );
            }
            #endif

        }
        else {
            bv_buf_URAMS[partition_idx-BV_NUM_BRAM_PARTITIONS][uram_element_idx] = cur_bv_val_uram;

            #ifdef __DO_DEBUG_PRINTS__
            printf("QUERY UNIT %d %d - %d, uram%d\\n",
                    strm_idx, hash_idx, partition_idx, uram_element_idx);
            for (int j = 0; j < BV_URAM_PACKED_BITWIDTH; ++j) {
                BIT_DTYPE tmp;
                tmp.range(0,0) = bv_buf_URAMS[partition_idx-BV_NUM_BRAM_PARTITIONS][uram_element_idx].range(j,j);
                printf("QUERY UNIT %d %d - bv[%d] = %d\\n",
                        strm_idx,
                        hash_idx,

                        hash_idx*BV_NUM_LOADS*BV_URAM_PACKED_BITWIDTH +
                        partition_idx*BV_PARTITION_LENGTH +
                            (uram_element_idx)*BV_URAM_PACKED_BITWIDTH+j,

                        tmp.to_int()
                );
            }
            #endif

        }

    }


    ////////////////////////////////////////////


    PROCESS_QUERIES:
    for (int i = 0; i < KEYS_PER_STM; i +=2) {
    #pragma HLS PIPELINE II=1
 
        HASHONLY_DTYPE cur_hash_kp0                 = hash_stream_0.read();
        HASHONLY_DTYPE outer_partition_idx_kp0      = cur_hash_kp0/BV_PARTITION_LENGTH;
        HASHONLY_DTYPE bitidx_in_partition_kp0      = cur_hash_kp0%BV_PARTITION_LENGTH;

        BIT_DTYPE cur_bv_kp0;

        if (outer_partition_idx_kp0 < BV_NUM_BRAM_PARTITIONS) {
            HASHONLY_DTYPE  bram_part_idx_0     = bitidx_in_partition_kp0 / BV_BRAM_PACKED_BITWIDTH;
            HASHONLY_DTYPE  bitidx_0            = bitidx_in_partition_kp0 % BV_BRAM_PACKED_BITWIDTH;
            cur_bv_kp0.range(0, 0) = bv_buf_BRAMS[outer_partition_idx_kp0][bram_part_idx_0].range(bitidx_0, bitidx_0);
        }
        else {
            HASHONLY_DTYPE  uram_part_idx_0     = bitidx_in_partition_kp0 / BV_URAM_PACKED_BITWIDTH;
            HASHONLY_DTYPE  bitidx_0            = bitidx_in_partition_kp0 % BV_URAM_PACKED_BITWIDTH;
            cur_bv_kp0.range(0, 0) = bv_buf_URAMS[outer_partition_idx_kp0-BV_NUM_BRAM_PARTITIONS][uram_part_idx_0].range(bitidx_0, bitidx_0);
        }

        ////////////////////////////////

        HASHONLY_DTYPE cur_hash_kp1                 = hash_stream_1.read();
        HASHONLY_DTYPE outer_partition_idx_kp1      = cur_hash_kp1/BV_PARTITION_LENGTH;
        HASHONLY_DTYPE bitidx_in_partition_kp1      = cur_hash_kp1%BV_PARTITION_LENGTH;

        BIT_DTYPE cur_bv_kp1;

        if (outer_partition_idx_kp1 < BV_NUM_BRAM_PARTITIONS) {
            HASHONLY_DTYPE  bram_part_idx_1     = bitidx_in_partition_kp1 / BV_BRAM_PACKED_BITWIDTH;
            HASHONLY_DTYPE  bitidx_1            = bitidx_in_partition_kp1 % BV_BRAM_PACKED_BITWIDTH;
            cur_bv_kp1.range(0, 0) = bv_buf_BRAMS[outer_partition_idx_kp1][bram_part_idx_1].range(bitidx_1, bitidx_1);
        }
        else {
            HASHONLY_DTYPE  uram_part_idx_1     = bitidx_in_partition_kp1 / BV_URAM_PACKED_BITWIDTH;
            HASHONLY_DTYPE  bitidx_1            = bitidx_in_partition_kp1 % BV_URAM_PACKED_BITWIDTH;
            cur_bv_kp1.range(0, 0) = bv_buf_URAMS[outer_partition_idx_kp1-BV_NUM_BRAM_PARTITIONS][uram_part_idx_1].range(bitidx_1, bitidx_1);
        }

        #ifdef __DO_DEBUG_PRINTS__
        printf("QUERY UNIT %d - Input #%d, hash #%d (with value %d) is giving BV value %d\\n",
                strm_idx,
                i, hash_idx, cur_hash_kp0.to_int(), cur_bv_kp0.to_int()
        );
        printf("QUERY UNIT %d - Input #%d, hash #%d (with value %d) is giving BV value %d\\n",
                strm_idx,
                i+1, hash_idx, cur_hash_kp1.to_int(), cur_bv_kp1.to_int()
        );
        #endif

        query_bv_stream_0.write(cur_bv_kp0);
        query_bv_stream_1.write(cur_bv_kp1);
    }

    #ifdef __DO_DEBUG_PRINTS__
    printf("QUERY UNIT %d hash %d - DONE NOW\\n", strm_idx, hash_idx);
    #endif

    return;
}




void aggregate(
        int strm_idx
        ,tapa::istreams<BIT_DTYPE, NUM_HASH> & query_bv_stream
        ,tapa::ostream<BIT_DTYPE>            & aggregate_stream
){
    BIT_DTYPE cur_bv_val = 0;
    for (int i = 0; i < KEYPAIRS_PER_STM; ++i)
    {
    #pragma HLS PIPELINE II=1

        cur_bv_val = 1;
        for (int j = 0; j < NUM_HASH; ++j)
        {
            cur_bv_val &= query_bv_stream[j].read();
        }

        #ifdef __DO_DEBUG_PRINTS__
        printf("AGGREGATE %d - Input #%d aggregated to value %d\\n",
                strm_idx,
                i, cur_bv_val.to_int()
        );
        #endif

        aggregate_stream.write(cur_bv_val);
    }
 
    #ifdef __DO_DEBUG_PRINTS__
    printf("AGGREGATE %d - DONE NOW\\n", strm_idx);
    #endif
    return;
}


void DEBUG_aggregate_sink(
        int strm_idx
        ,tapa::istream<BIT_DTYPE>&   aggregate_stream
) {
    for (int i = 0; i < KEYPAIRS_PER_STM; ++i)
    {
    #pragma HLS PIPELINE II=1
        aggregate_stream.read();

        #ifdef __DO_DEBUG_PRINTS__
        printf("DEBUG_aggregate_sink %d - Input #%d\\n",
                strm_idx, i);
        #endif
    }
}


void packOutput(
        int strm_idx
        ,tapa::istream<BIT_DTYPE>            & aggregate_stream_0
        ,tapa::istream<BIT_DTYPE>            & aggregate_stream_1
        ,tapa::ostream<OUT_PACKED_DTYPE>     & packed_outputs_stream
) {
    int                 pk_idx_0;
    int                 pk_idx_1;
    OUT_PACKED_DTYPE    packed;
    BIT_DTYPE           val_0;
    BIT_DTYPE           val_1;

    #ifdef __DO_DEBUG_PRINTS__
    int num_writes = 0;
    #endif

    for (int i = 0; i < KEYS_PER_STM; i += 2) {
    #pragma HLS PIPELINE II=1
        pk_idx_0 = (i+0) % OUT_PACKED_BITWIDTH;
        val_0 = aggregate_stream_0.read();

        pk_idx_1 = (i+1) % OUT_PACKED_BITWIDTH;
        val_1 = aggregate_stream_1.read();

        packed.range(pk_idx_0, pk_idx_0) = val_0.range(0, 0);
        packed.range(pk_idx_1, pk_idx_1) = val_1.range(0, 0);

        if (pk_idx_1 == OUT_PACKED_BITWIDTH - 1){
            packed_outputs_stream.write(packed);
            packed = 0;

            #ifdef __DO_DEBUG_PRINTS__
            num_writes += 1;
            #endif
        }
    }

    #ifdef __DO_DEBUG_PRINTS__
    printf("PACKOUTPUT #%d - finishing after writing %d times.\\n",
            strm_idx, num_writes
    );
    #endif
}





void writeOutput(
        int strm_idx
        ,tapa::istream<OUT_PACKED_DTYPE>&       packed_outputs_stream
        ,tapa::async_mmap<OUT_PACKED_DTYPE>&    outmmap
){
    int i_req = 0;
    int i_resp = 0;
    unsigned int tmp = 0;
    OUT_PACKED_DTYPE val;

    while (i_resp < PACKED_OUTPAIRS_PER_STM)
    {
    #pragma HLS PIPELINE II = 1
        if (i_req < PACKED_OUTPAIRS_PER_STM &&
            !outmmap.write_addr.full() &&
            !outmmap.write_data.full())
        {
            val = packed_outputs_stream.read();

            outmmap.write_addr.write(i_req++);
            outmmap.write_data.write(val);
        }
        if (!outmmap.write_resp.empty())
        {
            tmp = (unsigned int)(outmmap.write_resp.read(nullptr));
            i_resp += tmp + 1;
        }
    }

    #ifndef __SYNTHESIS__
    printf("WRITEOUTPUT %d - exiting with i_req = %d, i_resp = %d\\n",
            strm_idx,
            i_req, i_resp);
    #endif

    return;
}


void writeOutput_synchronous(
        int strm_idx,
        tapa::istream<OUT_PACKED_DTYPE>&    packed_outputs_stream,
        tapa::mmap<OUT_PACKED_DTYPE>        outmmap
){
    for (int i = 0; i < PACKED_OUTPAIRS_PER_STM; ++i) {
    #pragma HLS PIPELINE II=1
        outmmap[i] = packed_outputs_stream.read();
    }

    #ifdef __DO_DEBUG_PRINTS__
    printf("WRITEOUTPUT %d - DONE NOW\\n", strm_idx);
    #endif
}



#define DECLARE_STREAMS_FOR_PE(PE)  \\
    tapa::stream<KEY_DTYPE, 2>                          key_stream_0_PE##PE;    \\
    tapa::stream<KEY_DTYPE, 2>                          key_stream_1_PE##PE;    \\
    tapa::streams<BV_URAM_PACKED_DTYPE, NUM_HASH, 2>    bv_load_stream_PE##PE;  \\
    \\
    tapa::streams<HASHONLY_DTYPE, NUM_HASH, 2>          hash_stream_0_PE##PE;   \\
    tapa::streams<HASHONLY_DTYPE, NUM_HASH, 2>          hash_stream_1_PE##PE;   \\
    \\
    tapa::streams<BIT_DTYPE, NUM_HASH, 2>               query_bv_stream_0_PE##PE;   \\
    tapa::streams<BIT_DTYPE, NUM_HASH, 2>               query_bv_stream_1_PE##PE;   \\
    \\
    tapa::stream<BIT_DTYPE, 2>                          aggregate_stream_0_PE##PE;  \\
    tapa::stream<BIT_DTYPE, 2>                          aggregate_stream_1_PE##PE;  \\
    \\
    tapa::stream<OUT_PACKED_DTYPE, 2>                   packed_output_stream_PE##PE;    \\




#define QUERY_INVOKE_FOR_PE_HASH(PE, HASH)  \\
        .invoke(queryResult_per_hash \\
                , PE    \\
                , HASH     \\
                , hash_stream_0_PE##PE[HASH]  \\
                , hash_stream_1_PE##PE[HASH]  \\
                , bv_load_stream_PE##PE[HASH] \\
                , query_bv_stream_0_PE##PE[HASH]  \\
                , query_bv_stream_1_PE##PE[HASH]  \\
        )   \\


""")


        codeArr.append('#define QUERY_INVOKES_FOR_PE(PE)    \\' + "\n")
        for h in range(0, self.config.num_hash):
            codeArr.append('        QUERY_INVOKE_FOR_PE_HASH(PE, {h}) \\'.format(h=h) + "\n")

        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")



        codeArr.append('#define INVOKES_FOR_PE(PE)  \\' + "\n")
        codeArr.append('        .invoke(loadKey \\' + "\n")
        codeArr.append('                , PE    \\' + "\n")
        codeArr.append('                , key##PE   \\' + "\n")
        codeArr.append('                , key_stream_0_PE##PE   \\' + "\n")
        codeArr.append('                , key_stream_1_PE##PE   \\' + "\n")
        codeArr.append('        )   \\' + "\n")
        codeArr.append('        .invoke(loadBV  \\' + "\n")
        codeArr.append('                , PE    \\' + "\n")
        codeArr.append('                , input_bv_##PE \\' + "\n")
        for h in range(0, self.config.num_hash):
            codeArr.append('                , bv_load_stream_PE##PE[{h}] \\'.format(h=h) + "\n")
        codeArr.append('        )   \\' + "\n")
        codeArr.append('        \\' + "\n")
        codeArr.append('        .invoke(computeHash \\' + "\n")
        codeArr.append('                , PE    \\' + "\n")
        codeArr.append('                , key_stream_0_PE##PE   \\' + "\n")
        codeArr.append('                , hash_stream_0_PE##PE  \\' + "\n")
        codeArr.append('        )   \\' + "\n")
        codeArr.append('        .invoke(computeHash \\' + "\n")
        codeArr.append('                , PE    \\' + "\n")
        codeArr.append('                , key_stream_1_PE##PE   \\' + "\n")
        codeArr.append('                , hash_stream_1_PE##PE  \\' + "\n")
        codeArr.append('        )   \\' + "\n")
        codeArr.append('        \\' + "\n")
        codeArr.append('        QUERY_INVOKES_FOR_PE(PE)    \\' + "\n")
        codeArr.append('        \\' + "\n")
        codeArr.append('        .invoke(aggregate   \\' + "\n")
        codeArr.append('                , PE    \\' + "\n")
        codeArr.append('                , query_bv_stream_0_PE##PE  \\' + "\n")
        codeArr.append('                , aggregate_stream_0_PE##PE \\' + "\n")
        codeArr.append('        )   \\' + "\n")
        codeArr.append('        .invoke(aggregate   \\' + "\n")
        codeArr.append('                , PE    \\' + "\n")
        codeArr.append('                , query_bv_stream_1_PE##PE  \\' + "\n")
        codeArr.append('                , aggregate_stream_1_PE##PE \\' + "\n")
        codeArr.append('        )   \\' + "\n")
        codeArr.append('        \\' + "\n")
        codeArr.append('        .invoke(packOutput  \\' + "\n")
        codeArr.append('                , PE    \\' + "\n")
        codeArr.append('                , aggregate_stream_0_PE##PE \\' + "\n")
        codeArr.append('                , aggregate_stream_1_PE##PE \\' + "\n")
        codeArr.append('                , packed_output_stream_PE##PE   \\' + "\n")
        codeArr.append('        )   \\' + "\n")
        codeArr.append('        \\' + "\n")
        codeArr.append('        .invoke(writeOutput_synchronous \\' + "\n")
        codeArr.append('                , PE    \\' + "\n")
        codeArr.append('                , packed_output_stream_PE##PE   \\' + "\n")
        codeArr.append('                , out##PE   \\' + "\n")
        codeArr.append('        )   \\' + "\n")

        codeArr.append("\n\n\n")

        return codeArr





    def generate(self):
        codeArr = []
        codeArr.extend(self.generate_modules())
        codeArr.append("\n\n/*************************************************************************************/\n\n")
        return codeArr
