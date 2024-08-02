
from ..types import ArbiterType

class TopLevelCodeGenerator:
    def __init__(self, config):
        self.config = config




    def generate_func_declaration(self):
        codeArr = []
        codeArr.append('void workload(' + "\n")
        codeArr.append('    tapa::mmap<BV_LOAD_DTYPE>       input_bv' + "\n")

        codeArr.append('    ,tapa::mmap<LOAD_DTYPE>         key_in' + "\n")
        codeArr.append('    ,tapa::mmap<STORE_DTYPE>        out_bits' + "\n")

        codeArr.append('    #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('    , crash! //crash on purpose; we may need more streams.' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    ,tapa::mmap<PERFCTR_DTYPE>       perfctr_mmap' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('     //Add a dummy, useless variable because TAPA fast-cosim doesnt work without it.' + "\n")
        codeArr.append('    ,int UNUSED_DUMMY' + "\n")
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
            codeArr.append('    tapa::streams<HASHONLY_DTYPE, NUM_STM, STM_DEPTH> hash_stream_h{}_kp0;'.format(i) + "\n")
            codeArr.append('    tapa::streams<HASHONLY_DTYPE, NUM_STM, STM_DEPTH> hash_stream_h{}_kp1;'.format(i) + "\n")
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
        codeArr.append('    tapa::streams<PERFCTR_DTYPE, 1, NUM_PERFCTR_OUTPUTS>            perfctr_streams_loadBV;' + "\n")
        for i in range(0, self.config.num_partitions):
            codeArr.append('    tapa::streams<PERFCTR_DTYPE, NUM_ARBITER_ATOMS, NUM_PERFCTR_OUTPUTS>   perfctr_streams_ArbRateMon_{};'.format(i) + "\n")
        codeArr.append('        #if BV_NUM_PARTITIONS != {}'.format(self.config.num_partitions) + "\n")
        codeArr.append('        crash!' + "\n")
        codeArr.append('        #endif' + "\n")
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

        if (self.config.arbiter_type == ArbiterType.HIERARCHICAL):
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
        codeArr.append('' + "\n")
        codeArr.append('                #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('                ,perfctr_streams_loadBV' + "\n")
        codeArr.append('                #endif' + "\n")
        codeArr.append('        )' + "\n")

        codeArr.append('' + "\n")
        codeArr.append('        .invoke(loadKey, key_in, key_stream_kp0, key_stream_kp1)'.format(i=i) + "\n")
        codeArr.append('' + "\n")

        codeArr.append("\n\n")
        return codeArr





    def generate_compute_invokes(self):
        codeArr = []
        codeArr.append('        COMPUTEHASH_INVOKES_FOR_KP(0)' + "\n")
        codeArr.append('        COMPUTEHASH_INVOKES_FOR_KP(1)' + "\n")
        codeArr.append("\n\n")
        return codeArr


    def generate_monoarb_invokes(self):
        codeArr = []

        codeArr.append('        .invoke(bloom_monolithic_arbiter' + "\n")
        codeArr.append('                    , 0' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                    , hash_stream_h{}_kp0'.format(i) + "\n")
        codeArr.append('' + "\n")

        codeArr.append('                    //#if ENABLE_PERF_CTRS' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                    //, perfctr_streams_ArbRateMon_{}'.format(i) + "\n")
        codeArr.append('                    //#endif' + "\n")
        codeArr.append('' + "\n")

        for i in range(0, self.config.num_hash):
            codeArr.append('                    , bv_lookup_stream_h{}_kp0'.format(i) + "\n")
        codeArr.append('        )' + "\n")


        codeArr.append('        .invoke(bloom_monolithic_arbiter' + "\n")
        codeArr.append('                    , 1' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                    , hash_stream_h{}_kp1'.format(i) + "\n")
        codeArr.append('' + "\n")

        codeArr.append('                    //#if ENABLE_PERF_CTRS' + "\n")
        for i in range(0, self.config.num_hash):
            codeArr.append('                    //, perfctr_streams_ArbRateMon_{}'.format(i) + "\n")
        codeArr.append('                    //#endif' + "\n")
        codeArr.append('' + "\n")

        for i in range(0, self.config.num_hash):
            codeArr.append('                    , bv_lookup_stream_h{}_kp1'.format(i) + "\n")
        codeArr.append('        )' + "\n")

        return codeArr



    def generate_splitarb_invokes(self):
        codeArr = []
        codeArr.append('        SPLIT_MONOARB_INVOKES_FOR_KP(0)' + "\n")
        codeArr.append('        SPLIT_MONOARB_INVOKES_FOR_KP(1)' + "\n")
        codeArr.append("\n\n")
        return codeArr




    def generate_hierarb_invokes(self):
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
        if (self.config.arbiter_type == ArbiterType.HIERARCHICAL):
            codeArr.extend(self.generate_hierarb_invokes())

        elif (self.config.arbiter_type == ArbiterType.SPLIT_MONOLITHIC):
            codeArr.extend(self.generate_splitarb_invokes())

        elif (self.config.arbiter_type == ArbiterType.SINGLE_MONOLITHIC):
            codeArr.extend(self.generate_monoarb_invokes())

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
            codeArr.append('        .invoke(packOutput, {i}, 0, aggregate_stream_kp0[{i}], packed_output_stm_kp0[{i}])'.format(i=i) + "\n")
        codeArr.append('' + "\n")

        for i in range(0, self.config.num_stm):
            codeArr.append('        .invoke(packOutput, {i}, 1, aggregate_stream_kp1[{i}], packed_output_stm_kp1[{i}])'.format(i=i) + "\n")
        codeArr.append('' + "\n")

        codeArr.append('        .invoke(writeOutput_synchronous' + "\n")
        for i in range(0, self.config.num_stm):
            codeArr.append('                ,packed_output_stm_kp0[{i}]'.format(i=i) + "\n")
            codeArr.append('                ,packed_output_stm_kp1[{i}]'.format(i=i) + "\n")
        codeArr.append('                ,out_bits)' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")

        codeArr.append("\n\n")
        return codeArr


    def generate_perfctr_invokes(self):
        codeArr = []
        codeArr.append('        #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('        .invoke(write_perfctrs' + "\n")
        codeArr.append('            ,perfctr_streams_loadBV' + "\n")
        codeArr.append('            ,perfctr_streams_ArbRateMon_0' + "\n")
        codeArr.append('            ,perfctr_streams_ArbRateMon_1' + "\n")
        codeArr.append('            ,perfctr_streams_ArbRateMon_2' + "\n")
        codeArr.append('            ,perfctr_streams_ArbRateMon_3' + "\n")
        codeArr.append('            ,perfctr_streams_shuffle' + "\n")
        codeArr.append('            ,perfctr_mmap' + "\n")
        codeArr.append('        )' + "\n")
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

























