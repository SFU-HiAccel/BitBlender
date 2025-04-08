#!/bin/bash
#SBATCH -A hpc-prf-haqc
#SBATCH --job-name=qcv-build
#SBATCH --array=0-4     ### THIS LINE IS AUTOMATICALLY CHANGED BY /localhdd/kenny/BloomFilter/BitBlender/scripts/config_selection/config_sel.py
#SBATCH -t 28:00:00
#SBATCH -p largemem
#SBATCH --cpus-per-task=6
#SBATCH --mem-per-cpu=15G
#SBATCH --output=BUILD_LOGS/build_log_%A_%a.out



archive_design_for_routing_estimator() {
    printf "\n\n\n\nArchiving HLS design now...\n\n\n"
    local DESIGN_NAME="BloomFilter_${CODEGEN_DESIGN_TYPE}"
    local TAPA_DIR=""
    local METADATA_STRING=""

    if (( $(echo "$VIVADO_VERSION > 2021.2" | bc -l) )); then
        TAPA_DIR="_x.hw_multistream_BitBlender.xilinx_u280_xdma_201920_3"
    else
        TAPA_DIR="_x.hw_multistream_BitBlender.xilinx_u280_gen3x16_xdma_1_202211_1"
    fi

    METADATA_STRING="NUM_HASH,$(echo "$MY_CONFIG" | cut -d'-' -f1)"
    METADATA_STRING="$METADATA_STRING:NUM_PARTITIONS,$(echo "$MY_CONFIG" | cut -d'-' -f2)"
    METADATA_STRING="$METADATA_STRING:NUM_STRM,$(echo "$MY_CONFIG" | cut -d'-' -f3)"
    METADATA_STRING="$METADATA_STRING:ARB_RATELIM_DIST,$(echo "$MY_CONFIG" | cut -d'-' -f4)"
    METADATA_STRING="$METADATA_STRING:BV_SECTION_LEN,$(echo "$MY_CONFIG" | cut -d'-' -f5 | cut -d'_' -f1)"
    METADATA_STRING="$METADATA_STRING:datetime,$(date '+%Y-%m-%d_%H:%M')"

    echo "archive_hls_design --tapa_dir ${TAPA_DIR} --target-platform u280 --design-name ${DESIGN_NAME} --meta ${METADATA_STRING}"
    source /mnt/glusterfs/hacc-common/shell-env/shsetup/setuprc.sh
    source /scratch/hpc-prf-haqc/.software/hls-design-arcve/configure.sh
    archive_hls_design --tapa-dir "${TAPA_DIR}" --target-platform u280 --design-name "${DESIGN_NAME}" --meta "${METADATA_STRING}"
}



source designs_to_generate.sh
MY_CONFIG=${HTSB_CONFIGS[$SLURM_ARRAY_TASK_ID]}

# configuration
slurm_build_dir="/dev/shm/build_${SLURM_ARRAY_TASK_ID}/"
source_dir="${SLURM_SUBMIT_DIR}"
output_dir="$PWD/BUILD_OUTPUTS/${MY_CONFIG}"
###mkdir -p "$PWD/BUILD_OUTPUTS"
mkdir -p $output_dir


# load modules and configure environment
module reset
module load fpga


################################################################
#### CHANGE ME !!!!!!!!!!!!!!!!!!!!!!
################################################################

if [[ "$VIVADO_VERSION" == "2021.2" ]]; then
    echo "Using VIVADO_VERSION=21.2";
    module load fpga/xilinx/vivado/21.2
    module load fpga/xilinx/vitis/21.2
    module load fpga/xilinx/xrt/2.12
    module load fpga/xilinx/u280/xdma_201920_3_2789161

elif [[ "$VIVADO_VERSION" == "2022.1" ]]; then
    echo "Using VIVADO_VERSION=22.1";
    module load fpga/xilinx/vivado/22.1
    module load fpga/xilinx/vitis/22.1
    module load fpga/xilinx/xrt/2.13
    module load fpga/xilinx/u280/xdma_202211_1

elif [[ "$VIVADO_VERSION" == "2022.2" ]]; then
    echo "Using VIVADO_VERSION=22.2";
    module load fpga/xilinx/vivado/22.2
    module load fpga/xilinx/vitis/22.2
    module load fpga/xilinx/xrt/2.14
    module load fpga/xilinx/u280/xdma_202211_1


elif [[ "$VIVADO_VERSION" == "2023.2" ]]; then
    echo "Using VIVADO_VERSION=23.2";
    module load fpga/xilinx/vivado/23.2
    module load fpga/xilinx/vitis/23.2
    module load fpga/xilinx/xrt/2.16
    module load fpga/xilinx/u280/xdma_202211_1

else
    echo "This VIVADO_VERSION ($VIVADO_VERSION) is not yet added to the build sweep script."
    echo "Please add this value and run it again"
    exit
fi

################################################################
#### END OF CHANGE ME
################################################################


module load lang
#module load Anaconda3
module load lang/Miniforge3/24.1.2-0
module load lang/Python/3.9.5-GCCcore-10.3.0
module load compiler
module load compiler/Clang/12.0.1-GCCcore-10.3.0
module load lib/gurobi/952

export TMPDIR="/dev/shm"
export SLURM_TMPDIR="/dev/shm"
export XILINX_LOCAL_USER_DATA="no" # to prevent "Failed to install all user apps" error

# setup project files
rm -rf "${slurm_build_dir}"
mkdir -p "${slurm_build_dir}"
cp -r "${source_dir}"/* "${slurm_build_dir}"
cd "${slurm_build_dir}" || { echo "Failed to change directory to ${slurm_build_dir}"; exit 1; }


### GENERATE & RUN THE HW BUILD
python3 generate_BVSharing_design.py -htsb ${MY_CONFIG} --design_type ${CODEGEN_DESIGN_TYPE} --vivado_version ${VIVADO_VERSION}
cd ${MY_CONFIG} || { echo "Failed to change directory to ${MY_CONFIG}/"; exit 1; }
time make all TARGET=hw AURORA=${AURORA_ENABLED_STRING}
python3 collect_resource_usages.py


# copy results
cp RESOURCES_AND_IIs.log "${output_dir}/"
cp -r src/ "${output_dir}/"
cp Makefile "${output_dir}/"
cp ${HOST_EXE_NAME} "${output_dir}/"        ### Host binary, so we can run the xclbin.
cp -r build_script "${output_dir}/"         ### Generated floorplan tcl script.
cp -r vitis_run_hw/ "${output_dir}/"        ### HBM-version hw directory (hardcoded into TAPA)
cp -r aurora_build_dir*/ "${output_dir}/"   ### QSFP-version xclbin directory (defined in BitBlender Makefile)
cp -r K_tmp_v++_dir/ "${output_dir}/"       ### QSFP-version hw build-logs directory (defined in BitBlender Makefile)
cp -r _x.*/ "${output_dir}/"                ### TAPA HLS directory (hardcoded into TAPA)



# Archive the design, for Philip's routing estimator.
archive_design_for_routing_estimator


