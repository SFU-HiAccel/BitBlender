import os
from itertools import product

"""
THE purpose of this python script is to work with a shell script to run the sweep.
    This script generates a Bash script, which contains all of the config-strings
    to generate with generate_BVSharing_design.py.
"""

NUM_HASHES      = [3,4,5,6,7,8,9]
NUM_PARTITIONS  = [8]
NUM_STM         = [2,3,4,5,6,7,8]
SHUFBUF_SZ      = [16]
BV_LENS_IN_MEBI = [16]

config_script_name      = "designs_to_generate.sh"



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



def generate_file_contents(HTSBS):
    _lines_to_write = []
    
    _lines_to_write.append('#!/bin/bash' + "\n")
    _lines_to_write.append('' + "\n")
    _lines_to_write.append('HTSB_CONFIGS=(' + "\n")
    
    for cfg in HTSBS:
        _lines_to_write.append('    "{}"'.format(cfg) + "\n")

    _lines_to_write.append(')' + "\n")

    return _lines_to_write


def change_sweep_array_length(array_len):
    run_sweep_fname = "run_build_sweep.sh"

    if (os.path.exists(run_sweep_fname)):
        escaped_pyscript_name = __file__.replace("/", "\\/")
        sed_cmd = "sed -i 's/^#SBATCH --array=.*/#SBATCH --array=0-{arrlen}     ### THIS LINE IS AUTOMATICALLY CHANGED BY {this_python_script_name}/' {fname}".format(
                arrlen = array_len-1
                ,fname = run_sweep_fname
                ,this_python_script_name = escaped_pyscript_name
            )

        os.system(sed_cmd)

    else:
        raise FileNotFoundError(" '{fname}': file not found".format(run_sweep_fname))



if __name__ == "__main__":
    if not (NUM_HASHES and NUM_PARTITIONS and NUM_STM and SHUFBUF_SZ and BV_LENS_IN_MEBI):
        print("ERROR: Need nonempty config lists.")
        exit(-1)

    tmp_htsbs           = list(product(NUM_HASHES, NUM_PARTITIONS, NUM_STM, SHUFBUF_SZ, BV_LENS_IN_MEBI))
    HTSB_configs        = [ str(tmp_htsbs[i]) for i in range(0, len(tmp_htsbs)) ]

    #tmp_htsbs_1         = list(product(NUM_HASHES_1, NUM_PARTITIONS_1, NUM_STM_1, SHUFBUF_SZ_1, BV_LENS_IN_MEBI_1))
    #HTSB_configs_1      = [ str(tmp_htsbs_1[i]) for i in range(0, len(tmp_htsbs_1)) ]
    #HTSB_configs.extend(HTSB_configs_1)

    for i in range(0, len(HTSB_configs)):
        HTSB_configs[i] = HTSB_configs[i].strip(" ()")
        HTSB_configs[i] = HTSB_configs[i].replace(" ", "")
        HTSB_configs[i] = HTSB_configs[i].replace(",", "-")

    HTSB_configs    = prune_designs(HTSB_configs)
    file_contents   = generate_file_contents(HTSB_configs)

    with open(config_script_name, 'w') as f:
        f.writelines(file_contents)

    change_sweep_array_length( len(HTSB_configs) )














