import os
from argparse import ArgumentParser

from codegen.normal_krnl.krnl_gen_includes  import IncludesCodeGenerator as NORMAL_IncludesCodeGenerator
from codegen.normal_krnl.krnl_gen_loadbv    import LoadBVCodeGenerator as NORMAL_LoadBVCodeGenerator
from codegen.normal_krnl.krnl_gen_loadkey   import LoadKeyCodeGenerator as NORMAL_LoadKeyCodeGenerator
from codegen.normal_krnl.krnl_gen_compute   import ComputeCodeGenerator as NORMAL_ComputeCodeGenerator
from codegen.normal_krnl.krnl_gen_arb       import ArbCodeGenerator as NORMAL_ArbCodeGenerator
from codegen.normal_krnl.krnl_gen_query     import QueryCodeGenerator as NORMAL_QueryCodeGenerator
from codegen.normal_krnl.krnl_gen_shuffle   import ShuffleCodeGenerator as NORMAL_ShuffleCodeGenerator
from codegen.normal_krnl.krnl_gen_aggr      import AggrCodeGenerator as NORMAL_AggrCodeGenerator
from codegen.normal_krnl.krnl_gen_writeout  import WriteOutCodeGenerator as NORMAL_WriteOutCodeGenerator
from codegen.normal_krnl.krnl_gen_toplevel  import TopLevelCodeGenerator as NORMAL_TopLevelCodeGenerator

from codegen.naive_krnl.krnl_NAIVE_gen_toplevel import TopLevelCodeGenerator as NAIVE_TopLevelCodeGenerator
from codegen.naive_krnl.krnl_NAIVE_gen_modules import ModuleCodeGenerator as NAIVE_ModuleCodeGenerator

from codegen.gen_python_scripts     import PyScriptGenerator
from codegen.gen_hostcode           import HostCodeGenerator
from codegen.gen_sw_murmurhash      import SWMurmurHashGenerator
from codegen.gen_bitblender_header  import BitBlenderHeaderFileGenerator
from codegen.gen_inifile            import IniCodeGenerator
from codegen.gen_Makefile           import MakeFileGenerator

from common.config import Config
import codegen.types as Types


def generate_naive_krnl_file(config):
    naive_krnl_file_name    = "naive_multistream_Bloomfilter.cpp"
    modules                 = NAIVE_ModuleCodeGenerator(config)
    topLevel                = NAIVE_TopLevelCodeGenerator(config)

    with open(naive_krnl_file_name, 'w') as f:
        f.writelines(modules    .generate())
        f.writelines(topLevel   .generate())




def generate_normal_krnl_file(config):
    normal_krnl_file_name   = "multistream_BitBlender.cpp"
    includes_generator      = NORMAL_IncludesCodeGenerator(config)
    loadKey                 = NORMAL_LoadKeyCodeGenerator(config)
    loadBV                  = NORMAL_LoadBVCodeGenerator(config)
    compute                 = NORMAL_ComputeCodeGenerator(config)
    arbiter                 = NORMAL_ArbCodeGenerator(config)
    query                   = NORMAL_QueryCodeGenerator(config)
    shuffle                 = NORMAL_ShuffleCodeGenerator(config)
    aggregate               = NORMAL_AggrCodeGenerator(config)
    writeOut                = NORMAL_WriteOutCodeGenerator(config)
    topLevel                = NORMAL_TopLevelCodeGenerator(config)

    with open(normal_krnl_file_name, 'w') as f:
        f.writelines(includes_generator .generate())
        f.writelines(loadKey            .generate())
        f.writelines(loadBV             .generate())
        f.writelines(compute            .generate())
        f.writelines(arbiter            .generate())
        f.writelines(query              .generate())
        f.writelines(shuffle            .generate())
        f.writelines(aggregate          .generate())
        f.writelines(writeOut           .generate())
        f.writelines(topLevel           .generate())




def generate_bitblender_header_file(config):
    bb_header_file_name = "BitBlender.h"
    bb_header_file_generator = BitBlenderHeaderFileGenerator(config)

    with open(bb_header_file_name, 'w') as f:
        f.writelines(bb_header_file_generator.generate())






def generate_host_code(config):
    SW_Murmur_file_name = "SW_MurmurHash3.cpp"
    hostcode_generator = HostCodeGenerator(config)
    SW_Murmur_generator = SWMurmurHashGenerator(config)
    
    hostcode_generator.generate_all_host_files()

    with open(SW_Murmur_file_name, 'w') as f:
        f.writelines(SW_Murmur_generator.generate())





def generate_inifile(config):
    ini_file_name = "BitBlender.ini"
    ini_file_generator = IniCodeGenerator(config)

    with open(ini_file_name, 'w') as f:
        f.writelines(ini_file_generator.generate())





def generate_Makefile(config):
    make_file_name = "Makefile"
    makefile_generator = MakeFileGenerator(config)

    with open(make_file_name, 'w') as f:
        f.writelines(makefile_generator.generate())



def generate_python_scripts(config):
    debug_fname = "debug_reorder_prints.py"
    py_generator = PyScriptGenerator(config)
    with open(debug_fname, 'w') as f:
        f.writelines(py_generator.generate_debug_script())

    datacoll_fname = "collect_resource_usages.py"
    with open(datacoll_fname, 'w') as f:
        f.writelines(py_generator.generate_datacoll_script())

    ## rs_fname = "rapidstream_run.py"
    ## with open(rs_fname, 'w') as f:
    ##     f.writelines(py_generator.generate_rapidstream_script())




def generate_src_dir(config):
    if (config.design_type == Types.DesignType.NAIVE_MULTISTREAM):
        generate_naive_krnl_file(config)
    else:
        generate_normal_krnl_file(config)

    generate_inifile(config)
    generate_bitblender_header_file(config)
    generate_host_code(config)




"""
From https://stackoverflow.com/questions/57025836/how-to-check-if-a-given-number-is-a-power-of-two
"""
def is_power_of_two(n):
    if ( (n & (n-1) == 0) and n != 0 ):
        return 1
    else:
        return 0


def ReadArguments():
    parser = ArgumentParser()
    parser.add_argument("-htsb", "--num_hash", dest="htsb_config",
                        help="The (NUM_HASH/BV_NUM_PARTITIONS/NUM_STM/SHUFBUF_SZ/BV_LEN) config to generate, where values are separated by dashes. And the BV LEN is in Mebis (i.e. groups of 1024*1024)",
                        required=True
    )
    parser.add_argument("-dt", "--design_type", dest="design_type",
                        help="The design type: either 'bitblender', or 'naive' (for naive-multistream). For singlestream, please use naive-multistream with 1 stream.",
                        required=True
    )
    parser.add_argument("-vv", "--vivado_version", dest="vivado_version",
                        help="Which version of the Vivado/Vitis toolchain are you using? Must be 2021 or 2022",
                        required=True
    )
    parser.add_argument("-ni", "--Kiinserts_per_stm", dest="ni",
                        help="How many inserts per stream, in Kibis (i.e. in groups of 1024). E.g. specifying 4 will result in 4096.",
                        required=False,
                        default=128
    )
    parser.add_argument("-nq", "--Miqueries_per_stm", dest="nq",
                        help="How many queries per stream, in Mebis (i.e. in groups of 1024*1024). E.g. specifying 4 will result in 4194304.",
                        required=False,
                        default=8
    )
    args = parser.parse_args()

    htsb_split_uscore = args.htsb_config.split("_")

    if (len(htsb_split_uscore) == 2):
        build_copyidx = htsb_split_uscore[1]
        build_copyidx = build_copyidx.replace("n", "")
        build_copyidx = int(build_copyidx)
    else:
        build_copyidx = 0

    design_type = args.design_type.lower()
    split_config = htsb_split_uscore[0]
    split_config = split_config.split("-")
    if len(split_config) != 5:
        raise ValueError("There should be five config values, separated by '-'.")
    try:
        h   = int(split_config[0])
        t   = int(split_config[1])
        s   = int(split_config[2])
        b   = int(split_config[3])
        bv  = int(split_config[4])
        nq  = int(args.nq)
        ni  = int(args.ni)

        #if ((not is_power_of_two(t)) or (not is_power_of_two(b)) or (not is_power_of_two(bv))):
        #if ((not is_power_of_two(b))):
        #    raise ValueError("B must be a power of 2")

        if (not is_power_of_two(nq)) or (not is_power_of_two(ni)):
            raise ValueError("nq and ni must be a power of 2")

        if (nq > 16):
            raise ValueError("nq cant be higher than 16, otherwise we overflow on the input idx")

    except Exception as e:
        raise ValueError("All values must be integers")

    if (h <= 0 or t <= 0 or s <= 0 or b <= 0 or bv <= 0 or nq <= 0 or ni <= 0):
        if (design_type == "naive" and b <= 0):
            ### The naive design doesn't use b, so ignore that error.
            pass
        else:
            raise ValueError("All values must be positive")

    if (t != 5 and design_type == "naive"):
        raise ValueError("For a naive design, t should always be set to 5 to correctly split BRAM and URAM usage.")

    if (design_type == "bitblender"):
        design_type_to_generate = Types.DesignType.NORMAL_MULTISTREAM
    elif (design_type == "naive"):
        design_type_to_generate = Types.DesignType.NAIVE_MULTISTREAM
    else:
        raise ValueError("design_type must be one of 'bitblender' and 'naive'.")

    vivado_version = args.vivado_version

    return (h, t, s, b, bv, ni, nq, design_type_to_generate, vivado_version, build_copyidx)






if __name__ == "__main__":
    print("")

    (h, t, s, b, bv, ninsert, nquery,
        design_type_to_generate, vivado_version, build_copyidx) = ReadArguments()

    print("Generating a ({}-{}-{}-{}-{}_n{}) design...".format(h, t, s, b, bv, build_copyidx))
    print("With {}Mi bits per hash, {}ki inserts per stm, {}Mi queries per stm".format(bv, ninsert, nquery))

    fpga_name = "U280"

    config = Config(
                        _design_type            = design_type_to_generate

                        ,_BV_LEN_PER_HASH       = bv
                        ,_INSERTS_PER_STM       = ninsert
                        ,_INPUT_QUERIES_PER_STM = nquery

                        ,_NUM_HASH              = h
                        ,_NUM_BV_PARTITIONS     = t
                        ,_NUM_STM               = s
                        ,_SHUFFLEBUF_SZ         = b

                        #,_arbiter_type          = Types.ArbiterType.SINGLE_MONOLITHIC
                        #,_arbiter_type          = Types.ArbiterType.UNSEPARATED_MONOARB_PER_HASH
                        ,_arbiter_type          = Types.ArbiterType.SEPARATED_HIERARB_PER_HASH                 ### THIS IS THE BEST VERSION.
                        #,_arbiter_type          = Types.ArbiterType.SEPARATED_HIERARB_PER_HASH_SINGLECYCLE_EXIT_CHECK
                        #,_arbiter_type          = Types.ArbiterType.SEPARATED_MONOARB_PER_HASH
                        #,_arbiter_type          = crash_python

                        #,_shuffle_type          = Types.ShuffleType.SPLIT_MONOLITHIC
                        #,_shuffle_type          = Types.ShuffleType.SEPARATED_BUFFER_BASED
                        ,_shuffle_type          = Types.ShuffleType.SEPARATED_FIFO_BASED            ### THIS IS THE BEST VERSION.
                        #,_shuffle_type          = crash_python

                        ,_enable_arbiter_sink   = 0

                        ,_vivado_version        = vivado_version
                        ,_fpga_name             = fpga_name
                        ,_target_freq_mhz       = 225
    )

    print(" {func}: targeting Vitis/Vivado v{version}, and FPGA {fpga}".format(func=__name__, version=vivado_version, fpga=fpga_name))

    baseDir = os.getcwd()
    gen_design_dirname  = "{}-{}-{}-{}-{}_n{}".format(h,t,s,b,bv,build_copyidx)
    gen_design_dir      = os.path.join(baseDir, gen_design_dirname)
    gen_design_src_dir  = os.path.join(gen_design_dir, "src")
    os.mkdir(gen_design_dir)
    os.chdir(gen_design_dir)
    os.mkdir(gen_design_src_dir)

    os.chdir(gen_design_src_dir)
    generate_src_dir(config)

    os.chdir(gen_design_dir)
    generate_Makefile(config)
    generate_python_scripts(config)

    print("")






















