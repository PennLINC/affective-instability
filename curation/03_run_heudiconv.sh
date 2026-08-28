#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=48:00:00

/cbica/projects/pafin/.bashrc
# Convert the DICOMs to BIDS with heudiconv.
#
# The session directories are handed to heudiconv with --files, which searches
# them recursively, instead of the fixed-depth -d glob it used to use.
# 'syngo MR XA60' sessions write single-file (enhanced) series one directory
# shallower than 'syngo MR E11' sessions do, so no single glob depth finds all
# of the DICOMs in both.

mamba activate curation

heuristic="/cbica/projects/pafin/code/curation/heuristic.py"
out_dir="/cbica/projects/pafin/dset"
dicom_dir="/cbica/projects/pafin/sourcedata/imaging/scitran/bbl/PAFIN_844353"

# Run heudiconv on the first session
subjects=($(ls -d /cbica/projects/pafin/sourcedata/imaging/scitran/bbl/PAFIN_844353/*_* | sed 's|.*/\([0-9a-zA-Z]*\)_.*|\1|' | sort -u))

# Filter out already-converted subjects
subjects=($(for s in "${subjects[@]}"; do [ ! -d "/cbica/projects/pafin/dset/sub-$s/ses-1" ] && echo "$s"; done))
subjects=("25636")
for sub in "${subjects[@]}"
do
    echo "$sub"
    heudiconv \
        -f "${heuristic}" \
        -o "${out_dir}" \
        --files "${dicom_dir}/${sub}"_*/ \
        --subjects "$sub" \
        --ses 1 \
        -g all \
        --bids \
        --queue SLURM \
        --minmeta \
        -c dcm2niix
done
