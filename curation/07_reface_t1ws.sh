#!/bin/bash
# Reface the T1w and T2w images in the dataset, overwriting the original files.
#
# Refacing is not safe to repeat: rerunning it on an image that has already been
# refaced burns a job and resamples the data a second time.  In a dataset where a
# newly converted batch sits alongside subjects curated earlier, most of what is
# on disk has already been done, so each job records what it did in the image's
# sidecar, under DeidentificationMethod, and this script skips any image whose
# sidecar already carries that record.
#
# The check used to be "does this session have NORDIC-denoised files", since
# NORDIC ran after refacing and its outputs therefore marked a session as already
# curated.  NORDIC is no longer part of the pipeline, so nothing writes that
# marker any more and every image in the dataset was being resubmitted.
#
# Subjects refaced before the sidecar record existed need it backfilled once, with
# 07a_backfill_reface_metadata.py, before this script is run over them.
#
# Usage:
#   bash 07_reface_t1ws.sh       submit the jobs
#   bash 07_reface_t1ws.sh -n    report what would be submitted, submit nothing

set -u

DSET_DIR="/cbica/projects/pafin/dset"
PYTHON="/cbica/projects/pafin/miniforge3/envs/curation/bin/python"
AFNI_MODULE="afni/2022_05_03"
# Nothing but the reface job writes this string into a sidecar, so finding it
# there means the image beside it has been refaced.
REFACER="@afni_refacer_run"

dry_run=false
while getopts ":n" opt; do
    case "${opt}" in
        n)
            dry_run=true
            ;;
        *)
            echo "Usage: $0 [-n]" >&2
            exit 1
            ;;
    esac
done

# Submit one refacing job, which records itself in the sidecar once it succeeds.
submit_reface_job() {
    local input_file=$1
    local json_file=$2
    local tmp_script

    tmp_script=$(mktemp)
    cat > "${tmp_script}" <<EOF
#!/bin/bash
#SBATCH --job-name=reface
#SBATCH --time=12:00:00
#SBATCH --mem=16G
#SBATCH --output=logs/reface_%j.out
#SBATCH --error=logs/reface_%j.err

set -e

module load ${AFNI_MODULE}

@afni_refacer_run \\
    -input "${input_file}" \\
    -mode_reface \\
    -no_images \\
    -overwrite \\
    -prefix "${input_file}"

# Only reached when the refacer exited cleanly, so an image whose job crashed
# keeps an unmarked sidecar and is picked up again the next time 07 is run.
afni_version=\$(afni -vnum)
"${PYTHON}" - "${json_file}" "\${afni_version}" <<'PYEOF'
"""Record in the sidecar that this image has been refaced."""
import json
import os
import sys

json_file, afni_version = sys.argv[1], sys.argv[2]

if os.path.isfile(json_file):
    with open(json_file, "r") as fo:
        metadata = json.load(fo)
else:
    # The image had no sidecar, which is a problem for BIDS but not for us. Write
    # the record anyway, so the image is not refaced again on the next run.
    print(f"Warning: creating missing sidecar {json_file}", file=sys.stderr)
    metadata = {}

metadata["DeidentificationMethod"] = (
    f"Face replaced with AFNI's @afni_refacer_run ({afni_version}) in reface mode."
)

with open(json_file, "w") as fo:
    json.dump(metadata, fo, indent=4, sort_keys=True)
PYEOF
EOF

    sbatch "${tmp_script}"
    rm -f "${tmp_script}"
}

# Create logs directory if it doesn't exist
mkdir -p logs

anat_files=()
while IFS= read -r anat_file; do
    anat_files+=("${anat_file}")
done < <(
    find "${DSET_DIR}"/sub-*/ses-*/anat \
        \( -name "*_T1w.nii.gz" -o -name "*_T2w.nii.gz" \) | sort
)

if [ ${#anat_files[@]} -eq 0 ]; then
    echo "No anatomical images found under ${DSET_DIR}" >&2
    exit 1
fi

n_submitted=0
n_skipped=0
for anat_file in "${anat_files[@]}"
do
    json_file="${anat_file%.nii.gz}.json"

    if [ -f "${json_file}" ] && grep -q "${REFACER}" "${json_file}"; then
        echo "Skipping (already refaced): ${anat_file}"
        n_skipped=$((n_skipped + 1))
        continue
    fi

    if [ ! -f "${json_file}" ]; then
        echo "Warning: ${anat_file} has no sidecar; refacing it and creating one" >&2
    fi

    if [ "${dry_run}" = true ]; then
        echo "Would submit: ${anat_file}"
    else
        echo "Submitting job for: ${anat_file}"
        submit_reface_job "${anat_file}" "${json_file}"
    fi
    n_submitted=$((n_submitted + 1))
done

if [ "${dry_run}" = true ]; then
    echo "${n_submitted} image(s) to reface, ${n_skipped} already refaced"
else
    echo "Submitted ${n_submitted} job(s), skipped ${n_skipped} already-refaced image(s)"
fi
