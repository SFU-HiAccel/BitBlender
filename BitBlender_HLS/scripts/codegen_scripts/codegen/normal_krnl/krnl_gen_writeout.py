
class WriteOutCodeGenerator:
    def __init__(self, config):
        self.config = config



    def generate_perfctr_out(self):
        codeArr = []

        codeArr.append('/*************************************************************************************/' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('void write_perfctrs(' + "\n")
        codeArr.append('    tapa::istreams<PERFCTR_DTYPE, NUM_PERFCTR_MODULES>  & querycycle_in' + "\n")
        codeArr.append('    ,tapa::mmap<PERFCTR_DTYPE>                          perfctr_mmap' + "\n")
        codeArr.append(') {' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_PERFCTR_MODULES; ++i) {' + "\n")
        codeArr.append('        perfctr_mmap[i] = querycycle_in[i].read();' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('/*************************************************************************************/' + "\n")

        return codeArr






    def generate_writeOut_wrapper(self):
        codeArr = []
        tmp_stm_ctr = 0
        axi_ctr = 0
        codeArr.append('#define WRITEOUT_INVOKES    \\' + "\n")

        ###################
        ### Generate the MAXSTM invocations
        for a in range(0, self.config.keys_num_axi_ports-1):
            codeArr.append('        .invoke(writeOutput_MAXSTM  \\' + "\n")
            for sidx in range(0, self.config.KEYS_MAX_AXI_PACK_FACTOR):
                codeArr.append('                ,packed_output_stm_kp0[{s}] \\'.format(s=tmp_stm_ctr) + "\n")
                codeArr.append('                ,packed_output_stm_kp1[{s}] \\'.format(s=tmp_stm_ctr) + "\n")
                tmp_stm_ctr += 1
            codeArr.append('                ,out_bits_{a}  \\'.format(a=axi_ctr) + "\n")
            codeArr.append('                ,NUM_LOADS_PER_STM  \\' + "\n")
            codeArr.append('    )    \\' + "\n")
            axi_ctr += 1

        ###################
        ### Generate the REMAINDER invocation
        codeArr.append('    .invoke(writeOutput_REMAINDERSTM   \\' + "\n")
        for sidx in range(0, self.config.keys_num_remainder_stm):
            codeArr.append('                ,packed_output_stm_kp0[{s}] \\'.format(s=tmp_stm_ctr) + "\n")
            codeArr.append('                ,packed_output_stm_kp1[{s}] \\'.format(s=tmp_stm_ctr) + "\n")
            tmp_stm_ctr += 1
        codeArr.append('                ,out_bits_{a}  \\'.format(a=axi_ctr) + "\n")
        codeArr.append('                ,NUM_LOADS_PER_STM  \\' + "\n")
        codeArr.append('    )    \\' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        return codeArr





    def generate_packOutput(self):
        codeArr = []

        codeArr.append(
        """
void packOutput(
        int strm_idx
        ,int kp_idx
        ,tapa::istream<BIT_DTYPE>           & aggregate_stream
        ,tapa::ostream<OUT_PACKED_DTYPE>    & packed_outputs_stream
        ,int NUM_LOADS_PER_STM
) {
    int                 pk_idx;
    OUT_PACKED_DTYPE    packed;
    BIT_DTYPE           val;

    #ifdef __DO_DEBUG_PRINTS__
    int num_writes = 0;
    #endif

    for (int i = 0; i < NUM_LOADS_PER_STM; ++i) {
        pk_idx = i % OUT_PACKED_BITWIDTH;

        val = aggregate_stream.read();
        packed.range(pk_idx, pk_idx) = val.range(0, 0);

        if (pk_idx == OUT_PACKED_BITWIDTH - 1){
            packed_outputs_stream.write(packed);
            packed = 0;

            #ifdef __DO_DEBUG_PRINTS__
            num_writes += 1;
            #endif
        }
    }

    #ifdef __DO_DEBUG_PRINTS__
    printf("PACKOUTPUT #%d kp%d - finishing after writing %d times.\\n",
            strm_idx, kp_idx, num_writes
    );
    #endif
}
"""
        )
        codeArr.append("\n\n\n\n\n\n")
        return codeArr



    def generate_writeOutput_maxstm(self):
        codeArr = []
        codeArr.append('void writeOutput_MAXSTM(' + "\n")
        for s in range(0, self.config.KEYS_MAX_AXI_PACK_FACTOR):
            codeArr.append('        tapa::istream<OUT_PACKED_DTYPE>&  packed_outputs_stream_s{s}_kp0,'.format(s=s) + "\n")
            codeArr.append('        tapa::istream<OUT_PACKED_DTYPE>&  packed_outputs_stream_s{s}_kp1,'.format(s=s) + "\n")
        codeArr.append('#if _KENNY_USING_AURORA_' + "\n")
        codeArr.append('        tapa::ostream<STORE_DTYPE>     & out_bits_stm,' + "\n")
        codeArr.append('#else' + "\n")
        codeArr.append('        tapa::mmap<STORE_DTYPE>        out_bits_mmap,' + "\n")
        codeArr.append('#endif' + "\n")
        codeArr.append('        int NUM_LOADS_PER_STM' + "\n")
        codeArr.append('){' + "\n")

        codeArr.append('    STORE_DTYPE     to_store;' + "\n")
        codeArr.append('    int NUM_PACKED_OUTPUTS_PER_STM = CEIL_DIVISION(NUM_LOADS_PER_STM, OUT_PACKED_BITWIDTH);' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_PACKED_OUTPUTS_PER_STM; ++i) {' + "\n")

        for s in range(0, self.config.KEYS_MAX_AXI_PACK_FACTOR):
            codeArr.append('        to_store.s{s}_k0 = packed_outputs_stream_s{s}_kp0.read();'.format(s=s) + "\n")
            codeArr.append('        to_store.s{s}_k1 = packed_outputs_stream_s{s}_kp1.read();'.format(s=s) + "\n")
            codeArr.append('' + "\n")

        codeArr.append('#if _KENNY_USING_AURORA_' + "\n")
        codeArr.append('        out_bits_stm.write(to_store);' + "\n")
        codeArr.append('#else' + "\n")
        codeArr.append('        out_bits_mmap[i] = to_store;' + "\n")
        codeArr.append('#endif' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    printf("WRITEOUTPUT - (synchronous version) exiting now\\n");' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append("\n\n\n\n\n\n")
        return codeArr












    def generate_writeOutput_remainderstm(self):
        codeArr = []
        codeArr.append('void writeOutput_REMAINDERSTM(' + "\n")
        for s in range(0, self.config.keys_num_remainder_stm):
            codeArr.append('        tapa::istream<OUT_PACKED_DTYPE>&  packed_outputs_stream_s{s}_kp0,'.format(s=s) + "\n")
            codeArr.append('        tapa::istream<OUT_PACKED_DTYPE>&  packed_outputs_stream_s{s}_kp1,'.format(s=s) + "\n")
        codeArr.append('#if _KENNY_USING_AURORA_' + "\n")
        codeArr.append('        tapa::ostream<STORE_DTYPE>     & out_bits_stm,' + "\n")
        codeArr.append('#else' + "\n")
        codeArr.append('        tapa::mmap<STORE_DTYPE>        out_bits_mmap,' + "\n")
        codeArr.append('#endif' + "\n")
        codeArr.append('        int NUM_LOADS_PER_STM' + "\n")
        codeArr.append('){' + "\n")

        codeArr.append('    STORE_DTYPE     to_store;' + "\n")
        codeArr.append('    int NUM_PACKED_OUTPUTS_PER_STM = CEIL_DIVISION(NUM_LOADS_PER_STM, OUT_PACKED_BITWIDTH);' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    for (int i = 0; i < NUM_PACKED_OUTPUTS_PER_STM; ++i) {' + "\n")

        for s in range(0, self.config.keys_num_remainder_stm):
            codeArr.append('        to_store.s{s}_k0 = packed_outputs_stream_s{s}_kp0.read();'.format(s=s) + "\n")
            codeArr.append('        to_store.s{s}_k1 = packed_outputs_stream_s{s}_kp1.read();'.format(s=s) + "\n")
            codeArr.append('' + "\n")

        codeArr.append('#if _KENNY_USING_AURORA_' + "\n")
        codeArr.append('        out_bits_stm.write(to_store);' + "\n")
        codeArr.append('#else' + "\n")
        codeArr.append('        out_bits_mmap[i] = to_store;' + "\n")
        codeArr.append('#endif' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    printf("WRITEOUTPUT - (synchronous version) exiting now\\n");' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append("\n\n\n\n\n\n")
        return codeArr












    def generate(self):
        codeArr = []

        if (self.config.enable_perf_ctrs):
            codeArr.extend(self.generate_perfctr_out())

        codeArr.extend(self.generate_packOutput())
        codeArr.extend(self.generate_writeOutput_maxstm())
        codeArr.extend(self.generate_writeOutput_remainderstm())
        codeArr.extend(self.generate_writeOut_wrapper())
        codeArr.append("\n\n/*************************************************************************************/\n\n")
        return codeArr


