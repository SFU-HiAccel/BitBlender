import sys 

FNAME_TO_READ = "KENNY_swemu"
FNAME_TO_WRITE = "KENNY_makecheck_sw_REORDERED"

lines_input = []
lines_output = []
delimiters = [
    "HOST",
    "LOADBV",
    "LOADKEY",
    "COMPUTEHASH_FEEDER",
    "COMPUTEHASH_COMPUTER",
    "ARBITER_MONO",
    "ARBITER FORWARDER",
    "ARBITER ATOM",
    "ARBITER RATEMON",
    "QUERY UNIT",
    "DEBUG_QUERY_SINK",
    "SHUFFLE TtoS",
    "SHUFFLE ORDERING",
    "AGGREGATE",
    "PACKOUTPUT",
    "WRITEOUTPUT"
]
numbered_delimiters = [

    "COMPUTEHASH_FEEDER",
    "COMPUTEHASH_COMPUTER",
    "ARBITER FORWARDER",
    "ARBITER ATOM",
    "ARBITER RATEMON",
    "QUERY UNIT",
    "DEBUG_QUERY_SINK",
    "SHUFFLE TtoS",
    "SHUFFLE ORDERING",
    "AGGREGATE",
    "PACKOUTPUT"
]

if __name__ == "__main__":
    f = open(FNAME_TO_READ, "r")
    lines_input = f.readlines()
    #print("WARNING! WARNING! WARNING")
    #print("THIS IS CONFIGURED FOR DUMB_MULTISTREAM.")
    #print("WARNING! WARNING! WARNING")
    for delimiter in delimiters:
        tmp = []
        lines_output.append("\n")

        if delimiter in numbered_delimiters:
            print("Found a numbered delimiter: " + delimiter)
            for line in lines_input:
                if (delimiter in line):
                    tmp.append(line)
                    found_one = 1

            ### Sorting the list of strings, according to the string before a "-". 
            #### https://stackoverflow.com/questions/21431052/sort-list-of-strings-by-a-part-of-the-string
            tmp.sort(key=lambda x: x.split("-")[0])
            for line in tmp:
                lines_output.append(line)

        else:
            print("Found a regular delimiter: " + delimiter)
            for line in lines_input:
                if (delimiter in line):
                    lines_output.append(line)
    
    f.close()

    f = open(FNAME_TO_WRITE, "w")
    f.writelines(lines_output)
    print("")
