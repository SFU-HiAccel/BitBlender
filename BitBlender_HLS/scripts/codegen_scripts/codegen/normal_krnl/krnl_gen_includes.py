
class IncludesCodeGenerator:
    def __init__(self, config):
        self.config = config

    def generate(self):
        codeArr = []
        
        codeArr.append("""
//#ifndef __SYNTHESIS__
//    #include <time.h>
//#endif

#include "MurmurHash3.h"

#if NAIVE_MULTISTREAM != 0
void crash_compilation(
crash compilation.
}
#endif
"""
        )
        codeArr.append("\n\n")
        return codeArr
