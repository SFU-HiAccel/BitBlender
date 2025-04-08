import os
from itertools import product
from argparse import ArgumentParser

"""
THE purpose of this python script is to work with a shell script to run the sweep.
    This script generates a Bash script, which contains all of the HTSB_config-strings
    to generate with generate_BVSharing_design.py.
"""

ARB_FREQ_ABLATION = [
     "3-4-3-16-8_n0",
     "3-4-3-16-8_n1",
     "5-6-5-16-8_n0",
     "5-6-5-16-8_n1",
     "7-8-8-16-8_n0",
     "7-8-8-16-8_n1",
]



NAIVE_SWEEP = [
    #############################
    #### 1e-5 FPRATES:
    # 4 M inserts, 1e-5 fprate  (2/3 streams)
    "17-5-2-0-5_n0",
    "17-5-3-0-5_n0",
    # 6 M inserts, 1e-5 fprate  (1/2 streams)
    "17-5-1-0-8_n0",
    "17-5-2-0-8_n0",
    # 8 M inserts, 1e-5 fprate  (1 stream)
    "17-5-1-0-11_n0",
    # 10M inserts, 1e-5 fprate  (1 stream)
    "17-5-1-0-13_n0",
    # 11M inserts, 1e-5 fprate  (1 stream)
    "17-5-1-0-15_n0",


    #############################
    #### 2e-5 FPRATES:
    # 4 M inserts, 2e-5 fprate  (2/3 streams)
    "16-5-2-0-5_n0",
    "16-5-3-0-5_n0",
    # 6 M inserts, 2e-5 fprate  (1/2 streams)
    "16-5-1-0-8_n0",
    "16-5-2-0-8_n0",
    # 8 M inserts, 2e-5 fprate  (1 stream)
    "16-5-1-0-11_n0",
    # 10M inserts, 2e-5 fprate  (1 stream)
    "16-5-1-0-13_n0",

    #############################
    #### 5e-5 FPRATES:
    # 4 M inserts, 5e-5 fprate  (2/3 streams)
    "14-5-2-0-6_n0",
    "14-5-3-0-6_n0",
    # 6 M inserts, 5e-5 fprate  (1/2 streams)
    "14-5-1-0-8_n0",
    "14-5-2-0-8_n0",
    # 8 M inserts, 5e-5 fprate  (1 stream)
    "14-5-1-0-11_n0",
    # 10M inserts, 5e-5 fprate  (1 stream)
    "14-5-1-0-14_n0",
    # 12M inserts, 5e-5 fprate  (1 stream)
    "14-5-1-0-17_n0",

    #############################
    #### 1e-4 FPRATES:
    # 4 M inserts, 1e-4 fprate  (2/3 streams)
    "13-5-2-0-6_n0",
    "13-5-3-0-6_n0",
    # 6 M inserts, 1e-4 fprate  (1/2 streams)
    "13-5-1-0-8_n0",
    "13-5-2-0-8_n0",
    # 8 M inserts, 1e-4 fprate  (1/2 streams)
    "13-5-1-0-11_n0",
    "13-5-2-0-11_n0",
    # 10M inserts, 1e-4 fprate  (1 stream)
    "13-5-1-0-14_n0",

    #############################
    #### 2e-4 FPRATES:
    # 6 M inserts, 2e-4 fprate  (2/3 streams)
    "12-5-2-0-8_n0",
    "12-5-3-0-8_n0",
    # 8 M inserts, 2e-4 fprate  (1/2 streams)
    "12-5-1-0-11_n0",
    "12-5-2-0-11_n0",
    # 10M inserts, 2e-4 fprate  (1 stream)
    "12-5-1-0-14_n0",
    # 12M inserts, 2e-4 fprate  (1 stream)
    "12-5-1-0-17_n0",
    # 13M inserts, 2e-4 fprate  (1 stream)
    "12-5-1-0-18_n0",
    # 14M inserts, 2e-4 fprate  (1 stream)
    "12-5-1-0-20_n0",
]



### NUM_PART_SWEEP_CONFIGS = [
###     "3-4-8-16-16_n0",
###     "3-5-8-16-16_n0",
###     "3-6-8-16-16_n0",
###     "3-7-8-16-16_n0",
###     "3-8-8-16-16_n0",
###     "3-9-8-16-16_n0",
###     "3-10-8-16-16_n0",
###     "3-11-8-16-16_n0",
###     "3-12-8-16-16_n0",
### 
###     "4-4-8-16-16_n0",
###     "4-5-8-16-16_n0",
###     "4-6-8-16-16_n0",
###     "4-7-8-16-16_n0",
###     "4-8-8-16-16_n0",
###     "4-9-8-16-16_n0",
###     "4-10-8-16-16_n0",
###     "4-11-8-16-16_n0",
###     "4-12-8-16-16_n0",
### 
###     "5-4-8-16-16_n0",
###     "5-5-8-16-16_n0",
###     "5-6-8-16-16_n0",
###     "5-7-8-16-16_n0",
###     "5-8-8-16-16_n0",
###     "5-9-8-16-16_n0",
###     "5-10-8-16-16_n0",
###     "5-11-8-16-16_n0",
###     "5-12-8-16-16_n0",
### 
###     "6-4-8-16-16_n0",
###     "6-5-8-16-16_n0",
###     "6-6-8-16-16_n0",
###     "6-7-8-16-16_n0",
###     "6-8-8-16-16_n0",
###     "6-9-8-16-16_n0",
###     "6-10-8-16-16_n0",
###     "6-11-8-16-16_n0",
###     "6-12-8-16-16_n0",
### 
###     "7-4-8-16-16_n0",
###     "7-5-8-16-16_n0",
###     "7-6-8-16-16_n0",
###     "7-7-8-16-16_n0",
###     "7-8-8-16-16_n0",
###     "7-9-8-16-16_n0",
###     "7-10-8-16-16_n0",
###     "7-11-8-16-16_n0",
###     "7-12-8-16-16_n0",
### 
###     "8-4-8-16-16_n0",
###     "8-5-8-16-16_n0",
###     "8-6-8-16-16_n0",
###     "8-7-8-16-16_n0",
###     "8-8-8-16-16_n0",
###     "8-9-8-16-16_n0",
###     "8-10-8-16-16_n0",
###     "8-11-8-16-16_n0",
###     "8-12-8-16-16_n0",
### 
###     "9-4-8-16-16_n0",
###     "9-5-8-16-16_n0",
###     "9-6-8-16-16_n0",
###     "9-7-8-16-16_n0",
###     "9-8-8-16-16_n0",
###     "9-9-8-16-16_n0",
###     "9-10-8-16-16_n0",
###     "9-11-8-16-16_n0",
###     "9-12-8-16-16_n0",
### 
###     "10-4-8-16-16_n0",
###     "10-5-8-16-16_n0",
###     "10-6-8-16-16_n0",
###     "10-7-8-16-16_n0",
###     "10-8-8-16-16_n0",
###     "10-9-8-16-16_n0",
###     "10-10-8-16-16_n0",
###     "10-11-8-16-16_n0",
###     "10-12-8-16-16_n0",
### 
###     "11-4-8-16-16_n0",
###     "11-5-8-16-16_n0",
###     "11-6-8-16-16_n0",
###     "11-7-8-16-16_n0",
###     "11-8-8-16-16_n0",
###     "11-9-8-16-16_n0",
###     "11-10-8-16-16_n0",
###     "11-11-8-16-16_n0",
###     "11-12-8-16-16_n0",
### ]
### 
### NUM_STM_SWEEP_CONFIGS = [
###     "3-9-2-16-16_n0",
###     "3-9-3-16-16_n0",
###     "3-9-4-16-16_n0",
###     "3-9-5-16-16_n0",
###     "3-9-6-16-16_n0",
###     "3-9-7-16-16_n0",
###     "3-9-8-16-16_n0",
###     "3-9-9-16-16_n0",
### 
###     "4-9-2-16-16_n0",
###     "4-9-3-16-16_n0",
###     "4-9-4-16-16_n0",
###     "4-9-5-16-16_n0",
###     "4-9-6-16-16_n0",
###     "4-9-7-16-16_n0",
###     "4-9-8-16-16_n0",
###     "4-9-9-16-16_n0",
### 
###     "5-9-2-16-16_n0",
###     "5-9-3-16-16_n0",
###     "5-9-4-16-16_n0",
###     "5-9-5-16-16_n0",
###     "5-9-6-16-16_n0",
###     "5-9-7-16-16_n0",
###     "5-9-8-16-16_n0",
###     "5-9-9-16-16_n0",
### 
###     "6-9-2-16-16_n0",
###     "6-9-3-16-16_n0",
###     "6-9-4-16-16_n0",
###     "6-9-5-16-16_n0",
###     "6-9-6-16-16_n0",
###     "6-9-7-16-16_n0",
###     "6-9-8-16-16_n0",
###     "6-9-9-16-16_n0",
### 
###     "7-9-2-16-16_n0",
###     "7-9-3-16-16_n0",
###     "7-9-4-16-16_n0",
###     "7-9-5-16-16_n0",
###     "7-9-6-16-16_n0",
###     "7-9-7-16-16_n0",
###     "7-9-8-16-16_n0",
###     "7-9-9-16-16_n0",
### 
###     "8-9-2-16-16_n0",
###     "8-9-3-16-16_n0",
###     "8-9-4-16-16_n0",
###     "8-9-5-16-16_n0",
###     "8-9-6-16-16_n0",
###     "8-9-7-16-16_n0",
###     "8-9-8-16-16_n0",
###     "8-9-9-16-16_n0",
### 
###     "9-9-2-16-16_n0",
###     "9-9-3-16-16_n0",
###     "9-9-4-16-16_n0",
###     "9-9-5-16-16_n0",
###     "9-9-6-16-16_n0",
###     "9-9-7-16-16_n0",
###     "9-9-8-16-16_n0",
###     "9-9-9-16-16_n0",
### 
###     "10-9-2-16-16_n0",
###     "10-9-3-16-16_n0",
###     "10-9-4-16-16_n0",
###     "10-9-5-16-16_n0",
###     "10-9-6-16-16_n0",
###     "10-9-7-16-16_n0",
###     "10-9-8-16-16_n0",
###     "10-9-9-16-16_n0",
### 
###     "11-9-2-16-16_n0",
###     "11-9-3-16-16_n0",
###     "11-9-4-16-16_n0",
###     "11-9-5-16-16_n0",
###     "11-9-6-16-16_n0",
###     "11-9-7-16-16_n0",
###     "11-9-8-16-16_n0",
###     "11-9-9-16-16_n0",
### 
### ]
### 
### RLDIST_SWEEP_CONFIGS = [
###     "3-9-8-2-16_n0",
###     "3-9-8-4-16_n0",
###     "3-9-8-8-16_n0",
###     "3-9-8-16-16_n0",
### 
###     "4-9-8-2-16_n0",
###     "4-9-8-4-16_n0",
###     "4-9-8-8-16_n0",
###     "4-9-8-16-16_n0",
### 
###     "5-9-8-2-16_n0",
###     "5-9-8-4-16_n0",
###     "5-9-8-8-16_n0",
###     "5-9-8-16-16_n0",
### 
###     "6-9-8-2-16_n0",
###     "6-9-8-4-16_n0",
###     "6-9-8-8-16_n0",
###     "6-9-8-16-16_n0",
### 
###     "7-9-8-2-16_n0",
###     "7-9-8-4-16_n0",
###     "7-9-8-8-16_n0",
###     "7-9-8-16-16_n0",
### 
###     "8-9-8-2-16_n0",
###     "8-9-8-4-16_n0",
###     "8-9-8-8-16_n0",
###     "8-9-8-16-16_n0",
### 
###     "9-9-8-2-16_n0",
###     "9-9-8-4-16_n0",
###     "9-9-8-8-16_n0",
###     "9-9-8-16-16_n0",
### 
###     "10-9-8-2-16_n0",
###     "10-9-8-4-16_n0",
###     "10-9-8-8-16_n0",
###     "10-9-8-16-16_n0",
### 
###     "11-9-8-2-16_n0",
###     "11-9-8-4-16_n0",
###     "11-9-8-8-16_n0",
###     "11-9-8-16-16_n0",
### 
### ]
### 
### BVLEN_SWEEP_CONFIGS = [
###     "3-9-8-16-12_n0",
###     "3-9-8-16-16_n0",
###     "3-9-8-16-20_n0",
###     "3-9-8-16-24_n0",
### 
###     "4-9-8-16-12_n0",
###     "4-9-8-16-16_n0",
###     "4-9-8-16-20_n0",
###     "4-9-8-16-24_n0",
### 
###     "5-9-8-16-12_n0",
###     "5-9-8-16-16_n0",
###     "5-9-8-16-20_n0",
###     "5-9-8-16-24_n0",
### 
###     "6-9-8-16-12_n0",
###     "6-9-8-16-16_n0",
###     "6-9-8-16-20_n0",
###     "6-9-8-16-24_n0",
### 
###     "7-9-8-16-12_n0",
###     "7-9-8-16-16_n0",
###     "7-9-8-16-20_n0",
###     "7-9-8-16-24_n0",
### 
###     "8-9-8-16-12_n0",
###     "8-9-8-16-16_n0",
###     "8-9-8-16-20_n0",
###     "8-9-8-16-24_n0",
### 
###     "9-9-8-16-12_n0",
###     "9-9-8-16-16_n0",
###     "9-9-8-16-20_n0",
###     "9-9-8-16-24_n0",
### 
###     "10-9-8-16-12_n0",
###     "10-9-8-16-16_n0",
###     "10-9-8-16-20_n0",
###     "10-9-8-16-24_n0",
### 
###     "11-9-8-16-12_n0",
###     "11-9-8-16-16_n0",
###     "11-9-8-16-20_n0",
###     "11-9-8-16-24_n0",
### 
### ]







### NUM_HASHES      = [6]
### NUM_PARTITIONS  = [8,9]
### NUM_STM         = [6,8,9]
### SHUFBUF_SZ      = [16]
### BV_LENS_IN_MEBI = [16,20]
### 
### NUM_HASHES_1      = [8]
### NUM_PARTITIONS_1  = [7,8,9]
### NUM_STM_1         = [6,7,8,9]
### SHUFBUF_SZ_1      = [16]
### BV_LENS_IN_MEBI_1 = [10,16]


htsb_cfg_script_name    = "designs_to_generate.sh"




class SweepGen_Config:
    def __init__(   self
                    ,_design_type
                    ,_enable_aurora
                    ,_vivado_version
    ):
        self.design_type    = _design_type
        self.enable_aurora  = _enable_aurora
        self.vivado_version = _vivado_version





def prune_designs(HTSBS):
    pruned_HTSBS = []

    for i in range(0, len(HTSBS)):
        tmp = HTSBS[i].split("-")
        cur_htsb = [int(tmp[i]) for i in range(0, len(tmp))]

        ## If S > T+1 then don't use it
        if (cur_htsb[2] > cur_htsb[1]+1):
            pass
        else:
            pruned_HTSBS.append(HTSBS[i])

    return pruned_HTSBS



def generate_file_contents(config, HTSBS):
    _lines_to_write = []

    if (config.enable_aurora):
        enable_aurora_string = "enabled"
        host_exe_name = "host_QSFP_aurora"
    else:
        enable_aurora_string = "disabled"
        host_exe_name = "host_HBM"

    _lines_to_write.append('#!/bin/bash' + "\n")
    _lines_to_write.append('' + "\n")
    _lines_to_write.append('AURORA_ENABLED_STRING={}'.format(enable_aurora_string) + "\n")
    _lines_to_write.append('HOST_EXE_NAME={}'.format(host_exe_name) + "\n")
    _lines_to_write.append('VIVADO_VERSION={}'.format(config.vivado_version) + "\n")
    _lines_to_write.append('CODEGEN_DESIGN_TYPE={}'.format(config.design_type) + "\n")
    _lines_to_write.append('' + "\n")
    _lines_to_write.append('HTSB_CONFIGS=(' + "\n")
    
    for htsb_cfg in HTSBS:
        _lines_to_write.append('    "{}"'.format(htsb_cfg) + "\n")

    _lines_to_write.append(')' + "\n")

    return _lines_to_write




def change_sweep_array_length(array_len):
    run_sweep_fname = "run_build_sweep.sh"

    if (os.path.exists(run_sweep_fname)):
        escaped_pyscript_name = __file__.replace("/", "\\/")
        sed_cmd = "sed -i 's/^#SBATCH --array=.*/#SBATCH --array=0-{arrlen}     ### DO NOT MODIFY: THIS LINE IS AUTOMATICALLY CHANGED BY {this_python_script_name}/' {fname}".format(
                arrlen = array_len-1
                ,fname = run_sweep_fname
                ,this_python_script_name = escaped_pyscript_name
            )

        os.system(sed_cmd)

    else:
        raise FileNotFoundError(" '{fname}': file not found".format(run_sweep_fname))






def ReadArguments():
    parser = ArgumentParser()
    parser.add_argument("--num_build_copies_per_cfg", dest="num_build_copies"
                        ,help="How many COPIES of each config do we want to build. I.e. we're just building the same exact configs multiple times."
                        ,required=False
    )
    parser.add_argument("-a", "--enable_aurora", dest="enable_aurora"
                        ,help="Whether or not to use the Aurora core, to utilize QSFP connections."
                        ,required=True
    )
    parser.add_argument("-dt", "--design_type", dest="design_type"
                        ,help="The design type: either 'bitblender', or 'naive' (for naive-multistream). For singlestream, please use naive-multistream with 1 stream."
                        ,required=True
    )
    parser.add_argument("-vv", "--vivado_version", dest="vivado_version"
                        ,help="Which version of the Vivado/Vitis toolchain are you using? Must be specified in the format of '2021.2'."
                        ,required=True
    )
    args = parser.parse_args()

    design_type     = args.design_type.lower()
    vivado_version  = args.vivado_version
    enable_aurora   = int(args.enable_aurora)

    if (args.num_build_copies):
        num_build_copies = int(args.num_build_copies)
    else:
        num_build_copies = 1

    return (design_type, vivado_version, enable_aurora, num_build_copies)










if __name__ == "__main__":
    (design_type, vivado_version, enable_aurora, num_build_copies) = ReadArguments()
    build_copies_strs = [ "_n{}".format(copyidx) for copyidx in range(0, num_build_copies) ]

    config = SweepGen_Config(design_type, enable_aurora, vivado_version)

    # if not (NUM_HASHES and NUM_PARTITIONS and NUM_STM and SHUFBUF_SZ and BV_LENS_IN_MEBI):
    #     print("ERROR: Need nonempty HTSB_config lists.")
    #     exit(-1)

    # tmp_htsbs           = list(product(NUM_HASHES, NUM_PARTITIONS, NUM_STM, SHUFBUF_SZ, BV_LENS_IN_MEBI))
    # HTSB_configs        = [ str(tmp_htsbs[i]) for i in range(0, len(tmp_htsbs)) ]

    # tmp_htsbs_1         = list(product(NUM_HASHES_1, NUM_PARTITIONS_1, NUM_STM_1, SHUFBUF_SZ_1, BV_LENS_IN_MEBI_1))
    # HTSB_configs_1      = [ str(tmp_htsbs_1[i]) for i in range(0, len(tmp_htsbs_1)) ]
    # HTSB_configs.extend(HTSB_configs_1)

    # for i in range(0, len(HTSB_configs)):
    #     HTSB_configs[i] = HTSB_configs[i].strip(" ()")
    #     HTSB_configs[i] = HTSB_configs[i].replace(" ", "")
    #     HTSB_configs[i] = HTSB_configs[i].replace(",", "-")

    # HTSB_configs    = prune_designs(HTSB_configs)

    # tmp_htsbs       = list(product(HTSB_configs, build_copies_strs))
    # tmp_htsbs    = [ str(tmp_htsbs[i]) for i in range(0, len(tmp_htsbs)) ]
    # for i in range(0, len(tmp_htsbs)):
    #     tmp_htsbs[i] = tmp_htsbs[i].strip(" ()")
    #     tmp_htsbs[i] = tmp_htsbs[i].replace(" ", "")
    #     tmp_htsbs[i] = tmp_htsbs[i].replace("'", "")
    #     tmp_htsbs[i] = tmp_htsbs[i].replace(",", "")

    ########## OR:

    #HTSB_configs    = __EXPLICIT_HTSB_CONFIGS
    HTSB_configs = NAIVE_SWEEP

    file_contents   = generate_file_contents(config, HTSB_configs)

    with open(htsb_cfg_script_name, 'w') as f:
        f.writelines(file_contents)

    change_sweep_array_length( len(HTSB_configs) )














