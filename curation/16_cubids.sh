#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=48:00:00

/cbica/projects/pafin/.bashrc

mamba activate curation

cubids apply /cbica/projects/pafin/dset /cbica/projects/pafin/dset/code/CuBIDS/edited_v3_summary.tsv /cbica/projects/pafin/dset/code/CuBIDS/v3_files.tsv v4
