#!/bin/bash
unset LD_LIBRARY_PATH

subjects="24053_13187"
token=$(</cbica/projects/pafin/tokens/flywheel.txt)
~/bin/glibc-2.34/lib/ld-linux-x86-64.so.2 ~/bin/linux_amd64/fw login "$token"
cd "/cbica/projects/pafin/sourcedata/imaging" || exit

# Initialize download status file if it doesn't exist
download_status_file="/cbica/projects/pafin/code/curation/status_download.txt"
touch "$download_status_file"

# Read already downloaded subjects into an array
if [[ -f "$download_status_file" ]]; then
    mapfile -t downloaded_subjects < "$download_status_file"
else
    downloaded_subjects=()
fi

for subject in "${subjects[@]}"; do
    # Check if subject is already downloaded
    if [[ " ${downloaded_subjects[*]} " =~ " ${subject} " ]]; then
        echo "Subject ${subject} already downloaded, skipping..."
        continue
    fi

    echo "Downloading subject ${subject}..."
    #~/bin/glibc-2.34/lib/ld-linux-x86-64.so.2 ~/bin/linux_amd64/fw download --yes --zip "fw://bbl/PAFIN_844353/${subject}"
    if ~/bin/linux_amd64/fw download --yes --zip "fw://bbl/PAFIN_844353/${subject}"; then
        echo "Successfully downloaded ${subject}, adding to status file..."
        echo "${subject}" >> "$download_status_file"
    else
        echo "Failed to download ${subject}"
    fi
done
