#!/bin/bash

mkdir -p /cbica/projects/pafin/templateflow_home
export TEMPLATEFLOW_HOME=/cbica/projects/pafin/templateflow_home

babs init \
  --container_ds /cbica/projects/pafin/apptainer-ds/nordic-fmriprep-ds \
  --container_name nordic-0-0-1 \
  --container_config /cbica/projects/pafin/code/processing/nordic-fmriprep/babs_nordic_fmriprep.yaml \
  --processing_level subject \
  --queue slurm \
  /cbica/projects/pafin/derivatives/nordic_fmriprep_babs_project
