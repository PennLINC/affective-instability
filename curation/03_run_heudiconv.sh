#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=48:00:00

/cbica/projects/pafin/.bashrc

mamba activate curation

# Run heudiconv on the first session
subjects=($(ls -d /cbica/projects/pafin/sourcedata/imaging/scitran/bbl/PAFIN_844353/*_* | sed 's|.*/\([0-9a-zA-Z]*\)_.*|\1|' | sort -u))

# Filter out already-converted subjects
subjects=($(for s in "${subjects[@]}"; do [ ! -d "/cbica/projects/pafin/dset/sub-$s/ses-1" ] && echo "$s"; done))

for sub in "${subjects[@]}"
do
    echo "$sub"
    heudiconv \
        -f /cbica/projects/pafin/code/curation/heuristic.py \
        -o /cbica/projects/pafin/dset2 \
        -d "/cbica/projects/pafin/sourcedata/imaging/scitran/bbl/PAFIN_844353/{subject}_*/*/*/*/*.dcm" \
        --subjects "$sub" \
        --ses 1 \
        -g all \
        --bids \
        --queue SLURM
done
