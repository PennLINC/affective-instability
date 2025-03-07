"""Convert physio DICOM files with bidsphysio."""

import os
import re
from glob import glob

from bidsphysio.dcm2bids import dcm2bidsphysio


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin"

    subject_dirs = sorted(glob(os.path.join(in_dir, "sourcedata/imaging/scitran/bbl/PAFIN_844353/*_*")))
    for subject_dir in subject_dirs:
        subject_folder = os.path.basename(subject_dir)
        subject_id = subject_folder.split("_")[0]
        print(subject_id)
        session_id = "1"
        search = os.path.join(subject_dir, "CAMRIS^Satterthwait*/*func*_PhysioLog*")
        physio_dirs = sorted(glob(search))
        physio_folders = [os.path.basename(physio_dir) for physio_dir in physio_dirs]
        if not physio_dirs:
            print(f'No physio found with pattern {os.path.join(subject_dir, "CAMRIS^Satterthwait*/*func*_PhysioLog*")}')
        else:
            print("\t" + "\n\t".join(physio_dirs))

        run_types = sorted(set([f.split("_PhysioLog")[0] for f in physio_folders]))
        print("\n".join(run_types))
        for run_type in run_types:
            search2 = os.path.join(subject_dir, "CAMRIS^Satterthwait*", run_type + "_PhysioLog*")
            run_dirs = sorted(glob(search2))
            for i_run, run_dir in enumerate(run_dirs):
                run_num = i_run + 1
                physio_dicoms = sorted(glob(os.path.join(run_dir, "*.dcm")))
                if not physio_dicoms:
                    print(f"No dicoms in {run_dir}")
                    continue

                physio_dicom = physio_dicoms[0]
                out_dir = os.path.join(in_dir, f"dset/sub-{subject_id}/ses-{session_id}/func")
                fname = os.path.basename(physio_dicom)
                if "task" not in fname:
                    print(f"No 'task' found in {fname}")
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

                prefix += f"_run-{run_num:02d}"

                physio_data = dcm2bidsphysio.dcm2bids(physio_dicom)
                physio_data.save_to_bids(bids_fName=prefix)
