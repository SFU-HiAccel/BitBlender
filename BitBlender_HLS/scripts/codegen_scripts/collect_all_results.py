import sys
import os
import re

import csv


FILENOTFOUND_RETVAL = " (The file did not exist)"
BUILDS_DIR = "BUILD_OUTPUTS"
ALL_RESULTS_CSV = "all_results.csv"



def get_freqs_and_resources():
    freqs_and_resources = [0] * 7
    results_fname = "RESOURCES_AND_IIs.log"
    try:
        res_file = open(results_fname, 'r')
        data_lines = res_file.readlines()

        for line in data_lines:
            if ("HBM" in line):
                if (FILENOTFOUND_RETVAL not in line):
                    freqs_and_resources[0] = int(line.split(":")[1].strip())
                else:
                    freqs_and_resources[0] = '-'
            elif ("Kern" in line):
                if (FILENOTFOUND_RETVAL not in line):
                    freqs_and_resources[1] = int(line.split(":")[1].strip())
                else:
                    freqs_and_resources[1] = '-'
            elif ("LUT" in line):
                if (FILENOTFOUND_RETVAL not in line):
                    freqs_and_resources[2] = float(line.split(":")[1].strip())/100
                else:
                    freqs_and_resources[2] = '-'
            elif ("FF" in line):
                if (FILENOTFOUND_RETVAL not in line):
                    freqs_and_resources[3] = float(line.split(":")[1].strip())/100
                else:
                    freqs_and_resources[3] = '-'
            elif ("BRAM" in line):
                if (FILENOTFOUND_RETVAL not in line):
                    freqs_and_resources[4] = float(line.split(":")[1].strip())/100
                else:
                    freqs_and_resources[4] = '-'
            elif ("URAM" in line):
                if (FILENOTFOUND_RETVAL not in line):
                    freqs_and_resources[5] = float(line.split(":")[1].strip())/100
                else:
                    freqs_and_resources[5] = '-'
            elif ("DSP" in line):
                if (FILENOTFOUND_RETVAL not in line):
                    freqs_and_resources[6] = float(line.split(":")[1].strip())/100
                else:
                    freqs_and_resources[6] = '-'

    except FileNotFoundError:
        freqs_and_resources = ['-'] * 7

    return freqs_and_resources



def _get_num_autobridge_slots():
    res_fname = "RESOURCES_AND_IIs.log"
    num_autobridge_slots = '-'
    try:
        res_file = open(res_fname, 'r')
        data_lines = res_file.readlines()

        for line in data_lines:
            if ("Number of slots" in line):
                if (FILENOTFOUND_RETVAL not in line):
                    num_autobridge_slots = int(line.split(":")[1].strip())
                else:
                    num_autobridge_slots = '-'
    except FileNotFoundError:
        num_autobridge_slots = '-'

    return num_autobridge_slots


def _analyze_one_slack_violation(lines):
    retval = ""
    source_not_in_kernel = 0

    for line in lines:
        if ("Source:" in line):
            try:
                to_append = line.split("workload_inner_0/")[1].strip()
                to_append = to_append.split("grp")[0].strip()
                retval += to_append
            except IndexError:
                ## Sometimes, the source isn't inside our kernel. So check the destination instead.
                source_not_in_kernel = 1

        if (source_not_in_kernel and "Destination:" in line):
            try:
                to_append = line.split("workload_inner_0/")[1].strip()
                to_append = to_append.split("grp")[0].strip()
                retval += to_append
            except IndexError:
                ## I don't know if this is possible yet. Let's not add 'support' for it, until we see it,
                ## so we might know what to do.
                raise IndexError

        if ("Logic Levels:" in line):
            to_append = line.split("Logic Levels:")[1].strip()
            to_append = to_append.split(" ")[0].strip()
            retval += " ... LL: {}".format(to_append)

    return retval



def get_freq_debug_info():
    NUM_FREQDEBUG_INFO_ENTRIES = 10
    NUM_ENTRIES = NUM_FREQDEBUG_INFO_ENTRIES + 1    ### +1 for the autobridge slots
    ret_arr = []
    freq_debug_info = ['-'] * NUM_FREQDEBUG_INFO_ENTRIES
    DEVICE_NAMES = ["xilinx_u280_xdma_201920_3", "xilinx_u280_gen3x16_xdma_1_202211_1"]
    hw_rpt_dirs = ["vitis_run_hw/workload_{}.temp/reports/link/imp/".format(devname) for devname in DEVICE_NAMES]
    timing_rptname_subset = "bb_locked_timing_summary_postroute_physopted.rpt"

    num_autobridge_slots = _get_num_autobridge_slots()
    ret_arr.append(num_autobridge_slots)

    ## THE STRUCTURE OF THIS FILE IS as follows:
    ### Sections are denoted by delimiters of the form:
    ###     --------------------
    ###     | Section name
    ###     | -----------
    ###     --------------------
    ### We want to find the section named "Timing Details".
    ### Within this section, we want to find the clock report for clock
    ###    "clk_kernel_00_unbuffered_net", or "clkwiz_kernel".
    ### Then, we want to find info from each "Max Delay Paths".

    res_fname = ""
    section_found = 0
    fromclock_found = 0
    maxdelay_found = 0

    for rpt_dir in hw_rpt_dirs:
        try:
            all_files = os.listdir(rpt_dir)
            for fname in all_files:
                if (timing_rptname_subset in fname and
                    ".swp" not in fname
                ):
                    res_fname = rpt_dir + fname
        except FileNotFoundError:
            continue

    try:
        res_file = open(res_fname, 'r')
        data_lines = res_file.readlines()

        for lidx in range(0, len(data_lines)):
            line = data_lines[lidx]

            ###############
            ### FINDING THE CORRECT SECTION
            if ("| Timing Details" in line):
                print("SECTION FOUND")
                section_found = 1
            elif (  "From Clock:" in line and 
                    ("clk_kernel_00" in line or "clkwiz_kernel_0" in line) and
                    section_found
            ):
                print("FROMCLOCK FOUND")
                fromclock_found = 1
            elif ("Max Delay Paths" in line and fromclock_found):
                print("MAXDELAY FOUND")
                maxdelay_found = 1
            ###############

            elif (maxdelay_found):
                if ("Slack" in line and "VIOLATED" in line):
                    entry = _analyze_one_slack_violation(data_lines[lidx:lidx+30])
                    ret_arr.append(entry)

                if ("Slack" in line and "MET" in line):
                    ### We met the timing. Stop.
                    while (len(ret_arr) < NUM_ENTRIES):
                        ret_arr.append('MET')
                    break
                if ("Min Delay Paths" in line):
                    ### After the maxdelay paths, we're done.
                    break

    except FileNotFoundError:
        pass

    while (len(ret_arr) < NUM_ENTRIES):
        ret_arr.append('-')

    return ret_arr



def get_numqueries_and_fprates():
    nqueries            = '-'
    ninserts            = []
    actual_fprates      = []
    theoretical_fprates = []
    retval              = []
    results_fname = "KENNY_run_hw.log"

    try:
        res_file = open(results_fname, 'r')
        data_lines = res_file.readlines()
        val = 0

        for line in data_lines:
            if ("ACTUAL fp rate" in line):
                val = line.split("=")[1].strip(". \n")
                val = float(val)
                actual_fprates.append(val)

            elif ("THEORETICAL fp rate" in line):
                val = line.split("=")[1].strip(". \n")
                val = float(val)
                theoretical_fprates.append(val)

            elif ("number of inserted elements =" in line):
                val = line.split("=")[1].strip(". \n")
                val = int(val)
                ninserts.append(val)

            elif ("KDEBUG: TOTAL_NUM_KEYINPUT is" in line):
                val = line.split("is")[1].strip(". \n")
                val = int(val)
                nqueries = val

        retval.append(nqueries)
        
        assert( len(actual_fprates) == len(theoretical_fprates))
        assert( len(actual_fprates) == len(ninserts))

        for i in range(0, len(ninserts)):
            retval.append(actual_fprates[i])
            retval.append(theoretical_fprates[i])
            retval.append(ninserts[i])

    except FileNotFoundError:
        retval = ['-'] * 5

    return retval



def get_fpga_runtimes():
    runtimes = ['-'] * 4
    results_fname = "KENNY_run_hw.log"
    random_times = []

    try:
        res_file = open(results_fname, 'r')
        data_lines = res_file.readlines()
        idx = 0

        for line in data_lines:
            if ("gen_data_mode" in line):
                MODE = line.split("INPUT_GEN_MODE_")[1]
                if ("NO_CLASH" in MODE):
                    idx = 0
                elif ("CYCLIC_CLASH" in MODE):
                    idx = 1
                elif ("ALL_CLASH" in MODE):
                    idx = 2
                elif ("RANDOM" in MODE):
                    idx = 3
                else:
                    raise KeyError

                #print(line)
                #print(idx)

            if ("KERNEL time" in line):
                time = line.split(":")[1]
                time = time.split('s')[0]
                time = time.strip()
                if (idx == 3):
                    random_times.append(float(time))
                else:
                    runtimes[idx] = time

            if ("FAILED" in line):
                raise NameError
                break


    except FileNotFoundError:
        runtimes = ['-'] * 4
    except NameError:
        runtimes = ['failed verif'] * 4
    except KeyError:
        runtimes = ['wtf'] * 4

    # Drop the fastest and slowest 'outliers'.
    random_times.sort()
    random_times = random_times[1:-1]
    # Average the remaining times.
    if (len(random_times) == 0):
        random_runtime = '-'
    else:
        random_runtime = sum(random_times) / float(len(random_times))

    runtimes[3] = random_runtime

    return runtimes 


def collect_all_results():
    top_dir = os.getcwd()
    all_build_dirs = os.listdir(BUILDS_DIR)
    csv_file = open(ALL_RESULTS_CSV, 'w', newline="")
    csv_writer = csv.writer(csv_file)

    all_build_dirs.sort()

    for dirname in all_build_dirs:
        print(dirname)
        os.chdir(BUILDS_DIR)
        os.chdir(dirname)

        this_result = []

        htsbm = [int(num) for num in dirname.split('-')]
        this_result.extend(htsbm)

        this_result.extend(get_freqs_and_resources())

        this_result.extend(get_freq_debug_info())

        this_result.extend(get_fpga_runtimes())

        this_result.extend(get_numqueries_and_fprates())

        csv_writer.writerow(this_result)

        os.chdir(top_dir)



if __name__ == "__main__":
    if ((len(sys.argv) > 1)):
        print("")
        print("ERROR: Incorrect arguments.")
        print("     This program does not take any CLI arguments.")
        print("")
        sys.exit(-1)

    collect_all_results()
