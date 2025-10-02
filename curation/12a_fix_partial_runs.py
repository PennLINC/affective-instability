#!/cbica/projects/pafin/miniforge3/envs/curation/bin/python
"""Address partial runs by overwriting run-01 files with run-02 files (when they exist).

PAFIN only has single-run scans, so we can just overwrite run-01 files with run-02 files,
on the assumption that the run-01 files are from partial scans.
"""

import os
import shutil
from glob import glob


if __name__ == "__main__":
    dset_dir = "/cbica/projects/pafin/dset"
    subject_dirs = sorted(glob(os.path.join(dset_dir, "sub-*")))
    modify_subjects = []
    for subject_dir in subject_dirs:
        sub_id = os.path.basename(subject_dir)
        session_dirs = sorted(glob(os.path.join(subject_dir, "ses-*")))
        for session_dir in session_dirs:
            ses_id = os.path.basename(session_dir)
            print(f"Checking {sub_id} {ses_id}")

            func_dir = os.path.join(session_dir, "func")

            run02_files = sorted(glob(os.path.join(func_dir, "*run-02*")))
            if len(run02_files) == 0:
                print("\tNo run-02 files found")
                continue

            print(f"\t{len(run02_files)} run-02 files found")
            modify_subjects.append(sub_id)
            for run02_file in run02_files:
                run01_file = run02_file.replace("run-02", "run-01")
                run02_filename = os.path.basename(run02_file)
                run01_filename = os.path.basename(run01_file)
                if os.path.isfile(run01_file):
                    print(f"\t\tRemoving {run01_filename}")
                    os.remove(run01_file)

                print(f"\t\tCopying {run02_filename} to {run01_filename}")
                shutil.copyfile(run02_file, run01_file)

    print(f"Subjects to modify: {modify_subjects}")
