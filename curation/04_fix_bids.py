#!/cbica/home/salot/miniconda3/envs/salot/bin/python
"""Fix BIDS files after heudiconv conversion.

The necessary steps are:

1.  Split out noRF noise scans from multi-echo BOLD scans.
    -   Also copy the JSON.
2.  Copy first echo of each multi-echo field map without echo entity.
3.  Update filenames in the scans.tsv files.
4.  Remove events files.

TODO:

1.  Split m0scan into two volumes.
2.  Copy the two m0scan-derived volumes to anat as IRT1 with different inv entities.
    -   Need to add the right InversionTime values to the JSONs.
3.  Retain the first m0scan-derived volume as m0scan in the perf folder.
4.  Update the scans.tsv files accordingly.
5.  Drop part-phase bvec and bval files.
6.  Drop part entity from part-mag bvec and bval filenames.
7.  Add "Units": "arbitrary" to all phase JSONs.
8.  Add cbf scans to .bidsignore.
9.  Add multi-echo field maps to .bidsignore.
10. Add DatasetType to dataset_description.json.
11. Add ASL metadata:
    - M0Type: Separate
    - TotalAcquiredPairs: 4
    - ArterialSpinLabelingType: PCASL
    - PCASLType: unbalanced
    - LabelingDuration: 1.8
    - PostLabelingDelay: 1.8
    - BackgroundSuppression: True
    - BackgroundSuppressionNumberPulses: 4
    - RepetitionTimePreparation: Take from RepetitionTimeExcitation
12: Create aslcontext.tsv.
"""

import os
import shutil
from glob import glob

import nibabel as nb
import pandas as pd

N_NOISE_VOLS = 3


if __name__ == "__main__":
    dset_dir = "/Users/taylor/Documents/datasets/pafin/dset/"
    subject_dirs = sorted(glob(os.path.join(dset_dir, "sub-*")))
    for subject_dir in subject_dirs:
        sub_id = os.path.basename(subject_dir)
        session_dirs = sorted(glob(os.path.join(subject_dir, "ses-*")))
        for session_dir in session_dirs:
            ses_id = os.path.basename(session_dir)
            fmap_dir = os.path.join(session_dir, "fmap")
            func_dir = os.path.join(session_dir, "func")

            # Remove events files
            events_files = sorted(glob(os.path.join(func_dir, "*_events.tsv")))
            for events_file in events_files:
                os.remove(events_file)

            # Load scans file
            scans_file = os.path.join(session_dir, f"{sub_id}_{ses_id}_scans.tsv")
            assert os.path.isfile(scans_file), f"Scans file DNE: {scans_file}"
            scans_df = pd.read_table(scans_file)

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

                # Add noise scans to scans DataFrame
                i_row = len(scans_df.index)
                me_bold_fname = os.path.join("func", os.path.basename(me_bold))
                noise_fname = os.path.join("func", os.path.basename(noise_scan))
                scans_df.loc[i_row] = scans_df.loc[scans_df["filename"] == me_bold_fname].iloc[0]
                scans_df.loc[i_row, "filename"] = noise_fname

            # Copy first echo of multi-echo field maps without echo entity.
            me_fmaps = sorted(glob(os.path.join(fmap_dir, "*_acq-func*_echo-1*epi.*")))
            for me_fmap in me_fmaps:
                out_fmap = me_fmap.replace("_echo-1_", "_")
                if os.path.isfile(out_fmap):
                    print(f"File exists: {os.path.basename(out_fmap)}")
                    continue

                me_fmap_fname = os.path.join("fmap", os.path.basename(me_fmap))
                out_fmap_fname = os.path.join("fmap", os.path.basename(out_fmap))
                shutil.copyfile(me_fmap, out_fmap)
                if me_fmap.endswith(".nii.gz"):
                    i_row = len(scans_df.index)
                    scans_df.loc[i_row] = scans_df.loc[
                        scans_df["filename"] == me_fmap_fname
                    ].iloc[0]
                    scans_df.loc[i_row, "filename"] = out_fmap_fname

            # Save out the modified scans.tsv file.
            scans_df = scans_df.sort_values(by=["acq_time", "filename"])
            os.remove(scans_file)
            scans_df.to_csv(scans_file, sep="\t", na_rep="n/a", index=False)
