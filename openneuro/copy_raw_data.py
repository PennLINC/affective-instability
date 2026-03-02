import os
from glob import glob

in_dir = "/cbica/projects/pafin/dset"
out_dir = "/cbica/projects/pafin/ds006131"

in_subjects = sorted(glob(os.path.join(in_dir, "sub-*")))
in_subjects = [os.path.basename(sub) for sub in in_subjects]
out_subjects = sorted(glob(os.path.join(out_dir, "sub-*")))
out_subjects = [os.path.basename(sub) for sub in out_subjects]

subjects_to_copy = set(in_subjects) - set(out_subjects)

for subject in subjects_to_copy:
    in_subject_dir = os.path.join(in_dir, subject)
    out_subject_dir = os.path.join(out_dir, subject)
    # cp -RL in_subject_dir out_subject_dir
    os.system(f"cp -RL {in_subject_dir} {out_subject_dir}")
