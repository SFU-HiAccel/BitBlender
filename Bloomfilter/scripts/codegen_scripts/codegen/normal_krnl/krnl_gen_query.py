
class QueryCodeGenerator:
    def __init__(self, config):
        self.config = config



    def generate_query_per_hash(self):
        codeArr = []

        codeArr.append(
"""
void queryResult_per_hash(
        int hash_idx
        ,tapa::istream<BV_URAM_PACKED_DTYPE>                                & bv_load_stream
        ,tapa::istreams<PACKED_HASH_DTYPE, BV_NUM_PARTITIONS>               & bv_lookup_stream_kp0
        ,tapa::istreams<PACKED_HASH_DTYPE, BV_NUM_PARTITIONS>               & bv_lookup_stream_kp1
        ,tapa::ostreams<BV_PLUS_METADATA_PACKED_DTYPE, BV_NUM_PARTITIONS>   & query_bv_packed_stream_kp0
        ,tapa::ostreams<BV_PLUS_METADATA_PACKED_DTYPE, BV_NUM_PARTITIONS>   & query_bv_packed_stream_kp1
) {
    const int MAX_NUM_WRITES = NUM_STM*KEYS_PER_STM;
    int num_writes = 0;
    int num_reads = 0;
 
    /* This is pretty confusing. We LOAD in chunks of size URAM_PACKED_BITWIDTH
     *  but we need to put it into the BRAMS.
     *  So the BRAMs will take 64 bits, which gives it 2 packed-value.
     *  The URAMs also take 64 bits, but this only gives it 1 packed-value.
     */
    BV_BRAM_PACKED_DTYPE     bv_buf_BRAMS[BV_NUM_BRAM_PARTITIONS][BV_PARTITION_LENGTH_IN_BRAM_PACKED_ELEMS];
    #pragma HLS BIND_STORAGE variable=bv_buf_BRAMS type=RAM_T2P impl=bram
    #pragma HLS ARRAY_PARTITION variable=bv_buf_BRAMS dim=1 complete

    BV_URAM_PACKED_DTYPE     bv_buf_URAMS[BV_NUM_URAM_PARTITIONS][BV_PARTITION_LENGTH_IN_URAM_PACKED_ELEMS];
    #pragma HLS BIND_STORAGE variable=bv_buf_URAMS type=RAM_T2P impl=uram
    #pragma HLS ARRAY_PARTITION variable=bv_buf_URAMS dim=1 complete


    BV_URAM_PACKED_DTYPE cur_bv_val_uram;
    BV_BRAM_PACKED_DTYPE cur_bv_val_bram0;
    BV_BRAM_PACKED_DTYPE cur_bv_val_bram1;

    typedef struct {
        ap_uint<1>      valid;
        BV_PLUS_METADATA_PACKED_DTYPE data;
    } TO_WRITE_DTYPE;

    TO_WRITE_DTYPE bram_queried_vals_buf[BV_NUM_BRAM_PARTITIONS][2];
    #pragma HLS ARRAY_PARTITION variable=bram_queried_vals_buf dim=0 complete

    TO_WRITE_DTYPE uram_queried_vals_buf[BV_NUM_URAM_PARTITIONS][2];
    #pragma HLS ARRAY_PARTITION variable=uram_queried_vals_buf dim=0 complete

    #ifndef __SYNTHESIS__
    printf("INFO: We are using the SPLIT QUERY unit!\\n");
    #endif

    INIT_BRAM_QUERIED_VALS_BUF:
    for (int j = 0; j < BV_NUM_BRAM_PARTITIONS; ++j) {
    #pragma HLS UNROLL
        bram_queried_vals_buf[j][0].valid=0;
        bram_queried_vals_buf[j][1].valid=0;
    }

    INIT_URAM_QUERIED_VALS_BUF:
    for (int j = 0; j < BV_NUM_URAM_PARTITIONS; ++j) {
    #pragma HLS UNROLL
        uram_queried_vals_buf[j][0].valid=0;
        uram_queried_vals_buf[j][1].valid=0;
    }


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
            printf("QUERY UNIT %d - %d, bram%d\\n",
                    hash_idx, partition_idx, bram_element_idx);
            for (int j = 0; j < BV_BRAM_PACKED_BITWIDTH; ++j) {
                BIT_DTYPE tmp;
                tmp.range(0,0) = bv_buf_BRAMS[partition_idx][bram_element_idx+0].range(j,j);
                printf("QUERY UNIT %d - bv[%d] = %d\\n",
                        hash_idx,
                        partition_idx*BV_PARTITION_LENGTH +
                            (bram_element_idx+0)*BV_BRAM_PACKED_BITWIDTH+j,
                        tmp.to_int()
                );
            }
            for (int j = 0; j < BV_BRAM_PACKED_BITWIDTH; ++j) {
                BIT_DTYPE tmp;
                tmp.range(0,0) = bv_buf_BRAMS[partition_idx][bram_element_idx+1].range(j,j);
                printf("QUERY UNIT %d - bv[%d] = %d\\n",
                        hash_idx,
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
            printf("QUERY UNIT %d - %d, uram%d\\n",
                    hash_idx, partition_idx, uram_element_idx);
            for (int j = 0; j < BV_URAM_PACKED_BITWIDTH; ++j) {
                BIT_DTYPE tmp;
                tmp.range(0,0) = bv_buf_URAMS[partition_idx-BV_NUM_BRAM_PARTITIONS][uram_element_idx].range(j,j);
                printf("QUERY UNIT %d - bv[%d] = %d\\n",
                        hash_idx,
                        i*BV_URAM_PACKED_BITWIDTH+j,
                        tmp.to_int()
                );
            }
            #endif

        }
    }


    PROCESS_QUERIES:
    while (num_writes < MAX_NUM_WRITES){
    #pragma HLS PIPELINE II=1

        BV_BRAM_PARTITION_LOOP:
        for (int bram_partition_idx = 0; bram_partition_idx < BV_NUM_BRAM_PARTITIONS; ++bram_partition_idx) {
        #pragma HLS UNROLL

            //////////////////////////////////////////////////////////
            // READ LOGIC

            // READ PORT 0
            if (!bv_lookup_stream_kp0[bram_partition_idx].empty() &&
                !bram_queried_vals_buf[bram_partition_idx][0].valid)
            {
                PACKED_HASH_DTYPE   packed_hash;
                METADATA_DTYPE      cur_metadata;
                HASHONLY_DTYPE      bv_lookup_idx;
                BIT_DTYPE           cur_bv_val;
                BV_PLUS_METADATA_PACKED_DTYPE     data_to_write;

                HASHONLY_DTYPE      bv_outer_idx;
                HASHONLY_DTYPE      bv_inner_idx;

                packed_hash = bv_lookup_stream_kp0[bram_partition_idx].read();

                // Unpack the values
                cur_metadata = packed_hash.md;
                bv_lookup_idx = packed_hash.hash;

                // Read the bitvector
                bv_outer_idx = bv_lookup_idx/BV_BRAM_PACKED_BITWIDTH;
                bv_inner_idx = bv_lookup_idx%BV_BRAM_PACKED_BITWIDTH;
                cur_bv_val.range(0, 0) =
                    bv_buf_BRAMS[bram_partition_idx][bv_outer_idx].range(bv_inner_idx, bv_inner_idx);

                #ifdef __DO_DEBUG_PRINTS__
                printf("QUERY UNIT %d kp%d - h/p/s=(%d,%d,%d). input idx %d: This gave a bit value of %d.\\n",
                        hash_idx,
                        0,
                        hash_idx,
                        bram_partition_idx,
                        cur_metadata.sidx.to_int(),
                        cur_metadata.iidx.to_int(),
                        cur_bv_val.to_int()
                );
                #endif

                // Pack final payload
                data_to_write.md = cur_metadata;
                data_to_write.bv_val = cur_bv_val;

                bram_queried_vals_buf[bram_partition_idx][0].valid = 1;
                bram_queried_vals_buf[bram_partition_idx][0].data = data_to_write;
            }

            // READ PORT 1
            if (!bv_lookup_stream_kp1[bram_partition_idx].empty() &&
                !bram_queried_vals_buf[bram_partition_idx][1].valid)
            {
                PACKED_HASH_DTYPE   packed_hash;
                METADATA_DTYPE      cur_metadata;
                HASHONLY_DTYPE      bv_lookup_idx;
                BIT_DTYPE           cur_bv_val;
                BV_PLUS_METADATA_PACKED_DTYPE     data_to_write;

                HASHONLY_DTYPE      bv_outer_idx;
                HASHONLY_DTYPE      bv_inner_idx;

                packed_hash = bv_lookup_stream_kp1[bram_partition_idx].read();

                // Unpack the values
                cur_metadata = packed_hash.md;
                bv_lookup_idx = packed_hash.hash;

                // Read the bitvector
                bv_outer_idx = bv_lookup_idx/BV_BRAM_PACKED_BITWIDTH;
                bv_inner_idx = bv_lookup_idx%BV_BRAM_PACKED_BITWIDTH;
                cur_bv_val.range(0, 0) =
                    bv_buf_BRAMS[bram_partition_idx][bv_outer_idx].range(bv_inner_idx, bv_inner_idx);

                #ifdef __DO_DEBUG_PRINTS__
                printf("QUERY UNIT %d kp%d - h/p/s=(%d,%d,%d). input idx %d: This gave a bit value of %d.\\n",
                        hash_idx,
                        1,
                        hash_idx,
                        bram_partition_idx,
                        cur_metadata.sidx.to_int(),
                        cur_metadata.iidx.to_int(),
                        cur_bv_val.to_int()
                );
                #endif

                // Pack final payload
                data_to_write.md = cur_metadata;
                data_to_write.bv_val = cur_bv_val;

                bram_queried_vals_buf[bram_partition_idx][1].valid = 1;
                bram_queried_vals_buf[bram_partition_idx][1].data = data_to_write;
            }

            //////////////////////////////////////////////////////////
            // WRITE LOGIC
            // WRITE PORT 0
            if (bram_queried_vals_buf[bram_partition_idx][0].valid &&
                query_bv_packed_stream_kp0[bram_partition_idx].try_write(
                    bram_queried_vals_buf[bram_partition_idx][0].data
                )
            ) {
                ++num_writes;
                bram_queried_vals_buf[bram_partition_idx][0].valid = 0;
            }

            // WRITE PORT 1
            if (bram_queried_vals_buf[bram_partition_idx][1].valid &&
                query_bv_packed_stream_kp1[bram_partition_idx].try_write(
                    bram_queried_vals_buf[bram_partition_idx][1].data
                )
            ) {
                ++num_writes;
                bram_queried_vals_buf[bram_partition_idx][1].valid = 0;
            }
        }






























        BV_URAM_PARTITION_LOOP:
        for (int uram_partition_idx = 0; uram_partition_idx < BV_NUM_URAM_PARTITIONS; ++uram_partition_idx) {
        #pragma HLS UNROLL

            //////////////////////////////////////////////////////////
            // READ LOGIC

            // READ PORT 0
            if (!bv_lookup_stream_kp0[uram_partition_idx + BV_NUM_BRAM_PARTITIONS].empty() &&
                !uram_queried_vals_buf[uram_partition_idx][0].valid)
            {
                PACKED_HASH_DTYPE   packed_hash;
                METADATA_DTYPE      cur_metadata;
                HASHONLY_DTYPE      bv_lookup_idx;
                BIT_DTYPE           cur_bv_val;
                BV_PLUS_METADATA_PACKED_DTYPE     data_to_write;

                HASHONLY_DTYPE      bv_outer_idx;
                HASHONLY_DTYPE      bv_inner_idx;

                packed_hash = bv_lookup_stream_kp0[uram_partition_idx + BV_NUM_BRAM_PARTITIONS].read();

                // Unpack the values
                cur_metadata = packed_hash.md;
                bv_lookup_idx = packed_hash.hash;

                // Read the bitvector
                bv_outer_idx = bv_lookup_idx/BV_URAM_PACKED_BITWIDTH;
                bv_inner_idx = bv_lookup_idx%BV_URAM_PACKED_BITWIDTH;
                cur_bv_val.range(0, 0) =
                    bv_buf_URAMS[uram_partition_idx][bv_outer_idx].range(bv_inner_idx, bv_inner_idx);

                #ifdef __DO_DEBUG_PRINTS__
                printf("QUERY UNIT %d kp%d - h/p/s=(%d,%d,%d). input idx %d: This gave a bit value of %d.\\n",
                        hash_idx,
                        0,
                        hash_idx,
                        uram_partition_idx + BV_NUM_BRAM_PARTITIONS,
                        cur_metadata.sidx.to_int(),
                        cur_metadata.iidx.to_int(),
                        cur_bv_val.to_int()
                );
                #endif

                // Pack final payload
                data_to_write.md = cur_metadata;
                data_to_write.bv_val = cur_bv_val;

                uram_queried_vals_buf[uram_partition_idx][0].valid = 1;
                uram_queried_vals_buf[uram_partition_idx][0].data = data_to_write;
            }

            // READ PORT 1
            if (!bv_lookup_stream_kp1[uram_partition_idx + BV_NUM_BRAM_PARTITIONS].empty() &&
                !uram_queried_vals_buf[uram_partition_idx][1].valid)
            {
                PACKED_HASH_DTYPE   packed_hash;
                METADATA_DTYPE      cur_metadata;
                HASHONLY_DTYPE      bv_lookup_idx;
                BIT_DTYPE           cur_bv_val;
                BV_PLUS_METADATA_PACKED_DTYPE     data_to_write;

                HASHONLY_DTYPE      bv_outer_idx;
                HASHONLY_DTYPE      bv_inner_idx;

                packed_hash = bv_lookup_stream_kp1[uram_partition_idx + BV_NUM_BRAM_PARTITIONS].read();

                // Unpack the values
                cur_metadata = packed_hash.md;
                bv_lookup_idx = packed_hash.hash;

                // Read the bitvector
                bv_outer_idx = bv_lookup_idx/BV_URAM_PACKED_BITWIDTH;
                bv_inner_idx = bv_lookup_idx%BV_URAM_PACKED_BITWIDTH;
                cur_bv_val.range(0, 0) =
                    bv_buf_URAMS[uram_partition_idx][bv_outer_idx].range(bv_inner_idx, bv_inner_idx);

                #ifdef __DO_DEBUG_PRINTS__
                printf("QUERY UNIT %d kp%d - h/p/s=(%d,%d,%d). input idx %d: This gave a bit value of %d.\\n",
                        hash_idx,
                        1,
                        hash_idx,
                        uram_partition_idx + BV_NUM_BRAM_PARTITIONS,
                        cur_metadata.sidx.to_int(),
                        cur_metadata.iidx.to_int(),
                        cur_bv_val.to_int()
                );
                #endif

                // Pack final payload
                data_to_write.md = cur_metadata;
                data_to_write.bv_val = cur_bv_val;

                uram_queried_vals_buf[uram_partition_idx][1].valid = 1;
                uram_queried_vals_buf[uram_partition_idx][1].data = data_to_write;
            }

            //////////////////////////////////////////////////////////
            // WRITE LOGIC
            // WRITE PORT 0
            if (uram_queried_vals_buf[uram_partition_idx][0].valid &&
                query_bv_packed_stream_kp0[uram_partition_idx + BV_NUM_BRAM_PARTITIONS].try_write(
                    uram_queried_vals_buf[uram_partition_idx][0].data
                )
            ) {
                ++num_writes;
                uram_queried_vals_buf[uram_partition_idx][0].valid = 0;
            }

            // WRITE PORT 1
            if (uram_queried_vals_buf[uram_partition_idx][1].valid &&
                query_bv_packed_stream_kp1[uram_partition_idx + BV_NUM_BRAM_PARTITIONS].try_write(
                    uram_queried_vals_buf[uram_partition_idx][1].data
                )
            ) {
                ++num_writes;
                uram_queried_vals_buf[uram_partition_idx][1].valid = 0;
            }
        }

    }

    #ifdef __DO_DEBUG_PRINTS__
    printf("\\n\\nQUERY UNIT %d - DONE NOW.\\n\\n",
            hash_idx
    );
    #endif

    return;


}
"""
        )
        codeArr.append("\n\n\n")

        return codeArr









    def generate_query_wrapper(self):
        codeArr = []
        
        codeArr.append('#define QUERY_INVOKES   \\' + "\n")

        for i in range(0, self.config.num_hash):
            codeArr.append('        .invoke(\\' + "\n")
            codeArr.append('                queryResult_per_hash\\' + "\n")
            codeArr.append('                , {}\\'.format(i) + "\n")
            codeArr.append('                , bv_load_stream_{}\\'.format(i) + "\n")
            codeArr.append('                , bv_lookup_stream_h{}_kp0\\'.format(i) + "\n")
            codeArr.append('                , bv_lookup_stream_h{}_kp1\\'.format(i) + "\n")
            codeArr.append('                , query_bv_packed_stream_hash{}_kp0\\'.format(i) + "\n")
            codeArr.append('                , query_bv_packed_stream_hash{}_kp1\\'.format(i) + "\n")
            codeArr.append('        )\\' + "\n")

        return codeArr















    def generate(self):
        codeArr = []
        codeArr.extend(self.generate_query_per_hash())
        codeArr.extend(self.generate_query_wrapper())
        codeArr.append("\n\n/*************************************************************************************/\n\n")
        return codeArr


