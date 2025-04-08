
from .types import DesignType 

class HeaderFileGenerator:
    def __init__(self, config):
        self.config = config

    def gen_header(self):
        codeArr = []

        codeArr.append('#ifndef _MURMURHASH3_H_' + "\n")
        codeArr.append('#define _MURMURHASH3_H_' + "\n")
        codeArr.append('//#include <hls_math.h>' + "\n")
        codeArr.append('#include <stdint.h>' + "\n")
        codeArr.append('#include <inttypes.h>' + "\n")
        codeArr.append('#include <ap_int.h>' + "\n")
        codeArr.append('#include <tapa.h>' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('/*****************************/' + "\n")
        codeArr.append('// MACROS USED FOR CALCULATIONS' + "\n")
        codeArr.append('#define CEIL_DIVISION(X, Y) ( (X-1)/Y + 1)' + "\n")
        codeArr.append('// Power of 2 rounding : https://stackoverflow.com/questions/466204/rounding-up-to-next-power-of-2' + "\n")
        codeArr.append('#define K_MSH_(X,Y)             ((X-1) >> Y)' + "\n")
        codeArr.append('#define K_R1_(X)                ( K_MSH_(X,0)   | K_MSH_(X, 1) )' + "\n")
        codeArr.append('#define K_R2_(X)                ( K_R1_(X)      | (K_R1_(X) >> 2) )' + "\n")
        codeArr.append('#define K_R3_(X)                ( K_R2_(X)      | (K_R2_(X) >> 4) )' + "\n")
        codeArr.append('#define K_R4_(X)                ( K_R3_(X)      | (K_R3_(X) >> 8) )' + "\n")
        codeArr.append('#define K_R5_(X)                ( K_R4_(X)      | (K_R4_(X) >> 16 ) )' + "\n")
        codeArr.append('#define ROUND_UP_TO_NEXT_POW_TWO(X)   (K_R5_(X))+1' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#define __TWO_TO_POW_N__(n) \\' + "\n")
        codeArr.append('    (1 << (n))' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#define IS_POWER_OF_TWO(x) \\' + "\n")
        codeArr.append('    (x == __TWO_TO_POW_N__(0) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(1) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(2) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(3) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(4) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(5) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(6) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(7) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(8) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(9) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(10) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(11) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(12) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(13) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(14) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(15) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(16) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(17) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(18) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(19) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(20) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(21) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(22) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(23) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(24) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(25) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(26) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(27) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(28) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(29) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(30) ||\\' + "\n")
        codeArr.append('     x == __TWO_TO_POW_N__(31))' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('/*****************************/' + "\n")
        codeArr.append('' + "\n")

        ######################################################
        codeArr.append('/*****************************/' + "\n")
        codeArr.append('// CONFIGURE ME!' + "\n")
        codeArr.append('#define MULTI_STREAMS_ENABLED (1)' + "\n")
        codeArr.append('#define ENABLE_PERF_CTRS (0)' + "\n")
        codeArr.append('#define NUM_HASH ({})'.format(self.config.num_hash) + "\n")
        codeArr.append('' + "\n")

        if (self.config.design_type == DesignType.NAIVE_MULTISTREAM):
            codeArr.append('#define NAIVE_MULTISTREAM (1)' + "\n")
        else:
            codeArr.append('#define NAIVE_MULTISTREAM (0)' + "\n")
        codeArr.append('' + "\n")

        codeArr.append('#ifndef __SYNTHESIS__' + "\n")
        codeArr.append('    //#define __DO_DEBUG_PRINTS__' + "\n")
        codeArr.append('    #define __DO_THIS_DEBUG_PRINTS__' + "\n")
        codeArr.append('#endif' + "\n")
        codeArr.append('/*****************************/' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('// NOTE: IF THE BV_LENGTH IS NOT A POWER OF TWO, SOME MODULES MAY ACHIEVE POOR II.' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#define NUM_DESIRED_INPUT_KEYS (1024*1024*32)' + "\n")
        codeArr.append('#define BV_DESIRED_LENGTH ((1024*1024*4)*NUM_HASH)' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#define NUM_POPULATION_INPUTS (NUM_DESIRED_INPUT_KEYS>>8)' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#define KEY_BITWIDTH                (32)' + "\n")
        codeArr.append('const int HASHONLY_BITWIDTH         = 32;' + "\n")
        codeArr.append('#define BV_BRAM_PACKED_BITWIDTH     (32)    //On-chip memory for BV, packing this many bits into one cell  ' + "\n")
        codeArr.append('#define BV_URAM_PACKED_BITWIDTH     (64)    //On-chip memory for BV, packing this many bits into one cell  ' + "\n")
        codeArr.append('#define BV_LOAD_BITWIDTH            (BV_URAM_PACKED_BITWIDTH * NUM_HASH)' + "\n")
        codeArr.append('#define OUT_PACKED_BITWIDTH         (KEY_BITWIDTH)' + "\n")
        codeArr.append('const int BIT_BITWIDTH              = 1;' + "\n")
        codeArr.append('#define KEY_SIZE_IN_BYTES           (KEY_BITWIDTH / 8)' + "\n")
        codeArr.append('#define KEY_DTYPE                   ap_uint<KEY_BITWIDTH>' + "\n")
        codeArr.append('#define HASHONLY_DTYPE              ap_uint<HASHONLY_BITWIDTH>' + "\n")
        codeArr.append('#define BV_BRAM_PACKED_DTYPE        ap_uint<BV_BRAM_PACKED_BITWIDTH>' + "\n")
        codeArr.append('#define BV_URAM_PACKED_DTYPE        ap_uint<BV_URAM_PACKED_BITWIDTH>' + "\n")
        codeArr.append('#define OUT_PACKED_DTYPE            ap_uint<OUT_PACKED_BITWIDTH>' + "\n")
        codeArr.append('#define BIT_DTYPE                   ap_uint<BIT_BITWIDTH>' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('typedef struct {' + "\n")
        codeArr.append('    KEY_DTYPE   k0;' + "\n")
        codeArr.append('    KEY_DTYPE   k1;' + "\n")
        codeArr.append('} TWOKEY_DTYPE;' + "\n")
        codeArr.append('' + "\n")


        codeArr.append('typedef struct {' + "\n")

        padded_num_hash = 2**((self.config.num_hash-1).bit_length()) ### The next-highest power of 2
        for h in range(0, padded_num_hash):
            if (h < self.config.num_hash):
                codeArr.append('    BV_URAM_PACKED_DTYPE section{h};'.format(h=h) + "\n")
                codeArr.append('' + "\n")
            else:
                codeArr.append('    BV_URAM_PACKED_DTYPE padding{h};'.format(h=h) + "\n")

        codeArr.append('' + "\n")
        codeArr.append('    #if NUM_HASH != {}'.format(self.config.num_hash) + "\n")
        codeArr.append('    crash_compilation();' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('} BV_LOAD_DTYPE;' + "\n")
        codeArr.append('' + "\n")

        ######################################################
        codeArr.append('#if ENABLE_PERF_CTRS' + "\n")
        codeArr.append('    // For each arb-ratemonitor' + "\n")
        codeArr.append('    // For each shuffle unit' + "\n")
        codeArr.append('    // For each query unit' + "\n")
        codeArr.append('    #define NUM_PERFCTRS ((NUM_ARBITER_ATOMS*BV_NUM_PARTITIONS) + (NUM_HASH) + (1))' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #define PERFCTR_DTYPE uint64_t' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    // Make "enough" space in the buffer for the performance counter to give info.' + "\n")
        codeArr.append('    #define NUM_PERFCTR_OUTPUTS (8)' + "\n")
        codeArr.append('#endif' + "\n")

        ######################################################
        codeArr.append('' + "\n")
        codeArr.append('#if MULTI_STREAMS_ENABLED' + "\n")
        codeArr.append('    #define BV_NUM_PARTITIONS ({}) // each sub bv is further partitioned into this chunks'.format(self.config.num_partitions) + "\n")
        codeArr.append('    #define NUM_STM ({})'.format(self.config.num_stm) + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #define SHUFFLEBUF_SZ ({})   // Number of buffered elements we can have for each hash/partition, in the shuffle buffer.'.format(self.config.shufflebuf_sz) + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #define DEBUG_ARBITER_SINK  ({})'.format(self.config.enable_arbiter_sink) + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #define USING_HIER_ARBITER  (0)' + "\n")
        codeArr.append('    #define USE_SPLIT_QUERY (1)' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    const int STRM_IDX_BITWIDTH = 8;' + "\n")
        codeArr.append('    const int INPUT_IDX_BITWIDTH = 24;' + "\n")
        codeArr.append('    const int MAX_INPUT_IDX = ( 1<<(INPUT_IDX_BITWIDTH) ) - 1;' + "\n")
        codeArr.append('    const int METADATA_BITWIDTH = INPUT_IDX_BITWIDTH + STRM_IDX_BITWIDTH;' + "\n")
        codeArr.append('    const int MAX_STRM_IDX = ( 1<<(STRM_IDX_BITWIDTH) ) - 1;' + "\n")
        codeArr.append('    const int PACKED_HASH_BITWIDTH = HASHONLY_BITWIDTH + METADATA_BITWIDTH;' + "\n")
        codeArr.append('    const int BV_PLUS_METADATA_BITWIDTH = BIT_BITWIDTH + METADATA_BITWIDTH;' + "\n")
        codeArr.append('    const int BV_PLUS_IIDX_BITWIDTH     = BIT_BITWIDTH + INPUT_IDX_BITWIDTH;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #define STRM_IDX_DTYPE      ap_uint<STRM_IDX_BITWIDTH>' + "\n")
        codeArr.append('    #define INPUT_IDX_DTYPE     ap_uint<INPUT_IDX_BITWIDTH>' + "\n")
        codeArr.append('    /************************/' + "\n")
        codeArr.append('    //// Packed datatypes.  Packed as follows (MSB to LSB): [STRM_IDX, INPUT_IDX, HASH_VALUE]' + "\n")
        codeArr.append('    //#define PACKED_HASH_DTYPE   ap_uint<PACKED_HASH_BITWIDTH>' + "\n")
        codeArr.append('    //#define BV_PLUS_METADATA_PACKED_DTYPE     ap_uint<BV_PLUS_METADATA_BITWIDTH>' + "\n")
        codeArr.append('    //#define METADATA_DTYPE      ap_uint<METADATA_BITWIDTH>' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    typedef struct {' + "\n")
        codeArr.append('        INPUT_IDX_DTYPE     iidx;' + "\n")
        codeArr.append('        STRM_IDX_DTYPE      sidx;' + "\n")
        codeArr.append('    } METADATA_DTYPE;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    typedef struct {' + "\n")
        codeArr.append('        BIT_DTYPE           bv_val;' + "\n")
        codeArr.append('        METADATA_DTYPE      md;' + "\n")
        codeArr.append('    } BV_PLUS_METADATA_PACKED_DTYPE;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    typedef struct {' + "\n")
        codeArr.append('        BIT_DTYPE           bv_val;' + "\n")
        codeArr.append('        INPUT_IDX_DTYPE     iidx;' + "\n")
        codeArr.append('    } BV_PLUS_IIDX_PACKED_DTYPE;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    typedef struct {' + "\n")
        codeArr.append('        HASHONLY_DTYPE      hash;' + "\n")
        codeArr.append('        METADATA_DTYPE      md;' + "\n")
        codeArr.append('    } PACKED_HASH_DTYPE;' + "\n")
        codeArr.append('    /************************/' + "\n")
        codeArr.append('    #define _BV_ROUNDING_FACTOR_                    (NUM_HASH * BV_URAM_PACKED_BITWIDTH * BV_NUM_PARTITIONS)' + "\n")
        codeArr.append('    #define BV_LENGTH                               (CEIL_DIVISION(BV_DESIRED_LENGTH, _BV_ROUNDING_FACTOR_) * _BV_ROUNDING_FACTOR_)' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #define BV_NUM_BRAM_PARTITIONS                      CEIL_DIVISION(BV_NUM_PARTITIONS, 4)' + "\n")
        codeArr.append('    #define BV_NUM_URAM_PARTITIONS                      (BV_NUM_PARTITIONS - BV_NUM_BRAM_PARTITIONS)' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('    #define BV_NUM_LOADS                                CEIL_DIVISION(BV_LENGTH, BV_LOAD_BITWIDTH)' + "\n")
        codeArr.append('    #define BV_SECTION_LENGTH                           CEIL_DIVISION(BV_LENGTH, NUM_HASH)' + "\n")
        codeArr.append('    #define BV_SECTION_LENGTH_IN_URAM_PACKED_ELEMS      CEIL_DIVISION(BV_LENGTH, (NUM_HASH*BV_URAM_PACKED_BITWIDTH))' + "\n")
        codeArr.append('    #define BV_PARTITION_LENGTH                         CEIL_DIVISION(BV_LENGTH, (NUM_HASH*BV_NUM_PARTITIONS))' + "\n")
        codeArr.append('    #define BV_PARTITION_LENGTH_IN_BRAM_PACKED_ELEMS    CEIL_DIVISION(BV_LENGTH, (NUM_HASH*BV_BRAM_PACKED_BITWIDTH*BV_NUM_PARTITIONS))' + "\n")
        codeArr.append('    #define BV_PARTITION_LENGTH_IN_URAM_PACKED_ELEMS    CEIL_DIVISION(BV_LENGTH, (NUM_HASH*BV_URAM_PACKED_BITWIDTH*BV_NUM_PARTITIONS))' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#else // MULTI_STREAMS_ENABLED' + "\n")
        codeArr.append('    #define NUM_STM (1)' + "\n")
        codeArr.append('    #define BV_NUM_PARTITIONS (1)' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#endif // MULTI_STREAMS_ENABLED' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")


        codeArr.append('typedef struct {' + "\n")

        for s in range(0, self.config.keys_axi_port_pack_factor):
            if (s < self.config.num_stm):
                codeArr.append('    KEY_DTYPE    s{s}_k0;'.format(s=s) + "\n")
                codeArr.append('    KEY_DTYPE    s{s}_k1;'.format(s=s) + "\n")
                codeArr.append('' + "\n")
            else:
                codeArr.append('    KEY_DTYPE    padding_{s}_k0;'.format(s=s) + "\n")
                codeArr.append('    KEY_DTYPE    padding_{s}_k1;'.format(s=s) + "\n")
                codeArr.append('' + "\n")

        codeArr.append('    #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('    crash on purpose(,' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('} LOAD_DTYPE;' + "\n")
        codeArr.append('#if KEY_BITWIDTH != 32' + "\n")
        codeArr.append('crash on purpose(,' + "\n")
        codeArr.append('We need to add support for different key-bitwidths in the LOAD_DTYPE!!'+ "\n")
        codeArr.append('#endif' + "\n")

        codeArr.append('// This naming is potentially confusing - we datapack TWICE.' + "\n")
        codeArr.append('// Within each key-stream we pack 32 elements together.' + "\n")
        codeArr.append('// Then, we coalesce among key-streams.' + "\n")
        codeArr.append('typedef struct {' + "\n")

        for s in range(0, self.config.keys_axi_port_pack_factor):
            if (s < self.config.num_stm):
                codeArr.append('    OUT_PACKED_DTYPE    s{s}_k0;'.format(s=s) + "\n")
                codeArr.append('    OUT_PACKED_DTYPE    s{s}_k1;'.format(s=s) + "\n")
                codeArr.append('' + "\n")
            else:
                codeArr.append('    OUT_PACKED_DTYPE    padding_{s}_k0;'.format(s=s) + "\n")
                codeArr.append('    OUT_PACKED_DTYPE    padding_{s}_k1;'.format(s=s) + "\n")
                codeArr.append('' + "\n")

        codeArr.append('    #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('    crash on purpose(,' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('} STORE_DTYPE;' + "\n")
        codeArr.append('#if OUT_PACKED_BITWIDTH!= 32' + "\n")
        codeArr.append('crash on purpose(,' + "\n")
        codeArr.append('We need to add support for different out-packing-bitwidths in the STORE_DTYPE!!'+ "\n")
        codeArr.append('#endif' + "\n")






        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('/***************************************************/' + "\n")
        codeArr.append('/***************************************************/' + "\n")
        codeArr.append('/***************************************************/' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('/* STM_DEPTH: In the worst case, the arbiter can send all of the hashed values to the same FIFO.' + "\n")
        codeArr.append(' *  So that FIFO will get filled, and the shuffle unit wont be able to handle it.' + "\n")
        codeArr.append(' *  We need at least NUM_STM FIFO elements between arbiter and shuffle. */' + "\n")
        codeArr.append('#if (CEIL_DIVISION(NUM_STM, 2) < 2)' + "\n")
        codeArr.append('    #define STM_DEPTH (2)   // If less than 2, CSIM is very slow.' + "\n")
        codeArr.append('#else' + "\n")
        codeArr.append('    #define STM_DEPTH (CEIL_DIVISION(NUM_STM, 2))' + "\n")
        codeArr.append('#endif //(CEIL_DIVISION(NUM_STM, 2) < 2)' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#define KEYS_PER_STM                (ROUND_UP_TO_NEXT_POW_TWO( CEIL_DIVISION(NUM_DESIRED_INPUT_KEYS, NUM_STM) ))' + "\n")
        codeArr.append('const int KEYPAIRS_PER_STM          = KEYS_PER_STM/2;   // 2 reads per cycle (2port bram)' + "\n")
        codeArr.append('#define TOTAL_NUM_KEYINPUT          (KEYS_PER_STM * NUM_STM)' + "\n")
        codeArr.append('const int PACKED_OUTPUTS_PER_STM    = CEIL_DIVISION(KEYPAIRS_PER_STM, OUT_PACKED_BITWIDTH);' + "\n")
        codeArr.append('const int PACKED_OUTPAIRS_PER_STM   = PACKED_OUTPUTS_PER_STM * 2;   // same number of outputs but half the stms if we pair them' + "\n")
        codeArr.append('const int NUM_PACKED_OUTPUTS        = PACKED_OUTPUTS_PER_STM * NUM_STM * 2;   // 2 reads per cycle (2port bram)' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#define NUM_ARBITER_ATOMS       (NUM_STM - 1)' + "\n")
        codeArr.append('typedef struct {' + "\n")
        for i in range(0, self.config.num_stm):
            codeArr.append('    INPUT_IDX_DTYPE strm{}_out_idx;'.format(i) + "\n")
        codeArr.append('    #if NUM_STM != {}'.format(self.config.num_stm) + "\n")
        codeArr.append('    crash!' + "\n")
        codeArr.append('    #endif' + "\n")
        codeArr.append('} RATEMON_FEEDBACK_DTYPE;' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('' + "\n")
        codeArr.append('#endif  // _MURMURHASH3_H_' + "\n")

        return codeArr

    def generate(self):
        codeArr = []
        codeArr.extend(self.gen_header())
        return codeArr


























