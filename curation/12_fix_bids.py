#!/cbica/home/salot/miniconda3/envs/salot/bin/python
"""Fix BIDS files after heudiconv conversion.

The necessary steps are:

1.  Split out noRF noise scans from multi-echo BOLD scans.
    -   Also copy the JSON.
2.  Copy first echo of each multi-echo field map without echo entity,
    and change the acq entity from func+meepi to func.
3.  Remove events files.
4.  Drop part-phase bvec and bval files from fmap and dwi directories.
5.  Drop part entity from part-mag bvec and bval filenames in fmap and dwi directories.
6.  Add "Units": "arbitrary" to all phase JSONs.
7.  Add multi-echo field maps to .bidsignore.
"""

import json
import os
import shutil
from glob import glob

import nibabel as nb


N_NOISE_VOLS = 3


if __name__ == "__main__":
    dset_dir = "/cbica/projects/pafin/dset"
    subject_dirs = sorted(glob(os.path.join(dset_dir, "sub-*")))
    for subject_dir in subject_dirs:
        sub_id = os.path.basename(subject_dir)
        session_dirs = sorted(glob(os.path.join(subject_dir, "ses-*")))
        for session_dir in session_dirs:
            ses_id = os.path.basename(session_dir)

            fmap_dir = os.path.join(session_dir, "fmap")
            func_dir = os.path.join(session_dir, "func")
            dwi_dir = os.path.join(session_dir, "dwi")

            # Remove events files
            events_files = sorted(
                glob(os.path.join(func_dir, "*part-mag_events.tsv"))
                + glob(os.path.join(func_dir, "*part-phase_events.tsv"))
            )
            for events_file in events_files:
                os.remove(events_file)

            # Split out noise scans from all multi-echo BOLD files.
            me_bolds = sorted(glob(os.path.join(func_dir, "*echo-*_bold.nii.gz")))
            for me_bold in me_bolds:
                noise_scan = me_bold.replace("_bold.nii.gz", "_noRF.nii.gz")
                if os.path.isfile(noise_scan):
                    print(f"File exists: {os.path.basename(noise_scan)}")
                    continue

                img = nb.load(me_bold)
                n_vols = img.shape[-1]
                if n_vols not in (246, 366, 204):
                    print(f"File is a partial scan: {os.path.basename(me_bold)}")
                    continue

                noise_img = img.slicer[..., -N_NOISE_VOLS:]
                bold_img = img.slicer[..., :-N_NOISE_VOLS]

                # Overwrite the BOLD scan
                os.remove(me_bold)

                bold_img.to_filename(me_bold)
                noise_img.to_filename(noise_scan)

                # Copy the JSON as well
                shutil.copyfile(
                    me_bold.replace(".nii.gz", ".json"),
                    noise_scan.replace(".nii.gz", ".json"),
                )

            # Copy first echo of multi-echo field maps without echo entity.
            me_fmaps = sorted(glob(os.path.join(fmap_dir, "*_acq-func+meepi*_echo-1*epi.*")))
            for me_fmap in me_fmaps:
                out_fmap = me_fmap.replace("_echo-1_", "_").replace("_acq-func+meepi", "_acq-func")
                if os.path.isfile(out_fmap):
                    print(f"File exists: {os.path.basename(out_fmap)}")
                    continue

                me_fmap_fname = os.path.join("fmap", os.path.basename(me_fmap))
                out_fmap_fname = os.path.join("fmap", os.path.basename(out_fmap))
                shutil.copyfile(me_fmap, out_fmap)

            # Remove part-phase bvec and bval field map files
            part_phase_bvecs = sorted(glob(os.path.join(fmap_dir, "*_part-phase*.bvec")))
            for part_phase_bvec in part_phase_bvecs:
                os.remove(part_phase_bvec)
            part_phase_bvals = sorted(glob(os.path.join(fmap_dir, "*_part-phase*.bval")))
            for part_phase_bval in part_phase_bvals:
                os.remove(part_phase_bval)

            # Remove part-phase bvec and bval DWI files
            part_phase_bvecs = sorted(glob(os.path.join(dwi_dir, "*_part-phase*.bvec")))
            for part_phase_bvec in part_phase_bvecs:
                os.remove(part_phase_bvec)
            part_phase_bvals = sorted(glob(os.path.join(dwi_dir, "*_part-phase*.bval")))
            for part_phase_bval in part_phase_bvals:
                os.remove(part_phase_bval)

            # Drop part entity from part-mag bvec and bval field map filenames
            part_mag_bvecs = sorted(glob(os.path.join(fmap_dir, "*_part-mag*.bvec")))
            for part_mag_bvec in part_mag_bvecs:
                new_part_mag_bvec = part_mag_bvec.replace("_part-mag", "")
                os.rename(part_mag_bvec, new_part_mag_bvec)
            part_mag_bvals = sorted(glob(os.path.join(fmap_dir, "*_part-mag*.bval")))
            for part_mag_bval in part_mag_bvals:
                new_part_mag_bval = part_mag_bval.replace("_part-mag", "")
                os.rename(part_mag_bval, new_part_mag_bval)

            # Drop part entity from part-mag bvec and bval DWI filenames
            part_mag_bvecs = sorted(glob(os.path.join(dwi_dir, "*_part-mag*.bvec")))
            for part_mag_bvec in part_mag_bvecs:
                new_part_mag_bvec = part_mag_bvec.replace("_part-mag", "")
                os.rename(part_mag_bvec, new_part_mag_bvec)
            part_mag_bvals = sorted(glob(os.path.join(dwi_dir, "*_part-mag*.bval")))
            for part_mag_bval in part_mag_bvals:
                new_part_mag_bval = part_mag_bval.replace("_part-mag", "")
                os.rename(part_mag_bval, new_part_mag_bval)

            # Add Units: arbitrary to all phase JSONs
            phase_jsons = sorted(glob(os.path.join(session_dir, "*", "*part-phase*.json")))
            for phase_json in phase_jsons:
                with open(phase_json, "r") as f:
                    data = json.load(f)
                data["Units"] = "arbitrary"
                with open(phase_json, "w") as f:
                    json.dump(data, f, indent=4)

    # Add multi-echo field maps to .bidsignore.
    bidsignore_file = os.path.join(dset_dir, ".bidsignore")
    with open(bidsignore_file, "a") as f:
        f.write("\n*_acq-func+meepi*epi.*\n")
