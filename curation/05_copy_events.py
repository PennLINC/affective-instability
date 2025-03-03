"""Copy events files downloaded from Flywheel into the BIDS dataset."""

import os
from glob import glob

import pandas as pd


if __name__ == "__main__":
    out_dir = "/cbica/projects/pafin/dset"
    in_files = sorted(
        glob("/cbica/projects/pafin/sourcedata/imaging/scitran/bbl/PAFIN_844353/*_*/*_events.csv")
    )

    task_dict = {
        "task-Bao": "task-bao",
        "task-YFTR": "task-rat",
    }
    dir_dict = {
        "task-bao": "dir-AP",
        "task-rat": "dir-PA",
    }
    for in_file in in_files:
        fname = os.path.basename(in_file)
        print(fname)

        # Create appropriate output filename
        subject_id = fname.split("_")[0]
        session_id = "ses-1"
        task_id = fname.split("_")[1]
        task_id = task_dict.get(task_id, task_id)
        dir_id = dir_dict[task_id]
        file_out_dir = os.path.join(out_dir, subject_id, session_id, "func")
        out_fname = f"{subject_id}_{session_id}_{task_id}_{dir_id}_run-01_events.tsv"

        out_file = os.path.join(file_out_dir, out_fname)
        df = pd.read_csv(in_file)
        df = df[["onset", "duration", "trial_type", "stimulus"]]
        df.to_csv(out_file, sep="\t", index=False)
