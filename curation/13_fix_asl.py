#!/cbica/home/salot/miniconda3/envs/salot/bin/python
"""Prepare ASL data for BIDS compliance.

1.  Split m0scan into two volumes.
2.  Copy the two m0scan-derived volumes to anat as TDP with different acq entities.
    -   Need to add the right InversionTime values to the second(?) JSON.
3.  Retain the first m0scan-derived volume as m0scan in the perf folder.
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

import json
import os
import shutil
from glob import glob

import nibabel as nb
import pandas as pd


HARDCODED_ASL_METADATA = {
    "M0Type": "Separate",
    "TotalAcquiredPairs": 4,
    "ArterialSpinLabelingType": "PCASL",
    "PCASLType": "unbalanced",
    "LabelingDuration": 1.8,
    "PostLabelingDelay": 1.8,
    "BackgroundSuppression": True,
    "BackgroundSuppressionNumberPulses": 4,
}
ASLCONTEXT = pd.DataFrame(columns=["volume_type"], data=["label", "control"] * 4)


if __name__ == "__main__":
    dset_dir = "/cbica/projects/pafin/dset"
    subject_dirs = sorted(glob(os.path.join(dset_dir, "sub-*")))
    for subject_dir in subject_dirs:
        sub_id = os.path.basename(subject_dir)
        session_dirs = sorted(glob(os.path.join(subject_dir, "ses-*")))
        for session_dir in session_dirs:
            ses_id = os.path.basename(session_dir)

            perf_dir = os.path.join(session_dir, "perf")
            anat_dir = os.path.join(session_dir, "anat")

            # The first and second are TDP scans, but the first one is also used as the m0scan.
            m0scan_files = sorted(glob(os.path.join(perf_dir, "*_m0scan.nii.gz")))
            for m0scan_file in m0scan_files:
                print(f"Processing {os.path.basename(m0scan_file)}")
                img = nb.load(m0scan_file)
                n_vols = 1
                if img.ndim == 4:
                    n_vols = img.shape[3]

                if n_vols == 1:
                    print(f"M0scan has only one volume: {m0scan_file}")
                else:
                    tdp1_file = os.path.join(anat_dir, f"{sub_id}_{ses_id}_acq-tr1_TDP.nii.gz")
                    first_img = img.slicer[..., 0]
                    first_img.to_filename(tdp1_file)
                    tdp2_file = os.path.join(anat_dir, f"{sub_id}_{ses_id}_acq-tr2_TDP.nii.gz")
                    second_img = img.slicer[..., 1]
                    second_img.to_filename(tdp2_file)

                    # Overwrite the two-volume m0scan file with the first volume.
                    first_img.to_filename(m0scan_file)

                # Add RepetitionTimePreparation to the m0scan JSON
                m0scan_json = m0scan_file.replace(".nii.gz", ".json")
                with open(m0scan_json, "r") as f:
                    m0scan_metadata = json.load(f)

                m0scan_metadata["RepetitionTimePreparation"] = m0scan_metadata["RepetitionTime"]

                # Copy the m0scan JSON file to the TDP scans, with some modifications.
                tdp1_json = os.path.join(anat_dir, f"{sub_id}_{ses_id}_acq-tr1_TDP.json")
                tdp1_metadata = m0scan_metadata.copy()
                tdp1_metadata["SaturationPulseTime"] = 5
                with open(tdp1_json, "w") as f:
                    json.dump(tdp1_metadata, f, indent=4, sort_keys=True)

                tdp2_json = os.path.join(anat_dir, f"{sub_id}_{ses_id}_acq-tr2_TDP.json")
                tdp2_metadata = m0scan_metadata.copy()
       	       	tdp2_metadata["SaturationPulseTime"] = 5
                tdp2_metadata["InversionTime"] = 1.978
                with open(tdp2_json, "w") as f:
                    json.dump(tdp2_metadata, f, indent=4, sort_keys=True)

                # Add IntendedFor to the m0scan metadata
                # XXX: ASLPrep doesn't support BIDS-URIs yet.
                m0scan_metadata["IntendedFor"] = [
                    m0scan_file.replace("_m0scan.", "_asl.").replace(
                        os.path.join(dset_dir, sub_id) + "/", ""
                    )
                ]
                with open(m0scan_json, "w") as f:
                    json.dump(m0scan_metadata, f, indent=4, sort_keys=True)

            # Patch hardcoded metadata into the asl.json files.
            asl_jsons = sorted(glob(os.path.join(perf_dir, "*_asl.json")))
            for asl_json in asl_jsons:
                print(f"Processing {os.path.basename(asl_json)}")
                with open(asl_json, "r") as f:
                    asl_metadata = json.load(f)

                for key, value in HARDCODED_ASL_METADATA.items():
                    if key in asl_metadata:
                        print(f"Key {key} already in {asl_json}. Skipping.")
                    else:
                        asl_metadata[key] = value

                asl_metadata["RepetitionTimePreparation"] = asl_metadata["RepetitionTimeExcitation"]

                with open(asl_json, "w") as f:
                    json.dump(asl_metadata, f, indent=4, sort_keys=True)

                aslcontext_file = asl_json.replace("asl.json", "aslcontext.tsv")
                ASLCONTEXT.to_csv(aslcontext_file, sep="\t", na_rep="n/a", index=False)

    # Add cbf and TDP scans to .bidsignore.
    bidsignore_file = os.path.join(dset_dir, ".bidsignore")
    with open(bidsignore_file, "a") as f:
        f.write("\n*_cbf.*\n*_TDP.*\n")
