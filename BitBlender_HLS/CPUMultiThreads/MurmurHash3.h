#ifndef _MURMURHASH3_H_
#define _MURMURHASH3_H_
#endif

#include <inttypes.h>
#include <stdint.h>
#define LENGTH_MAX 32
#define KEY_SIZE (LENGTH_MAX / 4)

#define NUM_POPULATION_INSERTS (1024*1024)
#define NUM_QUERIES (1024*1024*8)
#define NUM_ITERATIONS (100)

#ifndef NUM_HASH
#define NUM_HASH 10
#endif
#ifndef BV_LENGTH
//#define BV_LENGTH 3512556 //1M insertion
//#define BV_LENGTH 1756278 //512K insertion
//#define BV_LENGTH 1478 // 1 K insert , fp=0.5, each bv is 1478 bits
#define BV_LENGTH 16*1024*1024*NUM_HASH/bit_vector_width // scalable BF for 1M inserts, 1/2 fp each chunk, 10 chunks
#endif

//#define DWIDTH 32
//#define INTERFACE_WIDTH ap_uint<DWIDTH>

const int bit_vector_width = 1;//On-chip memory for BV, packing 32 bits into one cell  
const int key_width = 32;//each key is 512 bits long


#define BV_SECTION_LENGTH BV_LENGTH/NUM_HASH
