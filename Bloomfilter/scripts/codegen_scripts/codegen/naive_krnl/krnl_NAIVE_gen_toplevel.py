

class TopLevelCodeGenerator:
    def __init__(self, config):
        self.config = config


    def generate_func_declaration(self):
        codeArr = []
        codeArr.append('void workload(' + "\n")

        for s in range(0, self.config.num_stm):
            if (s == 0):
                maybe_comma = ""
            else:
                maybe_comma = ","
            codeArr.append('     {comma}tapa::mmap<BV_LOAD_DTYPE>   input_bv_{s}'.format(s=s, comma=maybe_comma) + "\n")

        for s in range(0, self.config.num_stm):
            codeArr.append('    ,tapa::mmap<TWOKEY_DTYPE>       key{s}'.format(s=s) + "\n")
            codeArr.append('    ,tapa::mmap<OUT_PACKED_DTYPE>   out{s}'.format(s=s) + "\n")

        codeArr.append('' + "\n")
        codeArr.append('    #if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    ,tapa::mmap<PERFCTR_DTYPE>       perfctr_mmap' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    ,int UNUSED_DUMMY' + "\n")
        codeArr.append(')' + "\n")
        return codeArr




    def generate_invokes(self):
        codeArr = []

        for s in range(0, self.config.num_stm):
            codeArr.append('    DECLARE_STREAMS_FOR_PE({s})'.format(s=s) + "\n")

        codeArr.append('    tapa::task()' + "\n")
        for s in range(0, self.config.num_stm):
            codeArr.append('        INVOKES_FOR_PE({s})'.format(s=s) + "\n")
        codeArr.append('    ;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    return;' + "\n")
        codeArr.append('}' + "\n")
        codeArr.append("\n\n\n")

        return codeArr





    def generate(self):
        codeArr = []
        codeArr.extend(self.generate_func_declaration())
        codeArr.append('{' + "\n")
        codeArr.extend(self.generate_invokes())
        codeArr.append("\n\n/*************************************************************************************/\n\n")
        return codeArr
