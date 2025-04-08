
### Required by the included Makefiles:
HOST_ARCH := x86
SYSROOT :=

.PHONY: help

help::
	$(ECHO) "Makefile Usage:"
	$(ECHO) "  make all TARGET=<sw_emu/hw_emu/hw> AURORA=<enabled/disabled>"
	$(ECHO) "	  Command to generate the design for specified Target and Shell."
	$(ECHO) ""
	$(ECHO) "  make clean"
	$(ECHO) "	  Command to remove the generated non-hardware files."
	$(ECHO) ""
	$(ECHO) "  make cleanall"
	$(ECHO) "	  Command to remove all the generated files, including hardware files."
	$(ECHO) ""
	$(ECHO) "  make check TARGET=<sw_emu/hw_emu/hw> AURORA=<enabled/disabled>"
	$(ECHO) "	  Command to build and run application."
	$(ECHO) ""
	$(ECHO) "  make exe TARGET=<sw_emu/hw_emu/hw> AURORA=<enabled/disabled>"
	$(ECHO) "	  Command to build the host executable for BitBlender."
	$(ECHO) ""
	$(ECHO) "  make build TARGET=<sw_emu/hw_emu/hw> AURORA=<enabled/disabled>"
	$(ECHO) "	  Command to build xclbin."
	$(ECHO) ""

# Points to top directory of Git repository
COMMON_REPO = /localhdd/kenny/BloomFilter/BitBlender/krnl_includes
#COMMON_REPO = /scratch/hpc-prf-haqc/kenny/BloomFilter/BitBlender/krnl_includes
PWD = $(shell readlink -f .)
ABS_COMMON_REPO = $(shell readlink -f $(COMMON_REPO))

#VERSION := singlestream
VERSION := bitblender
#VERSION := naive_multistream

ifeq ($(VERSION), singlestream)
	APP = singlestream_Bloomfilter
else ifeq ($(VERSION), bitblender)
	APP = multistream_BitBlender
else ifeq ($(VERSION), naive_multistream)
	APP = naive_multistream_Bloomfilter
endif
KERNEL = workload
#DEVICE := xilinx_u200_xdma_201830_2
#DEVICE := xilinx_u280_xdma_201920_3
#DEVICE := xilinx_u280_gen3x16_xdma_1_202211_1
#DEVICE := xilinx_u50_gen3x16_xdma_5_202210_1
DEVICE := xilinx_u280_gen3x16_xdma_1_202211_1

TARGET := hw
AURORA := unspecified

ifeq ($(AURORA),$(filter $(AURORA),unspecified))
$(error Must specify AURORA variable)
endif

#Include Libraries
include $(ABS_COMMON_REPO)/utils.mk
include $(ABS_COMMON_REPO)/common/includes/opencl/opencl.mk
include $(ABS_COMMON_REPO)/common/includes/xcl2/xcl2.mk

XSA := $(call device2xsa, $(DEVICE))
TEMP_DIR := ./_x.$(TARGET)_$(APP).$(XSA)

ifeq ($(AURORA),$(filter $(AURORA),enabled))
BUILD_DIR := ./aurora_build_dir.$(TARGET).$(XSA)
else
BUILD_DIR := ./tapa_build_dir.$(TARGET).$(XSA)
endif

###VPP := v++ --profile_kernel=data:all:all:all
VPP := v++

AUTOBRG_FLOORPLAN_FILE = build_script/bitblender_floorplan.tcl

LDFLAGS += $(xcl2_LDFLAGS)
HOST_SRCS += $(xcl2_SRCS)

ifeq ($(VERSION), bitblender)
	DEFINE_FLAGS = -DNAIVE_MULTISTREAM=0
else ifeq ($(VERSION), naive_multistream)
	DEFINE_FLAGS = -DNAIVE_MULTISTREAM=1
endif

ifeq ($(TARGET),$(filter $(TARGET),hw))
ifeq ($(AURORA),$(filter $(AURORA),enabled))
	TAPAC_FLAGS=	--enable-synth-util \
					--run-floorplanning \
					--constraint $(AUTOBRG_FLOORPLAN_FILE) \
					--enable-hbm-binding-adjustment
else    # AURORA
	TAPAC_FLAGS=	--enable-synth-util \
					--run-floorplanning \
					--constraint $(AUTOBRG_FLOORPLAN_FILE) \
					--enable-hbm-binding-adjustment

endif   # AURORA
else    # TARGET
	TAPAC_FLAGS=
endif   # TARGET



CXXFLAGS += $(opencl_CXXFLAGS) $(DEFINE_FLAGS) -Wall -Wno-unused-label -Wno-unknown-pragmas -O0 -g -std=c++17
### ADDING THIS because v2021.2 moved it's include files.... stupid.
CXXFLAGS += -I$(XILINX_HLS)/include
CXXFLAGS += -fmessage-length=0

LDFLAGS += $(opencl_LDFLAGS)
LDFLAGS += -lrt -lstdc++
LDFLAGS += -ltapa -lfrt -lglog -lgflags -lxrt_coreutil

ifeq ($(AURORA),$(filter $(AURORA),enabled))
HOST_SRCS += src/host_QSFP_aurora.cpp #src/hostside_krnlhelpers.cpp
else
HOST_SRCS += src/host_HBM.cpp #src/hostside_krnlhelpers.cpp
endif
BLOOMFILTER_SRCS += src/$(APP).cpp


ifeq ($(TARGET),$(filter $(TARGET),sw_emu))
ifeq ($(AURORA),$(filter $(AURORA),enabled))
	echo "Cannot run SW_EMU with aurora enabled."
	exit 1
else
	CHECK_DEPENDENCY=$(EXECUTABLE)
endif
else
	CHECK_DEPENDENCY=all
endif

# Adding config files to linker
CONFIGFILE = src/BitBlender.h
INIFILE = src/BitBlender.ini
LDCLFLAGS += --config $(INIFILE)


ifeq ($(AURORA),$(filter $(AURORA),enabled))
	EXECUTABLE = host_QSFP_aurora
else
	EXECUTABLE = host_HBM
endif

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


.PHONY: MODIFY_CFGS
MODIFY_CFGS: $(CONFIGFILE)
ifeq ($(TARGET),$(filter $(TARGET),hw))
	sed -i 's/^#define NUM_DESIRED_INPUT_KEYS.*/#define NUM_DESIRED_INPUT_KEYS (1024*1024*8*NUM_STM)   \/\/ DO NOT MODIFY: Makefile automatically changes this line./' $(CONFIGFILE)
	sed -i 's/^#define BV_DESIRED_LENGTH.*/#define BV_DESIRED_LENGTH ((1024*1024*10)*NUM_HASH)          \/\/ DO NOT MODIFY: Makefile automatically changes this line./' $(CONFIGFILE)
	sed -i 's/^#define NUM_POPULATION_INPUTS.*/#define NUM_POPULATION_INPUTS ((1024*128)*NUM_STM)        \/\/ DO NOT MODIFY: Makefile automatically changes this line./' $(CONFIGFILE)

else	### SW or HW EMULATION
	sed -i 's/^#define NUM_DESIRED_INPUT_KEYS.*/#define NUM_DESIRED_INPUT_KEYS (256*8*NUM_STM)         \/\/ DO NOT MODIFY: Makefile automatically changes this line./' $(CONFIGFILE)
	sed -i 's/^#define BV_DESIRED_LENGTH.*/#define BV_DESIRED_LENGTH ((128*10)*NUM_HASH)                \/\/ DO NOT MODIFY: Makefile automatically changes this line./' $(CONFIGFILE)
	sed -i 's/^#define NUM_POPULATION_INPUTS.*/#define NUM_POPULATION_INPUTS ((2*128)*NUM_STM)           \/\/ DO NOT MODIFY: Makefile automatically changes this line./' $(CONFIGFILE)

endif	### SW or HW EMULATION

ifeq ($(AURORA),$(filter $(AURORA),enabled))
	sed -i 's/^#*\(.*sp=workload.key_in_0.*\)/#\1/' $(INIFILE)
	sed -i 's/^#define _KENNY_USING_AURORA_.*/#define _KENNY_USING_AURORA_ (1)    \/\/ DO NOT MODIFY: Makefile automatically changes this line./' $(CONFIGFILE)
else	# AURORA
	sed -i 's/^#*\(.*sp=workload.key_in_0.*\)/\1/' $(INIFILE)
	sed -i 's/^#define _KENNY_USING_AURORA_.*/#define _KENNY_USING_AURORA_ (0)    \/\/ DO NOT MODIFY: Makefile automatically changes this line./' $(CONFIGFILE)
endif	# AURORA



# Building kernel
$(KRNL_XO_FILE): $(BLOOMFILTER_SRCS) MODIFY_CFGS $(INIFILE)
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

ifeq ($(AURORA),$(filter $(AURORA),enabled))
$(KRNL_XCLBIN): $(KRNL_XO_FILE) aurora_xclbin
else	# AURORA
$(KRNL_XCLBIN): $(KRNL_XO_FILE)
	chmod +x $(TEMP_DIR)/$(APP)_generate_bitstream.sh
	$(TEMP_DIR)/$(APP)_generate_bitstream.sh
	### rapidstream rapidstream_run.py
endif	# AURORA

else	# TARGET

ifeq ($(AURORA),$(filter $(AURORA),enabled))
$(KRNL_XCLBIN):
	$(error hw_emu is not tested with the Aurora cores.)
else	# AURORA
$(KRNL_XCLBIN): $(KRNL_XO_FILE)
	chmod +x $(TEMP_DIR)/$(APP)_generate_bitstream.sh
	sed -i 's/TARGET=hw\>/#TARGET=hw/ ; s/^# TARGET=hw_emu/TARGET=hw_emu/ ; s/^# DEBUG=-g/DEBUG=-g/' $(TEMP_DIR)/$(APP)_generate_bitstream.sh
	$(TEMP_DIR)/$(APP)_generate_bitstream.sh
endif	# AURORA

endif	# TARGET

# Building Host
$(EXECUTABLE): check-xrt $(HOST_SRCS) MODIFY_CFGS $(BLOOMFILTER_SRCS)
	$(CXX) $(CXXFLAGS) $(HOST_SRCS) $(BLOOMFILTER_SRCS) -o '$@' $(LDFLAGS)

emconfig:$(EMCONFIG_DIR)/emconfig.json
$(EMCONFIG_DIR)/emconfig.json:
	emconfigutil --platform $(DEVICE) --od $(EMCONFIG_DIR)




AURORA_DIR=AURORA_STUFF
AURORA_LINKFLAGS= --link \
					--optimize 3 \
					--save-temps \
					--platform $(DEVICE) \

$(AURORA_DIR):
	cp -R $(COMMON_REPO)/../scripts/codegen_scripts/AURORA_XO_FILES/ .
	mv AURORA_XO_FILES $(AURORA_DIR)

### NOTE: $(KRNL_XO_FILE) IS NOT in this list because our MODIFY_CFGS logic will automatically rebuild it always.
BB_VPP_STRATEGY="Explore"
BB_VPP_PLACESTRATEGY="EarlyBlockPlacement"
aurora_xclbin: $(AURORA_DIR) $(AURORA_DIR)/aurora_hls_0.xo $(AURORA_DIR)/aurora_hls_1.xo $(AURORA_DIR)/aurora_hls_test_hw.cfg $(AURORA_DIR)/issue_hw.xo $(AURORA_DIR)/dump_hw.xo
	mkdir -p K_tmp_v++_dir
	cd K_tmp_v++_dir && \
		v++ $(AURORA_LINKFLAGS) \
			--report_level 2 \
			--target $(TARGET) \
			--temp_dir _x_aurora_hls_$(TARGET) \
			--config ../$(AURORA_DIR)/aurora_hls_test_hw.cfg \
			--output ../$(KRNL_XCLBIN) \
			--vivado.prop=run.impl_1.STEPS.PHYS_OPT_DESIGN.IS_ENABLED=1 \
			--vivado.prop=run.impl_1.STEPS.OPT_DESIGN.ARGS.DIRECTIVE=$(BB_VPP_STRATEGY) \
			--vivado.prop=run.impl_1.STEPS.PLACE_DESIGN.ARGS.DIRECTIVE=$(BB_VPP_PLACESTRATEGY) \
			--vivado.prop=run.impl_1.STEPS.PHYS_OPT_DESIGN.ARGS.DIRECTIVE=$(BB_VPP_STRATEGY) \
			--vivado.prop=run.impl_1.STEPS.ROUTE_DESIGN.ARGS.DIRECTIVE=$(BB_VPP_STRATEGY) \
			--vivado.prop=run.impl_1.STEPS.OPT_DESIGN.TCL.PRE=../$(AUTOBRG_FLOORPLAN_FILE) \
			../$(AURORA_DIR)/aurora_hls_0.xo \
			../$(AURORA_DIR)/aurora_hls_1.xo \
			../$(AURORA_DIR)/issue_hw.xo \
			../$(AURORA_DIR)/dump_hw.xo \
			../$(TEMP_DIR)/multistream_BitBlender.xo \
			--kernel_frequency 225  \
		&& cd ..





check: $(CHECK_DEPENDENCY)
ifeq ($(TARGET),$(filter $(TARGET),sw_emu))
	./$(EXECUTABLE)
else ifeq ($(TARGET),$(filter $(TARGET),hw_emu))
	echo "[Emulation]\nuser_pre_sim_script=dump_waveforms.tcl\ndebug_mode=batch\n\n[Debug]\nopencl_trace=true\ntrace_buffer_size=10G" > xrt.ini
	echo "log_wave -r *\nrun all\nexit" > dump_waveforms.tcl
	./$(EXECUTABLE) --bitstream=vitis_run_hw_emu/workload_$(DEVICE).xclbin
else

ifeq ($(AURORA),$(filter $(AURORA),disabled))
	./$(EXECUTABLE) --bitstream=vitis_run_hw/workload_$(DEVICE).xclbin
else
	./$(EXECUTABLE)
endif

endif




# Cleaning stuff
clean:
	-$(RMDIR) $(EXECUTABLE) $(XCLBIN)/{*sw_emu*,*hw_emu*}
	-$(RMDIR) profile_* TempConfig system_estimate.xtxt *.rpt *.csv
	-$(RMDIR) src/*.ll *v++* .Xil emconfig.json dltmp* xmltmp* *.log *.jou
	-$(RMDIR) .run
	-$(RMDIR) $(TEMP_DIR)

cleanall: clean
	-$(RMDIR) aurora_build_dir* tapa_build_dir* *.proj
	-$(RMDIR) _x* *xclbin.run_summary *.xclbin *.xclbin.* *.ltx *.link_summary
	-$(RMDIR) vitis_run_* .ipcache/ K_tmp_v++*
