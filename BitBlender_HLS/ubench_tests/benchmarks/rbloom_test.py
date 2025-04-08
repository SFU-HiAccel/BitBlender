import timeit
from rbloom import Bloom


if __name__ == "__main__":

    NUM_POPULATION_INPUTS = [1000, 1000000, 100000000]

    for PINPUTS in NUM_POPULATION_INPUTS:
        print("NUM POPULATION INPUTS = {}".format(PINPUTS))
        NUM_QUERIES = 2**23

        bf = Bloom(PINPUTS, 0.01)

        for i in range(0, PINPUTS):
            bf.add(i)

        start = timeit.default_timer()
        for i in range(0, NUM_QUERIES):
            i in bf
        end = timeit.default_timer()

        total = end-start

        print("Total time for {q} queries = {t}".format(q=NUM_QUERIES, t=total))


