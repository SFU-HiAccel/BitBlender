
from ..types import ArbiterType

class ArbCodeGenerator:
    def __init__(self, config):
        self.config = config

    def generate_preamble(self):
        codeArr = []
        codeArr.append("\n")
        codeArr.append("\n")
        codeArr.append("\n")
        codeArr.append("""
//////////////////////////////////////////////////
//////////////////////////////////////////////////
///////// Arbiter                           //////
//////////////////////////////////////////////////
//////////////////////////////////////////////////
"""
        )
        codeArr.append("\n")
        codeArr.append("\n")
        return codeArr


    def generate_postamble(self):
        codeArr = []
        codeArr.append("\n")
        codeArr.append("\n")
        codeArr.append("\n")
        codeArr.append("""
//////////////////////////////////////////////////
//////////////////////////////////////////////////
///////// END OF Arbiter                    //////
//////////////////////////////////////////////////
//////////////////////////////////////////////////
"""
        )
        codeArr.append("\n")
        codeArr.append("\n")
        codeArr.append("\n")
        return codeArr



    def generate_hier_arb_fwd(self):
        codeArr = []
        codeArr.append('void bloom_arb_forwarder(' + "\n")
        codeArr.append('        int arb_idx' + "\n")
        codeArr.append('        ,int kp_idx' + "\n")
        codeArr.append('        ,tapa::istreams<HASHONLY_DTYPE, NUM_STM>                         & hash_stream' + "\n")
        codeArr.append('        ,tapa::ostreams<PACKED_HASH_DTYPE, NUM_STM*BV_NUM_PARTITIONS>    & arb_stream' + "\n")
        codeArr.append('){' + "\n")
        codeArr.append('    typedef struct {' + "\n")
        codeArr.append('        ap_uint<1>          valid;' + "\n")
        codeArr.append('        PACKED_HASH_DTYPE   value;' + "\n")
        codeArr.append('        uint32_t            target_partition_idx;' + "\n")
        codeArr.append('    } XBAR_DTYPE;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    const int READ_STOP_COUNT =     NUM_STM * KEYPAIRS_PER_STM;' + "\n")
        codeArr.append('    const int WRITE_STOP_COUNT =    KEYPAIRS_PER_STM;' + "\n")
        codeArr.append('    int total_num_reads = 0;' + "\n")
        codeArr.append('    int total_num_writes = 0;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    int num_writes_per_stm[NUM_STM];' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=num_writes_per_stm dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __SYNTHESIS__' + "\n")
        codeArr.append('    /* TAPA Known-issue: Static keyword fails CSIM because this' + "\n")
        codeArr.append('       isnt thread-safe. But when running the HW build, it will ' + "\n")
        codeArr.append('       instantiate several copies of this function. So this is OK.' + "\n")
        codeArr.append('    */' + "\n")
        codeArr.append('    static' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('    INPUT_IDX_DTYPE     reads_per_input[NUM_STM];' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=reads_per_input dim=0 complete' + "\n")
        codeArr.append('    #ifdef __SYNTHESIS__' + "\n")
        codeArr.append('    /* TAPA Known-issue: Static keyword fails CSIM because this' + "\n")
        codeArr.append('       isnt thread-safe. But when running the HW build, it will ' + "\n")
        codeArr.append('       instantiate several copies of this function. So this is OK.' + "\n")
        codeArr.append('    */' + "\n")
        codeArr.append('    static' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('    XBAR_DTYPE          xbar[NUM_STM];' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=xbar dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifndef __SYNTHESIS__' + "\n")
        codeArr.append('    printf("NOTE: USING HIERARCHICAL ARBITER!!!\\n");' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    INIT_LOOP:' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_STM; ++i)' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('        reads_per_input[i] = 0;' + "\n")
        codeArr.append('        num_writes_per_stm[i] = 0;' + "\n")
        codeArr.append('        xbar[i].valid = 0;' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    MAIN_LOOP:' + "\n")
        codeArr.append('    while (total_num_reads < READ_STOP_COUNT  ||' + "\n")
        for i in range(0, self.config.num_stm):
            if (i < self.config.num_stm-1):
                OR = " ||"
            else:
                OR = ""
            codeArr.append('            num_writes_per_stm[{i}] < WRITE_STOP_COUNT {OR}'.format(i=i, OR=OR) + "\n")
        codeArr.append('            #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('             crash. ||' + "\n")
        codeArr.append('            #endif' + "\n")
        codeArr.append('    ) {' + "\n")
        codeArr.append('    #pragma HLS PIPELINE II=1' + "\n")
        codeArr.append('        RD_LOGIC:' + "\n")
        codeArr.append('        for (int strm_idx = 0; strm_idx < NUM_STM; ++strm_idx) {' + "\n")
        codeArr.append('        #pragma HLS UNROLL' + "\n")
        codeArr.append('            // Metadata:' + "\n")
        codeArr.append('            INPUT_IDX_DTYPE cur_input_idx;' + "\n")
        codeArr.append('            STRM_IDX_DTYPE cur_strm_idx;' + "\n")
        codeArr.append('            METADATA_DTYPE cur_metadata;' + "\n")
        codeArr.append('            PACKED_HASH_DTYPE packed_hashval;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            if (xbar[strm_idx].valid == 1)' + "\n")
        codeArr.append('            {' + "\n")
        codeArr.append('                // Dont replace this value.' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('            else if (!hash_stream[strm_idx].empty())' + "\n")
        codeArr.append('            {' + "\n")
        codeArr.append('                // Hash and partition data:' + "\n")
        codeArr.append('                HASHONLY_DTYPE  tmp_hash = hash_stream[strm_idx].read();' + "\n")
        codeArr.append('                HASHONLY_DTYPE  idx_inside_partition = tmp_hash % BV_PARTITION_LENGTH;' + "\n")
        codeArr.append('                int             partition_idx = (tmp_hash / BV_PARTITION_LENGTH);' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                total_num_reads++;' + "\n")
        codeArr.append('                reads_per_input[strm_idx]++;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                // Pack metadata' + "\n")
        codeArr.append('                cur_metadata.sidx = strm_idx;' + "\n")
        codeArr.append('                cur_metadata.iidx = reads_per_input[strm_idx];' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                // Pack final payload' + "\n")
        codeArr.append('                packed_hashval.md = cur_metadata;' + "\n")
        codeArr.append('                packed_hashval.hash = idx_inside_partition;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                xbar[strm_idx].valid = 1;' + "\n")
        codeArr.append('                xbar[strm_idx].value = packed_hashval;' + "\n")
        codeArr.append('                xbar[strm_idx].target_partition_idx = partition_idx;' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('        printf("ARBITER FORWARDER #%d kp%d - xbar[target_partition][strm_idx]\\n",' + "\n")
        codeArr.append('            arb_idx, kp_idx' + "\n")
        codeArr.append('        );' + "\n")
        codeArr.append('        for (int strm = 0; strm < NUM_STM; ++strm)' + "\n")
        codeArr.append('        {' + "\n")
        codeArr.append('            printf("ARBITER FORWARDER #%d kp%d - xbar[%d][%d]: valid=%d, input_idx=%d\\n",' + "\n")
        codeArr.append('                    arb_idx, kp_idx,' + "\n")
        codeArr.append('                    xbar[strm].target_partition_idx,' + "\n")
        codeArr.append('                    strm,' + "\n")
        codeArr.append('                    xbar[strm].valid.to_int(),' + "\n")
        codeArr.append('                    xbar[strm].value.md.iidx.to_int()' + "\n")
        codeArr.append('            );' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        WR_LOGIC:' + "\n")
        codeArr.append('        for (int partition_idx = 0; partition_idx < BV_NUM_PARTITIONS; ++partition_idx) ' + "\n")
        codeArr.append('        {' + "\n")
        codeArr.append('        #pragma HLS UNROLL' + "\n")
        codeArr.append('            bool                found = false;' + "\n")
        codeArr.append('            uint32_t            found_strm_idx = 0;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            for (int strm_idx = 0; strm_idx < NUM_STM; ++strm_idx)' + "\n")
        codeArr.append('            {' + "\n")
        codeArr.append('            #pragma HLS UNROLL' + "\n")
        codeArr.append('                int out_fifo_idx = partition_idx*NUM_STM + strm_idx;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                if (xbar[strm_idx].valid == 1 &&' + "\n")
        codeArr.append('                    xbar[strm_idx].target_partition_idx == partition_idx)' + "\n")
        codeArr.append('                {' + "\n")
        codeArr.append('                    if (arb_stream[out_fifo_idx].try_write( xbar[strm_idx].value ))' + "\n")
        codeArr.append('                    {' + "\n")
        codeArr.append('                        num_writes_per_stm[strm_idx]++;' + "\n")
        codeArr.append('                        xbar[strm_idx].valid = 0;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                        #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                        printf("ARBITER FORWARDER #%d kp%d - Wrote to outfifo %d\\n",' + "\n")
        codeArr.append('                                arb_idx, kp_idx, out_fifo_idx' + "\n")
        codeArr.append('                        );' + "\n")
        codeArr.append('                        #endif' + "\n")
        codeArr.append('                    }' + "\n")
        codeArr.append('                    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                    else{' + "\n")
        codeArr.append('                        printf("ARBITER FORWARDER #%d kp%d - Failed to write to outfifo %d\\n",' + "\n")
        codeArr.append('                                arb_idx, kp_idx, out_fifo_idx' + "\n")
        codeArr.append('                        );' + "\n")
        codeArr.append('                    }' + "\n")
        codeArr.append('                    #endif' + "\n")
        codeArr.append('                }' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    printf("\\n\\nARBITER FORWARDER #%d kp%d - DONE NOW.\\n\\n",' + "\n")
        codeArr.append('            arb_idx, kp_idx' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append("\n\n\n")

        return codeArr






    def generate_hier_arb_atom(self):
        codeArr = []

        codeArr.append('void bloom_hier_arbiter_atom(' + "\n")
        codeArr.append('        int arb_idx,' + "\n")
        codeArr.append('        int partition_idx,' + "\n")
        codeArr.append('        int kp_idx,' + "\n")
        codeArr.append('        int atom_ID,' + "\n")
        codeArr.append('        tapa::istream<RATEMON_FEEDBACK_DTYPE>   & ratemon_stream,' + "\n")
        codeArr.append('        tapa::istream<PACKED_HASH_DTYPE>        & in_stream0,' + "\n")
        codeArr.append('        tapa::istream<PACKED_HASH_DTYPE>        & in_stream1,' + "\n")
        codeArr.append('        tapa::ostream<PACKED_HASH_DTYPE>        & out_stream' + "\n")
        codeArr.append('){' + "\n")
        codeArr.append('    typedef struct {' + "\n")
        codeArr.append('        ap_uint<1>          valid;' + "\n")
        codeArr.append('        PACKED_HASH_DTYPE   value;' + "\n")
        codeArr.append('    } XBAR_DTYPE;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    XBAR_DTYPE xbar[2];' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=xbar dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    RATEMON_FEEDBACK_DTYPE  feedback;' + "\n")
        
        for s in range(0, self.config.num_stm):
            codeArr.append('    INPUT_IDX_DTYPE         min_output_idx_s{s} = 0;'.format(s=s) + "\n")

        codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    bool    print_xbar = 0;' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('    ' + "\n")
        codeArr.append('    /* Initialize for SW_EMU... but will this guaranteed work for HW builds?' + "\n")
        codeArr.append('     * It might not be needed for HW builds because each xbar entry should just' + "\n")
        codeArr.append('     * be invalidated anyways, after writing.' + "\n")
        codeArr.append('     */' + "\n")
        codeArr.append('    INIT_LOOP:' + "\n")
        codeArr.append('    for (int i = 0; i < 2; ++i) {' + "\n")
        codeArr.append('        xbar[i].valid = 0;' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    MAIN_LOOP:' + "\n")
        codeArr.append('    while (1) {' + "\n")
        codeArr.append('    #pragma HLS PIPELINE II=1' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        RATEMON_LOGIC:' + "\n")
        codeArr.append('        if (!ratemon_stream.empty()) {' + "\n")
        codeArr.append('            feedback = ratemon_stream.read();' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('            //if (partition_idx == 0 && atom_ID == \'a\')' + "\n")
        codeArr.append('            //{' + "\n")
        codeArr.append('            //    printf("ARBITER ATOM [%d][%d][%c] - feedback came in. %d, %d, %d, %d.\\n",' + "\n")
        codeArr.append('            //            arb_idx, partition_idx, atom_ID,' + "\n")
        codeArr.append('            //            feedback.strm0_out_idx.to_int(),' + "\n")
        codeArr.append('            //            feedback.strm1_out_idx.to_int(),' + "\n")
        codeArr.append('            //            feedback.strm2_out_idx.to_int(),' + "\n")
        codeArr.append('            //            feedback.strm3_out_idx.to_int()' + "\n")
        codeArr.append('            //    );' + "\n")
        codeArr.append('            //}' + "\n")
        codeArr.append('            #endif' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('    // Manually unroll the min_output_idx logic, to reduce latency within the atoms.' + "\n")
        codeArr.append('    // With only one variable this takes one more cycle.' + "\n")
        for s in range(0, self.config.num_stm):
            codeArr.append('            min_output_idx_s{s} = feedback.strm{s}_out_idx;'.format(s=s) + "\n")


        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        RD_LOGIC:' + "\n")
        codeArr.append('        if (xbar[0].valid == 1) {' + "\n")
        codeArr.append('            // Dont overwrite it' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (!in_stream0.empty()) {' + "\n")
        codeArr.append('            PACKED_HASH_DTYPE   packed_val = in_stream0.read();' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            xbar[0].value = packed_val;' + "\n")
        codeArr.append('            xbar[0].valid = 1;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('            printf("ARBITER ATOM [%d][%d][%c] kp%d - read from hash/part/strm (%d,%d,0)\\n",' + "\n")
        codeArr.append('                    arb_idx, partition_idx, atom_ID,' + "\n")
        codeArr.append('                    kp_idx,' + "\n")
        codeArr.append('                    arb_idx, partition_idx' + "\n")
        codeArr.append('            );' + "\n")
        codeArr.append('            print_xbar = 1;' + "\n")
        codeArr.append('            #endif' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        if (xbar[1].valid == 1) {' + "\n")
        codeArr.append('            // Dont overwrite it' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (!in_stream1.empty()) {' + "\n")
        codeArr.append('            PACKED_HASH_DTYPE   packed_val = in_stream1.read();' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            xbar[1].value = packed_val;' + "\n")
        codeArr.append('            xbar[1].valid = 1;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('            printf("ARBITER ATOM [%d][%d][%c] kp%d - read from hash/part/strm (%d,%d,1)\\n",' + "\n")
        codeArr.append('                    arb_idx, partition_idx, atom_ID,' + "\n")
        codeArr.append('                    kp_idx,' + "\n")
        codeArr.append('                    arb_idx, partition_idx' + "\n")
        codeArr.append('            );' + "\n")
        codeArr.append('            print_xbar = 1;' + "\n")
        codeArr.append('            #endif' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('        if (print_xbar){' + "\n")
        codeArr.append('            for (int i = 0; i < 2; ++i)' + "\n")
        codeArr.append('            {' + "\n")
        codeArr.append('                printf("ARBITER ATOM [%d][%d][%c] kp%d - xbar[%d]: valid=%d, input_idx=%d, strm_idx=%d, bv_idx=%d\\n",' + "\n")
        codeArr.append('                        arb_idx, partition_idx, atom_ID,' + "\n")
        codeArr.append('                        kp_idx,' + "\n")
        codeArr.append('                        i,' + "\n")
        codeArr.append('                        xbar[i].valid.to_int(),' + "\n")
        codeArr.append('                        xbar[i].value.md.iidx.to_int(),' + "\n")
        codeArr.append('                        xbar[i].value.md.sidx.to_int(),' + "\n")
        codeArr.append('                        xbar[i].value.hash.to_int()' + "\n")
        codeArr.append('                );' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('            printf("ARBITER ATOM [%d][%d][%c] kp%d - min_output_idx = %d\\n",' + "\n")
        codeArr.append('                    arb_idx, partition_idx, atom_ID,' + "\n")
        codeArr.append('                    kp_idx,' + "\n")
        codeArr.append('                    min_output_idx.to_int()' + "\n")
        codeArr.append('            );' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        WR_LOGIC:' + "\n")
        codeArr.append('        #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('        int     print_xbar_idx = -1;' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('        int     valid_idxes = 0;' + "\n")


        for s in range(0, self.config.num_stm):
            codeArr.append('        int allowed_idx_s{s} = min_output_idx_s{s} + (SHUFFLEBUF_SZ);'.format(s=s) + "\n")

        codeArr.append('        if (xbar[0].valid &&' + "\n")
        for s in range(0, self.config.num_stm):
            AND = "" if (s == self.config.num_stm-1) else "&&"
            codeArr.append('            xbar[0].value.md.iidx <= allowed_idx_s{s} {AND}'.format(s=s, AND=AND) + "\n")
        codeArr.append('        ) { valid_idxes += 1; }' + "\n")

        codeArr.append('        if (xbar[1].valid &&' + "\n")
        for s in range(0, self.config.num_stm):
            AND = "" if (s == self.config.num_stm-1) else "&&"
            codeArr.append('            xbar[1].value.md.iidx <= allowed_idx_s{s} {AND}'.format(s=s, AND=AND) + "\n")
        codeArr.append('        ) { valid_idxes += 2; }' + "\n")

        codeArr.append('        #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('        crash!' + "\n")
        codeArr.append('        #endif' + "\n")


        codeArr.append('' + "\n")
        codeArr.append('        if (valid_idxes == 3) {' + "\n")
        codeArr.append('            if (xbar[1].value.md.iidx <= xbar[0].value.md.iidx) {' + "\n")
        codeArr.append('                if (out_stream.try_write(xbar[1].value)) {' + "\n")
        codeArr.append('                    xbar[1].valid = 0;' + "\n")
        codeArr.append('                    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                    print_xbar_idx = 1;' + "\n")
        codeArr.append('                    #endif' + "\n")
        codeArr.append('                }' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('            else {' + "\n")
        codeArr.append('                if (out_stream.try_write(xbar[0].value)) {' + "\n")
        codeArr.append('                    xbar[0].valid = 0;' + "\n")
        codeArr.append('                    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                    print_xbar_idx = 0;' + "\n")
        codeArr.append('                    #endif' + "\n")
        codeArr.append('                }' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (valid_idxes == 2) {' + "\n")
        codeArr.append('            if (out_stream.try_write(xbar[1].value)) {' + "\n")
        codeArr.append('                xbar[1].valid = 0;' + "\n")
        codeArr.append('                #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                print_xbar_idx = 1;' + "\n")
        codeArr.append('                #endif' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (valid_idxes == 1) {' + "\n")
        codeArr.append('            if (out_stream.try_write(xbar[0].value)) {' + "\n")
        codeArr.append('                xbar[0].valid = 0;' + "\n")
        codeArr.append('                #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                print_xbar_idx = 0;' + "\n")
        codeArr.append('                #endif' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('        if (print_xbar_idx != -1) {' + "\n")
        codeArr.append('            printf("ARBITER ATOM [%d][%d][%c] kp%d - WROTE from xbar %d. hash/part/strm = (%d,%d,%d), input_idx=%d, allowed_idx=%d\\n",' + "\n")
        codeArr.append('                    arb_idx, partition_idx, atom_ID,' + "\n")
        codeArr.append('                    kp_idx,' + "\n")
        codeArr.append('                    print_xbar_idx,' + "\n")
        codeArr.append('                    arb_idx,' + "\n")
        codeArr.append('                    partition_idx,' + "\n")
        codeArr.append('                    xbar[1].value.md.sidx.to_int(),' + "\n")
        codeArr.append('                    xbar[1].value.md.iidx.to_int(),' + "\n")
        codeArr.append('                    allowed_idx' + "\n")
        codeArr.append('            );' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append("\n\n\n")

        return codeArr









    def generate_hier_arb_ratemon(self):
        FAST_HLS_MODE = 1
        codeArr = []


        codeArr.append('void bloom_arbiter_ratemonitor(' + "\n")
        codeArr.append('    int arb_idx' + "\n")
        codeArr.append('    ,int kp_idx' + "\n")
        codeArr.append('    ,char ratemon_ID' + "\n")
        codeArr.append('    ,tapa::istreams<PACKED_HASH_DTYPE, BV_NUM_PARTITIONS>       &arb_stream_in' + "\n")
        codeArr.append('    ,tapa::ostreams<PACKED_HASH_DTYPE, BV_NUM_PARTITIONS>       &arb_stream_out' + "\n")
        codeArr.append('' + "\n")

        for i in range(0, self.config.num_partitions):
            codeArr.append('    ,tapa::ostreams<RATEMON_FEEDBACK_DTYPE, NUM_ARBITER_ATOMS>  &fdbk_stream_{}'.format(i) + "\n")
        codeArr.append('    #if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
        codeArr.append('    crash!' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    ,tapa::ostream<PERFCTR_DTYPE>                               &perfctr_out' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('){' + "\n")
        codeArr.append('    int WRITE_STOP_COUNT = 0;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    /* Depending on which level this ratemon is in, ' + "\n")
        codeArr.append('     * it expects a different number of writes.' + "\n")
        codeArr.append('     */' + "\n")
        codeArr.append('    WRITE_STOP_COUNT = NUM_STM * KEYPAIRS_PER_STM;' + "\n")
        codeArr.append('    int writes_per_partition[BV_NUM_PARTITIONS] = {};' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    BIT_DTYPE       did_read;' + "\n")
        codeArr.append('    BIT_DTYPE       did_write;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    PERFCTR_DTYPE   stall_cycles = 0;' + "\n")
        codeArr.append('    PERFCTR_DTYPE   readonly_cycles = 0;' + "\n")
        codeArr.append('    PERFCTR_DTYPE   writeonly_cycles = 0;' + "\n")
        codeArr.append('    PERFCTR_DTYPE   readwrite_cycles = 0;' + "\n")
        codeArr.append('    PERFCTR_DTYPE   total_cycles = 0;' + "\n")
        codeArr.append('    #else' + "\n")
        codeArr.append('    int             CRASH_COMPILATION_IF_MISTAKE;' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    typedef struct {' + "\n")
        codeArr.append('        BIT_DTYPE           valid;' + "\n")
        codeArr.append('        PACKED_HASH_DTYPE   value;' + "\n")
        codeArr.append('    } XBAR_DTYPE;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    typedef enum {' + "\n")
        codeArr.append('        WR_FEEDBACK,' + "\n")
        codeArr.append('        WR_OUTPUT' + "\n")
        codeArr.append('    } RATEMON_MODE;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    XBAR_DTYPE              xbar[BV_NUM_PARTITIONS];' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=xbar dim=0 complete' + "\n")
        codeArr.append('    INPUT_IDX_DTYPE         min_output_idx[NUM_STM];' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=min_output_idx dim=0 complete' + "\n")
        codeArr.append('    BIT_DTYPE               idx_tracker[NUM_STM][SHUFFLEBUF_SZ];' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=idx_tracker dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    INIT_LOOP:' + "\n")
        codeArr.append('    for (int i = 0; i < BV_NUM_PARTITIONS; ++i) {' + "\n")
        codeArr.append('        xbar[i].valid = 0;' + "\n")
        codeArr.append('        writes_per_partition[i] = 0;' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    INIT_LOOP_2:' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_STM; ++i) {' + "\n")
        codeArr.append('        min_output_idx[i] = 0;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        for (int j = 0; j < SHUFFLEBUF_SZ; ++j) {' + "\n")
        codeArr.append('            idx_tracker[i][j] = 0;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    MAIN_LOOP:' + "\n")
        codeArr.append('    while (' + "\n")

        for p in range(0, self.config.num_partitions):
            if (p == self.config.num_partitions-1):
                maybe_plus = ""
            else:
                maybe_plus = "+"
            codeArr.append('            writes_per_partition[{p}] {maybe_plus}'.format(p=p, maybe_plus=maybe_plus) + "\n")

        codeArr.append('                                < WRITE_STOP_COUNT)' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('    #pragma HLS PIPELINE II=1' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #if BV_NUM_PARTITIONS != ({})       // BECAUSE OF THE LOOP BOUND ^'.format(self.config.num_partitions) + "\n")
        codeArr.append('        crash(crash' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        did_read = 0;' + "\n")
        codeArr.append('        did_write = 0;' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        RATEMON_FEEDBACK_DTYPE  feedback;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        RD_INPUTS:' + "\n")
        codeArr.append('        for (int partition_idx = 0; partition_idx < BV_NUM_PARTITIONS; ++partition_idx) {' + "\n")
        codeArr.append('            INPUT_IDX_DTYPE     cur_input_idx;' + "\n")
        codeArr.append('            STRM_IDX_DTYPE      cur_strm_idx;' + "\n")
        codeArr.append('            METADATA_DTYPE      cur_metadata;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            if (xbar[partition_idx].valid == 0 &&' + "\n")
        codeArr.append('                !arb_stream_in[partition_idx].empty()' + "\n")
        codeArr.append('            ){' + "\n")
        codeArr.append('                xbar[partition_idx].valid = 1;' + "\n")
        codeArr.append('                xbar[partition_idx].value = arb_stream_in[partition_idx].read();' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                printf("ARBITER RATEMON %d %c kp%d - Read from     h/p/s=(%d,%d,%d), input_idx=%d\\n",' + "\n")
        codeArr.append('                        arb_idx,' + "\n")
        codeArr.append('                        ratemon_ID,' + "\n")
        codeArr.append('                        kp_idx,' + "\n")
        codeArr.append('                        arb_idx,' + "\n")
        codeArr.append('                        partition_idx,' + "\n")
        codeArr.append('                        xbar[partition_idx].value.md.sidx.to_int(),' + "\n")
        codeArr.append('                        xbar[partition_idx].value.md.iidx.to_int()' + "\n")
        codeArr.append('                );' + "\n")
        codeArr.append('                #endif' + "\n")
        codeArr.append('                #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('                did_read = 1;' + "\n")
        codeArr.append('                #endif' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")


        if (FAST_HLS_MODE):
            codeArr.append('        ///////////////////////' + "\n")
            codeArr.append('        // WR_OUTPUTS:' + "\n")
            codeArr.append('        ///////////////////////' + "\n")
            codeArr.append('' + "\n")

            ### THIS VERSION OF THE CODE achieves worse frequency.
            if (self.config.vivado_year >= 2022):
                print(" {}: using FAST HLS Mode for vivado version {}, which might lead to poor frequency?".format(__name__, self.config.vivado_year))
                codeArr.append('        #define RATEMON_WR_OUTPUT_FOR_PART(PART)    \\' + "\n")
                codeArr.append('            for (int sidx = 0; sidx < NUM_STM; ++sidx) {    \\' + "\n")
                codeArr.append('                int offset = (xbar[PART].value.md.iidx) % SHUFFLEBUF_SZ;    \\' + "\n")
                codeArr.append('                if (xbar[PART].valid && \\' + "\n")
                codeArr.append('                    xbar[PART].value.md.sidx == sidx && \\' + "\n")
                codeArr.append('                    !arb_stream_out[PART].full())   \\' + "\n")
                codeArr.append('                {   \\' + "\n")
                codeArr.append('                    xbar[PART].valid = 0;   \\' + "\n")
                codeArr.append('                    arb_stream_out[PART].write(xbar[PART].value);   \\' + "\n")
                codeArr.append('                    idx_tracker[sidx][offset] = 1;  \\' + "\n")
                codeArr.append('                    writes_per_partition[PART]++;   \\' + "\n")
                codeArr.append('                    break;  \\' + "\n")
                codeArr.append('                }   \\' + "\n")
                codeArr.append('            }' + "\n")
                codeArr.append('' + "\n")
                codeArr.append('' + "\n")

            ### THIS VERSION OF THE CODE DOES NOT ACHIEVE II=1 on Vitis 2022 and later.
            else:
                print(" {}: using FAST HLS Mode for vivado version {}, which should be good".format(__name__, self.config.vivado_year))
                codeArr.append('        #define RATEMON_WR_OUTPUT_FOR_PART_STM(PART, STM)   \\' + "\n")
                codeArr.append('            if (xbar[PART].valid &&     \\' + "\n")
                codeArr.append('                xbar[PART].value.md.sidx == STM &&  \\' + "\n")
                codeArr.append('                !arb_stream_out[PART].full()    \\' + "\n")
                codeArr.append('            )   \\' + "\n")
                codeArr.append('            {   \\' + "\n")
                codeArr.append('                int offset = (xbar[PART].value.md.iidx) % SHUFFLEBUF_SZ;    \\' + "\n")
                codeArr.append('                xbar[PART].valid = 0;   \\' + "\n")
                codeArr.append('                arb_stream_out[PART].write(xbar[PART].value);   \\' + "\n")
                codeArr.append('                idx_tracker[ STM ][offset] = 1;    \\' + "\n")
                codeArr.append('                writes_per_partition[PART]++;   \\' + "\n")
                codeArr.append('            }' + "\n")
                codeArr.append('' + "\n")

                codeArr.append('        #define RATEMON_WR_OUTPUT_FOR_PART(PART)    \\' + "\n")
                for s in range(0, self.config.num_stm):
                    codeArr.append('            RATEMON_WR_OUTPUT_FOR_PART_STM(PART, {s}) \\'.format(s=s) + "\n")
                ### codeArr.append('            RATEMON_WR_OUTPUT_FOR_PART_STM(PART, 0) \\' + "\n")
                ### for s in range(1, self.config.num_stm):
                ###     codeArr.append('            else RATEMON_WR_OUTPUT_FOR_PART_STM(PART, {s}) \\'.format(s=s) + "\n")
                codeArr.append('        ' + "\n")

            for p in range(0, self.config.num_partitions):
                codeArr.append('        RATEMON_WR_OUTPUT_FOR_PART({p})'.format(p=p) + "\n")

            codeArr.append('            #if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
            codeArr.append('            crash!' + "\n")
            codeArr.append('            #endif' + "\n")



            codeArr.append('' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        ///////////////////////' + "\n")
            codeArr.append('        // UPDATE_IDCES:' + "\n")
            codeArr.append('        ///////////////////////' + "\n")
            codeArr.append('        #define RATEMON_UPDATE_IDX_FOR_STM(STM)     \\' + "\n")
            codeArr.append('            int shuf_idx##STM = (min_output_idx[STM] + 1) % SHUFFLEBUF_SZ;   \\' + "\n")
            codeArr.append('            if (idx_tracker[STM][shuf_idx##STM] == 1) {  \\' + "\n")
            codeArr.append('                min_output_idx[STM] += 1;   \\' + "\n")
            codeArr.append('                idx_tracker[STM][shuf_idx##STM] = 0;     \\' + "\n")
            codeArr.append('            }   \\' + "\n")
            codeArr.append('                //#ifdef __DO_DEBUG_PRINTS__    \\' + "\n")
            codeArr.append('                //printf("ARBITER RATEMON %d %c kp%d - Updating min_output_idx[%d]=%d\\n",   \\' + "\n")
            codeArr.append('                //        arb_idx,  \\' + "\n")
            codeArr.append('                //        ratemon_ID,   \\' + "\n")
            codeArr.append('                //        kp_idx,   \\' + "\n")
            codeArr.append('                //        STM,  \\' + "\n")
            codeArr.append('                //        min_output_idx[STM].to_int()  \\' + "\n")
            codeArr.append('                //);    \\' + "\n")
            codeArr.append('                //#endif    \\' + "\n")
            codeArr.append('' + "\n")

            for s in range(0, self.config.num_stm):
                codeArr.append('        RATEMON_UPDATE_IDX_FOR_STM({s})'.format(s=s) + "\n")

        else:
            print(" {}: using SLOW HLS Mode, which might lead to very long synthesis times".format(__name__))
            codeArr.append('        WR_OUTPUTS:' + "\n")
            codeArr.append('        for (int i = 0; i < BV_NUM_PARTITIONS; ++i) {' + "\n")
            codeArr.append('            if (xbar[i].valid) ' + "\n")
            codeArr.append('            {' + "\n")
            codeArr.append('                if ( arb_stream_out[i].try_write(xbar[i].value) ) {' + "\n")
            codeArr.append('                    int offset = (xbar[i].value.md.iidx) % SHUFFLEBUF_SZ;' + "\n")
            codeArr.append('                    xbar[i].valid = 0;' + "\n")
            codeArr.append('                    idx_tracker[ xbar[i].value.md.sidx ][offset] = 1;' + "\n")
            codeArr.append('                    writes_per_partition[i]++;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('                    #if ENABLE_PERF_CTRS' + "\n")
            codeArr.append('                    did_write = 1;' + "\n")
            codeArr.append('                    #endif' + "\n")
            codeArr.append('                }' + "\n")
            codeArr.append('            }' + "\n")
            codeArr.append('        }' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('        UPDATE_IDCES:' + "\n")
            codeArr.append('        for (int strm_idx = 0; strm_idx < NUM_STM; ++strm_idx) {' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('            /* TODO: I think if we mod by the nearest power-of-two ABOVE Shufflebuf_sz,' + "\n")
            codeArr.append('             * then SHUFFLEBUF_SZ doesnt have to be a power of 2. But,' + "\n")
            codeArr.append('             * the mod by SHUFFLEBUF_SZ will decrease our II if its not a power of 2.' + "\n")
            codeArr.append('             */' + "\n")
            codeArr.append('            for (int shuf_idx = (min_output_idx[strm_idx] + 1) % SHUFFLEBUF_SZ, count=0;' + "\n")
            codeArr.append('                        count < (SHUFFLEBUF_SZ);' + "\n")
            codeArr.append('                        shuf_idx = (shuf_idx+1)%SHUFFLEBUF_SZ, ++count' + "\n")
            codeArr.append('            ) {' + "\n")
            codeArr.append('                //#ifdef __DO_DEBUG_PRINTS__' + "\n")
            codeArr.append('                //if (count == 0)' + "\n")
            codeArr.append('                //{' + "\n")
            codeArr.append('                //    printf("ARBITER RATEMON %d %c kp%d - strm_idx = %d, shuf_idx = %d\\n",' + "\n")
            codeArr.append('                //            arb_idx,' + "\n")
            codeArr.append('                //            ratemon_ID,' + "\n")
            codeArr.append('                //            kp_idx,' + "\n")
            codeArr.append('                //            strm_idx,' + "\n")
            codeArr.append('                //            shuf_idx' + "\n")
            codeArr.append('                //    );' + "\n")
            codeArr.append('                //}' + "\n")
            codeArr.append('                //#endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('                if (idx_tracker[strm_idx][shuf_idx] == 1) {' + "\n")
            codeArr.append('                    min_output_idx[strm_idx] += 1;' + "\n")
            codeArr.append('                    idx_tracker[strm_idx][shuf_idx] = 0;' + "\n")
            codeArr.append('                    #ifdef __DO_DEBUG_PRINTS__' + "\n")
            codeArr.append('                    printf("ARBITER RATEMON %d %c kp%d - Updating min_output_idx[%d]=%d\\n",' + "\n")
            codeArr.append('                            arb_idx,' + "\n")
            codeArr.append('                            ratemon_ID,' + "\n")
            codeArr.append('                            kp_idx,' + "\n")
            codeArr.append('                            strm_idx,' + "\n")
            codeArr.append('                            min_output_idx[strm_idx].to_int()' + "\n")
            codeArr.append('                    );' + "\n")
            codeArr.append('                    #endif' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('                    break;' + "\n")
            codeArr.append('' + "\n")
            codeArr.append('                }' + "\n")
            codeArr.append('                else {' + "\n")
            codeArr.append('                    break;' + "\n")
            codeArr.append('                }' + "\n")
            codeArr.append('            }' + "\n")
            codeArr.append('        }' + "\n")




        codeArr.append('' + "\n")
        codeArr.append('        WRITE_FEEDBACK:' + "\n")
        codeArr.append('        /* For the ratemonitors NOT in the last level, we dont ' + "\n")
        codeArr.append('         * have the data from all 4 streams. So dont attempt to ratelimit' + "\n")
        codeArr.append('         * based on data we cant get.' + "\n")
        codeArr.append('         */' + "\n")

        for i in range(0, self.config.num_stm):
            codeArr.append('        feedback.strm{i}_out_idx = min_output_idx[{i}];'.format(i=i) + "\n")
        codeArr.append('        #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('        crash!' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('        for (int i = 0; i < NUM_ARBITER_ATOMS; ++i) {' + "\n")

        for p in range(0, self.config.num_partitions):
            codeArr.append('            fdbk_stream_{p}[i].try_write(feedback);'.format(p=p) + "\n")

        codeArr.append('            #if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
        codeArr.append('            crash!' + "\n")
        codeArr.append('            #endif' + "\n")
        codeArr.append('        }' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        UPDATE_PERF_CTRS:' + "\n")
        codeArr.append('        total_cycles++;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        if (did_write && !did_read){' + "\n")
        codeArr.append('            writeonly_cycles++;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (did_read && !did_write){' + "\n")
        codeArr.append('            readonly_cycles++;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (!did_read && !did_write){' + "\n")
        codeArr.append('            stall_cycles++;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (did_read && did_write){' + "\n")
        codeArr.append('            readwrite_cycles++;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    WRITE_PERF_CTRS:' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_PERFCTR_OUTPUTS; ++i) {' + "\n")
        codeArr.append('    #pragma HLS PIPELINE II=1' + "\n")
        codeArr.append('        if (i == 0){' + "\n")
        codeArr.append('            perfctr_out.write(stall_cycles);' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (i == 1){' + "\n")
        codeArr.append('            perfctr_out.write(readonly_cycles);' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (i == 2){' + "\n")
        codeArr.append('            perfctr_out.write(writeonly_cycles);' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (i == 3){' + "\n")
        codeArr.append('            perfctr_out.write(readwrite_cycles);' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (i == 4){' + "\n")
        codeArr.append('            perfctr_out.write(total_cycles);' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else{' + "\n")
        codeArr.append('            perfctr_out.write(55555);' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    printf("ARBITER RATEMON %d %c kp%d - stall_cycles       = %25lu\\n", ' + "\n")
        codeArr.append('        arb_idx, ratemon_ID, kp_idx, stall_cycles' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    printf("ARBITER RATEMON %d %c kp%d - readonly_cycles    = %25lu\\n", ' + "\n")
        codeArr.append('        arb_idx, ratemon_ID, kp_idx, readonly_cycles' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    printf("ARBITER RATEMON %d %c kp%d - writeonly_cycles   = %25lu\\n", ' + "\n")
        codeArr.append('        arb_idx, ratemon_ID, kp_idx, writeonly_cycles' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    printf("ARBITER RATEMON %d %c kp%d - readwrite_cycles   = %25lu\\n", ' + "\n")
        codeArr.append('        arb_idx, ratemon_ID, kp_idx, readwrite_cycles' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    printf("ARBITER RATEMON %d %c kp%d - total_cycles       = %25lu\\n", ' + "\n")
        codeArr.append('        arb_idx, ratemon_ID, kp_idx, total_cycles' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #endif  // ENABLE_PERF_CTRS' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    printf("ARBITER RATEMON %d %c - DONE NOW!\\n", arb_idx, ratemon_ID);' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append("\n\n\n")



        return codeArr




    def generate_hier_arb_singlepartition(self):
        codeArr = []

        codeArr.append('void bloom_arbiter_tree_singlepartition(' + "\n")
        codeArr.append('    int arb_idx' + "\n")
        codeArr.append('    ,int partition_idx' + "\n")
        codeArr.append('    ,int kp_idx' + "\n")
        codeArr.append('' + "\n")

        for i in range(0, self.config.num_stm):
            codeArr.append('    ,tapa::istream<PACKED_HASH_DTYPE>           &arb_stm{}'.format(i) + "\n")
        codeArr.append('    #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('    crash!' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    ,tapa::istreams<RATEMON_FEEDBACK_DTYPE, NUM_ARBITER_ATOMS>  &ratemon_feedback' + "\n")
        codeArr.append('    ,tapa::ostream<PACKED_HASH_DTYPE>                           &arbtree_out' + "\n")
        codeArr.append(') {' + "\n")

        #if self.config.num_stm not in [2, 4, 8, 16, 32, 64]:
        #    raise ValueError("Need to add support for non-pow2 streams to the hierarb generator.")
        #num_stages = 0
        #divider = 2
        #while ( float(self.config.num_stm) / float(divider) > 1):
        #    codeArr.append('    tapa::streams<PACKED_HASH_DTYPE, NUM_STM/{div}>     arb_stage{i}_outputs;'.format(div=divider, i=num_stages) + "\n")
        #    num_stages += 1
        #    divider *= 2


        """
         Here we define a "stage" as the input streams, and then the atoms.
         So the first index has NUM_STM streams followed by some number of atoms.
        """
        num_stms_cur_stage = self.config.num_stm
        atoms_per_stage = []

        # The number of FIFOS in each stage, INCLUDING The "remainder" FIFOS.
        logical_stms_per_stage = []

        # The number of FIFOS we INSTANTIATE. This doesn't include the "remainder" FIFOS,
        # because we can directly connect to the remainders from whichever stage we need.
        stms_to_define = [num_stms_cur_stage]

        while (num_stms_cur_stage > 1):
            logical_stms_per_stage.append(num_stms_cur_stage)
            num_stms_remaining = num_stms_cur_stage
            num_atoms_cur_stage = 0

            while (num_stms_remaining >= 2):
                num_stms_remaining -= 2
                num_atoms_cur_stage += 1

            num_stms_cur_stage = num_atoms_cur_stage + num_stms_remaining
            atoms_per_stage.append(num_atoms_cur_stage)
            stms_to_define.append(num_atoms_cur_stage)

        logical_stms_per_stage.append(1)

        if (sum(atoms_per_stage) != self.config.num_arb_atoms):
            raise ValueError("ERROR IN HIERARB CALCULATION: the number of atoms doesn't seem to be correct.")
        if (len(atoms_per_stage) != len(logical_stms_per_stage)-1):
            raise ValueError("ERROR IN HIERARB CALCULATION: something wrong in the num_stages calculation.")
            


        for stage_idx in range(1, len(stms_to_define)-1):
            num_stms  = stms_to_define[stage_idx]
            codeArr.append('    tapa::streams<PACKED_HASH_DTYPE, {STMS}>     arb_stage{i}_outputs;'.format(STMS=num_stms, i=stage_idx) + "\n")

        codeArr.append('    #if NUM_ARBITER_ATOMS != {}'.format(self.config.num_arb_atoms) + "\n")
        codeArr.append('    crash!' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    tapa::task()' + "\n")
        
        total_atom_idx = 0
        remainder_stage_tracker = 0     # Keep track of which stage the "remainder" stream should connect from.
        for stage_idx in range(0, len(atoms_per_stage)):
            using_remainder = 0
            num_input_stms = logical_stms_per_stage[stage_idx]
            num_output_stms = logical_stms_per_stage[stage_idx+1]
            num_atoms = atoms_per_stage[stage_idx]

            if (num_input_stms%2 == 0):
                using_remainder = 1

            instm_idx_tracker = 0
            outstm_idx_tracker = 0
            for atom_idx in range(0, num_atoms):
                ## Calculate which stream(s), from which stage, our atom connects to.
                left_stm_idx = instm_idx_tracker
                right_stm_idx = instm_idx_tracker + 1
                instm_idx_tracker += 2
                out_stm_idx = outstm_idx_tracker
                outstm_idx_tracker += 1
                
                left_stage = stage_idx
                right_stage = stage_idx
                out_stage = stage_idx+1

                if (atom_idx == num_atoms - 1 and using_remainder):
                    right_stage = remainder_stage_tracker
                    right_stm_idx = logical_stms_per_stage[right_stage]-1
                    remainder_stage_tracker = stage_idx+1

                if (left_stage == 0):
                    left_stm_name = "arb_stm{i}".format(i=left_stm_idx)
                else:
                    left_stm_name = "arb_stage{stage}_outputs[{i}]".format(stage = left_stage, i = left_stm_idx)

                if (right_stage == 0):
                    right_stm_name = "arb_stm{i}".format(i=right_stm_idx)
                else:
                    right_stm_name = "arb_stage{stage}_outputs[{i}]".format(stage = right_stage, i = right_stm_idx)

                if (out_stage == len(atoms_per_stage)):
                    out_stm_name = "arbtree_out"
                else:
                    out_stm_name = "arb_stage{stage}_outputs[{i}]".format(stage = out_stage, i = out_stm_idx)

                codeArr.append('        .invoke<tapa::detach>(' + "\n")
                codeArr.append('                bloom_hier_arbiter_atom' + "\n")
                codeArr.append('                ,arb_idx' + "\n")
                codeArr.append('                ,partition_idx' + "\n")
                codeArr.append('                ,kp_idx' + "\n")
                codeArr.append('                ,\'{char}\''.format(char = chr(ord('a') + total_atom_idx) ) + "\n")
                codeArr.append('                ,ratemon_feedback[{a}]'.format(a=total_atom_idx) + "\n")
                codeArr.append('                ,{}'.format(left_stm_name) + "\n")
                codeArr.append('                ,{}'.format(right_stm_name) + "\n")
                codeArr.append('                ,{}'.format(out_stm_name) + "\n")
                codeArr.append('        )' + "\n")
                total_atom_idx += 1


        #if self.config.num_stm not in [2, 4, 8, 16, 32, 64]:
        #    raise ValueError("Need to add support for non-pow2 streams to the hierarb generator.")
        #total_atom_idx = 0
        #for stage_idx in range(0, num_stages+1):
        #    stage_width = pow(2, num_stages - stage_idx)
        #    for atom_idx in range(0, stage_width):
        #        codeArr.append('        .invoke<tapa::detach>(' + "\n")
        #        codeArr.append('                bloom_hier_arbiter_atom' + "\n")
        #        codeArr.append('                ,arb_idx' + "\n")
        #        codeArr.append('                ,partition_idx' + "\n")
        #        codeArr.append('                ,kp_idx' + "\n")
        #        codeArr.append('                ,\'{char}\''.format(char = chr(ord('a') + total_atom_idx) ) + "\n")
        #        codeArr.append('                ,ratemon_feedback[{a}]'.format(a=total_atom_idx) + "\n")
        #        if (stage_idx == 0):
        #            codeArr.append('                ,arb_stm{a}'.format(a = atom_idx*2 + 0) + "\n")
        #            codeArr.append('                ,arb_stm{a}'.format(a = atom_idx*2 + 1) + "\n")
        #        else:
        #            codeArr.append('                ,arb_stage{s}_outputs[{a}+0]'.format(s = stage_idx-1, a = atom_idx*2) + "\n")
        #            codeArr.append('                ,arb_stage{s}_outputs[{a}+1]'.format(s = stage_idx-1, a = atom_idx*2) + "\n")

        #        if (stage_idx == num_stages):
        #            codeArr.append('                ,arbtree_out' + "\n")
        #        else:
        #            codeArr.append('                ,arb_stage{i}_outputs[{a}]'.format(i=stage_idx, a=atom_idx) + "\n")
        #        codeArr.append('        )' + "\n")

        #        total_atom_idx += 1

        codeArr.append('        #if NUM_ARBITER_ATOMS != {}'.format(self.config.num_arb_atoms) + "\n")
        codeArr.append('        crash!' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('    ;' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append("\n\n\n")



        return codeArr







    def generate_hier_arb_single_arbiter(self):
        codeArr = []
        
        codeArr.append('void bloom_single_arbiter(' + "\n")
        codeArr.append('        int arb_idx' + "\n")
        codeArr.append('        , int kp_idx' + "\n")
        codeArr.append('        , tapa::istreams<PACKED_HASH_DTYPE, NUM_STM*BV_NUM_PARTITIONS>  &in_arb_streams' + "\n")
        codeArr.append('        , tapa::ostreams<PACKED_HASH_DTYPE, BV_NUM_PARTITIONS>          &bv_lookup_stream' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        ,tapa::ostreams<PERFCTR_DTYPE, NUM_ARBITER_ATOMS>           &perfctr_out' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append(') {' + "\n")
        codeArr.append('    tapa::streams<PACKED_HASH_DTYPE,    BV_NUM_PARTITIONS>      arbtree_outputs;' + "\n")
        codeArr.append('' + "\n")

        for p in range(0, self.config.num_partitions):
            codeArr.append('    tapa::streams<RATEMON_FEEDBACK_DTYPE, NUM_ARBITER_ATOMS>    ratemon_fdbk_streams_p{p};'.format(p=p) + "\n")
        codeArr.append('    #if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
        codeArr.append('    crash!' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    tapa::task()' + "\n")

        for p in range(0, self.config.num_partitions):
            codeArr.append('        .invoke<tapa::detach>(' + "\n")
            codeArr.append('                bloom_arbiter_tree_singlepartition' + "\n")
            codeArr.append('                ,arb_idx' + "\n")
            codeArr.append('                ,{p}'.format(p=p) + "\n")
            codeArr.append('                ,kp_idx' + "\n")
            for s in range(0, self.config.num_stm):
                codeArr.append('                ,in_arb_streams[NUM_STM*{p} + {s}]'.format(p=p, s=s)  + "\n")
            codeArr.append('                ,ratemon_fdbk_streams_p{p}'.format(p=p) + "\n")
            codeArr.append('                ,arbtree_outputs[{p}]'.format(p=p) + "\n")
            codeArr.append('        )' + "\n")
        codeArr.append('    #if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
        codeArr.append('    crash!' + "\n")
        codeArr.append('    #endif' + "\n")


        codeArr.append('        .invoke<tapa::detach>(' + "\n")
        codeArr.append('                bloom_arbiter_ratemonitor' + "\n")
        codeArr.append('                ,arb_idx' + "\n")
        codeArr.append('                ,kp_idx' + "\n")
        codeArr.append('                ,\'a\'' + "\n")
        codeArr.append('                ,arbtree_outputs' + "\n")
        codeArr.append('                ,bv_lookup_stream' + "\n")
        for p in range(0, self.config.num_partitions):
            codeArr.append('                ,ratemon_fdbk_streams_p{p}'.format(p=p) + "\n")
        codeArr.append('        )' + "\n")
        codeArr.append('    ;' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append("\n\n\n")

        return codeArr








    def generate_hier_arb_wrapper(self):
        codeArr = []

        codeArr.append('#define ARBITER_STREAM_DECLS_KP(KP_IDX)    \\' + "\n")
        for h in range(0, self.config.num_hash):
            codeArr.append('    tapa::streams<PACKED_HASH_DTYPE, NUM_STM*BV_NUM_PARTITIONS> arb{h}_streams_kp##KP_IDX;   \\'.format(h=h) + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#if NUM_HASH != ({})'.format(self.config.num_hash) + "\n")
        codeArr.append('crash!,' + "\n")
        codeArr.append('#endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('#define ARBITER_INVOKES_FOR_KP(KP_IDX)  \\' + "\n")
        for h in range(0, self.config.num_hash):
            codeArr.append('        .invoke( bloom_arb_forwarder,   \\' + "\n")
            codeArr.append('                    {h},  \\'.format(h=h) + "\n")
            codeArr.append('                    KP_IDX, \\' + "\n")
            codeArr.append('                    hash_stream_h{h}_kp##KP_IDX,  \\'.format(h=h) + "\n")
            codeArr.append('                    arb{h}_streams_kp##KP_IDX    \\'.format(h=h) + "\n")
            codeArr.append('        )   \\' + "\n")
        codeArr.append('\\' + "\n")

        for h in range(0, self.config.num_hash):
            codeArr.append('        .invoke( bloom_single_arbiter,  \\' + "\n")
            codeArr.append('                    {h},  \\'.format(h=h) + "\n")
            codeArr.append('                    KP_IDX, \\' + "\n")
            codeArr.append('                    arb{h}_streams_kp##KP_IDX,   \\'.format(h=h) + "\n")
            codeArr.append('                    bv_lookup_stream_h{h}_kp##KP_IDX  \\'.format(h=h) + "\n")
            if (self.config.enable_perfctrs):
                codeArr.append('                    , perfctr_out_{h}*/ \\' + "\n")
            codeArr.append('        )   \\' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#if NUM_HASH != ({})'.format(self.config.num_hash) + "\n")
        codeArr.append('crash!,' + "\n")
        codeArr.append('#endif' + "\n")

        return codeArr









    def generate_hier_arb(self):
        codeArr = []
        codeArr.extend(self.generate_hier_arb_fwd())
        codeArr.extend(self.generate_hier_arb_atom())
        codeArr.extend(self.generate_hier_arb_ratemon())
        codeArr.extend(self.generate_hier_arb_singlepartition())
        codeArr.extend(self.generate_hier_arb_single_arbiter())
        codeArr.extend(self.generate_hier_arb_wrapper())

        return codeArr



















    def generate_debug_sink(self):
        codeArr = []
        codeArr.append('#if DEBUG_ARBITER_SINK' + "\n")
        codeArr.append('void DEBUG_arbiter_sink(' + "\n")
        for i in range(0, self.config.num_hash):
            if (i == 0):
                comma = ""
            else:
                comma = ","
            codeArr.append('        {c}tapa::istreams<PACKED_HASH_DTYPE, BV_NUM_PARTITIONS> & bv_lookup_stream_h{i}_kp0'.format(c=comma, i=i) + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('        tapa::istreams<PACKED_HASH_DTYPE, BV_NUM_PARTITIONS> & bv_lookup_stream_h{}_kp1'.format(i) + "\n")
        codeArr.append('        #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('        ,crash,' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('        ,tapa::istream<BV_PACKED_DTYPE>                                  & bv_load_stream_{}'.format(i) + "\n")
        codeArr.append('        #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('        ,crash,' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append(') {' + "\n")
        codeArr.append('    const int           READ_STOP_COUNT = NUM_STM * KEYPAIRS_PER_STM;' + "\n")
        codeArr.append('    int                 num_reads_per_hash_kp[NUM_HASH][2];' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=num_reads_per_hash_kp dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    BV_PACKED_DTYPE     bv_buf[NUM_HASH][BV_NUM_PARTITIONS][BV_PARTITION_LENGTH_IN_PACKED_ELEMS];' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=bv_buf dim=1 complete' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=bv_buf dim=2 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    BV_PACKED_DTYPE cur_bv_val;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifndef __SYNTHESIS__' + "\n")
        codeArr.append('    printf("CRITICAL WARNING: The ARBITER SINK IS ENABLED\\n");' + "\n")
        codeArr.append('    printf("CRITICAL WARNING: The ARBITER SINK IS ENABLED\\n");' + "\n")
        codeArr.append('    printf("CRITICAL WARNING: The ARBITER SINK IS ENABLED\\n");' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    INIT_NUM_READS:' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_HASH; ++i) {' + "\n")
        codeArr.append('    #pragma HLS UNROLL' + "\n")
        codeArr.append('        num_reads_per_hash_kp[i][0] = 0;' + "\n")
        codeArr.append('        num_reads_per_hash_kp[i][1] = 0;' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    LOAD_BV_VALUES:' + "\n")
        codeArr.append('    for (int section_idx = 0; section_idx < NUM_HASH; ++section_idx) {' + "\n")
        codeArr.append('        for (int i = 0; i < BV_SECTION_LENGTH_IN_PACKED_ELEMS; ++i) {' + "\n")
        codeArr.append('        #pragma HLS PIPELINE II=1' + "\n")
        codeArr.append('' + "\n")

        for i in range(0, self.config.num_hash):
            codeArr.append('            if (section_idx == {}) {{'.format(i) + "\n")
            codeArr.append('                cur_bv_val = bv_load_stream_{}.read();'.format(i) + "\n")
            codeArr.append('            }' + "\n")
        codeArr.append('            #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('            ,crash,' + "\n")
        codeArr.append('            #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            int partition_idx = (i%BV_SECTION_LENGTH_IN_PACKED_ELEMS) / ' + "\n")
        codeArr.append('                                BV_PARTITION_LENGTH_IN_PACKED_ELEMS;' + "\n")
        codeArr.append('            int element_idx = i%BV_PARTITION_LENGTH_IN_PACKED_ELEMS;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            bv_buf[section_idx][partition_idx][element_idx] = cur_bv_val;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    ARBITER_SINK_LOOP:' + "\n")
        codeArr.append('    while (' + "\n")
        for i in range(0, self.config.num_hash):
            if (i != self.config.num_hash-1):
                OR = "   ||"
            else:
                OR = ""
            codeArr.append('            num_reads_per_hash_kp[{i}][0] < READ_STOP_COUNT   ||'.format(i=i) + "\n")
            codeArr.append('            num_reads_per_hash_kp[{i}][1] < READ_STOP_COUNT{OR}'.format(i=i, OR=OR) + "\n")
        codeArr.append('    ){' + "\n")
        codeArr.append('    #pragma HLS PIPELINE II=1' + "\n")

        codeArr.append('        for (int partition_idx = 0; partition_idx < BV_NUM_PARTITIONS; ++partition_idx)' + "\n")
        codeArr.append('        {' + "\n")
        codeArr.append('            PACKED_HASH_DTYPE   tmp;' + "\n")

        for i in range(0, self.config.num_hash):
            codeArr.append('            if ( bv_lookup_stream_h{i}_kp0[partition_idx].try_read(tmp) ) {{'.format(i=i) + "\n")
            codeArr.append('                num_reads_per_hash_kp[{i}][0]++;'.format(i=i) + "\n")
            codeArr.append('            }' + "\n")
            codeArr.append('            if ( bv_lookup_stream_h{i}_kp1[partition_idx].try_read(tmp) ) {{'.format(i=i) + "\n")
            codeArr.append('                num_reads_per_hash_kp[{i}][1]++;'.format(i=i) + "\n")
            codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append('#endif //DEBUG_ARBITER_SINK' + "\n")
        codeArr.append("\n\n\n\n\n")

        return codeArr














    
    def generate_split_monolithic_arb_func(self):
        codeArr = []
        codeArr.append('void bloom_monoarb_per_hash(' + "\n")
        codeArr.append('        int hash_idx' + "\n")
        codeArr.append('        , int kp_idx' + "\n")
        codeArr.append('        , tapa::istreams<HASHONLY_DTYPE, NUM_STM>         & hash_stream' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        //#if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        //,tapa::ostreams<PERFCTR_DTYPE, NUM_ARBITER_ATOMS>   & perfctr_out_0' + "\n")
        codeArr.append('        //,tapa::ostreams<PERFCTR_DTYPE, NUM_ARBITER_ATOMS>   & perfctr_out_1' + "\n")
        codeArr.append('        //        #if NUM_HASH != 2' + "\n")
        codeArr.append('        //        ,crash!' + "\n")
        codeArr.append('        //        #endif' + "\n")
        codeArr.append('        //#endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        , tapa::ostreams<PACKED_HASH_DTYPE, BV_NUM_PARTITIONS>   & bv_lookup_stream' + "\n")
        codeArr.append(') {' + "\n")
        codeArr.append('    typedef struct {' + "\n")
        codeArr.append('        ap_uint<1>          valid;' + "\n")
        codeArr.append('        PACKED_HASH_DTYPE   value;' + "\n")
        codeArr.append('        uint32_t            target_partition_idx;' + "\n")
        codeArr.append('    } XBAR_DTYPE;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    const int READ_STOP_COUNT =     NUM_STM * KEYPAIRS_PER_STM;' + "\n")
        codeArr.append('    const int WRITE_STOP_COUNT =    NUM_STM * KEYPAIRS_PER_STM;' + "\n")
        codeArr.append('    int total_num_reads = 0;' + "\n")
        codeArr.append('    int total_num_writes = 0;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __SYNTHESIS__' + "\n")
        codeArr.append('    /* TAPA Known-issue: Static keyword fails CSIM because this' + "\n")
        codeArr.append('       isnt thread-safe. But when running the HW build, it will ' + "\n")
        codeArr.append('       instantiate several copies of this function. So this is OK.' + "\n")
        codeArr.append('    */' + "\n")
        codeArr.append('    static' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('    INPUT_IDX_DTYPE     reads_per_input[NUM_STM] = {{}};' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=reads_per_input dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __SYNTHESIS__' + "\n")
        codeArr.append('    /* TAPA Known-issue: Static keyword fails CSIM because this' + "\n")
        codeArr.append('       isnt thread-safe. But when running the HW build, it will ' + "\n")
        codeArr.append('       instantiate several copies of this function. So this is OK.' + "\n")
        codeArr.append('    */' + "\n")
        codeArr.append('    static' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('    XBAR_DTYPE          xbar_output[NUM_STM];' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=xbar_output dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    ' + "\n")
        codeArr.append('    // Keep a running tally of the most-recently-sent index for each hash/stream.' + "\n")
        codeArr.append('    INPUT_IDX_DTYPE     cur_output_idces[NUM_STM] = {};' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=cur_output_idces dim=0 complete' + "\n")
        codeArr.append('    INPUT_IDX_DTYPE     allowed_output_idces = {};' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=allowed_output_idces dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    BIT_DTYPE       did_read;' + "\n")
        codeArr.append('    BIT_DTYPE       did_write;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    PERFCTR_DTYPE   stall_cycles = 0;' + "\n")
        codeArr.append('    PERFCTR_DTYPE   readonly_cycles = 0;' + "\n")
        codeArr.append('    PERFCTR_DTYPE   writeonly_cycles = 0;' + "\n")
        codeArr.append('    PERFCTR_DTYPE   readwrite_cycles = 0;' + "\n")
        codeArr.append('    PERFCTR_DTYPE   total_cycles = 0;' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    /* Keep track of the slowest input-streams for each hash function.' + "\n")
        codeArr.append('     * This is for dynamic arbitration. */' + "\n")
        codeArr.append('    STRM_IDX_DTYPE      slowest_stm_idces = {};' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=slowest_stm_idces dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifndef __SYNTHESIS__' + "\n")
        codeArr.append('    printf("WARNING! WARNING! Using SPLIT monolithic (non-hier) arbiter!!!\\n");' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    /* For some reason, multiple calls to the kernel will fail' + "\n")
        codeArr.append('       SW_EMU without the explicit initialization.' + "\n")
        codeArr.append('    */' + "\n")
        codeArr.append('    INIT_READS:' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_STM; ++i)' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('        reads_per_input[i] = 0;' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    INIT_OUTPUT_IDCES:' + "\n")
        codeArr.append('    allowed_output_idces = 1;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_STM; ++i)' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('        cur_output_idces[i] = 0;' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('    ' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    INIT_XBAR:' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_STM; ++i)' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('        xbar_output[i].valid = 0;' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    INPUTS_LOOP:' + "\n")
        codeArr.append('    while (total_num_reads < READ_STOP_COUNT  ||' + "\n")
        codeArr.append('            total_num_writes < WRITE_STOP_COUNT ' + "\n")
        codeArr.append('    )' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('    #pragma HLS PIPELINE II = 1' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        did_read = 0;' + "\n")
        codeArr.append('        did_write = 0;' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        RD_STM_LOOP:' + "\n")
        codeArr.append('        for(int strm_idx = 0; strm_idx < NUM_STM; strm_idx++){' + "\n")
        codeArr.append('            ' + "\n")
        codeArr.append('            // Metadata:' + "\n")
        codeArr.append('            INPUT_IDX_DTYPE cur_input_idx = reads_per_input[strm_idx];' + "\n")
        codeArr.append('            STRM_IDX_DTYPE cur_strm_idx = strm_idx;' + "\n")
        codeArr.append('            METADATA_DTYPE cur_metadata;' + "\n")
        codeArr.append('            PACKED_HASH_DTYPE packed_hashval;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            if (xbar_output[strm_idx].valid == 1) {' + "\n")
        codeArr.append('                // Dont replace this value - its still valid.' + "\n")
        codeArr.append('                #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                //printf("KDEBUG: ARBITER_MONO kp%d h%d - (Strm #%d): xbar [stream=%d] is already valid. Not replacing.\\n",' + "\n")
        codeArr.append('                //        kp_idx,' + "\n")
        codeArr.append('                //        hash_idx,' + "\n")
        codeArr.append('                //        strm_idx,' + "\n")
        codeArr.append('                //        strm_idx,' + "\n")
        codeArr.append('                //);' + "\n")
        codeArr.append('                #endif' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('            else if ( (!hash_stream[strm_idx].empty()) ) {' + "\n")
        codeArr.append('                // Hash and partition data:' + "\n")
        codeArr.append('                HASHONLY_DTYPE  tmp_hash;' + "\n")
        codeArr.append('                ' + "\n")
        codeArr.append('                tmp_hash = hash_stream[strm_idx].read();' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('                did_read = 1;' + "\n")
        codeArr.append('                #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                HASHONLY_DTYPE  idx_inside_partition = tmp_hash % BV_PARTITION_LENGTH;' + "\n")
        codeArr.append('                int             partition_idx = (tmp_hash / BV_PARTITION_LENGTH);' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                total_num_reads++;' + "\n")
        codeArr.append('                reads_per_input[strm_idx]++;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                cur_input_idx = reads_per_input[strm_idx];' + "\n")
        codeArr.append('                cur_strm_idx = strm_idx;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                // Pack metadata' + "\n")
        codeArr.append('                cur_metadata.sidx = cur_strm_idx;' + "\n")
        codeArr.append('                cur_metadata.iidx = cur_input_idx;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                // Pack final payload' + "\n")
        codeArr.append('                packed_hashval.md = cur_metadata;' + "\n")
        codeArr.append('                packed_hashval.hash = idx_inside_partition;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                xbar_output[strm_idx].valid = 1;' + "\n")
        codeArr.append('                xbar_output[strm_idx].value = packed_hashval;' + "\n")
        codeArr.append('                xbar_output[strm_idx].target_partition_idx = partition_idx;' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('        printf("KDEBUG: ARBITER_MONO kp%d h%d - xbar[target_partition][strm_idx]\\n",' + "\n")
        codeArr.append('                kp_idx, hash_idx' + "\n")
        codeArr.append('        );' + "\n")
        codeArr.append('        for (int strm = 0; strm < NUM_STM; ++strm)' + "\n")
        codeArr.append('        {' + "\n")
        codeArr.append('            printf("KDEBUG: ARBITER_MONO kp%d h%d - xbar[%d][%d]: valid=%d, input_idx=%d\\n",' + "\n")
        codeArr.append('                    kp_idx,' + "\n")
        codeArr.append('                    hash_idx,' + "\n")
        codeArr.append('                    xbar_output[strm].target_partition_idx,' + "\n")
        codeArr.append('                    strm,' + "\n")
        codeArr.append('                    xbar_output[strm].valid.to_int(),' + "\n")
        codeArr.append('                    xbar_output[strm].value.md.iidx.to_int()' + "\n")
        codeArr.append('            );' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        printf("KDEBUG: ARBITER_MONO kp%d h%d - allowed_output_idces = %d\\n",' + "\n")
        codeArr.append('                kp_idx,' + "\n")
        codeArr.append('                hash_idx,' + "\n")
        codeArr.append('                allowed_output_idces.to_int()' + "\n")
        codeArr.append('        );' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        WR_BV_PARTITION_LOOP:' + "\n")
        codeArr.append('        for (int partition_idx = 0; ' + "\n")
        codeArr.append('                partition_idx < BV_NUM_PARTITIONS; ' + "\n")
        codeArr.append('                ++partition_idx' + "\n")
        codeArr.append('        ) {' + "\n")
        codeArr.append('            bool                found = false;' + "\n")
        codeArr.append('            uint32_t            found_strm_idx = 0;' + "\n")
        codeArr.append('            PACKED_HASH_DTYPE   packed_hashval;' + "\n")
        codeArr.append('            int                 allowed_idx = allowed_output_idces + (SHUFFLEBUF_SZ);' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            WR_STM_LOOP0:' + "\n")
        codeArr.append('            //for (int strm_idx = 0; ' + "\n")
        codeArr.append('            //        strm_idx < NUM_STM;' + "\n")
        codeArr.append('            //        strm_idx++' + "\n")
        codeArr.append('            //)' + "\n")
        codeArr.append('            // Prioritizing slowest stream. For some reason, this increases II' + "\n")
        codeArr.append('            //  when using a larger config.' + "\n")
        codeArr.append('            for (int strm_idx = (slowest_stm_idces+1)%NUM_STM, it_ctr = 0; ' + "\n")
        codeArr.append('                    it_ctr < NUM_STM;' + "\n")
        codeArr.append('                    strm_idx = (strm_idx+1)%NUM_STM, ++it_ctr' + "\n")
        codeArr.append('            )' + "\n")
        codeArr.append('            {' + "\n")
        codeArr.append('                /* Enforce a strict priority -' + "\n")
        codeArr.append('                 *  Each stream can only output indices' + "\n")
        codeArr.append('                 *  within SHUFFLE_BUFFER_SIZE of the allowed idx.' + "\n")
        codeArr.append('                 *  The allowed idx is the lowest index that HAS NOT' + "\n")
        codeArr.append('                 *  been sent by every streams, for this hash function.' + "\n")
        codeArr.append('                 */' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                printf("KDEBUG: ARBITER_MONO kp%d h%d - (hash/stream) = (%d, %d), allowed_idx = %d\\n",' + "\n")
        codeArr.append('                        kp_idx,' + "\n")
        codeArr.append('                        hash_idx,' + "\n")
        codeArr.append('                        hash_idx, strm_idx, allowed_idx' + "\n")
        codeArr.append('                );' + "\n")
        codeArr.append('                #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                if (xbar_output[strm_idx].valid == 1 &&' + "\n")
        codeArr.append('                    xbar_output[strm_idx].target_partition_idx ==' + "\n")
        codeArr.append('                        partition_idx &&' + "\n")
        codeArr.append('                    allowed_idx >= 0 &&' + "\n")
        codeArr.append('                    xbar_output[strm_idx].value.md.iidx <= allowed_idx' + "\n")
        codeArr.append('                )' + "\n")
        codeArr.append('                {' + "\n")
        codeArr.append('                    found = true;' + "\n")
        codeArr.append('                    packed_hashval = xbar_output[strm_idx].value;' + "\n")
        codeArr.append('                    found_strm_idx = strm_idx;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    #ifndef __SYNTHESIS__' + "\n")
        codeArr.append('                    if (xbar_output[strm_idx].value.md.iidx > allowed_idx){' + "\n")
        codeArr.append('                        printf("\\n\\n\\n\\n\\n\\n\\n\\n");' + "\n")
        codeArr.append('                        printf("SOMETHING IS VERY WRONG IN THE ARBITER_MONO... Crashing now.");' + "\n")
        codeArr.append('                        printf("\\n\\n\\n\\n\\n\\n\\n\\n");' + "\n")
        codeArr.append('                        exit(-1);' + "\n")
        codeArr.append('                    }' + "\n")
        codeArr.append('                    #endif' + "\n")
        codeArr.append('                }' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            if (found){' + "\n")
        codeArr.append('                BIT_DTYPE did_write = 0;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                if (bv_lookup_stream[partition_idx].try_write(packed_hashval)) {' + "\n")
        codeArr.append('                    did_write = 1;' + "\n")
        codeArr.append('                }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                if (did_write)' + "\n")
        codeArr.append('                {' + "\n")
        codeArr.append('                    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                    printf("KDEBUG: ARBITER_MONO kp%d h%d - (Strm #%d): outputting to (hash, partition, stream) [%d][%d][%d] input_idx=%d\\n",' + "\n")
        codeArr.append('                        kp_idx,' + "\n")
        codeArr.append('                        hash_idx,' + "\n")
        codeArr.append('                        found_strm_idx,' + "\n")
        codeArr.append('                        hash_idx,' + "\n")
        codeArr.append('                        partition_idx,' + "\n")
        codeArr.append('                        found_strm_idx,' + "\n")
        codeArr.append('                        xbar_output[found_strm_idx].value.md.iidx.to_int()' + "\n")
        codeArr.append('                    );' + "\n")
        codeArr.append('                    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    cur_output_idces[found_strm_idx] = ' + "\n")
        codeArr.append('                            xbar_output[found_strm_idx].value.md.iidx;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    xbar_output[found_strm_idx].valid = 0;' + "\n")
        codeArr.append('                    total_num_writes++;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('                    did_read = 1;' + "\n")
        codeArr.append('                    #endif' + "\n")
        codeArr.append('                };' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        ' + "\n")
        codeArr.append('        /* Get the current-lowest output index, and update the allowed output indices' + "\n")
        codeArr.append('         * based on that.' + "\n")
        codeArr.append('         */' + "\n")
        codeArr.append('        INPUT_IDX_DTYPE min_idx = cur_output_idces[0];' + "\n")
        codeArr.append('        slowest_stm_idces = 0;' + "\n")
        codeArr.append('        for (int strm_idx = 1; strm_idx < NUM_STM; ++strm_idx) {' + "\n")
        codeArr.append('        #pragma HLS UNROLL' + "\n")
        codeArr.append('            if (min_idx > cur_output_idces[strm_idx]){' + "\n")
        codeArr.append('                min_idx = cur_output_idces[strm_idx];' + "\n")
        codeArr.append('                slowest_stm_idces = strm_idx;' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        allowed_output_idces = min_idx;' + "\n")
        codeArr.append('        ' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        UPDATE_PERF_CTRS:' + "\n")
        codeArr.append('        total_cycles++;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        if (did_write && !did_read){' + "\n")
        codeArr.append('            writeonly_cycles++;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (did_read && !did_write){' + "\n")
        codeArr.append('            readonly_cycles++;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (!did_read && !did_write){' + "\n")
        codeArr.append('            stall_cycles++;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (did_read && did_write){' + "\n")
        codeArr.append('            readwrite_cycles++;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    WRITE_PERF_CTRS:' + "\n")
        codeArr.append('    for (int arb_atom_idx = 0; arb_atom_idx < NUM_ARBITER_ATOMS; ++arb_atom_idx)' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('        for (int i = 0; i < NUM_PERFCTR_OUTPUTS; ++i) {' + "\n")
        codeArr.append('        #pragma HLS PIPELINE II=1' + "\n")
        codeArr.append('            if (i == 0){' + "\n")
        codeArr.append('                perfctr_out_0[arb_atom_idx].write(stall_cycles);' + "\n")
        codeArr.append('                perfctr_out_1[arb_atom_idx].write(stall_cycles);' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('            else if (i == 1){' + "\n")
        codeArr.append('                perfctr_out_0[arb_atom_idx].write(readonly_cycles);' + "\n")
        codeArr.append('                perfctr_out_1[arb_atom_idx].write(readonly_cycles);' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('            else if (i == 2){' + "\n")
        codeArr.append('                perfctr_out_0[arb_atom_idx].write(writeonly_cycles);' + "\n")
        codeArr.append('                perfctr_out_1[arb_atom_idx].write(writeonly_cycles);' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('            else if (i == 3){' + "\n")
        codeArr.append('                perfctr_out_0[arb_atom_idx].write(readwrite_cycles);' + "\n")
        codeArr.append('                perfctr_out_1[arb_atom_idx].write(readwrite_cycles);' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('            else if (i == 4){' + "\n")
        codeArr.append('                perfctr_out_0[arb_atom_idx].write(total_cycles);' + "\n")
        codeArr.append('                perfctr_out_1[arb_atom_idx].write(total_cycles);' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('            else{' + "\n")
        codeArr.append('                perfctr_out_0[arb_atom_idx].write(55555);' + "\n")
        codeArr.append('                perfctr_out_1[arb_atom_idx].write(55555);' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    printf("ARBITER_MONO kp%d h%d - stall_cycles         = %25lu\\n", ' + "\n")
        codeArr.append('                kp_idx, hash_idx, stall_cycles' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    printf("ARBITER_MONO kp%d h%d - readonly_cycles      = %25lu\\n", ' + "\n")
        codeArr.append('                kp_idx, hash_idx, readonly_cycles' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    printf("ARBITER_MONO kp%d h%d - writeonly_cycles     = %25lu\\n", ' + "\n")
        codeArr.append('                kp_idx, hash_idx, writeonly_cycles' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    printf("ARBITER_MONO kp%d h%d - readwrite_cycles     = %25lu\\n", ' + "\n")
        codeArr.append('                kp_idx, hash_idx, readwrite_cycles' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    printf("ARBITER_MONO kp%d h%d - total_cycles         = %25lu\\n", ' + "\n")
        codeArr.append('                kp_idx, hash_idx, total_cycles' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #endif  // ENABLE_PERF_CTRS' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    printf("\\n\\nARBITER_MONO kp%d h%d - DONE NOW.\\n\\n",' + "\n")
        codeArr.append('            kp_idx, hash_idx' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    return;' + "\n")
        codeArr.append('}' + "\n")
        return codeArr








    def generate_split_monolithic_arb_wrapper(self):
        codeArr = []

        codeArr.append('#define SPLIT_MONOARB_INVOKES_FOR_KP(KP_IDX)    \\' + "\n")

        for h in range(0, self.config.num_hash):
            codeArr.append('        .invoke( bloom_monoarb_per_hash,        \\' + "\n")
            codeArr.append('                    {},      \\'.format(h) + "\n")
            codeArr.append('                    KP_IDX,     \\' + "\n")
            codeArr.append('                    hash_stream_h{}_kp##KP_IDX,      \\'.format(h) + "\n")
            codeArr.append('                    bv_lookup_stream_h{}_kp##KP_IDX  \\'.format(h) + "\n")
            codeArr.append('        )       \\' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#if NUM_HASH != ({})'.format(self.config.num_hash) + "\n")
        codeArr.append('void crash(){crash' + "\n")
        codeArr.append('#endif' + "\n")

        return codeArr




    def generate_split_monolithic_arb(self):
        codeArr = []
        codeArr.extend(self.generate_split_monolithic_arb_func())
        codeArr.extend(self.generate_split_monolithic_arb_wrapper())
        return codeArr








    def generate_single_monolithic_arb(self):
        codeArr = []

        codeArr.append('void bloom_monolithic_arbiter(' + "\n")
        codeArr.append('        int kp_idx' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('        , tapa::istreams<HASHONLY_DTYPE, NUM_STM>         & hash_stream_{}'.format(i) + "\n")
        codeArr.append('        #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('        crash!' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        //#if ENABLE_PERF_CTRS' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('        //,tapa::ostreams<PERFCTR_DTYPE, NUM_ARBITER_ATOMS>   & perfctr_out_{}'.format(i) + "\n")
        codeArr.append('        //        #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('        //        ,crash!' + "\n")
        codeArr.append('        //        #endif' + "\n")
        codeArr.append('        //#endif' + "\n")
        codeArr.append('' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('        , tapa::ostreams<PACKED_HASH_DTYPE, BV_NUM_PARTITIONS>   & bv_lookup_stream_{}'.format(i) + "\n")
        codeArr.append('        #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('        ,crash,' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('){' + "\n")
        codeArr.append('    typedef struct {' + "\n")
        codeArr.append('        ap_uint<1>          valid;' + "\n")
        codeArr.append('        PACKED_HASH_DTYPE   value;' + "\n")
        codeArr.append('        uint32_t            target_partition_idx;' + "\n")
        codeArr.append('    } XBAR_DTYPE;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    const int READ_STOP_COUNT =     NUM_STM * KEYPAIRS_PER_STM*NUM_HASH;' + "\n")
        codeArr.append('    const int WRITE_STOP_COUNT =    NUM_STM * KEYPAIRS_PER_STM*NUM_HASH;' + "\n")
        codeArr.append('    int total_num_reads = 0;' + "\n")
        codeArr.append('    int total_num_writes = 0;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __SYNTHESIS__' + "\n")
        codeArr.append('    /* TAPA Known-issue: Static keyword fails CSIM because this' + "\n")
        codeArr.append('       isnt thread-safe. But when running the HW build, it will ' + "\n")
        codeArr.append('       instantiate several copies of this function. So this is OK.' + "\n")
        codeArr.append('    */' + "\n")
        codeArr.append('    static' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('    INPUT_IDX_DTYPE     reads_per_input[NUM_STM][NUM_HASH] = {{}};' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=reads_per_input dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __SYNTHESIS__' + "\n")
        codeArr.append('    /* TAPA Known-issue: Static keyword fails CSIM because this' + "\n")
        codeArr.append('       isnt thread-safe. But when running the HW build, it will ' + "\n")
        codeArr.append('       instantiate several copies of this function. So this is OK.' + "\n")
        codeArr.append('    */' + "\n")
        codeArr.append('    static' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('    XBAR_DTYPE          xbar_output[NUM_STM][NUM_HASH];' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=xbar_output dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    ' + "\n")
        codeArr.append('    // Keep a running tally of the most-recently-sent index for each hash/stream.' + "\n")
        codeArr.append('    INPUT_IDX_DTYPE     cur_output_idces[NUM_HASH][NUM_STM] = {};' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=cur_output_idces dim=0 complete' + "\n")
        codeArr.append('    INPUT_IDX_DTYPE     allowed_output_idces[NUM_HASH] = {};' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=allowed_output_idces dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    BIT_DTYPE       did_read;' + "\n")
        codeArr.append('    BIT_DTYPE       did_write;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    PERFCTR_DTYPE   stall_cycles = 0;' + "\n")
        codeArr.append('    PERFCTR_DTYPE   readonly_cycles = 0;' + "\n")
        codeArr.append('    PERFCTR_DTYPE   writeonly_cycles = 0;' + "\n")
        codeArr.append('    PERFCTR_DTYPE   readwrite_cycles = 0;' + "\n")
        codeArr.append('    PERFCTR_DTYPE   total_cycles = 0;' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    /* Keep track of the slowest input-streams for each hash function.' + "\n")
        codeArr.append('     * This is for dynamic arbitration. */' + "\n")
        codeArr.append('    STRM_IDX_DTYPE      slowest_stm_idces[NUM_HASH] = {};' + "\n")
        codeArr.append('    #pragma HLS ARRAY_PARTITION variable=slowest_stm_idces dim=0 complete' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifndef __SYNTHESIS__' + "\n")
        codeArr.append('    printf("WARNING! WARNING! WARNING! WARNING! Using monolithic (non-hier) arbiter!!!\\n");' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    /* For some reason, multiple calls to the kernel will fail' + "\n")
        codeArr.append('       SW_EMU without the explicit initialization.' + "\n")
        codeArr.append('    */' + "\n")
        codeArr.append('    INIT_READS:' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_STM; ++i)' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('        for (int j = 0; j < NUM_HASH; ++j)' + "\n")
        codeArr.append('        {' + "\n")
        codeArr.append('            reads_per_input[i][j] = 0;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    INIT_OUTPUT_IDCES:' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_HASH; ++i)' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('        allowed_output_idces[i] = 1;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        for (int j = 0; j < NUM_STM; ++j)' + "\n")
        codeArr.append('        {' + "\n")
        codeArr.append('            cur_output_idces[i][j] = 0;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    INIT_XBAR:' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_STM; ++i)' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('        for (int j = 0; j < NUM_HASH; ++j)' + "\n")
        codeArr.append('        {' + "\n")
        codeArr.append('            xbar_output[i][j].valid = 0;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    INPUTS_LOOP:' + "\n")
        codeArr.append('    while (total_num_reads < READ_STOP_COUNT  ||' + "\n")
        codeArr.append('            total_num_writes < WRITE_STOP_COUNT ' + "\n")
        codeArr.append('    )' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('    #pragma HLS PIPELINE II = 1' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        did_read = 0;' + "\n")
        codeArr.append('        did_write = 0;' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        RD_HASH_LOOP:' + "\n")
        codeArr.append('        for(int hash_idx = 0; hash_idx < NUM_HASH; hash_idx++){' + "\n")
        codeArr.append('            RD_STM_LOOP:' + "\n")
        codeArr.append('            for(int strm_idx = 0; strm_idx < NUM_STM; strm_idx++){' + "\n")
        codeArr.append('                ' + "\n")
        codeArr.append('                // Metadata:' + "\n")
        codeArr.append('                INPUT_IDX_DTYPE cur_input_idx = reads_per_input[strm_idx][hash_idx];' + "\n")
        codeArr.append('                STRM_IDX_DTYPE cur_strm_idx = strm_idx;' + "\n")
        codeArr.append('                METADATA_DTYPE cur_metadata;' + "\n")
        codeArr.append('                PACKED_HASH_DTYPE packed_hashval;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                if (xbar_output[strm_idx][hash_idx].valid == 1) {' + "\n")
        codeArr.append('                    // Dont replace this value - its still valid.' + "\n")
        codeArr.append('                    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                    //printf("KDEBUG: ARBITER_MONO kp%d - (Strm #%d): xbar [stream=%d][hash=%d] is already valid. Not replacing.\\n",' + "\n")
        codeArr.append('                    //        kp_idx,' + "\n")
        codeArr.append('                    //        strm_idx,' + "\n")
        codeArr.append('                    //        strm_idx,' + "\n")
        codeArr.append('                    //        hash_idx' + "\n")
        codeArr.append('                    //);' + "\n")
        codeArr.append('                    #endif' + "\n")
        codeArr.append('                }' + "\n")
        codeArr.append('                else if (' + "\n")

        for i in range(0, self.config.num_hash):
            if (i < self.config.num_hash - 1):
                OR = " ||"
            else:
                OR = ""
            codeArr.append('                    ( hash_idx == {i1} && !hash_stream_{i2}[strm_idx].empty() ) {OR}'.format(i1=i, i2=i, OR=OR) + "\n")
        codeArr.append('                        #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('                        crash &&' + "\n")
        codeArr.append('                        #endif' + "\n")

        codeArr.append('                ) {' + "\n")
        codeArr.append('                    // Hash and partition data:' + "\n")
        codeArr.append('                    HASHONLY_DTYPE  tmp_hash;' + "\n")
        codeArr.append('                    ' + "\n")

        for i in range(0, self.config.num_hash):
            codeArr.append('                    if (hash_idx == {i1}) {{ tmp_hash = hash_stream_{i2}[strm_idx].read(); }}'.format(i1=i, i2=i) + "\n")
        codeArr.append('                    #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('                    crash!' + "\n")
        codeArr.append('                    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('                    did_read = 1;' + "\n")
        codeArr.append('                    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    HASHONLY_DTYPE  idx_inside_partition = tmp_hash % BV_PARTITION_LENGTH;' + "\n")
        codeArr.append('                    int             partition_idx = (tmp_hash / BV_PARTITION_LENGTH);' + "\n")
        codeArr.append('                    ' + "\n")
        codeArr.append('                    total_num_reads++;' + "\n")
        codeArr.append('                    reads_per_input[strm_idx][hash_idx]++;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    cur_input_idx = reads_per_input[strm_idx][hash_idx];' + "\n")
        codeArr.append('                    cur_strm_idx = strm_idx;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    // Pack metadata' + "\n")
        codeArr.append('                    cur_metadata.sidx = cur_strm_idx;' + "\n")
        codeArr.append('                    cur_metadata.iidx = cur_input_idx;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    // Pack final payload' + "\n")
        codeArr.append('                    packed_hashval.md = cur_metadata;' + "\n")
        codeArr.append('                    packed_hashval.hash = idx_inside_partition;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    xbar_output[strm_idx][hash_idx].valid = 1;' + "\n")
        codeArr.append('                    xbar_output[strm_idx][hash_idx].value = packed_hashval;' + "\n")
        codeArr.append('                    xbar_output[strm_idx][hash_idx].target_partition_idx = partition_idx;' + "\n")
        codeArr.append('                }' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('        printf("KDEBUG: ARBITER_MONO kp%d - xbar[hash_idx][target_partition][strm_idx]\\n",' + "\n")
        codeArr.append('                kp_idx' + "\n")
        codeArr.append('        );' + "\n")
        codeArr.append('        for (int strm = 0; strm < NUM_STM; ++strm)' + "\n")
        codeArr.append('        {' + "\n")
        codeArr.append('            for (int hash = 0; hash < NUM_HASH; ++hash)' + "\n")
        codeArr.append('            {' + "\n")
        codeArr.append('                printf("KDEBUG: ARBITER_MONO kp%d - xbar[%d][%d][%d]: valid=%d, input_idx=%d\\n",' + "\n")
        codeArr.append('                        kp_idx,' + "\n")
        codeArr.append('                        hash,' + "\n")
        codeArr.append('                        xbar_output[strm][hash].target_partition_idx,' + "\n")
        codeArr.append('                        strm,' + "\n")
        codeArr.append('                        xbar_output[strm][hash].valid.to_int(),' + "\n")
        codeArr.append('                        xbar_output[strm][hash].value.md.iidx.to_int()' + "\n")
        codeArr.append('                );' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        printf("KDEBUG: ARBITER_MONO kp%d - allowed_output_idces[hash]\\n",' + "\n")
        codeArr.append('                kp_idx' + "\n")
        codeArr.append('        );' + "\n")
        codeArr.append('        for (int hash=0; hash < NUM_HASH; ++hash)' + "\n")
        codeArr.append('        {' + "\n")
        codeArr.append('            printf("KDEBUG: ARBITER_MONO kp%d - allowed_output_idces[%d] = %d\\n",' + "\n")
        codeArr.append('                    kp_idx,' + "\n")
        codeArr.append('                    hash, allowed_output_idces[hash].to_int()' + "\n")
        codeArr.append('            );' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        WR_HASH_LOOP:' + "\n")
        codeArr.append('        for(int hash_idx = 0; hash_idx < NUM_HASH; hash_idx++){' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            WR_BV_PARTITION_LOOP:' + "\n")
        codeArr.append('            for (int partition_idx = 0; ' + "\n")
        codeArr.append('                    partition_idx < BV_NUM_PARTITIONS; ' + "\n")
        codeArr.append('                    ++partition_idx' + "\n")
        codeArr.append('            ) {' + "\n")
        codeArr.append('                bool                found = false;' + "\n")
        codeArr.append('                uint32_t            found_strm_idx = 0;' + "\n")
        codeArr.append('                PACKED_HASH_DTYPE   packed_hashval;' + "\n")
        codeArr.append('                int                 allowed_idx = allowed_output_idces[hash_idx] + (SHUFFLEBUF_SZ);' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                WR_STM_LOOP0:' + "\n")

        #### USING THE DYNAMIC PRIORITY HERE.
        codeArr.append('                //for (int strm_idx = 0; ' + "\n")
        codeArr.append('                //        strm_idx < NUM_STM;' + "\n")
        codeArr.append('                //        strm_idx++' + "\n")
        codeArr.append('                //)' + "\n")
        codeArr.append('                // Prioritizing slowest stream. For some reason, this increases II' + "\n")
        codeArr.append('                //  when using a larger config.' + "\n")
        codeArr.append('                for (int strm_idx = (slowest_stm_idces[hash_idx]+1)%NUM_STM, it_ctr = 0; ' + "\n")
        codeArr.append('                        it_ctr < NUM_STM;' + "\n")
        codeArr.append('                        strm_idx = (strm_idx+1)%NUM_STM, ++it_ctr' + "\n")
        codeArr.append('                )' + "\n")
        codeArr.append('                {' + "\n")
        codeArr.append('                    /* Enforce a strict priority -' + "\n")
        codeArr.append('                     *  Each stream can only output indices' + "\n")
        codeArr.append('                     *  within SHUFFLE_BUFFER_SIZE of the allowed idx.' + "\n")
        codeArr.append('                     *  The allowed idx is the lowest index that HAS NOT' + "\n")
        codeArr.append('                     *  been sent by every streams, for this hash function.' + "\n")
        codeArr.append('                     */' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                    printf("KDEBUG: ARBITER_MONO kp%d - (hash/stream) = (%d, %d), allowed_idx = %d\\n",' + "\n")
        codeArr.append('                            kp_idx,' + "\n")
        codeArr.append('                            hash_idx, strm_idx, allowed_idx' + "\n")
        codeArr.append('                    );' + "\n")
        codeArr.append('                    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    if (xbar_output[strm_idx][hash_idx].valid == 1 &&' + "\n")
        codeArr.append('                        xbar_output[strm_idx][hash_idx].target_partition_idx ==' + "\n")
        codeArr.append('                            partition_idx &&' + "\n")
        codeArr.append('                        allowed_idx >= 0 &&' + "\n")
        codeArr.append('                        xbar_output[strm_idx][hash_idx].value.md.iidx <= allowed_idx' + "\n")
        codeArr.append('                    )' + "\n")
        codeArr.append('                    {' + "\n")
        codeArr.append('                        found = true;' + "\n")
        codeArr.append('                        packed_hashval = xbar_output[strm_idx][hash_idx].value;' + "\n")
        codeArr.append('                        found_strm_idx = strm_idx;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                        #ifndef __SYNTHESIS__' + "\n")
        codeArr.append('                        if (xbar_output[strm_idx][hash_idx].value.md.iidx > allowed_idx){' + "\n")
        codeArr.append('                            printf("\\n\\n\\n\\n\\n\\n\\n\\n");' + "\n")
        codeArr.append('                            printf("SOMETHING IS VERY WRONG IN THE ARBITER_MONO... Crashing now.");' + "\n")
        codeArr.append('                            printf("\\n\\n\\n\\n\\n\\n\\n\\n");' + "\n")
        codeArr.append('                            exit(-1);' + "\n")
        codeArr.append('                        }' + "\n")
        codeArr.append('                        #endif' + "\n")
        codeArr.append('                    }' + "\n")
        codeArr.append('                }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                if (found){' + "\n")
        codeArr.append('                    BIT_DTYPE did_write = 0;' + "\n")
        codeArr.append('' + "\n")

        for i in range(0, self.config.num_hash):
            codeArr.append('                    if (hash_idx == {} &&'.format(i) + "\n")
            codeArr.append('                        bv_lookup_stream_{i}[partition_idx].try_write(packed_hashval)) {{'.format(i=i) + "\n")
            codeArr.append('                        did_write = 1;' + "\n")
            codeArr.append('                    }' + "\n")

        codeArr.append('                    #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('                    crash!' + "\n")
        codeArr.append('                    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                    if (did_write)' + "\n")
        codeArr.append('                    {' + "\n")
        codeArr.append('                        #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('                        printf("KDEBUG: ARBITER_MONO kp%d - (Strm #%d): outputting to (hash, partition, stream) [%d][%d][%d] input_idx=%d\\n",' + "\n")
        codeArr.append('                            kp_idx,' + "\n")
        codeArr.append('                            found_strm_idx,' + "\n")
        codeArr.append('                            hash_idx,' + "\n")
        codeArr.append('                            partition_idx,' + "\n")
        codeArr.append('                            found_strm_idx,' + "\n")
        codeArr.append('                            xbar_output[found_strm_idx][hash_idx].value.md.iidx.to_int()' + "\n")
        codeArr.append('                        );' + "\n")
        codeArr.append('                        #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                        cur_output_idces[hash_idx][found_strm_idx] = ' + "\n")
        codeArr.append('                                xbar_output[found_strm_idx][hash_idx].value.md.iidx;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                        xbar_output[found_strm_idx][hash_idx].valid = 0;' + "\n")
        codeArr.append('                        total_num_writes++;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('                        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('                        did_read = 1;' + "\n")
        codeArr.append('                        #endif' + "\n")
        codeArr.append('                    };' + "\n")
        codeArr.append('                }' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            ' + "\n")
        codeArr.append('            /* Get the current-lowest output index, and update the allowed output indices' + "\n")
        codeArr.append('             * based on that.' + "\n")
        codeArr.append('             */' + "\n")
        codeArr.append('            INPUT_IDX_DTYPE min_idx = cur_output_idces[hash_idx][0];' + "\n")
        codeArr.append('            slowest_stm_idces[hash_idx] = 0;' + "\n")
        codeArr.append('            for (int strm_idx = 1; strm_idx < NUM_STM; ++strm_idx) {' + "\n")
        codeArr.append('            #pragma HLS UNROLL' + "\n")
        codeArr.append('                if (min_idx > cur_output_idces[hash_idx][strm_idx]){' + "\n")
        codeArr.append('                    min_idx = cur_output_idces[hash_idx][strm_idx];' + "\n")
        codeArr.append('                    slowest_stm_idces[hash_idx] = strm_idx;' + "\n")
        codeArr.append('                }' + "\n")
        codeArr.append('            }' + "\n")
        codeArr.append('            allowed_output_idces[hash_idx] = min_idx;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        UPDATE_PERF_CTRS:' + "\n")
        codeArr.append('        total_cycles++;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        if (did_write && !did_read){' + "\n")
        codeArr.append('            writeonly_cycles++;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (did_read && !did_write){' + "\n")
        codeArr.append('            readonly_cycles++;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (!did_read && !did_write){' + "\n")
        codeArr.append('            stall_cycles++;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        else if (did_read && did_write){' + "\n")
        codeArr.append('            readwrite_cycles++;' + "\n")
        codeArr.append('        }' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    WRITE_PERF_CTRS:' + "\n")
        codeArr.append('    for (int arb_atom_idx = 0; arb_atom_idx < NUM_ARBITER_ATOMS; ++arb_atom_idx)' + "\n")
        codeArr.append('    {' + "\n")
        codeArr.append('        for (int i = 0; i < NUM_PERFCTR_OUTPUTS; ++i) {' + "\n")
        codeArr.append('        #pragma HLS PIPELINE II=1' + "\n")

        codeArr.append('            if (i == 0){' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                perfctr_out_{}[arb_atom_idx].write(stall_cycles);'.format(i) + "\n")
        codeArr.append('            }' + "\n")

        codeArr.append('            else if (i == 1){' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                perfctr_out_{}[arb_atom_idx].write(readonly_cycles);'.format(i) + "\n")
        codeArr.append('            }' + "\n")

        codeArr.append('            else if (i == 2){' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                perfctr_out_{}[arb_atom_idx].write(writeonly_cycles);'.format(i) + "\n")
        codeArr.append('            }' + "\n")

        codeArr.append('            else if (i == 3){' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                perfctr_out_{}[arb_atom_idx].write(readwrite_cycles);'.format(i) + "\n")
        codeArr.append('            }' + "\n")

        codeArr.append('            else if (i == 4){' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                perfctr_out_{}[arb_atom_idx].write(total_cycles);'.format(i) + "\n")
        codeArr.append('            }' + "\n")

        codeArr.append('            else{' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                perfctr_out_{}[arb_atom_idx].write(55555);'.format(i) + "\n")
        codeArr.append('            }' + "\n")

        codeArr.append('        }' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    printf("ARBITER_MONO kp%d- stall_cycles         = %25lu\\n", kp_idx, stall_cycles);' + "\n")
        codeArr.append('    printf("ARBITER_MONO kp%d- readonly_cycles      = %25lu\\n", kp_idx, readonly_cycles);' + "\n")
        codeArr.append('    printf("ARBITER_MONO kp%d- writeonly_cycles     = %25lu\\n", kp_idx, writeonly_cycles);' + "\n")
        codeArr.append('    printf("ARBITER_MONO kp%d- readwrite_cycles     = %25lu\\n", kp_idx, readwrite_cycles);' + "\n")
        codeArr.append('    printf("ARBITER_MONO kp%d- total_cycles         = %25lu\\n", kp_idx, total_cycles);' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #endif  // ENABLE_PERF_CTRS' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    printf("\\n\\nARBITER_MONO kp%d - DONE NOW.\\n\\n",' + "\n")
        codeArr.append('            kp_idx' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    return;' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")

        return codeArr

































    def generate(self):
        codeArr = []
        codeArr.extend(self.generate_preamble())

        if (self.config.arbiter_type == ArbiterType.HIERARCHICAL):
            codeArr.extend(self.generate_hier_arb())

        elif (self.config.arbiter_type == ArbiterType.SPLIT_MONOLITHIC):
            codeArr.extend(self.generate_split_monolithic_arb())

        elif (self.config.arbiter_type == ArbiterType.SINGLE_MONOLITHIC):
            print("WARNING: USING SINGLE MONOLITHIC ARBITER... this is not recommended.")
            print("WARNING: USING SINGLE MONOLITHIC ARBITER... this is not recommended.")
            print("WARNING: USING SINGLE MONOLITHIC ARBITER... this is not recommended.")
            codeArr.extend(self.generate_single_monolithic_arb())

        if (self.config.enable_arbiter_sink == 1):
            codeArr.extend(self.generate_debug_sink())

        codeArr.extend(self.generate_postamble())

        return codeArr


