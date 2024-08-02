
class SWMurmurHashGenerator:
    def __init__(self, config):
        self.config = config


    def generate_SW_MurmurHash_x86_32(self):
        codeArr = []


        codeArr.append(

"""//-----------------------------------------------------------------------------
// MurmurHash3 was written by Austin Appleby, and is placed in the public domain.

// Note - The x86 and x64 versions do _not_ produce the same results, as the
// algorithms are optimized for their respective platforms. You can still
// compile and run any of them on any platform, but your performance with the
// non-native version will be less than optimal.

#include <stdint.h>

//-----------------------------------------------------------------------------
// Platform-specific functions and macros

#ifdef __GNUC__
#define FORCE_INLINE __attribute__((always_inline)) inline
#else
#define FORCE_INLINE inline
#endif

static FORCE_INLINE uint32_t rotl32 ( uint32_t x, int8_t r )
{
    return (x << r) | (x >> (32 - r));
}

#define	ROTL32(x,y)	rotl32(x,y)

//-----------------------------------------------------------------------------
// Block read - if your platform needs to do endian-swapping or can only
// handle aligned reads, do the conversion here

#define getblock(p, i) (p[i])

//-----------------------------------------------------------------------------
// Finalization mix - force all bits of a hash block to avalanche

static FORCE_INLINE uint32_t fmix32 ( uint32_t h )
{
    h ^= h >> 16;
    h *= 0x85ebca6b;
    h ^= h >> 13;
    h *= 0xc2b2ae35;
    h ^= h >> 16;

    return h;
}

//-----------------------------------------------------------------------------

uint32_t SW_MurmurHash3_x86_32 (KEY_DTYPE key,
                                int len,
                                uint32_t seed
) {
    const void * key_p = (void*)&key;
    const uint8_t * data = (const uint8_t*)key_p;
    const int nblocks = len / 4;
    int i;

    uint32_t h1 = seed;

    uint32_t c1 = 0xcc9e2d51;
    uint32_t c2 = 0x1b873593;

    //----------
    // body

    const uint32_t * blocks = (const uint32_t *)(data + nblocks*4);

    for(i = -nblocks; i; i++)
    {
        uint32_t k1 = getblock(blocks,i);

        k1 *= c1;
        k1 = ROTL32(k1,15);
        k1 *= c2;
        
        h1 ^= k1;
        h1 = ROTL32(h1,13); 
        h1 = h1*5+0xe6546b64;

        #if PRINT_HASH_VALUES
        printf("HOST DEBUG: key = %d, k1 = %d, h1 = %d, i = %d\\n",
                key.to_int(), k1, h1, i
        );
        #endif
    }

    //----------
    // tail

    const uint8_t * tail = (const uint8_t*)(data + nblocks*4);

    uint32_t k1 = 0;

    switch(len & 3)
    {
        case 3: k1 ^= tail[2] << 16;
        case 2: k1 ^= tail[1] << 8;
        case 1: k1 ^= tail[0];
                k1 *= c1; k1 = ROTL32(k1,15); k1 *= c2; h1 ^= k1;
    };

    //----------
    // finalization

    h1 ^= len;

    h1 = fmix32(h1);

    //// TEMP: NOT USING REAL HASH FUNCTION.
    //uint32_t h1 = (uint32_t)key * (seed+3);

    return h1;
} 
"""
        )

        return codeArr


    def generate(self):
        codeArr = []
        codeArr.extend(self.generate_SW_MurmurHash_x86_32())
        return codeArr





















