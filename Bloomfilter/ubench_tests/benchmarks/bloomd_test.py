import timeit
import time
import pprint
from pybloomd.pybloomd import BloomdClient





if __name__ == "__main__":
    NUM_POPULATION_INPUTS = 1000000
    NUM_QUERIES = 2**24
    # Create a client to a local bloomd server, default port
    client = BloomdClient(["localhost"])
    pp = pprint.PrettyPrinter(indent=4)
    
    for BATCH_SIZE in [1000, 10000, 100000, 1000000]:
        my_filter = client.create_filter("a")
        filter_name = my_filter.KNNY_get_name()
        
        ##############################
        ##############################
        ### POPULATION

        pop_inputs = []
        for i in range(0, int(NUM_POPULATION_INPUTS/BATCH_SIZE)):
            batch = [str(x) for x in range(i*BATCH_SIZE, (i+1)*BATCH_SIZE)]
            pop_inputs.append( batch )

        #pp.pprint(pop_inputs)
        start = timeit.default_timer()
        for i in range(0, int(NUM_POPULATION_INPUTS/BATCH_SIZE)):
            my_filter.add(pop_inputs[i])

        pop_time = timeit.default_timer() - start
        print("Time to populate with {p:,} inputs batched into {b:,} = {t}".format(p=NUM_POPULATION_INPUTS, b=BATCH_SIZE, t=pop_time))

        ##############################
        ##############################
        ### QUERYING

        ### MANUALLY BUILD the commands to send, and use my own functions that I added to the bloomdclient.
        ### Because their commands spend a lot of time doing python data structure stuff.
        ### I need to preprocess all of that.
        query_commands = []
        for i in range(0, int(NUM_QUERIES/BATCH_SIZE)):
            ### A multi-query command is of the form "m ${filter_name} ${QUERIES}"
            batch = [str(x) for x in range(i*BATCH_SIZE, (i+1)*BATCH_SIZE)]
            query_string = ("m %s " % filter_name) + " ".join(batch)
            query_commands.append( query_string )
            
        #pp.pprint(query_commands)
        start = timeit.default_timer()
        for i in range(0, int(NUM_QUERIES/BATCH_SIZE)):
            my_filter.KNNY_multi_with_command(query_commands[i])

        query_time = timeit.default_timer() - start
        print("Time to query with {q:,} inputs batched into {b:,} = {t}".format(q=NUM_QUERIES, b=BATCH_SIZE, t=query_time))
        
        my_filter.drop()
        time.sleep(5)
