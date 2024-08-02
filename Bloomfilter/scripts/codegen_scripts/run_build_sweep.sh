#!/bin/bash
#SBATCH -A hpc-prf-haqc
#SBATCH --job-name=qcv-build
#SBATCH --array=0-4     ### THIS LINE IS AUTOMATICALLY CHANGED BY /localhdd/kenny/BloomFilter/Bloomfilter/scripts/config_selection/config_sel.py
#SBATCH -t 28:00:00
#SBATCH -p largemem
#SBATCH --cpus-per-task=6
#SBATCH --mem-per-cpu=15G
#SBATCH --output=BUILD_LOGS/build_log_%A_%a.out

source designs_to_generate.sh
MY_CONFIG=${HTSB_CONFIGS[$SLURM_ARRAY_TASK_ID]}

# configuration
build_dir="/dev/shm/build_${SLURM_ARRAY_TASK_ID}/"
source_dir="${SLURM_SUBMIT_DIR}"
output_dir="$PWD/BUILD_OUTPUTS/${MY_CONFIG}"
mkdir "$PWD/BUILD_OUTPUTS"
mkdir $output_dir


# load modules and configure environment
module reset
module load fpga


################################################################
#### CHANGE ME !!!!!!!!!!!!!!!!!!!!!!
################################################################

module load fpga/xilinx/vivado/21.2
module load fpga/xilinx/vitis/21.2
module load fpga/xilinx/xrt/2.12
module load fpga/xilinx/u280/xdma_201920_3_2789161

#module load fpga/xilinx/vivado/22.2
#module load fpga/xilinx/vitis/22.2
#module load fpga/xilinx/xrt/2.14
#module load fpga/xilinx/u280/xdma_202211_1

#module load fpga/xilinx/vivado/23.2
#module load fpga/xilinx/vitis/23.2
#module load fpga/xilinx/xrt/2.16
#module load fpga/xilinx/u280/xdma_202211_1

################################################################
#### END OF CHANGE ME
################################################################


module load lang
module load Anaconda3
module load lang/Python/3.9.5-GCCcore-10.3.0
module load compiler
module load compiler/Clang/12.0.1-GCCcore-10.3.0
module load lib/gurobi/952

export TMPDIR="/dev/shm"
export SLURM_TMPDIR="/dev/shm"
export XILINX_LOCAL_USER_DATA="no" # to prevent "Failed to install all user apps" error

# setup project files
rm -rf "${build_dir}"
mkdir -p "${build_dir}"
cp -r "${source_dir}"/* "${build_dir}"
cd "${build_dir}" || { echo "Failed to change directory to ${build_dir}"; exit 1; }


### GENERATE & RUN THE HW BUILD
python3 generate_BVSharing_design.py -htsb ${MY_CONFIG}
cd ${MY_CONFIG} || { echo "Failed to change directory to ${MY_CONFIG}/"; exit 1; }
time make check TARGET=hw
python3 collect_resource_usages.py

# copy results
cp RESOURCES_AND_IIs.log "${output_dir}/"
cp -r src/ "${output_dir}/"
cp Makefile "${output_dir}/"
cp host "${output_dir}/"				### Host binary... just because.
cp -r build_script "${output_dir}/"		### Generated floorplan tcl script.
cp -r vitis_run_hw/ "${output_dir}/"
cp -r _x.*/ "${output_dir}/"

