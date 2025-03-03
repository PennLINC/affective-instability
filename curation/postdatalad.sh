#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=48:00:00

/cbica/projects/pafin/.bashrc

mamba activate curation

# python 12_fix_bids.py
# Had to run datalad unlock sub-*/ses-*/perf/*.nii.gz here
python 13_fix_asl.py
python 14_assign_b0fields.py
