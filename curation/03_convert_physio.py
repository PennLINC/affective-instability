"""Convert physio DICOM files with bidsphysio."""

import os
import re
from glob import glob

from bidsphysio.dcm2bids import dcm2bidsphysio

if __name__ == "__main__":
    in_dir = "/Users/taylor/Documents/datasets/pafin"

    physio_dicoms = sorted(
        glob(
            os.path.join(
                in_dir,
                "sourcedata/*_*/CAMRIS^Satterthwaite/*func*_PhysioLog*/*.dcm",
            )
        )
    )
    for physio_dicom in physio_dicoms:
        subpath = physio_dicom.split("sourcedata/")[1]
        subject_id, session_id = subpath.split("/")[0].split("_")
        out_dir = os.path.join(in_dir, f"dset/sub-{subject_id}/ses-{session_id}/func")
        fname = os.path.basename(physio_dicom)
        print(fname)
        if not fname.startswith("func"):
            print(f"Skipping {fname}")
            continue

        task = re.findall("_task-([a-zA-Z0-9]+)_", fname)[0]
        acqs_found = re.findall("_acq-([a-zA-Z0-9]+)_", fname)
        dirs_found = re.findall("_dir-([a-zA-Z0-9]+)_", fname)
        runs_found = re.findall("_run-(\d+)_", fname)

        prefix = os.path.join(
            out_dir,
            f"sub-{subject_id}_ses-{session_id}_task-{task}",
        )

        if len(acqs_found):
            prefix += f"_acq-{acqs_found[0]}"

        if len(dirs_found):
            prefix += f"_dir-{dirs_found[0]}"

        if len(runs_found):
            prefix += f"_run-{runs_found[0]}"

        physio_data = dcm2bidsphysio.dcm2bids(physio_dicom)
        physio_data.save_to_bids(bids_fName=prefix)
