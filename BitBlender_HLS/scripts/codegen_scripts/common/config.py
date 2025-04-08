

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
                    ,_vivado_year
                    ,_fpga_name
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


        self.vivado_year            = _vivado_year
        self.fpga_name              = _fpga_name

        ########################
        #### COMPUTED PARAMETERS
        ########################
        self.enable_perfctrs        = 0
        self.num_arb_atoms          = self.num_stm - 1

        ### The pack factor means the number of streams in each AXI port. Cap out at 512 bits per AXI.
        ### We need this because the AXI bitwidths must be in the set {32, 64, 128, 256, 512, 1024}.
        self.keys_axi_port_pack_factor       = 2**((self.num_stm-1).bit_length())
        if (self.keys_axi_port_pack_factor > 8):
            ### Currently each stream is (2*32) = (num_bram_ports * key_bitwidth).
            self.keys_axi_port_pack_factor   = 8

        if (self.num_stm > 8):
            raise ValueError("Need to add support for NUM_STM>8 in the input-port datapacking.")

        if (self.vivado_year >= 2022) and (self.fpga_name == "U50"):
            self.device_name = "xilinx_u50_gen3x16_xdma_5_202210_1"
        elif (self.vivado_year >= 2022) and (self.fpga_name == "U280"):
            self.device_name = "xilinx_u280_gen3x16_xdma_1_202211_1"
        elif (self.vivado_year < 2022) and (self.fpga_name == "U280"):
            self.device_name = "xilinx_u280_xdma_201920_3"
        else:
            raise ValueError("(FPGA name, vivado year) combination not currently supported.")

 
