#!/bin/bash

FMRIPREP_OUTPUT_RIA="/cbica/projects/pafin/derivatives/nordic_fmriprep_babs_project/output_ria"
ZIP_DIR="/cbica/projects/pafin/derivatives/nordic_fmriprep_zipped_ephemeral"
UNZIP_DIR="/cbica/projects/pafin/derivatives/ds006185"

mkdir -p "$UNZIP_DIR"

# Make a ephemeral clone of the output RIA
datalad clone \
    -D "Create reckless ephemeral clone of nordic_fmriprep outputs" \
    --reckless ephemeral \
    ria+file://${FMRIPREP_OUTPUT_RIA}#~data \
    ${ZIP_DIR}

cd "$ZIP_DIR" || exit 1

# Unzip each MRIQC zip file into the UNZIP_DIR
for z in *.zip; do
    echo "Unzipping $z ..."
    unzip -o "$z" -d "$UNZIP_DIR"
done
