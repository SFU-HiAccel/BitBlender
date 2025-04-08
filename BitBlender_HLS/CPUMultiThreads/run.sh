#!/bin/bash
#clear
rm bloom_filter_multi_threads

g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=3  -DLARGE_INPUT bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
./bloom_filter_multi_threads

g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=4  -DLARGE_INPUT bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
./bloom_filter_multi_threads

g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=5  -DLARGE_INPUT bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
./bloom_filter_multi_threads

g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=6  -DLARGE_INPUT bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
./bloom_filter_multi_threads

g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=7  -DLARGE_INPUT bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
./bloom_filter_multi_threads

g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=8  -DLARGE_INPUT bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
./bloom_filter_multi_threads

g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=9  -DLARGE_INPUT bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
./bloom_filter_multi_threads

g++ -std=c++11 -fopenmp -Ofast -march=native  -DNUM_HASH=10 -DLARGE_INPUT bloom_filter_multi_threads.cpp -o bloom_filter_multi_threads
./bloom_filter_multi_threads

