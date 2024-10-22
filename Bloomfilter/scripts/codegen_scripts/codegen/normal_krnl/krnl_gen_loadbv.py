

class LoadBVCodeGenerator:
    def __init__(self, config):
        self.config = config

    def generate(self):
        code = []
        code.append('void loadBV(' + "\n")
        code.append('    tapa::async_mmap<BV_LOAD_DTYPE>    & input_bv' + "\n")
        for i in range(self.config.num_hash):
            code.append('    ,tapa::ostream<BV_URAM_PACKED_DTYPE>    & bv_load_stream_{}'.format(i) + "\n")
        code.append('    #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        code.append('    ,crash,' + "\n")
        code.append('    #endif' + "\n")
        code.append('' + "\n")
        code.append('    #if ENABLE_PERF_CTRS' + "\n")
        code.append('    ,tapa::ostreams<PERFCTR_DTYPE, 1>                   & perfctr_out' + "\n")
        code.append('    #endif' + "\n")
        code.append('){' + "\n")
        code.append('' + "\n")
        code.append('    #if BV_LOAD_BITWIDTH > 1024' + "\n")
        code.append('    crash(); on purpose();' + "\n")
        code.append('    // We need more sophisticated loading logic. AXI bitwidth shouldnt be higher than 1024.' + "\n")
        code.append('    #endif' + "\n")
        code.append('' + "\n")
        code.append('    int section_idx = 0;' + "\n")
        code.append('    BV_LOAD_DTYPE  cur_bv_val;' + "\n")
        code.append('' + "\n")
        code.append('    #if ENABLE_PERF_CTRS' + "\n")
        code.append('    PERFCTR_DTYPE   load_cycles = 0;' + "\n")
        code.append('    #endif' + "\n")
        code.append('' + "\n")
        code.append('    for (int i_req = 0, i_resp = 0;' + "\n")
        code.append('            i_resp < BV_NUM_LOADS; )' + "\n")
        code.append('    {' + "\n")
        code.append('        #pragma HLS PIPELINE II=1' + "\n")
        code.append('' + "\n")
        code.append('        #if ENABLE_PERF_CTRS' + "\n")
        code.append('        load_cycles += 1;' + "\n")
        code.append('        #endif' + "\n")
        code.append('        ' + "\n")
        code.append('        if (i_req < BV_NUM_LOADS && input_bv.read_addr.try_write(i_req)) {' + "\n")
        code.append('            ++i_req;' + "\n")
        code.append('        }' + "\n")

        code.append('        if (!input_bv.read_data.empty()) {' + "\n")
        code.append('            cur_bv_val = input_bv.read_data.read(nullptr);' + "\n")
        code.append('' + "\n")

        for h in range(0, self.config.num_hash):
            code.append('            bv_load_stream_{h}.write(cur_bv_val.section{h});'.format(h=h) + "\n")

        code.append('            #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        code.append('            crash!!' + "\n")
        code.append('            #endif' + "\n")
        code.append('' + "\n")
        code.append('            #ifdef __DO_DEBUG_PRINTS__' + "\n")
        code.append('            for (int i = 0; i < BV_URAM_PACKED_BITWIDTH; ++i)' + "\n")
        code.append('            {' + "\n")
        code.append('                int total_idx = i_resp*BV_URAM_PACKED_BITWIDTH + i;' + "\n")
        code.append('                BIT_DTYPE cur_bit;' + "\n")
        code.append('                cur_bit.range(0,0) = cur_bv_val.section0.range(i, i);' + "\n")
        code.append('                printf("KDEBUG: LOADBV - The %dth packed BV value of section 0 is %d\\n",' + "\n")
        code.append('                        total_idx, cur_bit.to_int());' + "\n")
        code.append('            }' + "\n")
        code.append('            #endif' + "\n")
        code.append('' + "\n")
        code.append('            ++i_resp;' + "\n")
        code.append('        }' + "\n")


        code.append('    }' + "\n")
        code.append('' + "\n")
        code.append('    #if ENABLE_PERF_CTRS' + "\n")
        code.append('    WRITE_PERF_CTRS:' + "\n")
        code.append('    for (int i = 0; i < NUM_PERFCTR_OUTPUTS; ++i) {' + "\n")
        code.append('    #pragma HLS PIPELINE II=1' + "\n")
        code.append('        if (i == 0){' + "\n")
        code.append('            perfctr_out[0].write(load_cycles);' + "\n")
        code.append('        }' + "\n")
        code.append('        else{' + "\n")
        code.append('            perfctr_out[0].write(55555);' + "\n")
        code.append('        }' + "\n")
        code.append('    }' + "\n")
        code.append('    #endif  // ENABLE_PERF_CTRS' + "\n")
        code.append('' + "\n")
        code.append('    #ifdef __DO_DEBUG_PRINTS__' + "\n")
        code.append('    printf("\\n\\nLOADBV IS DONE NOW.\\n\\n");' + "\n")
        code.append('    #endif' + "\n")
        code.append('    return;' + "\n")
        code.append('}' + "\n")

        code.append("\n\n/*************************************************************************************/\n\n")
        return code
