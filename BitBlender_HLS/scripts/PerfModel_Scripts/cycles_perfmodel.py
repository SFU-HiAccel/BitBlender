
import math
from pprint import pprint
import random
import numpy as np

#import matplotlib.pyplot as plt


INPUTS_PER_STM = 2500


class Packet_T:
    def __init__(self):
        self.stm_idx = -1
        self.in_idx = -1

    def is_valid(self):
        if (self.stm_idx == -1 and self.in_idx == -1):
            return 0
        else:
            return 1

    def __init__(self, sidx, iidx):
        self.stm_idx = sidx
        self.in_idx = iidx

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if (self.is_valid()):
            color = chr(ord('a') + self.stm_idx)
            total = color + str(self.in_idx+1)
        else:
            # Pipeline bubbles
            total = "-"
        return "{: >8}".format(total)


def print_arb_outputs(arb_outputs, NUM_STM, NUM_PART, BUF_SZ):
    print("------------------------------------------------------------------------")
    print("ARB Outputs, with NUM_PART={:>4}, NUM_STM={:>4}, BUF_SZ={:>4}".format(
            NUM_PART, NUM_STM, BUF_SZ)
    )
    max_cycles = 0

    for t in range(0, NUM_PART):
        print(str(arb_outputs[t]))
        if (len(arb_outputs[t]) > max_cycles):
            max_cycles = len(arb_outputs[t])

    print("Max cycles = {}".format(max_cycles))
    print("------------------------------------------------------------------------")



def print_LTSC(LTSC, NUM_STM, NUM_PART, BUF_SZ):
    start_print_idx = INPUTS_PER_STM-10

    print("------------------------------------------------------------------------")
    print("Last T Send Cycles, with NUM_PART={:>4}, NUM_STM={:>4}, BUF_SZ={:>4}".format(
            NUM_PART, NUM_STM, BUF_SZ)
    )

    for k in range(start_print_idx, INPUTS_PER_STM):
        print(" Input {:<6}:   ".format(k+1), end="")
        for t in range(0, NUM_PART):
            print("{:>6}, ".format( LTSC[k][t] ), end="")
        print("")
    print("------------------------------------------------------------------------")



"""
Using the performance model, build the LTSC array.
    LTSC(t,k) = The last cycle that input #k, from each stream, is sent to partition t.
"""
def compute_LTSC(NUM_STM, NUM_PART, BUF_SZ, all_clash_degrees=None, num_inputs_per_stm=INPUTS_PER_STM):
    num_generator = np.random.default_rng(seed=2024)
    LastTSendCycle_arr = []
    ARBITER_NUM_STAGES = math.ceil( math.log2(NUM_STM) )
    ARBITER_FEEDBACK_LATENCY = 2*ARBITER_NUM_STAGES + 3

    for k in range(0, num_inputs_per_stm):
        tmpTSC_arr = []

        ##################
        ### Compute the clash-degrees
        if (all_clash_degrees == None):
            curK_clash_degrees = []

            StoT_mapping = num_generator.integers(0, NUM_PART, NUM_STM).tolist()
            for t in range(0, NUM_PART):
                curK_clash_degrees.append( StoT_mapping.count(t) )
        else:
            curK_clash_degrees = all_clash_degrees[k]
        ##################

        choice1 = 0
        choice2 = 0
        choice3 = 0

        ##################
        ### NEW LTSC:
        for t in range(0, NUM_PART):
            choice1 = 0
            choice2 = 0
            if (k-1 < 0):
                choice1 = 0
            else:
                choice1 = LastTSendCycle_arr[k-1][t]

            choice2 = k

            if (k-BUF_SZ < 0):
                choice3 = 0
            else:
                choice3 = max( LastTSendCycle_arr[k-BUF_SZ] )
                choice3 += ARBITER_FEEDBACK_LATENCY

            sel = max(choice1, choice2, choice3) + curK_clash_degrees[t]
            tmpTSC_arr.append( sel )

        LastTSendCycle_arr.append(tmpTSC_arr)
        ##################

    return LastTSendCycle_arr






def compute_clash_degrees(target_partitions_per_input, NUM_STM, NUM_PART):
    clash_degrees = []

    for k in range(0, INPUTS_PER_STM):
        cur_k_clash_degrees = []
        for t in range(0, NUM_PART):
            cur_k_clash_degrees.append( target_partitions_per_input[k].count(t) )

        clash_degrees.append(cur_k_clash_degrees)

    return clash_degrees





"""
This ATTEMPTS to emulate the arbiter's outputs.
AS OF DEC 20 2023, I'm not sure how to make this accurately model
ratemonitoring latency. So it DOES NOT WORK RIGHT NOW.
"""
def compute_arb_outputs(partition_inputs, NUM_STM, NUM_PART, BUF_SZ):
    last_send_cycle_KminusB = [0] * BUF_SZ
    last_T_send_cycle       = [0] * NUM_PART
    read_ptrs               = [0] * NUM_PART
    partition_outputs       = []
    for i in range(0, NUM_PART):
        partition_outputs.append([])

    for in_idx in range(0, INPUTS_PER_STM):
        depend_idx = in_idx - BUF_SZ
        if (depend_idx < 0):
            min_cycle = in_idx
        else:
            min_cycle = max(in_idx, last_send_cycle_KminusB[depend_idx%BUF_SZ])

        for part_idx in range(0, NUM_PART):
            cur_clash_deg = 0
            new_outputs = []
            pad_cycles = min_cycle - last_T_send_cycle[part_idx]

            if (pad_cycles > 0):
                last_T_send_cycle[part_idx] += pad_cycles
                for i in range(0, pad_cycles):
                    partition_outputs[part_idx].append( Packet_T(-1, -1) )

            for stm_idx in range(0, NUM_STM):
                if (read_ptrs[part_idx] < len(partition_inputs[part_idx])):
                    ## Read and send:
                    if (partition_inputs[part_idx][read_ptrs[part_idx]].in_idx == in_idx and
                        partition_inputs[part_idx][read_ptrs[part_idx]].stm_idx == stm_idx
                    ):
                        partition_outputs[part_idx].append( Packet_T(stm_idx, in_idx) )
                        cur_clash_deg += 1
                        read_ptrs[part_idx] += 1

                    ## Read a bubble:
                    elif ( partition_inputs[part_idx][read_ptrs[part_idx]].is_valid() == 0 ):
                        read_ptrs[part_idx] += 1

            last_T_send_cycle[part_idx] += cur_clash_deg

        last_send_cycle_KminusB[in_idx%BUF_SZ] = max(last_T_send_cycle)

    return partition_outputs



"""
For each input set, emulate a single hash function - i.e. 
generate NUM_STM target partitions.

Generates a list of lists - the 0'th element in sublist 2 is STREAM 2's target partition
for the 0'th key. (NUM_HASH doesn't matter - different hashes are assumed independent)
"""
def generate_input_to_target_partitions(NUM_STM, NUM_PART, MODE):
    stm_input_to_partition_mapping = []

    ### Build the input -> partition mapping
    for in_idx in range(0, INPUTS_PER_STM):
        cur_stm_input_partition_mapping = []

        for stm_idx in range(0, NUM_STM):
            ## Random
            if (MODE == 0):
                cur_stm_input_partition_mapping.append( random.randint(0, NUM_PART-1) )

            ## Clashless mapping
            elif (MODE == 1):
                cur_stm_input_partition_mapping.append( stm_idx%NUM_PART )
            ## Cyclic clashing
            elif (MODE == 2):
                cur_stm_input_partition_mapping.append( in_idx%NUM_PART )
            ## Full clashing
            elif (MODE == 3):
                cur_stm_input_partition_mapping.append(0)

        stm_input_to_partition_mapping.append(cur_stm_input_partition_mapping)

    #pprint(stm_input_to_partition_mapping)
    return stm_input_to_partition_mapping



"""
Given the input -> partitions mapping, create the partitions -> inputs mapping.
That is, generate the inputs in the order that each partition will see them,
assuming NO ratemonitoring.
"""
def generate_partition_inputs(target_partitions_per_input, NUM_STM, NUM_PART):
    partition_inputs = []

    ### Use the input -> partition mapping to generate the inputs of each partition
    for part_idx in range(0, NUM_PART):
        cur_part_inputs = []

        for in_idx in range(0, INPUTS_PER_STM):

            ## Insert bubbles, to make packet (k) arrive on AT LEAST
            ## cycle (k).
            pad_amount = in_idx - len(cur_part_inputs)
            if (pad_amount > 0):
                for i in range(0, pad_amount):
                    cur_part_inputs.append( Packet_T(-1, -1) )

            for stm_idx in range(0, NUM_STM):
                if (target_partitions_per_input[in_idx][stm_idx] == part_idx):
                    cur_part_inputs.append( Packet_T(stm_idx, in_idx) )

        partition_inputs.append(cur_part_inputs)

    #pprint(partition_inputs)
    return partition_inputs





"""
Plot the IDEAL #cycles and ACTUAL #cycles of our performance model,
for different NUM_STM (S_arr), NUM_PARTITIONS (T_arr), and SHUFBUF_SZ (B_arr).
"""
def plot_cycles(best, actual, S_arr, T_arr, B_arr):
    for sidx in range(0, len(S_arr)):
        t_vals = []
        b_vals = []
        best_cycles = []
        actual_cycles = []
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        for pidx in range(0, len(T_arr)):
            for bidx in range(0, len(B_arr)):
                t_vals.append(T_arr[pidx])
                b_vals.append(B_arr[bidx])
                best_cycles.append(best[sidx][pidx][bidx])
                actual_cycles.append(actual[sidx][pidx][bidx])

        ax.scatter(t_vals, b_vals, best_cycles, marker='o')
        ax.scatter(t_vals, b_vals, actual_cycles, marker='^')
        ax.set_xlabel("# Partitions")
        ax.set_ylabel("ShufBuf size")
        ax.set_zlabel("# Cycles")
        plt.title("NUM_STM = {}".format(S_arr[sidx]))
        #plt.show()
        plt.savefig("figs/PerfModel_{}Streams.png".format(S_arr[sidx]))






if __name__ == "__main__":
    print("")
    random.seed(5)

    NUM_PART_TO_TEST = [4,8,16,32]
    NUM_STM_TO_TEST = [2,3,4,5,6,7,8]
    BUF_SZ_TO_TEST = [2,4,8,16,32]
    best_possible_num_cycles = [[[0 for b in range(len(BUF_SZ_TO_TEST))] 
                                    for t in range(len(NUM_PART_TO_TEST))]
                                    for s in range(len(NUM_STM_TO_TEST))]
    actual_num_cycles = [[[0 for b in range(len(BUF_SZ_TO_TEST))] 
                                    for t in range(len(NUM_PART_TO_TEST))]
                                    for s in range(len(NUM_STM_TO_TEST))]



    for tidx in range(0, len(NUM_PART_TO_TEST)):
        NUM_PART = NUM_PART_TO_TEST[tidx]

        for sidx in range(0, len(NUM_STM_TO_TEST)):
            NUM_STM = NUM_STM_TO_TEST[sidx]

            for INPUT_MODE in [0]: #[0, 1, 2, 3]:
                ##### GENERATE INPUTS
                target_partitions_per_input =  generate_input_to_target_partitions(NUM_STM, NUM_PART, INPUT_MODE)
                partition_inputs =  generate_partition_inputs(target_partitions_per_input, NUM_STM, NUM_PART)
                clash_degrees = compute_clash_degrees(target_partitions_per_input, NUM_STM, NUM_PART)

                optimal_cycles = 0
                for p in range(0, NUM_PART):
                    if (len(partition_inputs[p]) > optimal_cycles):
                        optimal_cycles = len(partition_inputs[p])

                print("{:=>250}".format("="))
                #print("INPUT:")
                #for p in range(0, NUM_PART):
                #    if (1): #(NUM_STM==2 and NUM_PART==8):
                #        print(str(partition_inputs[p]))


                for bidx in range(0, len(BUF_SZ_TO_TEST)):
                    BUF_SZ = BUF_SZ_TO_TEST[bidx]
                    print("\n\n\n\nNEW TEST:")
                    arb_total_cycles = 0
                    arb_outputs = compute_arb_outputs(partition_inputs, NUM_STM, NUM_PART, BUF_SZ)
                    LTSC = compute_LTSC( NUM_STM, NUM_PART, BUF_SZ, clash_degrees )

                    print("Best POSSIBLE cycles = {}".format(optimal_cycles))
                    #print_arb_outputs(arb_outputs, NUM_STM, NUM_PART, BUF_SZ)
                    #print_LTSC(LTSC, NUM_STM, NUM_PART, BUF_SZ)

                    #for t in range(0, NUM_PART):
                    #    arb_total_cycles = max(arb_total_cycles, len(arb_outputs[t]))
                    LTSC_total_cycles = max(LTSC[INPUTS_PER_STM-1])

                    print("NUM_PART, NUM_STM, BUF_SZ = ")
                    print(" {},{},{}".format( 
                        NUM_PART, NUM_STM, BUF_SZ)
                    )

                    #if not (arb_total_cycles == LTSC_total_cycles):
                    #    print("ERROR: SOMETHING IS WRONG IN THE PERFMODEL HERE!")

                    print("Best = {}, arb = {}, LTSC = {}".format(
                            optimal_cycles, arb_total_cycles, LTSC_total_cycles)
                    )
                    print(" Expected % of optimal (assuming 1cyc per input) = {}".format(100 * float(LTSC_total_cycles)/float(INPUTS_PER_STM)))

                    #### NOTE: This total speedup refers to the naive-singlestream USING ONLY ONE BRAM PORT Per cycle.
                    numerator = float(2*INPUTS_PER_STM * NUM_STM)       ## 2 because of 2 keys per input.
                    speedup = numerator/float(LTSC_total_cycles)
                    if (speedup > 2*NUM_STM):
                        print("ERROR: SOMETHING IS WRONG in the speedup calculation.")
                        exit(-1)
                    print(" Expected TOTAL SPEEDUP over naive single-stream (assuming 0.5cyc per key) = {}".format(numerator/float(LTSC_total_cycles)))

                    #best_possible_num_cycles[sidx][tidx][bidx]  = optimal_cycles
                    #actual_num_cycles[sidx][tidx][bidx]         = arb_total_cycles


    #plot_cycles(best_possible_num_cycles, 
    #            actual_num_cycles, 
    #            NUM_STM_TO_TEST,
    #            NUM_PART_TO_TEST,
    #            BUF_SZ_TO_TEST
    #)




