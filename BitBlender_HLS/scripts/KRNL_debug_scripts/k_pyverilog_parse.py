import sys
import os
from pyverilog.vparser import parser

VERILOG_FOLDER = "../_x.hw_emu.xilinx_u280_xdma_201920_3/hdl"

if __name__ == "__main__":
    filenames = os.listdir(VERILOG_FOLDER)


    codeparser = parser.VerilogCodeParser(
        filenames,
        preprocess_output=os.path.join(os.getcwd(), "preprocess.output"),
        outputdir=os.getcwd(),
        debug=True,
    )
    codeparser.parse()

    for fname in filenames:
        print("PARSING FILE: {}".format(fname))

        total_fname = os.path.join(VERILOG_FOLDER, fname)
        files = [fname]
        f = open(total_fname, "r")

        codeparser = parser.VerilogCodeParser(
            files,
            preprocess_output=os.path.join(os.getcwd(), "preprocess.output"),
            outputdir=os.getcwd(),
            debug=True,
        )
        codeparser.parse()


