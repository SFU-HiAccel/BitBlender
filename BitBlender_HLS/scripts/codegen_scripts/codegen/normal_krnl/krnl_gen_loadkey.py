
class LoadKeyCodeGenerator:
    def __init__(self, config):
        self.config = config

    def generate(self):
        codeArr = []
        codeArr.append(
"""
void loadKey(
        tapa::async_mmap<LOAD_DTYPE>            & key_in
        ,tapa::ostreams<KEY_DTYPE, NUM_STM>     & key_stream_kp0
        ,tapa::ostreams<KEY_DTYPE, NUM_STM>     & key_stream_kp1
){
    LOAD_DTYPE cur_load;

    for (int i_req = 0, i_resp = 0;
            i_resp < KEYPAIRS_PER_STM; )
    {
        #pragma HLS PIPELINE II=1
        
        if (i_req < KEYPAIRS_PER_STM && key_in.read_addr.try_write(i_req)) {
            ++i_req;
        }
        if (!key_in.read_data.empty()) {
            cur_load = key_in.read_data.read(nullptr);

            #define WRITE_SIDX(SIDX)    \\
                key_stream_kp0[SIDX].write(cur_load.s##SIDX##_k0); \\
                key_stream_kp1[SIDX].write(cur_load.s##SIDX##_k1);

""")

        for s in range(0, self.config.num_stm):
            codeArr.append('            WRITE_SIDX({s})'.format(s=s) + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('            crash on purpose(,' + "\n")
        codeArr.append('            #endif' + "\n")

        codeArr.append("""

            #ifdef __DO_DEBUG_PRINTS__
            printf("KDEBUG: LOADKEY - The %d'th keypair = %d, %d\\n",
                    i_resp,
                    cur_keypair.k0.to_int(),
                    cur_keypair.k1.to_int()
            );
            #endif

            ++i_resp;
        }
    }

    #ifdef __DO_DEBUG_PRINTS__
    printf("\\n\\nLOADKEY - IS DONE NOW.\\n\\n");
    #endif
    return;
}
"""
        )
        codeArr.append("\n\n/*************************************************************************************/\n\n")

        return codeArr
