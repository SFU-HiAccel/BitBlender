
from ..types import ArbiterType

class TopLevelCodeGenerator:
    def __init__(self, config):
        self.config = config




    def generate_func_declaration(self):
        codeArr = []
        codeArr.append('void workload(' + "\n")
        codeArr.append('    tapa::mmap<BV_LOAD_DTYPE>       input_bv' + "\n")

        codeArr.append('#if _KENNY_USING_AURORA_' + "\n")
        for a in range(0, self.config.keys_num_axi_ports):
            codeArr.append('    ,tapa::istream<LOAD_DTYPE>      & key_in_{a}'.format(a=a) + "\n")

        for a in range(0, self.config.keys_num_axi_ports):
            codeArr.append('    ,tapa::ostream<STORE_DTYPE>     & out_bits_{a}'.format(a=a) + "\n")

        codeArr.append('#else   //_KENNY_USING_AURORA_' + "\n")
        for a in range(0, self.config.keys_num_axi_ports):
            codeArr.append('    ,tapa::mmap<LOAD_DTYPE>         key_in_{a}'.format(a=a) + "\n")

        for a in range(0, self.config.keys_num_axi_ports):
            codeArr.append('    ,tapa::mmap<STORE_DTYPE>        out_bits_{a}'.format(a=a) + "\n")

        codeArr.append('#endif  //_KENNY_USING_AURORA_' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #if NUM_AXI_PORTS != {}'.format(self.config.keys_num_axi_ports) + "\n")
        codeArr.append('    crash(compilation)' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('    , crash! //crash on purpose; we may need more streams.' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    ,tapa::mmap<PERFCTR_DTYPE>      perfctr_mmap' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    ,int                            NUM_LOADS_PER_STM' + "\n")

        codeArr.append('#if _KENNY_USING_AURORA_' + "\n")
        codeArr.append('    ,tapa::ostream<bool>            DUMMY_ack_out' + "\n")
        codeArr.append('    ,tapa::istream<bool>            DUMMY_ack_in' + "\n")
        codeArr.append('#endif  //_KENNY_USING_AURORA_' + "\n")
        codeArr.append(')' + "\n")
        codeArr.append("\n\n")
        return codeArr





    def generate_intermodule_fifo_decls(self):
        codeArr = []
        codeArr.append('    //////////////////////////////////////////////////////////' + "\n")
        codeArr.append('    // Connections BETWEEN modules:' + "\n")
        codeArr.append('    tapa::streams<KEY_DTYPE, NUM_STM, STM_DEPTH> key_stream_kp0;' + "\n")
        codeArr.append('    tapa::streams<KEY_DTYPE, NUM_STM, STM_DEPTH> key_stream_kp1;' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    // loadBV outputs' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('    tapa::stream<BV_URAM_PACKED_DTYPE, STM_DEPTH> bv_load_stream_{};'.format(i) + "\n")
        codeArr.append('    #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('    crash!' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    // Computehash outputs (kp stands for key-pair)' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('    tapa::streams<COMP2ARB_DTYPE, NUM_STM, STM_DEPTH> comp2arb_stream_h{}_kp0;'.format(i) + "\n")
            codeArr.append('    tapa::streams<COMP2ARB_DTYPE, NUM_STM, STM_DEPTH> comp2arb_stream_h{}_kp1;'.format(i) + "\n")
        codeArr.append('    #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('    crash!' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    // Arbiter outputs' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('    tapa::streams<PACKED_HASH_DTYPE, BV_NUM_PARTITIONS, STM_DEPTH> bv_lookup_stream_h{}_kp0;'.format(i) + "\n")
            codeArr.append('    tapa::streams<PACKED_HASH_DTYPE, BV_NUM_PARTITIONS, STM_DEPTH> bv_lookup_stream_h{}_kp1;'.format(i) + "\n")
        codeArr.append('    #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('    crash!' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    // Query unit outputs' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('    tapa::streams<BV_PLUS_METADATA_PACKED_DTYPE, BV_NUM_PARTITIONS, STM_DEPTH> query_bv_packed_stream_hash{}_kp0;'.format(i) + "\n")
            codeArr.append('    tapa::streams<BV_PLUS_METADATA_PACKED_DTYPE, BV_NUM_PARTITIONS, STM_DEPTH> query_bv_packed_stream_hash{}_kp1;'.format(i) + "\n")
        codeArr.append('    #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('    crash!!!' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    // Shuffle unit output' + "\n")
        for i in range(0, self.config.num_stm):
            codeArr.append('    tapa::streams<BIT_DTYPE, NUM_HASH, STM_DEPTH> reconstruct_stream_stm{}_kp0;'.format(i) + "\n")
            codeArr.append('    tapa::streams<BIT_DTYPE, NUM_HASH, STM_DEPTH> reconstruct_stream_stm{}_kp1;'.format(i) + "\n")
        codeArr.append('    #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('    crash!!!!!!!' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    // Aggregate output' + "\n")
        codeArr.append('    tapa::streams<BIT_DTYPE,        NUM_STM, STM_DEPTH>     aggregate_stream_kp0;' + "\n")
        codeArr.append('    tapa::streams<BIT_DTYPE,        NUM_STM, STM_DEPTH>     aggregate_stream_kp1;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    // Datapacked outputs' + "\n")
        codeArr.append('    tapa::streams<OUT_PACKED_DTYPE,   NUM_STM, STM_DEPTH>     packed_output_stm_kp0;' + "\n")
        codeArr.append('    tapa::streams<OUT_PACKED_DTYPE,   NUM_STM, STM_DEPTH>     packed_output_stm_kp1;' + "\n")
        codeArr.append('    ' + "\n")

        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    // Perfctr info' + "\n")
        codeArr.append('    tapa::streams<PERFCTR_DTYPE, NUM_PERFCTR_MODULES, STM_DEPTH>   perfctr_stms;' + "\n")
        codeArr.append('    #endif' + "\n")

        codeArr.append("\n\n")
        return codeArr


    def generate_intramodule_fifo_decls(self):
        codeArr = []
        codeArr.append('    //////////////////////////////////////////////////////////' + "\n")
        codeArr.append('    // Connections WITHIN modules:' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('    // FIFOS within compute:' + "\n")
        codeArr.append('    COMPUTEHASH_STREAM_DECLS_KP(0)' + "\n")
        codeArr.append('    COMPUTEHASH_STREAM_DECLS_KP(1)' + "\n")
        codeArr.append('' + "\n")

        if (
            self.config.arbiter_type == ArbiterType.SEPARATED_HIERARB_PER_HASH
            or
            self.config.arbiter_type == ArbiterType.SEPARATED_HIERARB_PER_HASH_SINGLECYCLE_EXIT_CHECK
            or
            self.config.arbiter_type == ArbiterType.SEPARATED_HIERARB_PER_HASH_NORATELIM
            or
            self.config.arbiter_type == ArbiterType.SEPARATED_MONOARB_PER_HASH
        ):
            codeArr.append('    ARBITER_STREAM_DECLS_KP(0)' + "\n")
            codeArr.append('    ARBITER_STREAM_DECLS_KP(1)' + "\n")
            codeArr.append('' + "\n")

        codeArr.append('    SHUFFLE_STREAM_DECLS_KP(0)' + "\n")
        codeArr.append('    SHUFFLE_STREAM_DECLS_KP(1)' + "\n")
        codeArr.append('' + "\n")

        return codeArr





    def generate_load_invokes(self):
        codeArr = []
        codeArr.append('        .invoke(loadBV' + "\n")
        codeArr.append('                ,input_bv' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                ,bv_load_stream_{}'.format(i) + "\n")
        codeArr.append('                #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('                crash!' + "\n")
        codeArr.append('                #endif' + "\n")
        codeArr.append('        )' + "\n")

        codeArr.append('' + "\n")
        ##codeArr.append('        .invoke(loadKey, key_in, key_stream_kp0, key_stream_kp1)'.format(i=i) + "\n")
        codeArr.append('        LOAD_INVOKES' + "\n")
        codeArr.append('' + "\n")

        codeArr.append("\n\n")
        return codeArr





    def generate_compute_invokes(self):
        codeArr = []
        codeArr.append('        COMPUTEHASH_INVOKES_FOR_KP(0)' + "\n")
        codeArr.append('        COMPUTEHASH_INVOKES_FOR_KP(1)' + "\n")
        codeArr.append("\n\n")
        return codeArr


    def generate_single_monoarb_invokes(self):
        codeArr = []

        codeArr.append('        .invoke(bloom_monolithic_arbiter' + "\n")
        codeArr.append('                    , 0' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                    , comp2arb_stream_h{}_kp0'.format(i) + "\n")
        codeArr.append('' + "\n")


        for i in range(0, self.config.num_hash):
            codeArr.append('                    , bv_lookup_stream_h{}_kp0'.format(i) + "\n")
        codeArr.append('        )' + "\n")


        codeArr.append('        .invoke(bloom_monolithic_arbiter' + "\n")
        codeArr.append('                    , 1' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                    , comp2arb_stream_h{}_kp1'.format(i) + "\n")
        codeArr.append('' + "\n")

        for i in range(0, self.config.num_hash):
            codeArr.append('                    , bv_lookup_stream_h{}_kp1'.format(i) + "\n")
        codeArr.append('        )' + "\n")

        return codeArr



    def generate_unseparated_arb_invokes_invokes(self):
        codeArr = []
        codeArr.append('        SPLIT_MONOARB_INVOKES_FOR_KP(0)' + "\n")
        codeArr.append('        SPLIT_MONOARB_INVOKES_FOR_KP(1)' + "\n")
        codeArr.append("\n\n")
        return codeArr




    def generate_separated_arb_invokes(self):
        codeArr = []

        codeArr.append('        ARBITER_INVOKES_FOR_KP(0)' + "\n")
        codeArr.append('        ARBITER_INVOKES_FOR_KP(1)' + "\n")
        codeArr.append("\n\n")

        return codeArr








    def generate_arb_sink_invoke(self):
        codeArr = []
        codeArr.append('    #if DEBUG_ARBITER_SINK' + "\n")
        codeArr.append('        .invoke(DEBUG_arbiter_sink' + "\n")
        for i in range(self.config.num_hash):
            codeArr.append('                , bv_lookup_stream_h{}_kp0'.format(i) + "\n")
        codeArr.append('' + "\n")
        for i in range(self.config.num_hash):
            codeArr.append('                , bv_lookup_stream_h{}_kp1'.format(i) + "\n")
        codeArr.append('' + "\n")

        for i in range(self.config.num_hash):
            codeArr.append('                ,bv_load_stream_{}'.format(i) + "\n")
        codeArr.append('' + "\n")
        codeArr.append('        )' + "\n")
        codeArr.append('    ;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #endif  // DEBUG_ARBITER_SINK' + "\n")
        return codeArr


    def generate_arbiter_invokes(self):
        codeArr = []
        if (
            self.config.arbiter_type == ArbiterType.SEPARATED_HIERARB_PER_HASH
            or
            self.config.arbiter_type == ArbiterType.SEPARATED_HIERARB_PER_HASH_SINGLECYCLE_EXIT_CHECK
            or
            self.config.arbiter_type == ArbiterType.SEPARATED_HIERARB_PER_HASH_NORATELIM
            or
            self.config.arbiter_type == ArbiterType.SEPARATED_MONOARB_PER_HASH
        ):
            codeArr.extend(self.generate_separated_arb_invokes())

        elif (self.config.arbiter_type == ArbiterType.UNSEPARATED_MONOARB_PER_HASH):
            codeArr.extend(self.generate_unseparated_arb_invokes_invokes())

        elif (self.config.arbiter_type == ArbiterType.SINGLE_MONOLITHIC):
            codeArr.extend(self.generate_single_monoarb_invokes())

        if (self.config.enable_arbiter_sink == 1):
            print("WARNING: Enabling ARBITER SINK!")
            codeArr.extend(self.generate_arb_sink_invoke())

        return codeArr


    def generate_query_invokes(self):
        codeArr = []
        codeArr.append('        QUERY_INVOKES' + "\n")
        codeArr.append("\n\n")
        return codeArr


    def generate_shuffle_invokes(self):
        codeArr = []

        codeArr.append('        SHUFFLE_INVOKES_FOR_KP(0)' + "\n")
        codeArr.append('        SHUFFLE_INVOKES_FOR_KP(1)' + "\n")

        codeArr.append("\n\n")
        return codeArr


    def generate_aggr_invokes(self):
        codeArr = []

        codeArr.append('        AGGREGATE_INVOKES_FOR_KP(0)' + "\n")
        codeArr.append('        AGGREGATE_INVOKES_FOR_KP(1)' + "\n")

        codeArr.append("\n\n")
        return codeArr


    def generate_writeOut_invokes(self):
        codeArr = []

        for i in range(0, self.config.num_stm):
            codeArr.append('        .invoke(packOutput, {i}, 0, aggregate_stream_kp0[{i}], packed_output_stm_kp0[{i}], NUM_LOADS_PER_STM)'.format(i=i) + "\n")
        codeArr.append('' + "\n")

        for i in range(0, self.config.num_stm):
            codeArr.append('        .invoke(packOutput, {i}, 1, aggregate_stream_kp1[{i}], packed_output_stm_kp1[{i}], NUM_LOADS_PER_STM)'.format(i=i) + "\n")
        codeArr.append('' + "\n")

        codeArr.append('        WRITEOUT_INVOKES' + "\n")
        #codeArr.append('        .invoke(writeOutput_synchronous' + "\n")
        #for i in range(0, self.config.num_stm):
        #    codeArr.append('                ,packed_output_stm_kp0[{i}]'.format(i=i) + "\n")
        #    codeArr.append('                ,packed_output_stm_kp1[{i}]'.format(i=i) + "\n")
        #codeArr.append('                ,out_bits)' + "\n")
        #codeArr.append('' + "\n")
        codeArr.append('' + "\n")

        codeArr.append("\n\n")
        return codeArr


    def generate_perfctr_invokes(self):
        codeArr = []
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        .invoke(write_perfctrs, perfctr_stms, perfctr_mmap)' + "\n")
        codeArr.append('        #endif' + "\n")
        codeArr.append("\n\n")
        return codeArr




    def generate_invokes(self):
        codeArr = []
        codeArr.append('    //////////////////////////////////////////////////////////' + "\n")
        codeArr.append('    // MODULE INVOCATIONS.' + "\n")
        codeArr.append('    tapa::task()' + "\n")

        codeArr.extend(self.generate_load_invokes())
        codeArr.extend(self.generate_compute_invokes())
        codeArr.extend(self.generate_arbiter_invokes())
        codeArr.extend(self.generate_query_invokes())
        codeArr.extend(self.generate_shuffle_invokes())
        codeArr.extend(self.generate_aggr_invokes())
        codeArr.extend(self.generate_writeOut_invokes())
        codeArr.extend(self.generate_perfctr_invokes())

        codeArr.append('    ;' + "\n")
        codeArr.append('    return;' + "\n")
        codeArr.append('}' + "\n")
        return codeArr






    def generate(self):
        codeArr = []
        codeArr.extend(self.generate_func_declaration())
        codeArr.append('{' + "\n")
        codeArr.extend(self.generate_intermodule_fifo_decls())
        codeArr.extend(self.generate_intramodule_fifo_decls())
        codeArr.extend(self.generate_invokes())
        return codeArr

























