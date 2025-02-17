#!/cbica/home/salot/miniconda3/envs/salot/bin/python
"""Prepare ASL data for BIDS compliance.

1.  Split m0scan into two volumes.
2.  Copy the two m0scan-derived volumes to anat as TDP with different acq entities.
    -   Need to add the right InversionTime values to the second(?) JSON.
3.  Retain the first m0scan-derived volume as m0scan in the perf folder.

TODO:

4.  Add cbf scans to .bidsignore.
5.  Add ASL metadata:
    -   M0Type: Separate
    -   TotalAcquiredPairs: 4
    -   ArterialSpinLabelingType: PCASL
    -   PCASLType: unbalanced
    -   LabelingDuration: 1.8
    -   PostLabelingDelay: 1.8
    -   BackgroundSuppression: True
    -   BackgroundSuppressionNumberPulses: 4
    -   RepetitionTimePreparation: Take from RepetitionTimeExcitation
6.  Create aslcontext.tsv.
"""

import os
from glob import glob

import nibabel as nb
import pandas as pd


N_NOISE_VOLS = 3


if __name__ == "__main__":
    dset_dir = "/cbica/home/salot/datasets/pafin"
    subject_dirs = sorted(glob(os.path.join(dset_dir, "sub-*")))
    for subject_dir in subject_dirs:
        sub_id = os.path.basename(subject_dir)
        session_dirs = sorted(glob(os.path.join(subject_dir, "ses-*")))
        for session_dir in session_dirs:
            ses_id = os.path.basename(session_dir)

            # Load scans file
            scans_file = os.path.join(session_dir, f"{sub_id}_{ses_id}_scans.tsv")
            assert os.path.isfile(scans_file), f"Scans file DNE: {scans_file}"
            scans_df = pd.read_table(scans_file)

            perf_dir = os.path.join(session_dir, "perf")

            # Split m0scan into two volumes under the anat directory.
            anat_dir = os.path.join(session_dir, "anat")
            anat_files = sorted(glob(os.path.join(anat_dir, "*_TDP.nii.gz")))
            if len(anat_files) == 0:
                # No TDP scans, so we need to split the m0scan into two volumes.
                # The first and second are TDP scans, but the first one is also used as the m0scan.
                m0scan_files = sorted(glob(os.path.join(perf_dir, "*_m0scan.nii.gz")))
                for m0scan_file in m0scan_files:
                    img = nb.load(m0scan_file)
                    n_vols = img.shape[3]
                    if n_vols == 1:
                        print(f"M0scan has only one volume: {m0scan_file}")
                    else:
                        tdp1_file = os.path.join(
                            anat_dir,
                            f"{sub_id}_{ses_id}_acq-tr1_TDP.nii.gz",
                        )
                        first_img = img.slicer[..., 0]
                        first_img.to_filename(tdp1_file)
                        tdp2_file = os.path.join(
                            anat_dir,
                            f"{sub_id}_{ses_id}_acq-tr2_TDP.nii.gz",
                        )
                        second_img = img.slicer[..., 1]
                        second_img.to_filename(tdp2_file)

                        # Overwrite the two-volume m0scan file with the first volume.
                        first_img.to_filename(m0scan_file)

            # Save out the modified scans.tsv file.
            scans_df = scans_df.sort_values(by=["acq_time", "filename"])
            os.remove(scans_file)
            scans_df.to_csv(scans_file, sep="\t", na_rep="n/a", index=False)
