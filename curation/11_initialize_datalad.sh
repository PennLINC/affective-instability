#!/usr/bin/env bash
# Add .heudiconv/ and sourcedata/ to the .gitignore file
echo ".heudiconv/" >> /cbica/projects/pafin/dset/.gitignore
echo "sourcedata/" >> /cbica/projects/pafin/dset/.gitignore

# Create the datalad dataset after anonymizing anatomical images and metadata
datalad create --force -c text2git /cbica/projects/pafin/dset

# Save the datalad dataset
datalad save -d /cbica/projects/pafin/dset -m "Initial commit"
