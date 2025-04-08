
class AggrCodeGenerator:
    def __init__(self, config):
        self.config = config


    def generate_single_aggr(self):
        codeArr = []

        codeArr.append("""
void bloom_aggregate_SPLIT(
        int     agg_idx,
        int     kp_idx,
        tapa::istreams<BIT_DTYPE, NUM_HASH>   & reconstruct_stream,
        tapa::ostream<BIT_DTYPE>   & aggregate_stream
){
    #ifndef __SYNTHESIS__
    //printf("NOTE: Using SPLIT AGGREGATE!!\\n");
    #endif

    int num_writes_TOTAL = 0;
    int num_reads = 0;
    int all_hashes_available = 0;
    uint32_t result = 1;

    while (num_writes_TOTAL < KEYPAIRS_PER_STM)
    {
    #pragma HLS PIPELINE=1
        // Check if all of our hash values are available:
        all_hashes_available = 1;

        for (int i = 0; i < NUM_HASH; ++i) {
            if (reconstruct_stream[i].empty()) {
                all_hashes_available = 0;
            } 
        }

        if (all_hashes_available)
        {
            result = 1;
            for (int i = 0; i < NUM_HASH; ++i) {
                result &= reconstruct_stream[i].read();
            }

            num_reads++;
            #ifdef __DO_DEBUG_PRINTS__
            printf("AGGREGATE #%d kp%d - input query %d got a value of %d\\n",
                    agg_idx, kp_idx, num_reads, result
            );
            #endif

            aggregate_stream.write(result);
            num_writes_TOTAL++;
        }
    }

    #ifdef __DO_DEBUG_PRINTS__
    printf("\\n\\nAGGREGATE #%d kp%d - DONE NOW.\\n\\n",
            agg_idx, kp_idx
    );
    #endif
    return;
}
"""
        )
        codeArr.append("\n\n\n")

        return codeArr




    def generate_aggr_wrapper(self):
        codeArr = []

        codeArr.append('#define AGGREGATE_INVOKES_FOR_KP(KP_IDX)    \\' + "\n")
        for s in range(0, self.config.num_stm):
            codeArr.append('        .invoke(bloom_aggregate_SPLIT,  \\' + "\n")
            codeArr.append('                    {s},  \\'.format(s=s) + "\n")
            codeArr.append('                    KP_IDX, \\' + "\n")
            codeArr.append('                    reconstruct_stream_stm{s}_kp##KP_IDX, \\'.format(s=s) + "\n")
            codeArr.append('                    aggregate_stream_kp##KP_IDX[{s}]  \\'.format(s=s) + "\n")
            codeArr.append('        )   \\' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('#if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('crash!!!' + "\n")
        codeArr.append('#endif' + "\n")

        return codeArr




    def generate(self):
        codeArr = []
        codeArr.extend(self.generate_single_aggr())
        codeArr.extend(self.generate_aggr_wrapper())
        codeArr.append("\n\n/*************************************************************************************/\n\n")
        return codeArr
