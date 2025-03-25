#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=90G
#SBATCH --time=48:00:00

/cbica/projects/pafin/.bashrc

mamba activate processing

python calculate_phase_jolt.py
