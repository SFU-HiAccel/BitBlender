#!/bin/bash
#clear
rm bloom_filter_multi_threads

for h in {5..8};
do
    for l in {4..16..4};
    do
        g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=${h} -DSECTION_LEN_MI=${l} bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
        ./bloom_filter_multi_threads
    done
done



#g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=3  bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
#./bloom_filter_multi_threads
#
#g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=4  bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
#./bloom_filter_multi_threads
#
#g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=5  bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
#./bloom_filter_multi_threads
#
#g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=6  bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
#./bloom_filter_multi_threads
#
#g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=7  bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
#./bloom_filter_multi_threads
#
#g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=8  bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
#./bloom_filter_multi_threads
#
#g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=9  bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
#./bloom_filter_multi_threads
#
#g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=10 bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
#./bloom_filter_multi_threads
#
#g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=11 bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
#./bloom_filter_multi_threads
#
#g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=12 bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
#./bloom_filter_multi_threads

