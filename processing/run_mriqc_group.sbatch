#!/bin/bash
#SBATCH --job-name=mriqc
#SBATCH --cpus-per-task=20
#SBATCH --mem-per-cpu=4gb
#SBATCH --time=36:00:00
# Outputs ----------------------------------
#SBATCH --output=/cbica/projects/pafin/code/processing/jobs/mriqc_group_%A.out
#SBATCH --error=/cbica/projects/pafin/code/processing/jobs/mriqc_group_%A.err
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

cmd="apptainer run --cleanenv \
      -B ${BIDS_DIR}:/data \
      -B ${DERIVS_DIR}:/deriv \
      -B ${SCRATCH_DIR}:/work \
      -B ${CODE_DIR}:/code \
      /cbica/projects/pafin/apptainer/mriqc-25.0.0rc0.sif \
      /data \
      /deriv/mriqc \
      group \
      -w /work \
      --bids-filter-file /code/processing/filter.json \
      --omp-nthreads ${SLURM_CPUS_PER_TASK} \
      --nprocs ${SLURM_CPUS_PER_TASK} \
      --mem-gb 39"

eval "$cmd"
exitcode=$?
