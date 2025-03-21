"""Calculate phase jolt and phase jump time series from phase data."""

import os
import subprocess
from glob import glob


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/dset"
    out_dir = "/cbica/projects/pafin/derivatives/phase_jolt"

    for subject_dir in glob(os.path.join(in_dir, "sub-*")):
        subject_id = os.path.basename(subject_dir)
        print(subject_id)

        for session_dir in glob(os.path.join(subject_dir, "ses-*")):
            session_id = os.path.basename(session_dir)
            print(f"\t{session_id}")

            out_sub_dir = os.path.join(out_dir, subject_id, session_id, "func")
            os.makedirs(out_sub_dir, exist_ok=True)

            phase_files = sorted(glob(os.path.join(session_dir, "func", "*part-phase_bold.nii.gz")))
            for phase_file in phase_files:
                print(f"\t\t{os.path.basename(phase_file)}")

                out_prefix = os.path.join(
                    out_sub_dir,
                    os.path.basename(phase_file).replace("_part-phase_bold.nii.gz", ""),
                )

                cmd = (
                    "/cbica/projects/pafin/laynii/LN2_PHASE_JOLT "
                    f"-input {phase_file} "
                    "-int13 -phase_jump "
                    f"-output {out_prefix}"
                )
                print(cmd)
                subprocess.run(
                    cmd.split(),
                )
