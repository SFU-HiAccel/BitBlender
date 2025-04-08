
import math
from pprint import pprint
import random
import numpy as np
from typing import Dict, List, Tuple


#import matplotlib.pyplot as plt


INPUTS_PER_STM = 2500


class Packet_T:
    def __init__(self, sidx=-1, iidx=-1):
        self.stm_idx = sidx
        self.in_idx = iidx

    def is_valid(self):
        if (self.stm_idx == -1 and self.in_idx == -1):
            return 0
        else:
            return 1

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





def print_arb_outputs(
    arb_outputs : List[List[Packet_T]]
    ,NUM_STM : int
    ,NUM_PART : int
    ,BUF_SZ : int
) -> None:

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






def print_LTSC(
    LTSC : List[List[int]]
    ,NUM_STM : int
    ,NUM_PART : int
    ,BUF_SZ : int
) -> None:

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
Using the performance model, build the LTSC (Last T-Send Cycle) array.
    LTSC(t,k) = The last cycle that input #k, from each stream, is sent to partition t.
"""
def compute_LTSC(
    NUM_STM : int
    ,NUM_PART : int
    ,BUF_SZ : int
    ,all_clash_degrees=None
    ,num_inputs_per_stm=INPUTS_PER_STM
) -> List[List[int]]:

    num_generator = np.random.default_rng(seed=2024)
    LastTSendCycle_arr : List[List[int]] = []
    #ARBITER_NUM_STAGES = math.ceil( math.log2(NUM_STM) )
    #ARBITER_FEEDBACK_LATENCY = 3*ARBITER_NUM_STAGES + 4
    ARB_NUM_STAGES_NOTROUNDED = math.log2(NUM_STM)
    ARBNODE_LATENCY = 3*ARB_NUM_STAGES_NOTROUNDED
    ARBRATEMON_LATENCY = 4
    ARBITER_FEEDBACK_LATENCY = ARBNODE_LATENCY + ARBRATEMON_LATENCY

    choice_frequencies = [0, 0, 0, 0]

    for k in range(0, num_inputs_per_stm):
        tmpTSC_arr = []
        TESTING_ARR = []

        ##################
        ### Compute the clash-degrees
        if (all_clash_degrees == None):
            curK_clash_degrees = []

            #### Here, we sample a binomial distribution.
            for t in range(0, NUM_PART):
                success_probability = 1 / NUM_PART
                sample = num_generator.binomial(NUM_STM, success_probability)
                curK_clash_degrees.append( sample )

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

            #####################
            ### TESTING CODE
            tmp_testing = max(choice1, choice2, choice3)

            if (tmp_testing == choice1):
                choice_frequencies[0] += 1
            if (tmp_testing == choice2):
                choice_frequencies[1] += 1
            if (tmp_testing == choice3):
                choice_frequencies[2] += 1

            ### TESTING_ARR.append( [choice1, choice2, choice3] )
            #####################

            sel = max(choice1, choice2, choice3) + curK_clash_degrees[t]
            tmpTSC_arr.append( sel )

        ### pprint(TESTING_ARR)

        LastTSendCycle_arr.append(tmpTSC_arr)
        ##################

    #print("CHOICE FREQUENCIES (with total inputs = {}): {}, {}, {}".format(
    #    INPUTS_PER_STM * NUM_STM,
    #    choice_frequencies[0], choice_frequencies[1], choice_frequencies[2])
    #)

    #pprint(LastTSendCycle_arr)
    return LastTSendCycle_arr






"""
Build the clash-degrees array:
    clash_degrees[k][t] = the clash-degree on partition t, for input index k.
"""
def compute_clash_degrees(
    target_partitions_per_input : List[List[int]]
    ,NUM_STM : int
    ,NUM_PART : int
) -> List[List[int]]:

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
def compute_arb_outputs(
    partition_inputs : List[List[Packet_T]]
    ,NUM_STM : int
    ,NUM_PART : int
    ,BUF_SZ : int
) -> List[List[Packet_T]]:

    print("WARNING: This function isn't expected to work very well to model the ratemonitor feedback latency.")

    last_send_cycle_KminusB : List[int]             = [0] * BUF_SZ
    last_T_send_cycle       : List[int]             = [0] * NUM_PART
    read_ptrs               : List[int]             = [0] * NUM_PART
    partition_outputs       : List[List[Packet_T]]  = []
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
generate NUM_STM target partitions (one for each input in the set).

Generates a list of lists - the 0'th element in sublist 2 is STREAM 2's target partition
for the 0'th key. (NUM_HASH doesn't matter - different hashes are assumed independent)
"""
def generate_input_to_target_partitions(
    NUM_STM : int
    ,NUM_PART : int
    ,MODE : int
) -> List[List[int]]:

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
assuming NO ratemonitoring (i.e. without bubbles).
"""
def generate_partition_inputs(
    target_partitions_per_input
    ,NUM_STM
    ,NUM_PART
) -> List[List[Packet_T]]:

    partition_inputs : List[List[Packet_T]] = []

    ### Use the input -> partition mapping to generate the inputs of each partition
    for part_idx in range(0, NUM_PART):
        cur_part_inputs : List[Packet_T] = []

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
def plot_cycles(
    best : List[List[List[int]]]
    ,actual : List[List[List[int]]]
    ,S_arr : List[int]
    ,T_arr : List[int]
    ,B_arr : List[int]
):
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





"""
Compute and print the performance estimates, for a given S, T, B config,
and given the randomly-generated inputs and clash degrees.
"""
def compute_expected_perf_for_one_config(
    NUM_STM : int
    ,NUM_PART : int
    ,BUF_SZ : int
    ,partition_inputs : List[List[Packet_T]]
    ,clash_degrees : List[List[int]]
) -> None:
    arb_total_cycles = 0

    ### Simulate the inputs, or sample from a random distribution.
    LTSC_simulated = compute_LTSC( NUM_STM, NUM_PART, BUF_SZ, all_clash_degrees=clash_degrees )
    LTSC_rv = compute_LTSC( NUM_STM, NUM_PART, BUF_SZ, all_clash_degrees=None )

    ##arb_outputs = compute_arb_outputs(partition_inputs, NUM_STM, NUM_PART, BUF_SZ)
    ### print_arb_outputs(arb_outputs, NUM_STM, NUM_PART, BUF_SZ)
    ### print_LTSC(LTSC, NUM_STM, NUM_PART, BUF_SZ)
    ##for t in range(0, NUM_PART):
    ##    arb_total_cycles = max(arb_total_cycles, len(arb_outputs[t]))

    LTSC_sim_total_cycles = max(LTSC_simulated[INPUTS_PER_STM-1])
    LTSC_rv_total_cycles = max(LTSC_rv[INPUTS_PER_STM-1])
    ###if not (arb_total_cycles == LTSC_sim_total_cycles):
    ###    print("ERROR: SOMETHING IS WRONG IN THE PERFMODEL HERE!")
    ###    #raise AssertionError()

    print("NUM_PART, NUM_STM, BUF_SZ = ")
    print(" {},{},{}".format( 
        NUM_PART, NUM_STM, BUF_SZ)
    )

    print("Theoretically best possible = {}, arb = {}, simulated = {}, estimated = {}".format(
            optimal_cycles_infB,
            arb_total_cycles,
            LTSC_sim_total_cycles,
            LTSC_rv_total_cycles,
            )
    )
    cycles_per_query = float(LTSC_rv_total_cycles)/float(INPUTS_PER_STM)
    print(" Expected cycles, as a % of inputs-per-stm (e.g. if we assume 1cyc per input) = 1/efficiency = {}%".format(cycles_per_query*100))

    f = open("out.csv", "a")
    f.write("{T},{S},{B},{cyc}\n".format(T=NUM_PART, S=NUM_STM, B=BUF_SZ, cyc=cycles_per_query))

    #### NOTE: This total speedup refers to the naive-singlestream USING TWO BRAM PORTS Per cycle.
    numerator = float(INPUTS_PER_STM * NUM_STM)
    speedup = numerator/float(LTSC_rv_total_cycles)
    if (speedup > NUM_STM):
        print("ERROR: SOMETHING IS WRONG in the speedup calculation.")
        exit(-1)
    print(" Expected TOTAL SPEEDUP over naive single-stream (assuming 0.5cyc per key) = {}".format(speedup))





if __name__ == "__main__":
    print("")
    random.seed(5)

    NUM_PART_TO_TEST = [3,4,5,6,7,8,9,10,11,12]
    NUM_STM_TO_TEST = [3,4,5,6,7,8,9]
    BUF_SZS_TO_TEST = [2,4,8,16]
    best_possible_num_cycles = [[[0 for b in range(len(BUF_SZS_TO_TEST))] 
                                    for t in range(len(NUM_PART_TO_TEST))]
                                    for s in range(len(NUM_STM_TO_TEST))]
    actual_num_cycles = [[[0 for b in range(len(BUF_SZS_TO_TEST))] 
                                    for t in range(len(NUM_PART_TO_TEST))]
                                    for s in range(len(NUM_STM_TO_TEST))]



    for tidx in range(0, len(NUM_PART_TO_TEST)):
        NUM_PART = NUM_PART_TO_TEST[tidx]

        for sidx in range(0, len(NUM_STM_TO_TEST)):
            NUM_STM = NUM_STM_TO_TEST[sidx]

            for INPUT_MODE in [0]: #[0, 1, 2, 3]:
                print("{:=>250}".format("="))

                #### GENERATE INPUTS
                target_partitions_per_input = generate_input_to_target_partitions(NUM_STM, NUM_PART, INPUT_MODE)
                partition_inputs = generate_partition_inputs(target_partitions_per_input, NUM_STM, NUM_PART)
                clash_degrees = compute_clash_degrees(target_partitions_per_input, NUM_STM, NUM_PART)

                optimal_cycles_infB = 0
                for p in range(0, NUM_PART):
                    if (len(partition_inputs[p]) > optimal_cycles_infB):
                        optimal_cycles_infB = len(partition_inputs[p])

                for bidx in range(0, len(BUF_SZS_TO_TEST)):
                    BUF_SZ = BUF_SZS_TO_TEST[bidx]
                    print("\n\n\n\nNEW TEST:")
                    compute_expected_perf_for_one_config(
                        NUM_STM,
                        NUM_PART,
                        BUF_SZ,
                        partition_inputs,
                        clash_degrees
                    )


    #plot_cycles(best_possible_num_cycles, 
    #            actual_num_cycles, 
    #            NUM_STM_TO_TEST,
    #            NUM_PART_TO_TEST,
    #            BUF_SZS_TO_TEST
    #)




