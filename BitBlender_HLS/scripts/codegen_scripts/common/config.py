import math


class Config:
    def __init__(   self
                    ,_design_type
                    ,_BV_LEN_PER_HASH
                    ,_INSERTS_PER_STM
                    ,_INPUT_QUERIES_PER_STM
                    ,_NUM_STM
                    ,_NUM_HASH
                    ,_NUM_BV_PARTITIONS
                    ,_SHUFFLEBUF_SZ
                    ,_arbiter_type
                    ,_shuffle_type
                    ,_enable_arbiter_sink
                    ,_vivado_version
                    ,_fpga_name
                    ,_target_freq_mhz
    ):
        self.design_type            = _design_type

        self.Mibv_len_per_hash      = _BV_LEN_PER_HASH
        ### Round up to the nearest power of 2 (https://stackoverflow.com/questions/14267555/find-the-smallest-power-of-2-greater-than-or-equal-to-n-in-python).
        self.Miqueries_per_stm      = 2**((_INPUT_QUERIES_PER_STM-1).bit_length())
        self.Kiinserts_per_stm      = 2**((_INSERTS_PER_STM-1).bit_length())

        self.num_stm                = _NUM_STM
        self.num_hash               = _NUM_HASH
        self.num_partitions         = _NUM_BV_PARTITIONS
        self.shufflebuf_sz          = _SHUFFLEBUF_SZ

        self.arbiter_type           = _arbiter_type

        self.shuffle_type           = _shuffle_type
        self.enable_arbiter_sink    = _enable_arbiter_sink


        self.vivado_version         = _vivado_version       ### Of the format "2021.2".
        self.fpga_name              = _fpga_name
        self.target_freq_mhz        = _target_freq_mhz

        self.enable_perfctrs        = 0

        ########################
        #### NON-INPUT PARAMETERS
        ########################
        self.enable_perf_ctrs       = 1

        self.num_arb_atoms          = self.num_stm - 1

        self.target_clkT_ns         = round(1000*(1/self.target_freq_mhz), 2)   ## Rounded to 2 decimal places

        self.vivado_year            = int(self.vivado_version.split(".")[0])

        ### The pack factor means the number of streams in each AXI port. Cap out at 512 bits per AXI.
        ### We need this because the AXI bitwidths must be in the set {32, 64, 128, 256, 512, 1024}.
        self.KEYS_MAX_AXI_PACK_FACTOR = 8
        self.keys_num_axi_ports = math.ceil( self.num_stm / self.KEYS_MAX_AXI_PACK_FACTOR )

        ### Mod, but from [1, MAX] instead of [0, MAX-1].
        self.keys_num_remainder_stm = self.num_stm % self.KEYS_MAX_AXI_PACK_FACTOR
        if (self.keys_num_remainder_stm == 0):
            self.keys_num_remainder_stm = self.KEYS_MAX_AXI_PACK_FACTOR

        if (self.keys_num_remainder_stm < 0):
            raise ValueError("LOGIC ERROR")

        if (self.vivado_year != 2021 and self.vivado_year != 2022):
            raise ValueError("The requested vivado-year is not tested.")


        #### Set the device name:
        self.device_name = None
        if (self.fpga_name == "U50"):
            if (self.vivado_year >= 2022):
                self.device_name = "xilinx_u50_gen3x16_xdma_5_202210_1"

        elif (self.fpga_name == "U280"):
            if (self.vivado_year >= 2022):
                self.device_name = "xilinx_u280_gen3x16_xdma_1_202211_1"
            else:
                self.device_name = "xilinx_u280_xdma_201920_3"

        if (self.device_name is None):
            raise ValueError("(FPGA name, vivado year) combination not currently supported.")

        print("DEVICE name is set to: {}".format(self.device_name))
 
