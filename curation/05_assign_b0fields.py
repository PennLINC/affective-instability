#!/cbica/home/salot/miniconda3/envs/salot/bin/python
"""Assign IntendedFor and related metadata fields.

This will do the following:

1. Remove IntendedFor and B0FieldIdentifier fields from multi-echo field maps.
2. Add IntendedFor and B0FieldIdentifier fields to single-echo field maps.
3. Add B0FieldIdentifier (medic) and B0FieldSource (pepolar) fields to BOLD scans.
4. Add IntendedFor and B0FieldIdentifier fields to DWI field maps.
5. Add B0FieldIdentifier (topupdwi) and B0FieldSource (topupdwi) fields to DWI scans.

This script ignores cases where there are multiple field maps.
We will need more advanced logic for that (e.g., based on ShimSettings or acquisition time).

Run this *after* fix_bids.py.

TODO:

1.  Figure out how to handle multiple field maps.
2.  Switch BIDS-URI IntendedFors in the DWI scans for relative paths.
"""

import json
import os
from glob import glob


if __name__ == "__main__":
    dset_dir = "/Users/taylor/Documents/datasets/pafin/dset/"
    subject_dirs = sorted(glob(os.path.join(dset_dir, "sub-*")))
    for subject_dir in subject_dirs:
        subject = os.path.basename(subject_dir)

        session_dirs = sorted(glob(os.path.join(subject_dir, "ses-*")))
        for session_dir in session_dirs:
            session = os.path.basename(session_dir)

            fmap_dir = os.path.join(session_dir, "fmap")
            func_dir = os.path.join(session_dir, "func")
            dmri_dir = os.path.join(session_dir, "dwi")

            # Remove intendedfor-related fields from multi-echo field maps.
            me_fmap_jsons = sorted(
                glob(os.path.join(fmap_dir, "*_acq-func*_echo-*_sbref.json"))
                + glob(os.path.join(fmap_dir, "*_acq-func*_echo-*_epi.json"))
            )
            for me_fmap_json in me_fmap_jsons:
                with open(me_fmap_json, "r") as fo:
                    json_metadata = json.load(fo)

                if "B0FieldIdentifier" in json_metadata.keys():
                    json_metadata.pop("B0FieldIdentifier")

                if "B0FieldSource" in json_metadata.keys():
                    json_metadata.pop("B0FieldSource")

                if "IntendedFor" in json_metadata.keys():
                    json_metadata.pop("IntendedFor")

                with open(me_fmap_json, "w") as fo:
                    json.dump(json_metadata, fo, sort_keys=True, indent=4)

            # Add intendedfor-related fields to single-echo field maps.
            se_fmap_jsons = sorted(glob(os.path.join(fmap_dir, "*acq-func_*_epi.json")))
            se_fmap_jsons = [f for f in se_fmap_jsons if "echo-" not in f]
            for ap_fmap_json in se_fmap_jsons:
                pa_fmap_json = ap_fmap_json.replace("_dir-AP_", "_dir-PA_")
                with open(ap_fmap_json, "r") as fo:
                    ap_metadata = json.load(fo)

                with open(pa_fmap_json, "r") as fo:
                    pa_metadata = json.load(fo)

                # B0Field names should be funcpepolar[run]
                # Extract run number from filename
                run_number = ap_fmap_json.split("_run-")[1].split("_")[0]
                b0fieldname = f"funcpepolar{run_number}"

                target_files = sorted(glob(os.path.join(func_dir, "*bold.nii.gz")))
                target_jsons = [f.replace(".nii.gz", ".json") for f in target_files]
                ap_metadata["B0FieldIdentifier"] = [b0fieldname]
                pa_metadata["B0FieldIdentifier"] = [b0fieldname]
                target_filenames = ["bids::" + tf.replace(dset_dir, "") for tf in target_files]
                ap_metadata["IntendedFor"] = target_filenames
                pa_metadata["IntendedFor"] = target_filenames

                with open(ap_fmap_json, "w") as fo:
                    json.dump(ap_metadata, fo, sort_keys=True, indent=4)

                with open(pa_fmap_json, "w") as fo:
                    json.dump(pa_metadata, fo, sort_keys=True, indent=4)

                for target_json in target_jsons:
                    task = target_json.split("_task-")[1].split("_")[0]
                    run = target_json.split("_run-")[1].split("_")[0]
                    medic_name = f"medic{task}{run}"

                    with open(target_json, "r") as fo:
                        target_metadata = json.load(fo)

                    # if "B0FieldSource" not in target_metadata.keys():
                    target_metadata["B0FieldSource"] = []
                    target_metadata["B0FieldSource"].append(b0fieldname)
                    target_metadata["B0FieldSource"].append(medic_name)
                    target_metadata["B0FieldIdentifier"] = [medic_name]

                    with open(target_json, "w") as fo:
                        json.dump(target_metadata, fo, sort_keys=True, indent=4)

            # Add intendedfor-related fields to dwi field maps.
            dwi_fmap_jsons = sorted(glob(os.path.join(fmap_dir, "*acq-dwi*_epi.json")))
            for dwi_fmap_json in dwi_fmap_jsons:
                run = dwi_fmap_json.split("_run-")[1].split("_")[0]
                with open(dwi_fmap_json, "r") as fo:
                    json_metadata = json.load(fo)

                target_files = sorted(glob(os.path.join(dmri_dir, "*dwi.nii.gz")))
                target_jsons = [f.replace(".nii.gz", ".json") for f in target_files]
                json_metadata["IntendedFor"] = [
                    "bids::" + tf.replace(dset_dir, "") for tf in target_files
                ]
                b0fieldname = f"topupdwi{run}"
                json_metadata["B0FieldIdentifier"] = [b0fieldname]

                with open(dwi_fmap_json, "w") as fo:
                    json.dump(json_metadata, fo, sort_keys=True, indent=4)

                for target_json in target_jsons:
                    with open(target_json, "r") as fo:
                        target_metadata = json.load(fo)

                    target_metadata["B0FieldSource"] = [b0fieldname]
                    target_metadata["B0FieldIdentifier"] = [b0fieldname]

                    with open(target_json, "w") as fo:
                        json.dump(target_metadata, fo, sort_keys=True, indent=4)
