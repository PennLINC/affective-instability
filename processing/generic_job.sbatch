#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=90G
#SBATCH --time=100:00:00
#SBATCH --partition=long

/cbica/projects/pafin/.bashrc

mamba activate processing

python run_tedana.py
