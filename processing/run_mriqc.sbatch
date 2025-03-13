#!/bin/bash
#SBATCH --job-name=mriqc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --array=1-12
#SBATCH --cpus-per-task=20
#SBATCH --mem-per-cpu=4gb
#SBATCH --time=36:00:00
# Outputs ----------------------------------
#SBATCH --output=/cbica/projects/pafin/code/processing/jobs/mriqc_%A-%a.out
#SBATCH --error=/cbica/projects/pafin/code/processing/jobs/mriqc_%A-%a.err
# ------------------------------------------

pwd; hostname; date
set -e

#==============Shell script==============#
# Location of the *reduced* BIDS dataset
BIDS_DIR="/cbica/projects/pafin/dset"
CODE_DIR="/cbica/projects/pafin/code"
SCRATCH_DIR="/cbica/comp_space/pafin/pafin-mriqc"
DERIVS_DIR="/cbica/projects/pafin/derivatives"
mkdir -p ${SCRATCH_DIR}
mkdir -p ${DERIVS_DIR}

# Parse the participants.tsv file and extract one subject ID from the line corresponding to this SLURM task.
subject=$( sed -n -E "$((${SLURM_ARRAY_TASK_ID} + 1))s/sub-(\S*)\>.*/\1/gp" ${BIDS_DIR}/participants.tsv )

# Compose the command line
mem_gb=$(echo "${SLURM_MEM_PER_CPU} * ${SLURM_CPUS_PER_TASK}" | bc -l)

cmd="apptainer run --cleanenv \
      -B ${BIDS_DIR}:/data \
      -B ${DERIVS_DIR}:/deriv \
      -B ${SCRATCH_DIR}:/work \
      -B ${CODE_DIR}:/code \
      /cbica/projects/pafin/apptainer/mriqc-25.0.0rc0.sif \
      /data \
      /deriv/mriqc \
      participant \
      --participant-label ${subject} \
      -w /work \
      --bids-filter-file /code/processing/filter.json \
      --omp-nthreads ${SLURM_CPUS_PER_TASK} \
      --nprocs ${SLURM_CPUS_PER_TASK} \
      --mem-gb 39"

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
