
from .types import DesignType 

class IniCodeGenerator:
    def __init__(self, config):
        self.config = config


    def generate_naive_inifile(self):
        codeArr = []
        used_ports = 0

        codeArr.append('[connectivity]' + "\n")

        for i in range(0, self.config.num_stm):
            codeArr.append('sp=workload.input_bv_{i}:HBM[{p}]'.format(i=i, p=used_ports) + "\n")
            used_ports += 1
        codeArr.append('' + "\n")

        for i in range(0, self.config.num_stm):
            codeArr.append('sp=workload.key{i}:HBM[{p}]'.format(i=i, p=used_ports) + "\n")
            used_ports += 1
        codeArr.append('' + "\n")

        for i in range(0, self.config.num_stm):
            codeArr.append('sp=workload.out{i}:HBM[{p}]'.format(i=i, p=used_ports) + "\n")
            used_ports += 1

        codeArr.append('' + "\n")
        codeArr.append('#sp=workload.perfctr_mmap:HBM[{p}'.format(p=used_ports) + "\n")
        return codeArr
    

    def generate_normal_inifile(self):
        codeArr = []
        used_ports = 0

        codeArr.append('[connectivity]' + "\n")
        codeArr.append('sp=workload.input_bv:HBM[{}]'.format(used_ports) + "\n")
        used_ports += 1

        codeArr.append('sp=workload.key_in:HBM[{p}]'.format(p=used_ports) + "\n")
        used_ports += 1
        codeArr.append('sp=workload.out_bits:HBM[{p}]'.format(p=used_ports) + "\n")
        used_ports += 1
        codeArr.append('' + "\n")

        codeArr.append('#sp=workload.perfctr_mmap:HBM[{p}]'.format(p=used_ports) + "\n")
        return codeArr


    def generate(self):
        codeArr = []
        
        if (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            codeArr.extend(self.generate_naive_inifile())

        else:
            codeArr.extend(self.generate_normal_inifile())

        return codeArr






























