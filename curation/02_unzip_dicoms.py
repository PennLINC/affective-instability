"""Expand dicom zip files in order to heudiconv."""

import os
import zipfile
from glob import glob


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/sourcedata/imaging/scitran/bbl/PAFIN_844353"
    status_file = "/cbica/projects/pafin/sourcedata/curation_files/02_status_unzip_dicoms.txt"
    if os.path.exists(status_file):
        with open(status_file, "r") as f:
            unzipped_subjects = f.read().splitlines()
    else:
        unzipped_subjects = []

    subjects = sorted(glob(os.path.join(in_dir, "*")))
    subjects = [os.path.basename(subject) for subject in subjects]

    for subject in subjects:
        if subject in unzipped_subjects:
            print(f"Subject {subject} already processed, skipping...")
            continue

        zip_files = sorted(glob(os.path.join(in_dir, subject, "*", "*", "*.dicom.zip")))
        print(f"Processing {subject}...")
        for zip_file in zip_files:
            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                zip_ref.extractall(os.path.dirname(zip_file))

            os.remove(zip_file)

        with open(status_file, "a") as f:
            f.write(f"{subject}\n")
