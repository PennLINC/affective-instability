#!/bin/bash
#SBATCH --job-name=xcp_d
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --array=1-2
#SBATCH --cpus-per-task=20
#SBATCH --mem-per-cpu=4gb
#SBATCH --time=100:00:00
#SBATCH --partition=long
# Outputs ----------------------------------
#SBATCH --output=/cbica/home/salot/datasets/pafin/code/jobs/xcpd_%A-%a.out
#SBATCH --error=/cbica/home/salot/datasets/pafin/code/jobs/xcpd_%A-%a.err
# ------------------------------------------

pwd; hostname; date
set -e

#==============Shell script==============#
#Load the software needed
xcp_d_ver=0.10.0rc3

# Location of the *reduced* BIDS dataset
BIDS_DIR="/cbica/home/salot/datasets/pafin/dset"
INPUT_DIR="/cbica/home/salot/datasets/pafin/derivatives/fmriprep"
CODE_DIR="/cbica/home/salot/datasets/pafin/code"
SCRATCH_DIR="/cbica/comp_space/salot/pafin-xcp_d"
DERIVS_DIR="/cbica/home/salot/datasets/pafin/derivatives/xcp_d"
mkdir -p ${SCRATCH_DIR}
mkdir -p ${DERIVS_DIR}

# Make sure FS_LICENSE is defined in the container.
FS_LICENSE="/cbica/home/salot/datasets/mobile-phenomics/freesurfer_license.txt"

# Parse the participants.tsv file and extract one subject ID from the line corresponding to this SLURM task.
subject=$( sed -n -E "$((${SLURM_ARRAY_TASK_ID} + 1))s/sub-(\S*)\>.*/\1/gp" ${BIDS_DIR}/participants.tsv )

# Compose the command line
cmd="apptainer run --cleanenv \
    -B ${INPUT_DIR}:/data \
    -B ${DERIVS_DIR}:/out \
    -B ${SCRATCH_DIR}:/work \
    -B ${FS_LICENSE}:/license.txt \
    /cbica/home/salot/apptainer/xcp_d_${xcp_d_ver}.sif \
    /data \
    /out \
    participant \
    --participant-label ${subject} \
    -w /work/ \
    --omp-nthreads ${SLURM_CPUS_PER_TASK} \
    --nprocs ${SLURM_CPUS_PER_TASK} \
    --mem-gb 79 \
    --mode linc \
    --fs-license-file /license.txt"

# Setup done, run the command
echo Running task "${SLURM_ARRAY_TASK_ID}"
echo Commandline: "$cmd"
eval "$cmd"
exitcode=$?

# Output results to a table
echo "sub-$subject   ${SLURM_ARRAY_TASK_ID}    $exitcode" \
      >> ${CODE_DIR}/jobs/"${SLURM_JOB_NAME}"."${SLURM_ARRAY_JOB_ID}".tsv
echo Finished tasks "${SLURM_ARRAY_TASK_ID}" with exit code $exitcode
exit $exitcode
