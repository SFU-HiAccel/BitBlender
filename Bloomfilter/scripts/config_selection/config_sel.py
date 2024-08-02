import sys
import os
import math
import csv
import pprint
from argparse import ArgumentParser

from itertools import product as cartesian_product

### To use the qor ML models
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

### To use our cycle-performance models
import sys
sys.path.append('../PerfModel_Scripts/')
import cycles_perfmodel as bb_perfmodel


MAX_NUM_HASHES = 25
OUTPUT_CSV = "CONFIGS.csv"
qor_models_dir = "./qor_models/"


"""
The user is expected to give us two values, and we generate several Bloom Filter configs.
The number of elements to INSERT to the bloom filter,
and the desired false-positive rate.

    https://en.wikipedia.org/wiki/Bloom_filter#Probability_of_false_positives
        - n                                     = number of inserted elements
        - They call it epsilon, we call it fp   = desired false-positive rate
        - They call it m, we call it L          = number of bits in the BV
        - They call it k, we call it h          = number of hash functions
"""
def ReadArguments():
    parser = ArgumentParser()
    parser.add_argument("-s", "--sweep", dest="sweep",
                        help="If we should generate a sweep over several (n, fp).",
                        required=True,
                        default="1"
    )
    parser.add_argument("-n", "--num_inserts", dest="n",
                        help="the number of items expected to be inserted to the bloom filter. You can use K as shorthand for thousand, and M as shorthand for million.",
                        required=False,
                        default="-1"
    )
    parser.add_argument("-f", "--fp_rate", dest="fp",
                        help="the desired false-positive rate of the bloom filter. You can use % if you wish to enter it in percentages.",
                        required=False,
                        default="-1"
    )
    args = parser.parse_args()

    try:
        if (args.n == "-1") or (args.fp == "-1"):
            sweep = args.sweep
        else:
            sweep = 0

        if ('M' in args.n):
            n = 1000000*int( args.n.split("M")[0] )
        elif ('K' in args.n):
            n = 1000*int( args.n.split("K")[0] )
        else:
            n = int( args.n )

        if ("%" in args.fp):
            fp = float( args.fp.split("%")[0] ) / 100.0
        else:
            fp = float(args.fp)
    except Error:
        raise ValueError("The specified false-positive rate must be a float, and num_inserts must be an int.")

    if (sweep == 0) and (fp >= 1 or fp <= 0):
        raise ValueError("The specified false-positive rate is not legal.")
    if (sweep == 0) and (n <= 0):
        raise ValueError("The specified num-inserts is not legal.")

    return (sweep, n, fp)



"""
Given #INSERTS, FP-RATE, and #HASH, we compute the corresponding BVLength.
"""
def compute_optimal_bvlen(n, fp, h):
    kth_root_of_eps = fp**(1/h)
    denom = math.log(1 - kth_root_of_eps)

    return math.ceil( (-h*n)/denom )




"""
https://stackoverflow.com/questions/14267555/find-the-smallest-power-of-2-greater-than-or-equal-to-n-in-python
"""
def round_up_pow_2(n):
    return 2**(n-1).bit_length()







def change_sweep_array_length(array_len):
    run_sweep_fname = "../codegen_scripts/run_build_sweep.sh"

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







class TSBConfig:
    ### We include a frequency estimate with the TSBConfig
    def __init__(self, T, S, B, freq_estimate=None, cpi = None):
        self.t = T
        self.s = S
        self.b = B
        self.freq_estimate = freq_estimate
        self.cpi = cpi
        self.thruput_est = -1

    def __repr__(self):
        ret = "T={:<3}, S={:<3}, B={:<3}, freq={:<7}, cpi={:<8}, thruput={:<10}".format(
                    self.t, self.s, self.b,
                    self.freq_estimate,
                    self.cpi,
                    self.thruput_est
        )
        return ret

    def def_freq(self, freq_estimate):
        self.freq_estimate = freq_estimate

    def def_cpi(self, cpi):
        self.cpi = cpi

    def def_throughput_estimate(self, t):
        self.thruput_est = t

    def get_tsb_tuple(self):
        return (self.t, self.s, self.b)









class BloomFilterDesignGenerator:
    def __init__(self, n, fp):
        self.n = n
        self.fp = fp
        self.PROPOSALS_TO_KEEP_AFTER_PRUNING = 5

        # Harr and Larr : array of corresponding entries, where each
        #   entry-pair represents a combination of (h, L) that satisfies
        #   the (n, fp) constraint.
        self.Harr = []
        self.Larr = []
        self.seclen_arr = []

        # proposals_per_hl : dict, mapping each (H,SECLEN) value to an associated list of TSBConfig objects.
        self.proposals_per_hl = {}

        # pruned_proposals: A list, containing proposals after pruning.
        self.pruned_proposals = []


    def print_all_proposals(self):
        for k in self.proposals_per_hl:
            print("{} : ".format(k))

            for tsb in self.proposals_per_hl[k]:
                print("        {}".format(tsb))




    def print_pruned_proposals(self):
        print("-----------------------------")
        print("PRUNED proposals:")
        for item in self.pruned_proposals:
            print("     H={:<3}, L={:<3}, {}".format(item[0], item[1], item[2]))







    """
    This function is meant to work with a shell script to run the sweep.
        Here we generate a Bash script, which contains all of the config-strings
        to generate with generate_BVSharing_design.py.
    """
    def generate_design_shellscript(self):
        _lines_to_write = []
        fname = "../codegen_scripts/designs_to_generate.sh"

        _lines_to_write.append('#!/bin/bash' + "\n")
        _lines_to_write.append('' + "\n")
        _lines_to_write.append('HTSB_CONFIGS=(' + "\n")

        for cfg in self.pruned_proposals:
            tsb = cfg[2]
            HTSBL_string = "{h}-{t}-{s}-{b}-{l}".format(
                                                    h = cfg[0]
                                                    ,t=tsb.t
                                                    ,s=tsb.s
                                                    ,b=tsb.b
                                                    ,l = cfg[1]
            )
            _lines_to_write.append('    "{}"'.format(HTSBL_string) + "\n")

        _lines_to_write.append(')' + "\n")

        with open(fname, "w") as f:
            f.writelines(_lines_to_write)

        change_sweep_array_length(len(self.pruned_proposals))









    """
    This function generates the H and L arrays.
    """
    def gen_HLarr(self):
        numhash_arr = list(range(1, MAX_NUM_HASHES))
        bvlen_arr = []

        for h in numhash_arr:
            bvlen_arr.append(compute_optimal_bvlen(n, fp, h))

        ### View the BV lengths (L) as a function of #HASH. This function
        ### will decrease to a local minimum at some h value, and then increase.
        ### We don't want anything after it increases.
        ### Here, we find all (h,L) until they reach that local minimum.
        i = 0
        while (i == 0) or (bvlen_arr[i] < bvlen_arr[i-1]):
            print("h = {h:>3}, L = {L:>15,}".format(h=numhash_arr[i], L=bvlen_arr[i]))
            i += 1

        num_HL = i

        numhash_arr = numhash_arr[0:num_HL]
        bvlen_arr = bvlen_arr[0:num_HL]


        for i in range(0, num_HL):
            self.Harr.append(numhash_arr[i])
            self.Larr.append(bvlen_arr[i])

            section_len = int(bvlen_arr[i] / numhash_arr[i])
            ## Round up to a power of 2: https://stackoverflow.com/questions/14267555/find-the-smallest-power-of-2-greater-than-or-equal-to-n-in-python
            section_len = 1<<(section_len-1).bit_length()

            self.seclen_arr.append(section_len)





    """
    This function populates the proposals_per_hl dict.
     - Go through [h,L] combos, and propose several possible [t,s,b], corresponding to each [h,L].
    """
    def gen_all_proposals(self):
        num_HL = len(self.Harr)

        with open(qor_models_dir + "/bitstream_model.pkl", 'rb') as modelfile:
            bitstream_completion_model = pickle.load(modelfile)
        with open(qor_models_dir + "/frequency_model.pkl", 'rb') as modelfile:
            frequency_model = pickle.load(modelfile)

        possible_T = [2,4,8]
        possible_S = range(2,8)
        possible_B = [8, 16]

        possible_TSBs = list( cartesian_product(possible_T, possible_S, possible_B) )

        for i in range(0, num_HL):
            h = self.Harr[i]
            seclen_M = math.ceil((self.seclen_arr[i])/(1024*1024))
            hl = (h, seclen_M)
            self.proposals_per_hl[hl] = []

            if (seclen_M > 32):
                continue

            for val in possible_TSBs:
                tsb = TSBConfig(*val)
                ### Ignore configs with #PARTITIONS < #STM
                if (tsb.t < tsb.s):
                    continue
                ### Ignore configs with 'too many' more #PARTITIONS than #STM
                if (tsb.t > tsb.s+3):
                    continue

                feature_names = ["NUM HASH","NUM PART","NUM STM","SHUFBUF_SZ","BVLEN PER HASH"]

                ### This must be 2D - the first idx is a row (but we only have 1 row, so it looks dumb).
                htsbl = [[]]
                htsbl[0] = [h]
                htsbl[0].extend( [tsb.t, tsb.s, tsb.b] )
                htsbl[0].append(seclen_M)

                labelled_data = pd.DataFrame(htsbl, columns=feature_names)

                tmp = bitstream_completion_model.predict( labelled_data )
                bitstream_will_generate = 1 if (tmp[0] > 0.5) else 0

                freq_estimate = frequency_model.predict(labelled_data)
                freq_estimate = round( freq_estimate[0], 2 )
                tsb.def_freq(freq_estimate)

                if (bitstream_will_generate):
                    self.proposals_per_hl[hl].append(tsb)





    """
    This function prunes the proposals_per_hl dict.
     - Go through all proposals_per_hl. Create a massive list of every proposal, ranked
       by the expected throughput and frequency (lower freq -> more likely to fail xclbin)
    """
    def prune_proposals(self):
        SIMULATED_INPUTS_PER_STM = 2500

        for key in self.proposals_per_hl:

            ### Compute a throughput estimate for each proposal
            for idx in range( len(self.proposals_per_hl[key]) ):
                tsb = self.proposals_per_hl[key][idx]
                B = tsb.b
                S = tsb.s
                T = tsb.t
                freq_est = tsb.freq_estimate

                LTSC = bb_perfmodel.compute_LTSC(NUM_STM=S, NUM_PART=T, BUF_SZ=B, num_inputs_per_stm=SIMULATED_INPUTS_PER_STM)

                cycles_per_input = float(max(LTSC[-1])) / SIMULATED_INPUTS_PER_STM
                tsb.def_cpi(cycles_per_input)

                throughput_estimate = freq_est * 2 * S / cycles_per_input
                tsb.def_throughput_estimate(throughput_estimate)

                self.proposals_per_hl[key][idx] = tsb

            self.proposals_per_hl[key].sort( key=lambda x : x.thruput_est, reverse=1 )

            n = min(self.PROPOSALS_TO_KEEP_AFTER_PRUNING, len(self.proposals_per_hl[key]))
            for i in range(0, n):
                cur_proposal = self.proposals_per_hl[key][i]
                cur_proposal = key + (cur_proposal,)
                self.pruned_proposals.append(cur_proposal)

        ### Sort by the highest throughput estimates
        self.pruned_proposals.sort( key = lambda x : x[2].thruput_est, reverse=1 )
        n = min(self.PROPOSALS_TO_KEEP_AFTER_PRUNING, len(self.pruned_proposals))
        self.pruned_proposals = self.pruned_proposals[0:n]




    """
    - A "request" is a pair of (n,fp) - so a user is requesting a bloom filter design 
        that meets these two algorithmic parameters.
    - This function generates many design PROPOSALS, for one request.
    """
    def gen_proposals_for_one_request(self):
        print("Received num_insertions = {n:,}, fp_rate = {fp}".format(n=n, fp=fp), flush=True)
        self.gen_HLarr()
        self.gen_all_proposals()
        self.prune_proposals()

        self.print_pruned_proposals()
        self.generate_design_shellscript()









if __name__ == "__main__":
    print("")

    (sweep, n, fp) = ReadArguments()

    if (not sweep):
        dg = BloomFilterDesignGenerator(n, fp)
        dg.gen_proposals_for_one_request()


    elif (sweep):
        proposed_eps = [0.01, 0.005, 0.002, 0.001]
        proposed_n = [8000000]
        for fp in proposed_eps:
            print("---")
            for n in proposed_n:
                dg = BloomFilterDesignGenerator(n, fp)
                dg.gen_proposals_for_one_request()
                print("")
    print("")








