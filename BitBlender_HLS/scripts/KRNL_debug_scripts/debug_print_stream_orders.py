import re

NUM_HASH = 3
NUM_STM = 2
NUM_PART = 2
FNAME_TO_READ = "KENNY_makecheck_sw_REORDERED"

lines = []


if __name__ == "__main__":
    f = open(FNAME_TO_READ, "r")
    lines_input = f.readlines()
    f.close()

    for line in lines_input:
        if "outputting to" in line:
            lines.append(line)

    cur_stream_parsedlines = []
    parsedlines = [ [ [] for i in range(0, NUM_PART) ] for j in range(0, NUM_HASH) ]
    delimiters = []
    
    strm_and_input_idx_regex = "^.*\[(.)\] input_idx=(.*)$"
    
    for hash_idx in range(0, NUM_HASH):
        for part_idx in range(0, NUM_PART):
            cur_delimiter = ") [" + str(hash_idx) + "][" + str(part_idx) + "]["
    
            for line in lines:
                if cur_delimiter in line:
                    parsedlines[hash_idx][part_idx].append(line)
    
    #for hash_idx in range(0, NUM_HASH):
    #    for part_idx in range(0, NUM_PART):
    #        print(parsedlines[hash_idx][part_idx])
    
    for hash_idx in range(0, NUM_HASH):
        for part_idx in range(0, NUM_PART):
            for line in parsedlines[hash_idx][part_idx]:
                matches = re.match(strm_and_input_idx_regex, line)
                
                if (matches.group(1) == '0'):
                    color = "b"
                elif (matches.group(1) == '1'):
                    color = "r"
    
                input_idx = matches.group(2)
    
                totalstring = color + str(input_idx)
                print("{0: >6}".format(totalstring), end="")
    
            print("")
        print("")

