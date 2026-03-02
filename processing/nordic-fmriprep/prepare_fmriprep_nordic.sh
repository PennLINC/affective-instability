cd /cbica/projects/pafin/apptainer-ds
datalad create -D "NORDIC-fMRIPrep dataset" nordic-fmriprep-ds
apptainer pull --name /cbica/projects/pafin/apptainer/fmriprep-25.2.4.sif docker://nipreps/fmriprep:25.2.4
cd /cbica/projects/pafin/apptainer-ds/nordic-fmriprep-ds/
datalad containers-add --url /cbica/projects/pafin/apptainer/nordic-0-0-1.sif nordic-0-0-1
datalad containers-add --url /cbica/projects/pafin/apptainer/fmriprep-25.2.4.sif fmriprep-25-2-4
