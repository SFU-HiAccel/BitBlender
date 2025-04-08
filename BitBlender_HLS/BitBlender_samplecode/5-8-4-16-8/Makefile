

.PHONY: help

help::
	$(ECHO) "Makefile Usage:"
	$(ECHO) "  make check TARGET=<sw_emu/hw_emu/hw>"
	$(ECHO) "	  Command to run application in emulation."
	$(ECHO) ""
	$(ECHO) "  make build TARGET=<sw_emu/hw_emu/hw>"
	$(ECHO) "	  Command to build xclbin application."
	$(ECHO) ""
	$(ECHO) "  make clean "
	$(ECHO) "	  Command to remove the generated non-hardware files."
	$(ECHO) ""
	$(ECHO) "  make cleanall"
	$(ECHO) "	  Command to remove all the generated files."
	$(ECHO) ""

# Points to top directory of Git repository
COMMON_REPO = /localhdd/kenny/BloomFilter/Bloomfilter/
#COMMON_REPO = /scratch/hpc-prf-haqc/kenny/BloomFilter/Bloomfilter/
PWD = $(shell readlink -f .)
ABS_COMMON_REPO = $(shell readlink -f $(COMMON_REPO))

#VERSION := singlestream
VERSION := new_multistream
#VERSION := naive_multistream

ifeq ($(VERSION), singlestream)
	APP = singlestream_MurmurHash3
else ifeq ($(VERSION), new_multistream)
	APP = multistream_MurmurHash3
else ifeq ($(VERSION), naive_multistream)
	APP = naive_multistream_MurmurHash3
endif
KERNEL = workload
#DEVICE := xilinx_u200_xdma_201830_2
#DEVICE := xilinx_u280_xdma_201920_3
#DEVICE := xilinx_u280_gen3x16_xdma_1_202211_1
#DEVICE := xilinx_u50_gen3x16_xdma_5_202210_1
DEVICE := xilinx_u280_xdma_201920_3
TARGET := hw
HOST_ARCH := x86
SYSROOT :=

#Include Libraries
include $(ABS_COMMON_REPO)/utils.mk
include $(ABS_COMMON_REPO)/common/includes/opencl/opencl.mk
include $(ABS_COMMON_REPO)/common/includes/xcl2/xcl2.mk

XSA := $(call device2xsa, $(DEVICE))
TEMP_DIR := ./_x.$(TARGET)_$(APP).$(XSA)
BUILD_DIR := ./build_dir.$(TARGET).$(XSA)

###VPP := v++ --profile_kernel=data:all:all:all
VPP := v++


LDFLAGS += $(xcl2_LDFLAGS)
HOST_SRCS += $(xcl2_SRCS)

ifeq ($(VERSION), new_multistream)
	DEFINE_FLAGS = -DNAIVE_MULTISTREAM=0
else ifeq ($(VERSION), naive_multistream)
	DEFINE_FLAGS = -DNAIVE_MULTISTREAM=1
endif

ifeq ($(TARGET),$(filter $(TARGET),hw))
	TAPAC_FLAGS=	--enable-synth-util \
					--run-floorplanning \
					--constraint build_script/knn_floorplan.tcl \
					--enable-hbm-binding-adjustment \

else
	TAPAC_FLAGS=
endif


CXXFLAGS += $(opencl_CXXFLAGS) $(DEFINE_FLAGS) -Wall -O0 -g -std=c++17
### ADDING THIS because v2021.2 moved it's include files.... stupid.
CXXFLAGS += -I$(XILINX_HLS)/include
CXXFLAGS += -fmessage-length=0

LDFLAGS += $(opencl_LDFLAGS)
LDFLAGS += -lrt -lstdc++
LDFLAGS += -ltapa -lfrt -lglog -lgflags

HOST_SRCS += src/host.cpp
BLOOMFILTER_SRCS += src/$(APP).cpp


ifeq ($(TARGET),$(filter $(TARGET),sw_emu))
	CHECK_DEPENDENCY=$(EXECUTABLE)
else
	CHECK_DEPENDENCY=all
endif

CONFIGFILE = src/MurmurHash3.h
INIFILE = src/MurmurHash3.ini
LDCLFLAGS += --config $(INIFILE) 

# Adding config files to linker
EXECUTABLE = host
CMD_ARGS = $(BUILD_DIR)/$(APP).xclbin
EMCONFIG_DIR = $(TEMP_DIR)

KRNL_XCLBIN += $(BUILD_DIR)/$(APP).xclbin
KRNL_XO_FILE += $(TEMP_DIR)/$(APP).xo

CP = cp -rf

.PHONY: all clean cleanall docs emconfig
all: check-devices $(EXECUTABLE) $(KRNL_XCLBIN) emconfig

.PHONY: exe
exe: $(EXECUTABLE)

.PHONY: build
build: $(KRNL_XCLBIN)


ifeq ($(TARGET),$(filter $(TARGET),hw))
.PHONY: MODIFY_CONFIGFILE
MODIFY_CONFIGFILE: $(CONFIGFILE)
	sed -i 's/^#define NUM_DESIRED_INPUT_KEYS.*/#define NUM_DESIRED_INPUT_KEYS (1024*1024*8*NUM_STM)/' $(CONFIGFILE)
	sed -i 's/^#define BV_DESIRED_LENGTH.*/#define BV_DESIRED_LENGTH ((1024*1024*8)*NUM_HASH)/' $(CONFIGFILE)
	sed -i 's/^#define NUM_POPULATION_INPUTS.*/#define NUM_POPULATION_INPUTS ((1024*128)*NUM_STM)/' $(CONFIGFILE)

else    ### SW or HW EMULATION
.PHONY: MODIFY_CONFIGFILE
MODIFY_CONFIGFILE: $(CONFIGFILE)
	sed -i 's/^#define NUM_DESIRED_INPUT_KEYS.*/#define NUM_DESIRED_INPUT_KEYS (256*8*NUM_STM)/' $(CONFIGFILE)
	sed -i 's/^#define BV_DESIRED_LENGTH.*/#define BV_DESIRED_LENGTH ((128*8)*NUM_HASH)/' $(CONFIGFILE)
	sed -i 's/^#define NUM_POPULATION_INPUTS.*/#define NUM_POPULATION_INPUTS ((2*128)*NUM_STM)/' $(CONFIGFILE)
	###sed -i 's/^#define NUM_DESIRED_INPUT_KEYS.*/#define NUM_DESIRED_INPUT_KEYS (1024*1*NUM_STM)/' $(CONFIGFILE)
	###sed -i 's/^#define BV_DESIRED_LENGTH.*/#define BV_DESIRED_LENGTH (512*(NUM_HASH))/' $(CONFIGFILE)
	###sed -i 's/^#define NUM_POPULATION_INPUTS.*/#define NUM_POPULATION_INPUTS (64*1*NUM_STM)/' $(CONFIGFILE)

endif


# Building kernel
$(KRNL_XO_FILE): $(BLOOMFILTER_SRCS) MODIFY_CONFIGFILE $(INIFILE)
	mkdir -p $(TEMP_DIR)
	mkdir -p build_script
	tapac \
		--work-dir $(TEMP_DIR) \
		--top $(KERNEL) \
          --part-num xcu280-fsvh2892-2L-e \
		--platform $(DEVICE) \
		--clock-period 4.44 \
		-o $(TEMP_DIR)/$(APP).xo \
		--max-parallel-synth-jobs 18 \
		--run-tapacc \
		--run-hls \
		--generate-top-rtl \
		--generate-task-rtl \
		--pack-xo \
		--connectivity $(INIFILE) \
		--read-only-args key.* \
		--read-only-args input.* \
		--write-only-args out.* \
		$(TAPAC_FLAGS) \
		src/$(APP).cpp


ifeq ($(TARGET),$(filter $(TARGET),hw))
$(KRNL_XCLBIN): $(KRNL_XO_FILE)

	chmod +x $(TEMP_DIR)/$(APP)_generate_bitstream.sh
	$(TEMP_DIR)/$(APP)_generate_bitstream.sh
else
$(KRNL_XCLBIN): $(KRNL_XO_FILE)
	chmod +x $(TEMP_DIR)/$(APP)_generate_bitstream.sh
	sed -i 's/TARGET=hw\>/#TARGET=hw/ ; s/^# TARGET=hw_emu/TARGET=hw_emu/ ; s/^# DEBUG=-g/DEBUG=-g/' $(TEMP_DIR)/$(APP)_generate_bitstream.sh
	$(TEMP_DIR)/$(APP)_generate_bitstream.sh
endif

# Building Host
$(EXECUTABLE): check-xrt $(HOST_SRCS) MODIFY_CONFIGFILE $(BLOOMFILTER_SRCS) $(HOST_HDRS)
	$(CXX) $(CXXFLAGS) $(HOST_SRCS) $(BLOOMFILTER_SRCS) $(HOST_HDRS) -o '$@' $(LDFLAGS)

emconfig:$(EMCONFIG_DIR)/emconfig.json
$(EMCONFIG_DIR)/emconfig.json:
	emconfigutil --platform $(DEVICE) --od $(EMCONFIG_DIR)



hostbinary: $(EXECUTABLE)



check: $(CHECK_DEPENDENCY)
ifeq ($(TARGET),$(filter $(TARGET),sw_emu))
	./$(EXECUTABLE)
else ifeq ($(TARGET),$(filter $(TARGET),hw_emu))
	echo "[Emulation]\nuser_pre_sim_script=dump_waveforms.tcl\ndebug_mode=batch\n\n[Debug]\nopencl_trace=true\ntrace_buffer_size=10G" > xrt.ini
	echo "log_wave -r *\nrun all\nexit" > dump_waveforms.tcl
	./$(EXECUTABLE) --bitstream=vitis_run_hw_emu/workload_$(DEVICE).xclbin
else
	./$(EXECUTABLE) --bitstream=vitis_run_hw/workload_$(DEVICE).xclbin
endif




# Cleaning stuff
clean:
	-$(RMDIR) $(EXECUTABLE) $(XCLBIN)/{*sw_emu*,*hw_emu*}
	-$(RMDIR) profile_* TempConfig system_estimate.xtxt *.rpt *.csv
	-$(RMDIR) src/*.ll *v++* .Xil emconfig.json dltmp* xmltmp* *.log *.jou *.wcfg *.wdb
	-$(RMDIR) .run
	-$(RMDIR) $(TEMP_DIR)

cleanall: clean
	-$(RMDIR) build_dir* sd_card* *.proj
	-$(RMDIR) _x.* *xclbin.run_summary qemu-memory-_* emulation/ _vimage/ pl* start_simulation.sh *.xclbin



