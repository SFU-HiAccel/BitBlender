#!/bin/bash
#SBATCH -A hpc-prf-haqc
#SBATCH --job-name=qcv-build
#SBATCH -t 8:00:00
#SBATCH -p fpga
#SBATCH --constraint=xilinx_u280_xrt2.13        ################# CHANGE ME!!!!!!!!!!!!!!!!
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=2G
#SBATCH --output=fpga_tests_log.out


source designs_to_generate.sh

# load modules and configure environment
module reset
module load fpga

################################################################
#### CHANGE ME !!!!!!!!!!!!!!!!!!!!!!
################################################################

if [[ "$VIVADO_VERSION" == "2022.1" ]]; then
    #module load fpga/xilinx/xrt/2.12   ### This is v2021.2  ################# CHANGE ME!!!!!!!!!!!!!!!!
    #module load fpga/xilinx/u280/xdma_201920_3_2789161

    module load fpga/xilinx/xrt/2.13    ### This is v2022.1  ################# CHANGE ME!!!!!!!!!!!!!!!!
    #module load fpga/xilinx/xrt/2.14   ### This is v2022.2  ################# CHANGE ME!!!!!!!!!!!!!!!!
    #module load fpga/xilinx/xrt/2.16   ### This is v2023.2  ################# CHANGE ME!!!!!!!!!!!!!!!!
    module load fpga/xilinx/u280/xdma_202211_1

else
    echo "Oops, you might need to change the SLURM --constraint field in the fpga tests script."
    echo "Otherwise, update the checked value for the VIVADO_VERSION."
    exit

fi

################################################################
#### END OF CHANGE ME
################################################################

module load fpga/changeFPGAlinks


# configuration
export XILINX_LOCAL_USER_DATA="no" # to prevent "Failed to install all user apps" error
build_outputs_dir="$PWD/BUILD_OUTPUTS"
run_dir_0="$PWD/TMP_RUN_DIR_DELETEME_0"
#run_dir_1="$PWD/TMP_RUN_DIR_DELETEME_1"
#run_dir_2="$PWD/TMP_RUN_DIR_DELETEME_2"

mkdir $run_dir_0
#mkdir $run_dir_1
#mkdir $run_dir_2


NUM_THREADS=1               ### Three FPGAs, one for each thread.
NUM_DESIGNS=${#HTSB_CONFIGS[@]}

DESIGNS_PER_THREAD=$(( (${NUM_DESIGNS}+2)/${NUM_THREADS} ))

process_section() {
    local start=$1
    local end=$2
    local run_dir=$4

    end=$((end > ${NUM_DESIGNS} ? ${NUM_DESIGNS} : end))

    for ((design_idx = start; design_idx < end && design_idx < ${NUM_DESIGNS}; design_idx++)); do

        MY_CONFIG=${HTSB_CONFIGS[$design_idx]}
        config_dir="${build_outputs_dir}/${MY_CONFIG}"

        printf "=======================================================================================\n"
        printf "NEW FOLDER: $MY_CONFIG\n"
        printf "=======================================================================================\n"

        ## In case we already ran this test, don't bother re-running it.
        if test -f "${config_dir}"/KENNY_run_hw.log; then
            if grep -q "xclbin not found" "${config_dir}"/KENNY_run_hw.log; then
                printf "\n\n\n\n\n"
                echo "Processing ${HTSB_CONFIGS[design_idx]} in thread $3"
            else
                printf "Skipping $MY_CONFIG... it was already run\n"
                continue
            fi
        fi

        ### # Rebuild the host executable (if needed)
        ### starting_dir=$(pwd)
        ### cd "${config_dir}" && pwd && make exe AURORA=disabled TARGET=hw
        ### cd "$starting_dir"

        # setup project files
        rm -rf "${run_dir}"
        mkdir -p "${run_dir}"

        ## Copy the host executable and the xclbin.
        cp "${config_dir}"/${HOST_EXE_NAME} "${run_dir}"
        cp "${config_dir}"/vitis_run_hw/*.xclbin "${run_dir}"/xclbin
        cp "${config_dir}"/aurora_build_dir*/*.xclbin "${run_dir}"/xclbin

        cd "${run_dir}" || { echo "Failed to change directory to ${run_dir}"; exit 1; }

        if [ "$AURORA_ENABLED_STRING" = "enabled" ]; then
            ### RESET AND SETUP QSFP CONNECTIONS
            #https://pc2.github.io/fpgalink-gui/index.html?import=%20--fpgalink%3Dn00%3Aacl1%3Ach0-n00%3Aacl1%3Ach1%20--fpgalink%3Dn00%3Aacl0%3Ach0-n00%3Aacl0%3Ach1%20--fpgalink%3Dn00%3Aacl2%3Ach0-n00%3Aacl2%3Ach1
            changeFPGAlinks --fpgalink=n00:acl1:ch0-n00:acl1:ch1 --fpgalink=n00:acl0:ch0-n00:acl0:ch1 --fpgalink=n00:acl2:ch0-n00:acl2:ch1
        fi

        if test -f xclbin; then
            xbutil reset --force --device 0000:a1:00.1 ###&& xbutil reset --force --device 0000:81:00.1 && xbutil reset --force --device 0000:01:00.1
            ./${HOST_EXE_NAME} --bitstream=xclbin |& tee KENNY_run_hw.log
        else
            echo "xclbin not found" |& tee KENNY_run_hw.log
        fi

        # copy results
        cp KENNY_run_hw.log "${config_dir}/"

        cd "/dev/shm/"
    done
}


start0=0
end0=$(( ${start0}+${DESIGNS_PER_THREAD} ))
start1=$(( ${end0} ))
end1=$(( ${start1}+${DESIGNS_PER_THREAD} ))
start2=$(( ${end1} ))
end2=$(( ${start2}+${DESIGNS_PER_THREAD} ))


echo "DESIGNS_PER_THREAD is ${DESIGNS_PER_THREAD}"
echo "${start0} ${end0} ${start1} ${end1} ${start2} ${end2}"

(process_section $start0 $end0 0 $run_dir_0 ) &
#(process_section $start1 $end1 1 $run_dir_1 ) &
#(process_section $start2 $end2 2 $run_dir_2 ) &

wait
echo "Done!"

