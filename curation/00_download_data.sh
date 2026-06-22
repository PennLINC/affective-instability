#!/bin/bash
unset LD_LIBRARY_PATH

# Read full list of subjects from file
token=$(</cbica/projects/pafin/tokens/flywheel.txt)
~/bin/glibc-2.34/lib/ld-linux-x86-64.so.2 ~/bin/linux_amd64/fw login "$token"
cd "/cbica/projects/pafin/sourcedata/imaging" || exit

# Define files
download_status_file="/cbica/projects/pafin/sourcedata/curation_files/00_status_download.txt"
participants_file="/cbica/projects/pafin/sourcedata/curation_files/pafin_participants.txt"

# Initialize download status file if it doesn't exist
touch "$download_status_file"

# Read full list of subjects from file, then reduce by already-downloaded
subjects=()
if [[ -f "$participants_file" ]]; then
    while IFS= read -r s; do
        [[ -n "$s" ]] && subjects+=("$s")
    done < "$participants_file"
else
    echo "Participants file not found: $participants_file" >&2
    exit 1
fi

# Reduce the list of subjects based on entries in status_download.txt
downloaded_set=()
if [[ -f "$download_status_file" ]]; then
    while IFS= read -r s; do
        [[ -n "$s" ]] && downloaded_set+=("$s")
    done < "$download_status_file"
fi

# Build lookup table
declare -A downloaded_lookup
for subj in "${downloaded_set[@]}"; do
    downloaded_lookup["$subj"]=1
done

# Filter subjects
filtered_subjects=()
for subj in "${subjects[@]}"; do
    if [[ -z "${downloaded_lookup[$subj]}" ]]; then
        filtered_subjects+=("$subj")
    fi
done

echo "Subjects"
echo ${filtered_subjects[*]}

for subject in "${filtered_subjects[@]}"; do

    echo "Downloading subject ${subject}..."
    #~/bin/glibc-2.34/lib/ld-linux-x86-64.so.2 ~/bin/linux_amd64/fw download --yes --zip "fw://bbl/PAFIN_844353/${subject}"
    if ~/bin/glibc-2.34/lib/ld-linux-x86-64.so.2 ~/bin/linux_amd64/fw download --yes --zip "fw://bbl/PAFIN_844353/${subject}"; then
        echo "Successfully downloaded ${subject}, adding to status file..."
        echo "${subject}" >> "$download_status_file"
    else
        echo "Failed to download ${subject}"
    fi
done
