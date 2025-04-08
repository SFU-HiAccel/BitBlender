import sys
import os
import re
import json

FILENOTFOUND_RETVAL = " (The file did not exist)"

#######################################
## GETTING IIs:
#######################################


def Log_IIs(_out_file_name):
    list_of_IIs = []
    out_file_contents = []
    list_of_IIs.append("\n\n\n\n")
    list_of_IIs.append("List of IIs:" + "\n")
    list_of_IIs.append("------------------------------------------------------------" + "\n")
    out_file_contents.append("\n\n\n\n")
    out_file_contents.append("II REPORTS" + "\n")
    out_file_contents.append("------------------------------------------------------------" + "\n")
    hls_rpts_dir = "_x.hw_multistream_MurmurHash3.xilinx_u280_xdma_201920_3/report/"

    ACHIEVED_II_OFFSET=5

    try:
        hls_rpts_fnames = os.listdir(hls_rpts_dir)

        for fname in hls_rpts_fnames:
            # Skip over vim swap files, in case Im reading those.
            if (".swp" in fname):
                continue
            if not ("_csynth.rpt" in fname):
                continue

            full_fname = hls_rpts_dir + fname
            f = open(full_fname, "r")
            hls_report_lines = f.readlines()
            IS_II_TBL = 0

            for line in hls_report_lines:
                if (IS_II_TBL):
                    out_file_contents.append(line)

                    ### This is the "interesting" line of the II table.
                    if ("Loop Name" in line):
                        entry = line.split("|")[ACHIEVED_II_OFFSET]
                        if (entry.strip() != "achieved"):
                            list_of_IIs.append("    ERROR: THIS TABLE ISNT REPORTING THE CORRECT THING" + "\n")

                    if ("|-" in line):
                        entry = line.split("|")[ACHIEVED_II_OFFSET]
                        entry = entry.strip()
                        if (int(entry) > 1):
                            tail = "!!! ERROR ERROR ERROR"
                        else:
                            tail = ""
                        list_of_IIs.append("    {name:>90} : II={ii:<5} {tail}".format(
                                            name=module_name.strip()
                                            ,ii=entry
                                            ,tail=tail
                                            ) + "\n"
                        )

                    ### After the table there is an empty line. Stop processing when we hit that.
                    if (line.strip() == ""):
                        break

                if "Vitis HLS Report" in line:
                    # Get the name of the module.
                    module_name = line[24:]
                    out_file_contents.append("-------" + "\n")
                    out_file_contents.append(module_name)
                elif "Loop:" in line:
                    # The start of the II table.
                    IS_II_TBL=1

    except FileNotFoundError:
        list_of_IIs.append(FILENOTFOUND_RETVAL)
        out_file_contents.append(FILENOTFOUND_RETVAL)

    finally:
        f = open(_out_file_name, "a")
        f.writelines(list_of_IIs)
        f.writelines(out_file_contents)

#######################################
## HLS Frequencies:
#######################################


def Log_HLS_freq_estimates(_out_file_name):
    out_file_contents = []
    out_file_contents.append("\n\n\n\n")
    out_file_contents.append("HLS Frequency Estimates:"+ "\n")
    out_file_contents.append("------------------------------------------------------------" + "\n")
    hls_logs_dir = "_x.hw_multistream_MurmurHash3.xilinx_u280_xdma_201920_3/log/"

    class ModuleFreq:
        def __init__(self):
            self.module = "module_name"
            self.freq = "0.0"
        def __init__(self, m, f):
            self.module = m 
            self.freq = f
        def to_str(self):
            return "{:>50} : {:<10}".format(self.module, self.freq)

    module_names = []
    freqs = []
    num_modules = 0
    fmax_regex = "\d+\.\d\d"

    try:
        hls_logs_fnames = os.listdir(hls_logs_dir)

        for fname in hls_logs_fnames:
            # Skip over vim swap files, in case Im reading those.
            if not (fname.endswith(".log")):
                continue

            full_fname = hls_logs_dir + fname
            f = open(full_fname, "r")
            log_lines = f.readlines()
            num_modules += 1

            for line in log_lines:
                # Get the name of the module
                if ("Generating Verilog RTL for" in line):
                    a = line.split("Generating Verilog RTL for")
                    module_name = a[1].strip().rstrip(".")
                    module_names.append(module_name)

                # Get the Estimated FMAX
                if ("Estimated Fmax" in line):
                    a = line.split("****")
                    a = a[1].strip()

                    match = re.search(fmax_regex, a)
                    if (match):
                        cur_freq = float(match[0])
                        freqs.append(cur_freq)

    except FileNotFoundError:
        out_file_contents.append(FILENOTFOUND_RETVAL)

    else:
        modules_and_freqs = []
        for i in range(0, num_modules):
            modules_and_freqs.append(ModuleFreq(module_names[i], freqs[i]))

        modules_and_freqs.sort(key=lambda x: x.freq)
        for i in range(0, num_modules):
            out_file_contents.append(modules_and_freqs[i].to_str() + "\n")


    finally:
        f = open(_out_file_name, "a")
        f.writelines(out_file_contents)



#######################################
## TAPA/Autobridge number of slots:
#######################################

def Log_TAPA_Num_Slots(_out_file_name):
    out_file_contents = []
    out_file_contents.append("\n\n\n\n")
    autobridge_dir = "_x.hw_multistream_MurmurHash3.xilinx_u280_xdma_201920_3/autobridge/"
    floorplan_fname = "floorplan-region-to-instances.json"

    try:
        floorplan_file = open(autobridge_dir + floorplan_fname, "r")
    except FileNotFoundError:
        out_file_contents.append("Number of slots used by Autobridge: {}".format(FILENOTFOUND_RETVAL))
    else:
        floorplan_json = json.load(floorplan_file)
        out_file_contents.append("Number of slots used by Autobridge: {}".format(len(floorplan_json)))
    finally:
        f = open(_out_file_name, "a")
        f.writelines(out_file_contents)



#######################################
## HW BUILD DATA:
#######################################


def _Get_HW_Resource_Total_CLB_LUT(util_report_lines):
    for line in util_report_lines:
        if ("CLB LUTs" in line):
            percentage_used = line.split("|")[6]
            percentage_used = percentage_used.strip()
            break

    return float(percentage_used)


def _Get_HW_Resource_Total_CLB_REG(util_report_lines):
    for line in util_report_lines:
        if ("CLB Registers" in line):
            percentage_used = line.split("|")[6]
            percentage_used = percentage_used.strip()
            break

    return float(percentage_used)


def _Get_HW_Resource_Total_BRAM(util_report_lines):
    section = 0
    for line in util_report_lines:
        if ("3. BLOCKRAM" in line):
            section += 1
        elif ("Block RAM Tile" in line) and (section == 2):
            percentage_used = line.split("|")[6]
            percentage_used = percentage_used.strip()
            break

    return float(percentage_used)

def _Get_HW_Resource_Total_URAM(util_report_lines):
    section = 0
    for line in util_report_lines:
        if ("3. BLOCKRAM" in line):
            section += 1
        elif ("URAM" in line) and (section == 2):
            percentage_used = line.split("|")[6]
            percentage_used = percentage_used.strip()
            break

    return float(percentage_used)


def _Get_HW_Resource_Total_DSP(util_report_lines):
    section = 0
    for line in util_report_lines:
        if ("4. ARITHMETIC" in line):
            section += 1
        elif ("DSPs" in line) and (section == 2):
            percentage_used = line.split("|")[6]
            percentage_used = percentage_used.strip()
            break

    return float(percentage_used)


def _Get_HW_Resource_CLB_per_SLR(util_report_lines):
    clb_per_slr = [0, 0, 0]
    section = 0
    for line in util_report_lines:
        if ("14. SLR CLB Logic and Dedicated Block Utilization" in line):
            section += 1
        elif ("CLB    " in line) and (section == 2):
            for i in range(0, 3):
                clb_per_slr[i] = line.split("|")[5+i]
                clb_per_slr[i] = clb_per_slr[i].strip()
                clb_per_slr[i] = float(clb_per_slr[i])
            break

    return clb_per_slr


def Log_HW_Resource_Usages(_out_file_name):
    out_file_contents = []
    out_file_contents.append("\n\n\n\n")
    out_file_contents.append("  UTILIZATION REPORTS" + "\n")
    out_file_contents.append("------------------------------------------------------------" + "\n")

    report_dir_relpath = "vitis_run_hw/workload_xilinx_u280_xdma_201920_3.temp/reports/link/imp/"
    util_report_fname = "impl_1_full_util_routed.rpt"

    try:
        util_report_file = open(report_dir_relpath + util_report_fname, "r")
        util_report_lines = util_report_file.readlines()
        total_LUT_usage     = _Get_HW_Resource_Total_CLB_LUT    (util_report_lines)
        total_FF_usage      = _Get_HW_Resource_Total_CLB_REG     (util_report_lines)
        total_BRAM_usage    = _Get_HW_Resource_Total_BRAM       (util_report_lines)
        total_URAM_usage    = _Get_HW_Resource_Total_URAM       (util_report_lines)
        total_DSP_usage     = _Get_HW_Resource_Total_DSP        (util_report_lines)

        out_file_contents.append("Total LUT Usage:  {}".format(total_LUT_usage) + "\n")
        out_file_contents.append("Total FF  Usage:  {}".format(total_FF_usage) + "\n")
        out_file_contents.append("Total BRAM Usage: {}".format(total_BRAM_usage) + "\n")
        out_file_contents.append("Total URAM Usage: {}".format(total_URAM_usage) + "\n")
        out_file_contents.append("Total DSP Usage:  {}".format(total_DSP_usage) + "\n")

    except FileNotFoundError:
        out_file_contents.append(FILENOTFOUND_RETVAL)

    finally:
        with open(_out_file_name, "a") as f:
            f.writelines(out_file_contents)



def Get_HW_frequencies():
    report_dir_relpath = "vitis_run_hw/"
    freq_report_fname = "workload_xilinx_u280_xdma_201920_3.xclbin.info"

    try:
        freq_report_file = open(report_dir_relpath + freq_report_fname, "r")
        freq_report_lines = freq_report_file.readlines()
    except FileNotFoundError:
        return (FILENOTFOUND_RETVAL, FILENOTFOUND_RETVAL)

    section = 0
    for line in freq_report_lines:
        if ("DATA_CLK" in line):
            section = 1
        elif ("hbm_aclk" in line):
            section = 2
        elif ("KERNEL_CLK" in line):
            section = 5
        elif ("Frequency" in line) and (section == 1):
            kern_freq = line.split(":")[1]
            kern_freq = kern_freq.split("MHz")[0].strip()
        elif ("Frequency" in line) and (section == 2):
            mem_freq = line.split(":")[1]
            mem_freq = mem_freq.split("MHz")[0].strip()

    return (mem_freq, kern_freq)



def Log_HW_frequencies(_out_file_name):
    out_file_contents = []
    out_file_contents.append("  FINAL HW FREQUENCIES" + "\n")
    out_file_contents.append("------------------------------------------------------------" + "\n")
    (mem_freq, kern_freq) = Get_HW_frequencies()

    out_file_contents.append(" HBM  Freq: {}".format(mem_freq) + "\n")
    out_file_contents.append(" Kern Freq: {}".format(kern_freq) + "\n")

    f = open(_out_file_name, "a")
    f.writelines(out_file_contents)




if __name__ == "__main__":
    if ((len(sys.argv) > 1)):
        print("")
        print("ERROR: Incorrect arguments.")
        print("     This program does not take any CLI arguments.")
        print("")
        sys.exit(-1)

    output_filename = "RESOURCES_AND_IIs.log"

    if (os.path.exists(output_filename)):
        os.remove(output_filename)

    Log_HW_frequencies(output_filename)

    Log_HW_Resource_Usages(output_filename)

    Log_TAPA_Num_Slots(output_filename)

    Log_HLS_freq_estimates(output_filename)

    Log_IIs(output_filename)
