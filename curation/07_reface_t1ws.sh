#!/bin/bash
module load afni/2022_05_03

t1w_files=$(find /cbica/projects/pafin/dset/sub-*/ses-*/anat/*T1w.nii.gz)
for t1w_file in $t1w_files
do
    echo "$t1w_file"
    @afni_refacer_run \
        -input "${t1w_file}" \
        -mode_reface \
        -no_images \
        -overwrite \
        -prefix "${t1w_file}"
done

t2w_files=$(find /cbica/projects/pafin/dset/sub-*/ses-*/anat/*T2w.nii.gz)
for t2w_file in $t2w_files
do
    echo "$t2w_file"
    @afni_refacer_run \
        -input "${t2w_file}" \
        -mode_reface \
        -no_images \
        -overwrite \
        -prefix "${t2w_file}"
done
