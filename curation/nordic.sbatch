#!/bin/bash
#SBATCH --job-name=nordic
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --array=1-120%10
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=40gb
#SBATCH --time=2:00:00
# Outputs ----------------------------------
#SBATCH --output=/cbica/projects/pafin/code/curation/jobs/nordic_%A-%a.out
#SBATCH --error=/cbica/projects/pafin/code/curation/jobs/nordic_%A-%a.err
# ------------------------------------------

/cbica/projects/pafin/.bashrc

mamba activate curation

pwd; hostname; date
set -e

#==============Shell script==============#
# Location of the *reduced* BIDS dataset
CODE_DIR="/cbica/projects/pafin/code"

# Select the file to process from the files_to_nordic.txt file
file=$( sed -n "${SLURM_ARRAY_TASK_ID}p" ${CODE_DIR}/curation/files_to_nordic.txt )

python ${CODE_DIR}/curation/17_run_nordic.py ${file}
