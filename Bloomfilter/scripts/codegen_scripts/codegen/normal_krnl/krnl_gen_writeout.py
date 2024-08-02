
class WriteOutCodeGenerator:
    def __init__(self, config):
        self.config = config




    def generate_packOutput(self):
        codeArr = []

        codeArr.append(
        """
void packOutput(
        int strm_idx
        ,int kp_idx
        ,tapa::istream<BIT_DTYPE>           & aggregate_stream
        ,tapa::ostream<OUT_PACKED_DTYPE>    & packed_outputs_stream
) {
    int                 pk_idx;
    OUT_PACKED_DTYPE    packed;
    BIT_DTYPE           val;

    #ifdef __DO_DEBUG_PRINTS__
    int num_writes = 0;
    #endif

    for (int i = 0; i < KEYPAIRS_PER_STM; ++i) {
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
        codeArr.append("\n\n\n")
        return codeArr



    def generate_writeOutput_sync(self):
        codeArr = []
        codeArr.append('void writeOutput_synchronous(' + "\n")
        for s in range(0, self.config.keys_axi_port_pack_factor):
            if (s < self.config.num_stm):
                codeArr.append('        tapa::istream<OUT_PACKED_DTYPE>&  packed_outputs_stream_s{s}_kp0,'.format(s=s) + "\n")
                codeArr.append('        tapa::istream<OUT_PACKED_DTYPE>&  packed_outputs_stream_s{s}_kp1,'.format(s=s) + "\n")
        codeArr.append('        tapa::mmap<STORE_DTYPE>      outmmap' + "\n")
        codeArr.append('){' + "\n")
        codeArr.append('    STORE_DTYPE     to_store;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    for (int i = 0; i < PACKED_OUTPUTS_PER_STM; ++i) {' + "\n")

        for s in range(0, self.config.keys_axi_port_pack_factor):
            if (s < self.config.num_stm):
                codeArr.append('        to_store.s{s}_k0 = packed_outputs_stream_s{s}_kp0.read();'.format(s=s) + "\n")
                codeArr.append('        to_store.s{s}_k1 = packed_outputs_stream_s{s}_kp1.read();'.format(s=s) + "\n")
                codeArr.append('' + "\n")

        codeArr.append('        outmmap[i] = to_store;' + "\n")
        codeArr.append('    }' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    printf("WRITEOUTPUT - (synchronous version) exiting now\\n",' + "\n")
        codeArr.append('    );' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('}' + "\n")
        return codeArr










    def generate(self):
        codeArr = []
        codeArr.extend(self.generate_packOutput())
        codeArr.extend(self.generate_writeOutput_sync())
        codeArr.append("\n\n/*************************************************************************************/\n\n")
        return codeArr


