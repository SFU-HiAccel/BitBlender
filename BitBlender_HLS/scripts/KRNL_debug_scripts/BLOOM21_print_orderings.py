import re

NUM_HASH = 2
NUM_PART = 4
NUM_STM = 2
FNAME_TO_READ = "KENNY_makecheck_sw"


def print_arb_outputs(lines_input):
    lines = []
    lines_to_print = [["" for i in range(0, NUM_PART)] for j in range(0, NUM_HASH)]

    for line in lines_input:
        if "ARBITER" in line and "outputting to" in line:
            lines.append(line)

    strm_and_input_idx_regex = "^.*\) \[(.)\]\[(.)\]\[(.)\] input_idx=(.*)$"
    
    for line in lines:
        matches = re.match(strm_and_input_idx_regex, line)
        cur_hash_idx = int(matches.group(1))
        cur_part_idx = int(matches.group(2))
        cur_strm_idx = int(matches.group(3))
        
        color = chr(ord('a')+cur_strm_idx)

        cur_input_idx = matches.group(4)

        for hash_idx in range(0, NUM_HASH):
            for part_idx in range(0, NUM_PART):
                if (cur_hash_idx == hash_idx) and (part_idx == cur_part_idx):
                    totalstring = color + str(cur_input_idx)
                    lines_to_print[hash_idx][part_idx] += "{0:>6}".format(totalstring)

                elif (cur_hash_idx == hash_idx) and (part_idx != cur_part_idx):
                    totalstring = ""
                    lines_to_print[hash_idx][part_idx] += "{0:>6}".format(totalstring)

                else:
                    # Dont append to the line to print.
                    pass
    
    print("\n\n\nARBITER OUTPUTS:\n\n\n")
    for hash_idx in range(0, NUM_HASH):
        hash_delimiter_str =  "(((HASH {})))".format(hash_idx) + ("-"*50)
        hash_delimiter_line = hash_delimiter_str * int(len(lines_to_print[hash_idx][0]) / len(hash_delimiter_str))
        print(hash_delimiter_line)

        for part_idx in range(0, NUM_PART):
            print(lines_to_print[hash_idx][part_idx])

        hash_delimiter_line = "-"* len(lines_to_print[hash_idx][0])
        print(hash_delimiter_line)


def print_compute_outputs(lines_input):
    lines = []
    lines_to_print = [["" for i in range(0, NUM_PART)] for j in range(0, NUM_HASH)]

    for line in lines_input:
        if "COMPUTEHASH - outputting" in line:
            lines.append(line)

    #strm_and_input_idx_regex = "^.*hash,part,strm\) = \[(.)\]\[(.)\]\[(.)\], input_idx=(.*)$"
    strm_and_input_idx_regex = "^.*hash,part,strm\) = \[(.)\]\[(.)\]\[(.)\], input_idx=(.*)$"

    for line in lines:
        matches = re.match(strm_and_input_idx_regex, line)
        cur_hash_idx = int(matches.group(1))
        cur_part_idx = int(matches.group(2))
        cur_strm_idx = int(matches.group(3))
        cur_input_idx = int(matches.group(4))
        color = chr(ord('a')+cur_strm_idx)

        for hash_idx in range(0, NUM_HASH):
            for part_idx in range(0, NUM_PART):
                if (cur_hash_idx == hash_idx) and (part_idx == cur_part_idx):
                    totalstring = color + str(cur_input_idx)
                    lines_to_print[hash_idx][part_idx] += "{0:>6}".format(totalstring)

                elif (cur_hash_idx == hash_idx) and (part_idx != cur_part_idx):
                    totalstring = ""
                    lines_to_print[hash_idx][part_idx] += "{0:>6}".format(totalstring)

                else:
                    # Dont append to the line to print.
                    pass

    print("\n\n\nCOMPUTE OUTPUTS:\n\n\n")
    for hash_idx in range(0, NUM_HASH):
        hash_delimiter_str =  "(((HASH {})))".format(hash_idx) + ("-"*50)
        hash_delimiter_line = hash_delimiter_str * int(len(lines_to_print[hash_idx][0]) / len(hash_delimiter_str))
        print(hash_delimiter_line)

        for part_idx in range(0, NUM_PART):
            print(lines_to_print[hash_idx][part_idx])

        hash_delimiter_line = "-"* len(lines_to_print[hash_idx][0])
        print(hash_delimiter_line)




if __name__ == "__main__":
    f = open(FNAME_TO_READ, "r")
    lines_input = f.readlines()
    f.close()
    print("DONT FORGET TO CHANGE THE SCRIPT To have the correct NUM_HASH, NUM_STM, NUM_PART.")
    print("")

    print_compute_outputs(lines_input)
    print_arb_outputs(lines_input)





