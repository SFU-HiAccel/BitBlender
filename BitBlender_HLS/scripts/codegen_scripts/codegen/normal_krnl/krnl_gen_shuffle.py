import codegen.types as Types

class ShuffleCodeGenerator:
    def __init__(self, config):
        self.config = config




    def generate_shuffle_TtoS(self):
        codeArr = []

        codeArr.append(
"""
void shuffle_TtoS_per_hash(
        int shuffle_idx
        ,int kp_idx

        ,tapa::istreams<BV_PLUS_METADATA_PACKED_DTYPE, BV_NUM_PARTITIONS> & query_bv_packed_stream
        ,tapa::ostreams<BV_PLUS_IIDX_PACKED_DTYPE, NUM_STM*BV_NUM_PARTITIONS> & inter_shuffle_stream

        #if ENABLE_PERF_CTRS
        ,tapa::ostream<PERFCTR_DTYPE>   &perfctr_out
        #endif
){
    #ifndef __SYNTHESIS__
    printf("INFO: Using bifurcated shuffle.\\n");
    #endif

    typedef struct {
        BIT_DTYPE       BV;
        INPUT_IDX_DTYPE     input_idx;
        bool                valid;
    } PEEKED_DTYPE;

    //int next_output_idx[NUM_STM];
    //#pragma HLS ARRAY_PARTITION variable=next_output_idx dim=0 complete

    // This is a buffer for data from each partition.
    // We also introduce a NUM_STM dimension, otherwise we hang.
    PEEKED_DTYPE shuffle_peek_emulator[BV_NUM_PARTITIONS][NUM_STM];
    #pragma HLS ARRAY_PARTITION variable=shuffle_peek_emulator dim=0 complete

    #if ENABLE_PERF_CTRS
    BIT_DTYPE       did_read;
    BIT_DTYPE       did_write;

    PERFCTR_DTYPE   stall_cycles = 0;
    PERFCTR_DTYPE   readonly_cycles = 0;
    PERFCTR_DTYPE   writeonly_cycles = 0;
    PERFCTR_DTYPE   readwrite_cycles = 0;
    PERFCTR_DTYPE   total_cycles = 0;
    #endif


    //NEXT_OUTPUT_IDX_INIT:
    //for (int i = 0; i < NUM_STM; ++i) {
    //#pragma HLS UNROLL
    //    next_output_idx[i] = 1;
    //}

    PEEK_EMULATOR_INITIALIZATION:
    for (int j=0; j<BV_NUM_PARTITIONS; ++j){
    #pragma HLS UNROLL
        for (int k=0; k<NUM_STM; ++k) {
        #pragma HLS UNROLL
            shuffle_peek_emulator[j][k].BV = 0;
            shuffle_peek_emulator[j][k].input_idx = 0;
            shuffle_peek_emulator[j][k].valid = 0;
        }
    }


    while(1)
    {
    #pragma HLS PIPELINE II=1

        #if ENABLE_PERF_CTRS
        did_read = 0;
        did_write = 0;
        #endif

        ////////////////////////////////////////////
        // READ LOGIC. Read from each partition stream
        ////////////////////////////////////////////
        RD_BV_PARTITION_LOOP:
        for (int partition_idx = 0;
                partition_idx < BV_NUM_PARTITIONS;
                ++partition_idx)
        {
        #pragma HLS UNROLL

            // DATAPACKED TRANSFER:
            INPUT_IDX_DTYPE     cur_input_idx;
            STRM_IDX_DTYPE      cur_strm_idx;
            BIT_DTYPE           cur_bv_val;
            METADATA_DTYPE      cur_metadata;
            BV_PLUS_METADATA_PACKED_DTYPE     cur_packed_data;
            bool                peek_success;

            peek_success = query_bv_packed_stream[partition_idx].try_peek(
                cur_packed_data
            );

            cur_metadata = cur_packed_data.md;
            cur_bv_val = cur_packed_data.bv_val;

            // Unpack metadata
            cur_strm_idx = cur_metadata.sidx;
            cur_input_idx = cur_metadata.iidx;

                // If the current "peeked" value is not valid, overwrite it
                // with valid data.
                if (peek_success &&
                    shuffle_peek_emulator[partition_idx][cur_strm_idx].valid == 0
                )
                {
                    query_bv_packed_stream[partition_idx].read();

                    // Write it into the buffer
                    shuffle_peek_emulator[partition_idx]
                        [cur_strm_idx].valid = 1;
                    shuffle_peek_emulator[partition_idx]
                        [cur_strm_idx].BV = cur_bv_val;
                    shuffle_peek_emulator[partition_idx]
                        [cur_strm_idx].input_idx = cur_input_idx;

                    #ifdef __DO_DEBUG_PRINTS__
                    printf("SHUFFLE TtoS #%d kp%d - (Strm #%d): Read from (hash, partition, stream) [%d][%d][%d], input_idx=%d\\n",
                        shuffle_idx,
                        kp_idx,
                        cur_strm_idx.to_int(),
                        shuffle_idx,
                        partition_idx,
                        cur_strm_idx.to_int(),
                        cur_input_idx.to_int()
                    );
                    #endif

                    #if ENABLE_PERF_CTRS
                    did_read = 1;
                    #endif
                }
                #ifdef __DO_DEBUG_PRINTS__
                else if (!peek_success)
                {
                    // do nothing
                } else {
                    printf("SHUFFLE TtoS #%d kp%d - peeked value is valid for hash %d, partition %d, strm %d\\n",
                            shuffle_idx,
                            kp_idx,
                            shuffle_idx,
                            partition_idx,
                            cur_strm_idx.to_int()
                    );
                }
                #endif
        }

        ////////////////////////////////////////////
        // WRITE OUTPUTS from the shuffle-buffer
        ////////////////////////////////////////////
        WR_STM_LOOP:
        for (int strm_idx = 0; strm_idx < NUM_STM; ++strm_idx)
        {
            WR_BV_PARTITION_LOOP:
            for (int partition_idx = 0;
                    partition_idx < BV_NUM_PARTITIONS;
                    ++partition_idx)
            {
            #pragma HLS UNROLL
                BV_PLUS_IIDX_PACKED_DTYPE   outval;
                outval.bv_val = shuffle_peek_emulator[partition_idx][strm_idx].BV;
                outval.iidx = shuffle_peek_emulator[partition_idx][strm_idx].input_idx;

                if (shuffle_peek_emulator[partition_idx][strm_idx].valid == 1 &&
                    inter_shuffle_stream[strm_idx*BV_NUM_PARTITIONS + partition_idx].try_write(outval)
                ) {
                    shuffle_peek_emulator[partition_idx][strm_idx].valid = 0;

                    #ifdef __DO_DEBUG_PRINTS__
                    INPUT_IDX_DTYPE     cur_input_idx;
                    cur_input_idx = shuffle_peek_emulator[partition_idx][strm_idx].input_idx;
                    printf("SHUFFLE TtoS #%d kp%d - (Strm #%d): Outputting BV_val=%d to partition=%d. From hash=%d, input_idx=%d\\n",
                            shuffle_idx,
                            kp_idx,
                            strm_idx,
                            outval.bv_val.to_int(),
                            partition_idx,
                            shuffle_idx,
                            cur_input_idx.to_int()
                    );
                    #endif
                }
            }
        }

        #if ENABLE_PERF_CTRS
        UPDATE_PERF_CTRS:
        total_cycles++;

        if (did_write && !did_read){
            writeonly_cycles++;
        }
        else if (did_read && !did_write){
            readonly_cycles++;
        }
        else if (!did_read && !did_write){
            stall_cycles++;
        }
        else if (did_read && did_write){
            readwrite_cycles++;
        }
        #endif
    }

    #if ENABLE_PERF_CTRS
    WRITE_PERF_CTRS:
    for (int i = 0; i < NUM_PERFCTR_OUTPUTS; ++i) {
    #pragma HLS PIPELINE II=1
        if (i == 0){
            perfctr_out.write(stall_cycles);
        }
        else if (i == 1){
            perfctr_out.write(readonly_cycles);
        }
        else if (i == 2){
            perfctr_out.write(writeonly_cycles);
        }
        else if (i == 3){
            perfctr_out.write(readwrite_cycles);
        }
        else if (i == 4){
            perfctr_out.write(total_cycles);
        }
        else{
            perfctr_out.write(55555);
        }
    }


    #ifdef __DO_DEBUG_PRINTS__
    printf("SHUFFLE TtoS #%d kp%d -  stall_cycles         = %25lu\\n",
        shuffle_idx, kp_idx, stall_cycles
    );
    printf("SHUFFLE TtoS #%d kp%d -  readonly_cycles      = %25lu\\n",
        shuffle_idx, kp_idx, readonly_cycles
    );
    printf("SHUFFLE TtoS #%d kp%d -  writeonly_cycles     = %25lu\\n",
        shuffle_idx, kp_idx, writeonly_cycles
    );
    printf("SHUFFLE TtoS #%d kp%d -  readwrite_cycles     = %25lu\\n",
        shuffle_idx, kp_idx, readwrite_cycles
    );
    printf("SHUFFLE TtoS #%d kp%d -  total_cycles         = %25lu\\n",
        shuffle_idx, kp_idx, total_cycles
    );
    #endif

    #endif  // ENABLE_PERF_CTRS



    #ifdef __DO_DEBUG_PRINTS__
    printf("\\n\\nSHUFFLE TtoS #%d kp%d - DONE NOW.\\n\\n",
            shuffle_idx, kp_idx
    );
    #endif

    return;
}
"""
        )
        codeArr.append("\n\n")
        return codeArr









    def generate_shuffle_reorder(self):
        SMALLER_BUFF_MODE = 0
        codeArr = []




        if (SMALLER_BUFF_MODE == 1):
            print(" {}: (BLOOM-97) -     USING SMALLER BUFF Mode, which might lead to better synth times and resource usage. Less congestion, but longer logic delays.".format(__name__))

            codeArr.append('void shuffle_reordering_per_hash(' + "\n")
            codeArr.append('        int shuffle_idx' + "\n")
            codeArr.append('        ,int stm_idx' + "\n")
            codeArr.append('        ,int kp_idx' + "\n")
            codeArr.append('' + "\n")

            for p in range(0, self.config.num_partitions):
                codeArr.append('        ,tapa::istream<BV_PLUS_IIDX_PACKED_DTYPE> & inter_shuffle_stream_p{p}'.format(p=p) + "\n")

            codeArr.append('        ' + "\n")
            codeArr.append('        #if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
            codeArr.append('        crash!,,,' + "\n")
            codeArr.append('        #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream' + "\n")
            codeArr.append(')' + "\n")
            codeArr.append('{' + "\n")
            codeArr.append('    typedef struct {' + "\n")
            codeArr.append('        BIT_DTYPE                   valid;' + "\n")
            codeArr.append('        BV_PLUS_IIDX_PACKED_DTYPE   value;' + "\n")
            codeArr.append('    } PEEK_BUF_DTYPE;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    typedef struct {' + "\n")
            codeArr.append('        BIT_DTYPE           bv;' + "\n")
            codeArr.append('        INPUT_IDX_DTYPE     iidx;' + "\n")
            codeArr.append('        bool                valid;' + "\n")
            codeArr.append('    } SHUFBUF_DTYPE;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    int next_output_idx = 1;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    PEEK_BUF_DTYPE              peek_buf[BV_NUM_PARTITIONS];' + "\n")
            codeArr.append('    #pragma HLS ARRAY_PARTITIONS variable=peek_buf dim=0 complete' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    SHUFBUF_DTYPE               shufbuf[SHUFFLEBUF_SZ];' + "\n")
            codeArr.append('    #pragma HLS ARRAY_PARTITION variable=shufbuf dim=0 complete' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
            codeArr.append('    printf("HELLO from shuffle-ordering, hash %d, stm %d, kp %d!\\n",' + "\n")
            codeArr.append('            shuffle_idx, stm_idx, kp_idx);' + "\n")
            codeArr.append('    #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    PEEK_EMULATOR_INIT:' + "\n")
            codeArr.append('    for (int p = 0; p < BV_NUM_PARTITIONS; ++p) {' + "\n")
            codeArr.append('        peek_buf[p].valid = 0;' + "\n")
            codeArr.append('    }' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    SHUFBUF_EMULATOR_INIT:' + "\n")
            codeArr.append('    for (int i = 0; i < SHUFFLEBUF_SZ; ++i) {' + "\n")
            codeArr.append('        shufbuf[i].bv = 0;' + "\n")
            codeArr.append('        shufbuf[i].iidx = 0;' + "\n")
            codeArr.append('        shufbuf[i].valid = 0;' + "\n")
            codeArr.append('    }' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    MAIN_LOOP:' + "\n")
            codeArr.append('    while(1)' + "\n")
            codeArr.append('    {' + "\n")
            codeArr.append('    #pragma HLS PIPELINE II=1' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        /////////////////////////////' + "\n")
            codeArr.append('        // PEEKBUF READ LOGIC' + "\n")
            codeArr.append('        /////////////////////////////' + "\n")
            codeArr.append('        #define SHUF_REORDER_READ_FROM_PARTITION(PART)  \\' + "\n")
            codeArr.append('            if (!inter_shuffle_stream_p##PART.empty() &&    \\' + "\n")
            codeArr.append('                peek_buf[PART].valid == 0   \\' + "\n")
            codeArr.append('            ) { \\' + "\n")
            codeArr.append('                peek_buf[PART].value = inter_shuffle_stream_p##PART.read(); \\' + "\n")
            codeArr.append('                peek_buf[PART].valid = 1;   \\' + "\n")
            codeArr.append('            }   \\' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            #ifdef __DO_DEBUG_PRINTS__' + "\n")
            codeArr.append('                crash();  we need to move this up lol' + "\n")
            codeArr.append('                printf("SHUFFLE ORDERING stm%d kp%d hash%d - Read from infifo %d\\n",    \\' + "\n")
            codeArr.append('                        stm_idx, kp_idx, shuffle_idx,   \\' + "\n")
            codeArr.append('                        PART    \\' + "\n")
            codeArr.append('                );  \\' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            #endif' + "\n")
            codeArr.append('' + "\n")

            for p in range(0, self.config.num_partitions):
                codeArr.append('        SHUF_REORDER_READ_FROM_PARTITION({p})'.format(p=p) + "\n")

            codeArr.append('' + "\n")
            codeArr.append('        #if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
            codeArr.append('        crash on purpose()' + "\n")
            codeArr.append('        #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        /////////////////////////////' + "\n")
            codeArr.append('        // SHUFBUF READ LOGIC' + "\n")
            codeArr.append('        /////////////////////////////' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        /*' + "\n")
            codeArr.append('        ***' + "\n")
            codeArr.append('        PERFORMANCE NOTE:' + "\n")
            codeArr.append('        This only reads ONE partition per cycle ... so if we' + "\n")
            codeArr.append('        have a "traffic jam" situation then we can backpressure.' + "\n")
            codeArr.append('        ***' + "\n")
            codeArr.append('        */' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        bool    made_selection = 0;' + "\n")
            codeArr.append('        int     chosen_pidx = -1;' + "\n")
            codeArr.append('        int     rd_buf_idx = 0;' + "\n")
            codeArr.append('        int     allowed_rd_iidx = next_output_idx + SHUFFLEBUF_SZ;' + "\n")
            codeArr.append('        PEEK_BUF_DTYPE      peek_item;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        for (int p = 0; p < BV_NUM_PARTITIONS; ++p)' + "\n")
            codeArr.append('        {' + "\n")
            codeArr.append('            if (peek_buf[p].value.iidx < allowed_rd_iidx && ' + "\n")
            codeArr.append('                peek_buf[p].valid == 1' + "\n")
            codeArr.append('            ) {' + "\n")
            codeArr.append('                made_selection = 1;' + "\n")
            codeArr.append('                chosen_pidx = p;' + "\n")
            codeArr.append('                break;' + "\n")
            codeArr.append('            }' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        #ifdef __DO_DEBUG_PRINTS__' + "\n")
            codeArr.append('        if (made_selection) {' + "\n")
            codeArr.append('            printf("SHUFFLE ORDERING stm%d kp%d hash%d - Chosen PIDX = %d, and allowed_rd_idx = %d\\n",' + "\n")
            codeArr.append('                    stm_idx, kp_idx, shuffle_idx' + "\n")
            codeArr.append('                    , chosen_pidx' + "\n")
            codeArr.append('                    , allowed_rd_idx' + "\n")
            codeArr.append('            );' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('        #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        rd_buf_idx = peek_buf[chosen_pidx].value.iidx % SHUFFLEBUF_SZ;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        if ( shufbuf[rd_buf_idx].valid == 0 &&' + "\n")
            codeArr.append('             made_selection' + "\n")
            codeArr.append('        ) {' + "\n")
            codeArr.append('            shufbuf[rd_buf_idx].bv      = peek_buf[chosen_pidx].value.bv_val;' + "\n")
            codeArr.append('            shufbuf[rd_buf_idx].iidx    = peek_buf[chosen_pidx].value.iidx;' + "\n")
            codeArr.append('            shufbuf[rd_buf_idx].valid   = 1;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            peek_buf[chosen_pidx].valid = 0;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            #ifdef __DO_DEBUG_PRINTS__' + "\n")
            codeArr.append('            printf("SHUFFLE ORDERING stm%d kp%d hash%d - Populated shufbuf[%d], with iidx = %d\\n",' + "\n")
            codeArr.append('                    stm_idx, kp_idx, shuffle_idx' + "\n")
            codeArr.append('                    , rd_buf_idx, shufbuf[rd_buf_idx].iidx.to_int()' + "\n")
            codeArr.append('            );' + "\n")
            codeArr.append('            #endif' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        /////////////////////////////' + "\n")
            codeArr.append('        // WRITE LOGIC' + "\n")
            codeArr.append('        /////////////////////////////' + "\n")
            codeArr.append('        bool    write_ready = 0;' + "\n")
            codeArr.append('        int     wr_buf_idx = next_output_idx % SHUFFLEBUF_SZ;' + "\n")
            codeArr.append('        int     ready_partition_idx = 0;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        if (shufbuf[wr_buf_idx].valid == 1 &&' + "\n")
            codeArr.append('            shufbuf[wr_buf_idx].iidx  == next_output_idx' + "\n")
            codeArr.append('        ) {' + "\n")
            codeArr.append('            write_ready = 1;' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('        #ifndef __SYNTHESIS__' + "\n")
            codeArr.append('        else if (shufbuf[wr_buf_idx].valid == 1) {' + "\n")
            codeArr.append('            printf("SHUFFLE ORDERING stm%d kp%d hash%d - Were probably hanging right? iidx = %d, nextidx = %d\\n",' + "\n")
            codeArr.append('                    stm_idx, kp_idx, shuffle_idx,' + "\n")
            codeArr.append('                    shufbuf[wr_buf_idx].iidx.to_int(), next_output_idx' + "\n")
            codeArr.append('            );' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('        #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        if (write_ready){' + "\n")
            codeArr.append('            BIT_DTYPE write_success;' + "\n")
            codeArr.append('            BIT_DTYPE v = shufbuf[wr_buf_idx].bv;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            write_success = reconstruct_stream.try_write(v);' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            if (write_success) {' + "\n")
            codeArr.append('                shufbuf[wr_buf_idx].valid = 0;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('                if (next_output_idx == KEYPAIRS_PER_STM) {' + "\n")
            codeArr.append('                    next_output_idx = 1;' + "\n")
            codeArr.append('                }' + "\n")
            codeArr.append('                else {' + "\n")
            codeArr.append('                    next_output_idx++;' + "\n")
            codeArr.append('                }' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('                #ifdef __DO_DEBUG_PRINTS__' + "\n")
            codeArr.append('                printf("SHUFFLE ORDERING stm%d kp%d hash%d - write BV %d from shufbuf[%d] with iidx %d\\n",' + "\n")
            codeArr.append('                        stm_idx, kp_idx, shuffle_idx,' + "\n")
            codeArr.append('                        v.to_int(),' + "\n")
            codeArr.append('                        wr_buf_idx,' + "\n")
            codeArr.append('                        shufbuf[wr_buf_idx].iidx.to_int()' + "\n")
            codeArr.append('                );' + "\n")
            codeArr.append('                #endif' + "\n")
            codeArr.append('            }' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('    }' + "\n")
            codeArr.append('}' + "\n")



        else:
            print(" {}: (BLOOM-97) - NOT USING SMALLER BUFF Mode, which might lead to worse synth times and resource usage. Higher congestion, lower logic delays.".format(__name__))

            codeArr.append('void shuffle_reordering_per_hash(' + "\n")
            codeArr.append('        int shuffle_idx' + "\n")
            codeArr.append('        ,int stm_idx' + "\n")
            codeArr.append('        ,int kp_idx' + "\n")
            codeArr.append('' + "\n")

            for p in range(0, self.config.num_partitions):
                codeArr.append('        ,tapa::istream<BV_PLUS_IIDX_PACKED_DTYPE> & inter_shuffle_stream_p{p}'.format(p=p) + "\n")

            codeArr.append('        ' + "\n")
            codeArr.append('        #if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
            codeArr.append('        crash!,,,' + "\n")
            codeArr.append('        #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream' + "\n")
            codeArr.append(')' + "\n")
            codeArr.append('{' + "\n")
            codeArr.append('    typedef struct {' + "\n")
            codeArr.append('        BIT_DTYPE           bv;' + "\n")
            codeArr.append('        INPUT_IDX_DTYPE     iidx;' + "\n")
            codeArr.append('        bool                valid;' + "\n")
            codeArr.append('    } PEEKED_DTYPE;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    int next_output_idx = 1;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    PEEKED_DTYPE                shufbuf[BV_NUM_PARTITIONS][SHUFFLEBUF_SZ];' + "\n")
            codeArr.append('    #pragma HLS ARRAY_PARTITION variable=shufbuf dim=0 complete' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
            codeArr.append('    printf("HELLO from shuffle-ordering, hash %d, stm %d, kp %d!\\n",' + "\n")
            codeArr.append('            shuffle_idx, stm_idx, kp_idx);' + "\n")
            codeArr.append('    #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    PEEK_EMULATOR_INIT:' + "\n")
            codeArr.append('    for (int p = 0; p < BV_NUM_PARTITIONS; ++p) {' + "\n")
            codeArr.append('        for (int i = 0; i < SHUFFLEBUF_SZ; ++i) {' + "\n")
            codeArr.append('            shufbuf[p][i].bv = 0;' + "\n")
            codeArr.append('            shufbuf[p][i].iidx = 0;' + "\n")
            codeArr.append('            shufbuf[p][i].valid = 0;' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('    }' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('    MAIN_LOOP:' + "\n")
            codeArr.append('    while(1)' + "\n")
            codeArr.append('    {' + "\n")
            codeArr.append('    #pragma HLS PIPELINE II=1' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        /////////////////////////////' + "\n")
            codeArr.append('        // READ LOGIC' + "\n")
            codeArr.append('        /////////////////////////////' + "\n")
            codeArr.append('' + "\n")

            codeArr.append('        #define READ_PARTITION(PART)    \\' + "\n")
            codeArr.append('            bool                        peek_success_p##PART;   \\' + "\n")
            codeArr.append('            int                         rd_buf_idx_p##PART; \\' + "\n")
            codeArr.append('            BV_PLUS_IIDX_PACKED_DTYPE   read_val_p##PART;   \\' + "\n")
            codeArr.append('            \\' + "\n")
            codeArr.append('            peek_success_p##PART = inter_shuffle_stream_p##PART.try_peek(read_val_p##PART);   \\' + "\n")
            codeArr.append('            rd_buf_idx_p##PART = read_val_p##PART.iidx % SHUFFLEBUF_SZ; \\' + "\n")
            codeArr.append('            if (peek_success_p##PART && \\' + "\n")
            codeArr.append('                shufbuf[PART][rd_buf_idx_p##PART].valid == 0  \\' + "\n")
            codeArr.append('            ) { \\' + "\n")
            codeArr.append('                inter_shuffle_stream_p##PART.read();  \\' + "\n")
            codeArr.append('            \\' + "\n")
            codeArr.append('                shufbuf[PART][rd_buf_idx_p##PART].bv = read_val_p##PART.bv_val;   \\' + "\n")
            codeArr.append('                shufbuf[PART][rd_buf_idx_p##PART].iidx = read_val_p##PART.iidx;   \\' + "\n")
            codeArr.append('                shufbuf[PART][rd_buf_idx_p##PART].valid = 1;  \\' + "\n")
            codeArr.append('            }   \\' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('                //#ifdef __DO_DEBUG_PRINTS__' + "\n")
            codeArr.append('                //printf("SHUFFLE ORDERING stm%d kp%d hash%d - read BV %d from partition %d, iidx %d, into buf_idx %d\\n",' + "\n")
            codeArr.append('                //        stm_idx, kp_idx, shuffle_idx,' + "\n")
            codeArr.append('                //        read_val.bv_val.to_int(),' + "\n")
            codeArr.append('                //        partition_idx,' + "\n")
            codeArr.append('                //        read_val.iidx.to_int(),' + "\n")
            codeArr.append('                //        rd_buf_idx' + "\n")
            codeArr.append('                //);' + "\n")
            codeArr.append('                //#endif' + "\n")
            codeArr.append('' + "\n")
            for p in range(0, self.config.num_partitions):
                codeArr.append('        READ_PARTITION({p})'.format(p=p) + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        #if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
            codeArr.append('        crash();' + "\n")
            codeArr.append('        #endif' + "\n")





            #codeArr.append('        for (int partition_idx = 0; partition_idx < BV_NUM_PARTITIONS; ++partition_idx)' + "\n")
            #codeArr.append('        {' + "\n")
            #codeArr.append('' + "\n")
            #codeArr.append('            bool                        peek_success;' + "\n")
            #codeArr.append('            int                         rd_buf_idx;' + "\n")
            #codeArr.append('            BV_PLUS_IIDX_PACKED_DTYPE   read_val;' + "\n")
            #codeArr.append('' + "\n")

            #for p in range(0, self.config.num_partitions):
            #    codeArr.append('            if (partition_idx == {p}) {{ peek_success = inter_shuffle_stream_p{p}.try_peek(read_val); }}'.format(p=p) + "\n")

            #codeArr.append('        ' + "\n")
            #codeArr.append('            #if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
            #codeArr.append('            crash!(;' + "\n")
            #codeArr.append('            #endif' + "\n")

            #codeArr.append('' + "\n")
            #codeArr.append('            rd_buf_idx = read_val.iidx % SHUFFLEBUF_SZ;' + "\n")
            #codeArr.append('' + "\n")
            #codeArr.append('            if (peek_success &&' + "\n")
            #codeArr.append('                shufbuf[partition_idx][rd_buf_idx].valid == 0' + "\n")
            #codeArr.append('            ) {' + "\n")

            #for p in range(0, self.config.num_partitions):
            #    codeArr.append('                if (partition_idx == {p}) {{ inter_shuffle_stream_p{p}.read(); }}'.format(p=p) + "\n")

            #codeArr.append('' + "\n")
            #codeArr.append('                #if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
            #codeArr.append('                crash!(;' + "\n")
            #codeArr.append('                #endif' + "\n")
            #codeArr.append('' + "\n")

            #codeArr.append('                shufbuf[partition_idx][rd_buf_idx].bv       = read_val.bv_val;' + "\n")
            #codeArr.append('                shufbuf[partition_idx][rd_buf_idx].iidx     = read_val.iidx;' + "\n")
            #codeArr.append('                shufbuf[partition_idx][rd_buf_idx].valid    = 1;' + "\n")
            #codeArr.append('' + "\n")
            #codeArr.append('                #ifdef __DO_DEBUG_PRINTS__' + "\n")
            #codeArr.append('                printf("SHUFFLE ORDERING stm%d kp%d hash%d - read BV %d from partition %d, iidx %d, into buf_idx %d\\n",' + "\n")
            #codeArr.append('                        stm_idx, kp_idx, shuffle_idx,' + "\n")
            #codeArr.append('                        read_val.bv_val.to_int(),' + "\n")
            #codeArr.append('                        partition_idx,' + "\n")
            #codeArr.append('                        read_val.iidx.to_int(),' + "\n")
            #codeArr.append('                        rd_buf_idx' + "\n")
            #codeArr.append('                );' + "\n")
            #codeArr.append('                #endif' + "\n")
            #codeArr.append('' + "\n")
            #codeArr.append('' + "\n")
            #codeArr.append('' + "\n")
            #codeArr.append('                // DO WE NEED A BREAK STATEMENT FOR FREQUENCY? - No, I tested this and the HLS log says the freq gets worse.' + "\n")
            #codeArr.append('            }' + "\n")
            #codeArr.append('        }' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        /////////////////////////////' + "\n")
            codeArr.append('        // WRITE LOGIC' + "\n")
            codeArr.append('        /////////////////////////////' + "\n")
            codeArr.append('        bool    write_ready = 0;' + "\n")
            codeArr.append('        int     wr_buf_idx = next_output_idx % SHUFFLEBUF_SZ;' + "\n")
            codeArr.append('        int     ready_partition_idx = 0;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        for (int partition_idx = 0; partition_idx < BV_NUM_PARTITIONS; ++partition_idx)' + "\n")
            codeArr.append('        {' + "\n")
            codeArr.append('            if (shufbuf[partition_idx][wr_buf_idx].valid    == 1 &&' + "\n")
            codeArr.append('                shufbuf[partition_idx][wr_buf_idx].iidx     == next_output_idx' + "\n")
            codeArr.append('            )' + "\n")
            codeArr.append('            {' + "\n")
            codeArr.append('                write_ready = 1;' + "\n")
            codeArr.append('                ready_partition_idx = partition_idx;' + "\n")
            codeArr.append('                break;' + "\n")
            codeArr.append('            }' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        if (write_ready){' + "\n")
            codeArr.append('            BIT_DTYPE write_success;' + "\n")
            codeArr.append('            BIT_DTYPE v = shufbuf[ready_partition_idx][wr_buf_idx].bv;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            write_success = reconstruct_stream.try_write(v);' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            if (write_success) {' + "\n")
            codeArr.append('                shufbuf[ready_partition_idx][wr_buf_idx].valid = 0;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('                if (next_output_idx == KEYPAIRS_PER_STM) {' + "\n")
            codeArr.append('                    next_output_idx = 1;' + "\n")
            codeArr.append('                }' + "\n")
            codeArr.append('                else {' + "\n")
            codeArr.append('                    next_output_idx++;' + "\n")
            codeArr.append('                }' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('                #ifdef __DO_DEBUG_PRINTS__' + "\n")
            codeArr.append('                printf("SHUFFLE ORDERING stm%d kp%d hash%d - write BV %d from buf_idx %d\\n",' + "\n")
            codeArr.append('                        stm_idx, kp_idx, shuffle_idx,' + "\n")
            codeArr.append('                        v.to_int(),' + "\n")
            codeArr.append('                        wr_buf_idx' + "\n")
            codeArr.append('                );' + "\n")
            codeArr.append('                #endif' + "\n")
            codeArr.append('            }' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('    }' + "\n")
            codeArr.append('}' + "\n")


        return codeArr


    ##############################################
    ##############################################
    ##############################################
    ##############################################
    ##############################################
    ##############################################
    ##############################################
    ##############################################



    def generate_shuffle_per_hash(self):
        codeArr = []

        codeArr.append(
"""
void shuffle_per_hash(
        int shuffle_idx,
        int kp_idx,
        tapa::istreams<BV_PLUS_METADATA_PACKED_DTYPE, BV_NUM_PARTITIONS> & query_bv_packed_stream

        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm0
        #if NUM_STM>1
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm1
        #endif
        #if NUM_STM>2
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm2
        #endif
        #if NUM_STM>3
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm3
        #endif
        #if NUM_STM>4
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm4
        #endif
        #if NUM_STM>5
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm5
        #endif
        #if NUM_STM>6
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm6
        #endif
        #if NUM_STM>7
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm7
        #endif
        #if NUM_STM>8
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm8
        #endif
        #if NUM_STM>9
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm9
        #endif
        #if NUM_STM>10
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm10
        #endif
        #if NUM_STM>11
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm11
        #endif
        #if NUM_STM>12
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm12
        #endif
        #if NUM_STM>13
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm13
        #endif
        #if NUM_STM>14
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm14
        #endif
        #if NUM_STM>15
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm15
        #endif
        #if NUM_STM>16
        ,tapa::ostream<BIT_DTYPE> & reconstruct_stream_stm16
        #endif
        #if NUM_STM>17
        crash!!!!
        #endif

        #if ENABLE_PERF_CTRS
        ,tapa::ostream<PERFCTR_DTYPE>   &perfctr_out
        #endif
){
    #ifndef __SYNTHESIS__
    printf("WARNING: Using SPLIT-MONOLITHIC SHUFFLE.\\n");
    #endif

    typedef struct {
        BIT_DTYPE       BV;
        INPUT_IDX_DTYPE     input_idx;
        bool                valid;
    } PEEKED_DTYPE;

    int next_output_idx[NUM_STM];
    #pragma HLS ARRAY_PARTITION variable=next_output_idx dim=0 complete

    // This is a buffer for data from each partition.
    // We also introduce a NUM_STM dimension, otherwise we hang.
    // We introduce the SHUFFLEBUF_SZ dimension to (hopefully) improve performance.
    PEEKED_DTYPE shuffle_peek_emulator[BV_NUM_PARTITIONS][NUM_STM][SHUFFLEBUF_SZ];
    #pragma HLS ARRAY_PARTITION variable=shuffle_peek_emulator dim=0 complete

    #if ENABLE_PERF_CTRS
    BIT_DTYPE       did_read;
    BIT_DTYPE       did_write;

    PERFCTR_DTYPE   stall_cycles = 0;
    PERFCTR_DTYPE   readonly_cycles = 0;
    PERFCTR_DTYPE   writeonly_cycles = 0;
    PERFCTR_DTYPE   readwrite_cycles = 0;
    PERFCTR_DTYPE   total_cycles = 0;
    #endif


    NEXT_OUTPUT_IDX_INIT:
    for (int i = 0; i < NUM_STM; ++i) {
    #pragma HLS UNROLL
        next_output_idx[i] = 1;
    }

    PEEK_EMULATOR_INITIALIZATION:
    for (int j=0; j<BV_NUM_PARTITIONS; ++j){
    #pragma HLS UNROLL
        for (int k=0; k<NUM_STM; ++k) {
        #pragma HLS UNROLL
            for (int l=0; l<SHUFFLEBUF_SZ; ++l) {
            #pragma HLS UNROLL
                shuffle_peek_emulator[j][k][l].BV = 0;
                shuffle_peek_emulator[j][k][l].input_idx = 0;
                shuffle_peek_emulator[j][k][l].valid = 0;
            }
        }
    }


    while(1)
    {
    #pragma HLS PIPELINE II=1

        #if ENABLE_PERF_CTRS
        did_read = 0;
        did_write = 0;
        #endif

        ////////////////////////////////////////////
        // READ LOGIC. Read from each partition stream
        ////////////////////////////////////////////
        RD_BV_PARTITION_LOOP:
        for (int partition_idx = 0;
                partition_idx < BV_NUM_PARTITIONS;
                ++partition_idx)
        {
        #pragma HLS UNROLL

            // DATAPACKED TRANSFER:
            INPUT_IDX_DTYPE     cur_input_idx;
            STRM_IDX_DTYPE      cur_strm_idx;
            BIT_DTYPE           cur_bv_val;
            METADATA_DTYPE      cur_metadata;
            BV_PLUS_METADATA_PACKED_DTYPE     cur_packed_data;
            bool                peek_success;

            peek_success = query_bv_packed_stream[partition_idx].try_peek(
                cur_packed_data
            );

            cur_metadata = cur_packed_data.md;
            cur_bv_val = cur_packed_data.bv_val;

            // Unpack metadata
            cur_strm_idx = cur_metadata.sidx;
            cur_input_idx = cur_metadata.iidx;

            int buf_idx = cur_input_idx % SHUFFLEBUF_SZ;

                // If the current "peeked" value is not valid, overwrite it
                // with valid data.
                if (peek_success &&
                    shuffle_peek_emulator[partition_idx][cur_strm_idx][buf_idx].valid == 0
                )
                {
                    query_bv_packed_stream[partition_idx].read();

                    // Write it into the buffer
                    shuffle_peek_emulator[partition_idx]
                        [cur_strm_idx][buf_idx].valid = 1;
                    shuffle_peek_emulator[partition_idx]
                        [cur_strm_idx][buf_idx].BV = cur_bv_val;
                    shuffle_peek_emulator[partition_idx]
                        [cur_strm_idx][buf_idx].input_idx = cur_input_idx;

                    #ifdef __DO_DEBUG_PRINTS__
                    printf("SHUFFLE UNIT #%d kp%d - (Strm #%d): Read from (hash, partition, stream, bufidx) [%d][%d][%d][%d], input_idx=%d\\n",
                        shuffle_idx,
                        kp_idx,
                        cur_strm_idx.to_int(),
                        shuffle_idx,
                        partition_idx,
                        cur_strm_idx.to_int(),
                        buf_idx,
                        cur_input_idx.to_int()
                    );
                    #endif

                    #if ENABLE_PERF_CTRS
                    did_read = 1;
                    #endif
                }
                #ifdef __DO_DEBUG_PRINTS__
                else if (!peek_success)
                {
                    // do nothing
                } else {
                    printf("SHUFFLE UNIT #%d kp%d - peeked value is valid for hash %d, partition %d, strm %d, bufidx %d\\n",
                            shuffle_idx,
                            kp_idx,
                            shuffle_idx,
                            partition_idx,
                            cur_strm_idx.to_int(),
                            buf_idx
                    );
                }
                #endif
        }

        ////////////////////////////////////////////
        // WRITE OUTPUTS from the shuffle-buffer
        ////////////////////////////////////////////
        WR_STM_LOOP:
        for (int strm_idx = 0; strm_idx < NUM_STM; ++strm_idx)
        {
            BIT_DTYPE cur_stm_ready = 0;
            int ready_partition_idx = 0;
            int ready_buf_idx = 0;

            WR_BV_PARTITION_LOOP:
            for (int partition_idx = 0;
                    partition_idx < BV_NUM_PARTITIONS;
                    ++partition_idx)
            {
            #pragma HLS UNROLL

                int buf_idx = next_output_idx[strm_idx] % SHUFFLEBUF_SZ;

                if (shuffle_peek_emulator[partition_idx][strm_idx][buf_idx].valid == 1 &&
                    shuffle_peek_emulator[partition_idx][strm_idx][buf_idx].input_idx == next_output_idx[strm_idx]
                )
                {
                    cur_stm_ready       = 1;
                    ready_partition_idx = partition_idx;
                    ready_buf_idx       = buf_idx;
                    break;
                }
            }

            if (cur_stm_ready) {
                BIT_DTYPE       cur_bv_val;
                BIT_DTYPE       write_success = 0;

                cur_bv_val = shuffle_peek_emulator[ready_partition_idx]
                                    [strm_idx][ready_buf_idx].BV;

                #ifdef __DO_DEBUG_PRINTS__
                INPUT_IDX_DTYPE     cur_input_idx;
                cur_input_idx = shuffle_peek_emulator[ready_partition_idx]
                                    [strm_idx][ready_buf_idx].input_idx;
                printf("SHUFFLE UNIT #%d kp%d - (Strm #%d): Outputting BV_val=%d. From hash=%d, input_idx=%d\\n",
                        shuffle_idx,
                        kp_idx,
                        strm_idx,
                        cur_bv_val.to_int(),
                        shuffle_idx,
                        cur_input_idx.to_int()
                );
                #endif

                if (strm_idx == 0) {
                    write_success = reconstruct_stream_stm0.try_write(cur_bv_val);
                }
                #if NUM_STM>1
                if (strm_idx == 1) {
                    write_success = reconstruct_stream_stm1.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>2
                if (strm_idx == 2) {
                    write_success = reconstruct_stream_stm2.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>3
                if (strm_idx == 3) {
                    write_success = reconstruct_stream_stm3.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>4
                if (strm_idx == 4) {
                    write_success = reconstruct_stream_stm4.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>5
                if (strm_idx == 5) {
                    write_success = reconstruct_stream_stm5.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>6
                if (strm_idx == 6) {
                    write_success = reconstruct_stream_stm6.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>7
                if (strm_idx == 7) {
                    write_success = reconstruct_stream_stm7.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>8
                if (strm_idx == 8) {
                    write_success = reconstruct_stream_stm8.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>9
                if (strm_idx == 9) {
                    write_success = reconstruct_stream_stm9.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>10
                if (strm_idx == 10) {
                    write_success = reconstruct_stream_stm10.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>11
                if (strm_idx == 11) {
                    write_success = reconstruct_stream_stm11.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>12
                if (strm_idx == 12) {
                    write_success = reconstruct_stream_stm12.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>13
                if (strm_idx == 13) {
                    write_success = reconstruct_stream_stm13.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>14
                if (strm_idx == 14) {
                    write_success = reconstruct_stream_stm14.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>15
                if (strm_idx == 15) {
                    write_success = reconstruct_stream_stm15.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>16
                if (strm_idx == 16) {
                    write_success = reconstruct_stream_stm16.try_write(cur_bv_val);
                }
                #endif
                #if NUM_STM>17
                crash!!!!
                #endif

                if (write_success) {
                    shuffle_peek_emulator[ready_partition_idx]
                            [strm_idx][ready_buf_idx].valid = 0;

                    if (next_output_idx[strm_idx] == KEYPAIRS_PER_STM) {
                        next_output_idx[strm_idx] = 1;
                    }
                    else {
                        next_output_idx[strm_idx]++;
                    }

                    #if ENABLE_PERF_CTRS
                    did_write = 1;
                    #endif
                }
            }
            #ifdef __DO_DEBUG_PRINTS__
            else {
                printf("SHUFFLE UNIT #%d kp%d - shuffle_peek_emulator[partition_idx][strm_idx]\\n",
                        shuffle_idx, kp_idx
                );
                for (int strm_ii = 0; strm_ii < NUM_STM; ++strm_ii)
                {
                    for (int par_ii=0; par_ii < BV_NUM_PARTITIONS; ++par_ii)
                    {
                        for (int buf_ii=0; buf_ii < SHUFFLEBUF_SZ; ++buf_ii)
                        {
                            printf("SHUFFLE UNIT #%d kp%d - shuffle_peek_emulator[%d][%d][%d]: valid=%d, input_idx=%d\\n",
                                    shuffle_idx,
                                    kp_idx,
                                    par_ii, strm_ii, buf_ii,
                                    shuffle_peek_emulator[par_ii]
                                        [strm_ii][buf_ii].valid,
                                    shuffle_peek_emulator[par_ii]
                                        [strm_ii][buf_ii].input_idx.to_int()
                            );
                        }
                    }
                }
            }
            #endif
        }

        #if ENABLE_PERF_CTRS
        UPDATE_PERF_CTRS:
        total_cycles++;

        if (did_write && !did_read){
            writeonly_cycles++;
        }
        else if (did_read && !did_write){
            readonly_cycles++;
        }
        else if (!did_read && !did_write){
            stall_cycles++;
        }
        else if (did_read && did_write){
            readwrite_cycles++;
        }
        #endif
    }

    #if ENABLE_PERF_CTRS
    WRITE_PERF_CTRS:
    for (int i = 0; i < NUM_PERFCTR_OUTPUTS; ++i) {
    #pragma HLS PIPELINE II=1
        if (i == 0){
            perfctr_out.write(stall_cycles);
        }
        else if (i == 1){
            perfctr_out.write(readonly_cycles);
        }
        else if (i == 2){
            perfctr_out.write(writeonly_cycles);
        }
        else if (i == 3){
            perfctr_out.write(readwrite_cycles);
        }
        else if (i == 4){
            perfctr_out.write(total_cycles);
        }
        else{
            perfctr_out.write(55555);
        }
    }


    #ifdef __DO_DEBUG_PRINTS__
    printf("SHUFFLE UNIT #%d kp%d -  stall_cycles         = %25lu\\n",
        shuffle_idx, kp_idx, stall_cycles
    );
    printf("SHUFFLE UNIT #%d kp%d -  readonly_cycles      = %25lu\\n",
        shuffle_idx, kp_idx, readonly_cycles
    );
    printf("SHUFFLE UNIT #%d kp%d -  writeonly_cycles     = %25lu\\n",
        shuffle_idx, kp_idx, writeonly_cycles
    );
    printf("SHUFFLE UNIT #%d kp%d -  readwrite_cycles     = %25lu\\n",
        shuffle_idx, kp_idx, readwrite_cycles
    );
    printf("SHUFFLE UNIT #%d kp%d -  total_cycles         = %25lu\\n",
        shuffle_idx, kp_idx, total_cycles
    );
    #endif

    #endif  // ENABLE_PERF_CTRS



    #ifdef __DO_DEBUG_PRINTS__
    printf("\\n\\nSHUFFLE UNIT #%d kp%d - DONE NOW.\\n\\n",
            shuffle_idx, kp_idx
    );
    #endif

    return;
}
"""
        )
        codeArr.append("\n\n")
        return codeArr









    def generate_monoshuffle_wrapper(self):
        codeArr = []

        codeArr.append('#define SHUFFLE_STREAM_DECLS_KP(KP_IDX)     // Purposefully empty.' + "\n")

        codeArr.append('#define SHUFFLE_INVOKES_FOR_KP(KP_IDX)     \\' + "\n")
        for h in range(0, self.config.num_hash):
            codeArr.append('        .invoke<tapa::detach>(    \\' + "\n")
            codeArr.append('            shuffle_per_hash    \\' + "\n")
            codeArr.append('            , {h} \\'.format(h=h) + "\n")
            codeArr.append('            , KP_IDX    \\' + "\n")
            codeArr.append('            , query_bv_packed_stream_hash{h}_kp##KP_IDX  \\'.format(h=h) + "\n")

            for s in range(0, self.config.num_stm):
                codeArr.append('            , reconstruct_stream_stm{s}_kp##KP_IDX[{h}] \\'.format(s=s, h=h) + "\n")

            codeArr.append('            \\' + "\n")
            if (self.config.enable_perfctrs):
                codeArr.append('            ,perfctr_out[{h}] \\'.format(h=h) + "\n")
            codeArr.append('        )   \\' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('#if NUM_HASH != ({})'.format(self.config.num_hash) + "\n")
        codeArr.append('crash!' + "\n")
        codeArr.append('#endif' + "\n")
        codeArr.append("\n\n")

        return codeArr



    def generate_bifurcated_shuffle_wrapper(self):
        codeArr = []

        codeArr.append('#define SHUFFLE_STREAM_DECLS_KP(KP_IDX)    \\' + "\n")

        for h in range(0, self.config.num_hash):
            codeArr.append('    tapa::streams<BV_PLUS_IIDX_PACKED_DTYPE, NUM_STM*BV_NUM_PARTITIONS> inter_shuf{h}_stm_kp##KP_IDX;   \\'.format(h=h) + "\n")

        codeArr.append('' + "\n")
        codeArr.append('#if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('crash!,' + "\n")
        codeArr.append('#endif' + "\n")
        codeArr.append('' + "\n")


        codeArr.append('' + "\n")
        codeArr.append('#define SHUFFLE_REORDER_INVOKES_FOR_SHUF_KP(SHUF_IDX, KP_IDX)      \\' + "\n")

        for s in range(0, self.config.num_stm):
            codeArr.append('        .invoke<tapa::detach>(  \\' + "\n")
            codeArr.append('            shuffle_reordering_per_hash \\' + "\n")
            codeArr.append('            ,SHUF_IDX   \\' + "\n")
            codeArr.append('            ,{s}  \\'.format(s=s) + "\n")
            codeArr.append('            ,KP_IDX \\' + "\n")
            for p in range(0, self.config.num_partitions):
                codeArr.append('            ,inter_shuf##SHUF_IDX##_stm_kp##KP_IDX[{p}+BV_NUM_PARTITIONS*{s}]    \\'.format(p=p, s=s) + "\n")
            codeArr.append('            ,reconstruct_stream_stm{s}_kp##KP_IDX[SHUF_IDX] \\'.format(s=s) + "\n")
            codeArr.append('        )   \\' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('#if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
        codeArr.append('crash!,' + "\n")
        codeArr.append('#endif' + "\n")
        codeArr.append('#if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('crash!,' + "\n")
        codeArr.append('#endif' + "\n")
        codeArr.append('' + "\n")


        codeArr.append('' + "\n")
        codeArr.append('#define SHUFFLE_INVOKES_FOR_KP(KP_IDX)     \\' + "\n")

        for h in range(0, self.config.num_hash):
            codeArr.append('        .invoke<tapa::detach>(    \\' + "\n")
            codeArr.append('            shuffle_TtoS_per_hash    \\' + "\n")
            codeArr.append('            , {h} \\'.format(h=h) + "\n")
            codeArr.append('            , KP_IDX    \\' + "\n")
            codeArr.append('            , query_bv_packed_stream_hash{h}_kp##KP_IDX  \\'.format(h=h) + "\n")
            codeArr.append('            , inter_shuf{h}_stm_kp##KP_IDX \\'.format(h=h) + "\n")
            codeArr.append('            \\' + "\n")
            codeArr.append('        )   \\' + "\n")

        for h in range(0, self.config.num_hash):
            codeArr.append('        SHUFFLE_REORDER_INVOKES_FOR_SHUF_KP({h}, KP_IDX)  \\'.format(h=h) + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('crash!' + "\n")
        codeArr.append('#endif' + "\n")

        return codeArr




















    def generate(self):
        codeArr = []
        if (self.config.shuffle_type == Types.ShuffleType.SPLIT_MONOLITHIC):
            codeArr.extend(self.generate_shuffle_per_hash())
            codeArr.extend(self.generate_monoshuffle_wrapper())

        elif (self.config.shuffle_type == Types.ShuffleType.BIFURCATED):
            codeArr.extend(self.generate_shuffle_TtoS())
            codeArr.extend(self.generate_shuffle_reorder())
            codeArr.extend(self.generate_bifurcated_shuffle_wrapper())

        else:
            raise ValueError("The specified type of shuffle unit is not supported.")

        return codeArr











