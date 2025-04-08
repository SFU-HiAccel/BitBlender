
class LoadKeyCodeGenerator:
    def __init__(self, config):
        self.config = config


    def generate_load_wrapper(self):
        codeArr = []

        tmp_stm_ctr = 0
        axi_ctr = 0
        codeArr.append('#define LOAD_INVOKES    \\' + "\n")

        ###################
        ### Generate the MAXSTM invocations
        for a in range(0, self.config.keys_num_axi_ports-1):
            codeArr.append('    .invoke(loadKey_MAXSTM  \\' + "\n")
            codeArr.append('            ,key_in_{a}    \\'.format(a=axi_ctr) + "\n")
            for sidx in range(0, self.config.KEYS_MAX_AXI_PACK_FACTOR):
                codeArr.append('            ,key_stream_kp0[{s}]    \\'.format(s=tmp_stm_ctr) + "\n")
                codeArr.append('            ,key_stream_kp1[{s}]    \\'.format(s=tmp_stm_ctr) + "\n")
                tmp_stm_ctr += 1
            codeArr.append('            ,NUM_LOADS_PER_STM\\' + "\n")
            codeArr.append('    )    \\' + "\n")
            axi_ctr += 1

        ###################
        ### Generate the REMAINDER invocation
        codeArr.append('    .invoke(loadKey_REMAINDERSTM    \\' + "\n")
        codeArr.append('            ,key_in_{a}    \\'.format(a=axi_ctr) + "\n")
        for sidx in range(0, self.config.keys_num_remainder_stm):
            codeArr.append('            ,key_stream_kp0[{s}]    \\'.format(s=tmp_stm_ctr) + "\n")
            codeArr.append('            ,key_stream_kp1[{s}]    \\'.format(s=tmp_stm_ctr) + "\n")
            tmp_stm_ctr += 1
        codeArr.append('            ,NUM_LOADS_PER_STM\\' + "\n")
        codeArr.append('    )    \\' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #if NUM_AXI_PORTS != {}'.format(self.config.keys_num_axi_ports) + "\n")
        codeArr.append('    crash(compilation)' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")

        return codeArr





    def generate_load_remainderstm(self):
        codeArr = []
        codeArr.append('void loadKey_REMAINDERSTM(' + "\n")
        codeArr.append('#if _KENNY_USING_AURORA_' + "\n")
        codeArr.append('        tapa::istream<LOAD_DTYPE>   & key_in_stm' + "\n")
        codeArr.append('#else   //_KENNY_USING_AURORA_' + "\n")
        codeArr.append('        tapa::async_mmap<LOAD_DTYPE>   & key_in_mmap' + "\n")
        codeArr.append('#endif  //_KENNY_USING_AURORA_' + "\n")
        for s in range(0, self.config.keys_num_remainder_stm):
            codeArr.append('        ,tapa::ostream<KEY_DTYPE>       & key_stream_S{s}_kp0'.format(s=s) + "\n")
            codeArr.append('        ,tapa::ostream<KEY_DTYPE>       & key_stream_S{s}_kp1'.format(s=s) + "\n")
        codeArr.append('        ,int NUM_LOADS_PER_STM' + "\n")
        codeArr.append('){' + "\n")


        codeArr.append("""
    LOAD_DTYPE cur_load;

    for (int i_req = 0, i_resp = 0;
            i_resp < NUM_LOADS_PER_STM; )
    {
        #pragma HLS PIPELINE II=1

#if _KENNY_USING_AURORA_
        if (!key_in_stm.empty()){
            cur_load = key_in_stm.read(nullptr);
#else
        if (i_req < NUM_LOADS_PER_STM && key_in_mmap.read_addr.try_write(i_req)) {
            ++i_req;
        }
        if (!key_in_mmap.read_data.empty()) {
            cur_load = key_in_mmap.read_data.read(nullptr);
#endif

            #define WRITE_SIDX(SIDX)    \\
                key_stream_S##SIDX##_kp0.write(cur_load.s##SIDX##_k0); \\
                key_stream_S##SIDX##_kp1.write(cur_load.s##SIDX##_k1);

""")

        for s in range(0, self.config.keys_num_remainder_stm):
            codeArr.append('            WRITE_SIDX({s})'.format(s=s) + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('            crash on purpose(,' + "\n")
        codeArr.append('            #endif' + "\n")

        codeArr.append("""

            #ifdef __DO_DEBUG_PRINTS__
            printf("KDEBUG: LOADKEY_REMAINDERSTM - Loaded the %d'th keypair. In stm0, this is = %d, %d\\n",
                    i_resp,
                    cur_load.s0_k0.to_int(),
                    cur_load.s0_k1.to_int()
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

        codeArr.append("\n\n\n")
        return codeArr







    def generate_load_maxstm(self):
        codeArr = []
        codeArr.append('void loadKey_MAXSTM(' + "\n")
        codeArr.append('#if _KENNY_USING_AURORA_' + "\n")
        codeArr.append('        tapa::istream<LOAD_DTYPE>   & key_in_stm' + "\n")
        codeArr.append('#else   //_KENNY_USING_AURORA_' + "\n")
        codeArr.append('        tapa::async_mmap<LOAD_DTYPE>   & key_in_mmap' + "\n")
        codeArr.append('#endif  //_KENNY_USING_AURORA_' + "\n")
        for s in range(0, self.config.KEYS_MAX_AXI_PACK_FACTOR):
            codeArr.append('        ,tapa::ostream<KEY_DTYPE>           & key_stream_S{s}_kp0'.format(s=s) + "\n")
            codeArr.append('        ,tapa::ostream<KEY_DTYPE>           & key_stream_S{s}_kp1'.format(s=s) + "\n")
        codeArr.append('        ,int NUM_LOADS_PER_STM' + "\n")
        codeArr.append('){' + "\n")

        codeArr.append("""
    LOAD_DTYPE cur_load;

    for (int i_req = 0, i_resp = 0;
            i_resp < NUM_LOADS_PER_STM; )
    {
        #pragma HLS PIPELINE II=1

#if _KENNY_USING_AURORA_
        if (!key_in_stm.empty()){
            cur_load = key_in_stm.read(nullptr);
#else
        if (i_req < NUM_LOADS_PER_STM && key_in_mmap.read_addr.try_write(i_req)) {
            ++i_req;
        }
        if (!key_in_mmap.read_data.empty()) {
            cur_load = key_in_mmap.read_data.read(nullptr);
#endif

            #define WRITE_SIDX(SIDX)    \\
                key_stream_S##SIDX##_kp0.write(cur_load.s##SIDX##_k0); \\
                key_stream_S##SIDX##_kp1.write(cur_load.s##SIDX##_k1);

""")

        for s in range(0, self.config.KEYS_MAX_AXI_PACK_FACTOR):
            codeArr.append('            WRITE_SIDX({s})'.format(s=s) + "\n")
        codeArr.append('' + "\n")
        codeArr.append('            #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('            crash on purpose(,' + "\n")
        codeArr.append('            #endif' + "\n")

        codeArr.append("""

            #ifdef __DO_DEBUG_PRINTS__
            printf("KDEBUG: LOADKEY_MAXSTM - Loaded the %d'th keypair. In stm0, this is = %d, %d\\n",
                    i_resp,
                    cur_load.s0_k0.to_int(),
                    cur_load.s0_k1.to_int()
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
        codeArr.append("\n\n\n")

        return codeArr







    def generate(self):
        codeArr = []
        codeArr.extend(self.generate_load_maxstm())
        codeArr.extend(self.generate_load_remainderstm())
        codeArr.extend(self.generate_load_wrapper())

        codeArr.append("\n\n/*************************************************************************************/\n\n")
        return codeArr
