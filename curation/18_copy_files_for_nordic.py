"""Copy associated files for NORDIC-denoised BOLD runs."""

import json
import os
import shutil
from glob import glob


if __name__ == "__main__":
    in_dir = "/cbica/projects/pafin/dset"
    nordic_files = sorted(glob(os.path.join(in_dir, "sub-*/ses-*/func/*rec-nordic*.nii.gz")))
    map_dict = {}  # key: BIDS-URI for original file, value: BIDS-URI for NORDIC file

    for nordic_file in nordic_files:
        base_file = nordic_file.replace("_rec-nordic", "")
        base_uri = "bids::" + base_file.replace(in_dir + "/", "")
        map_dict[base_uri] = "bids::" + nordic_file.replace(in_dir + "/", "")

        # Copy the JSON file
        json_file = base_file.replace(".nii.gz", ".json")
        out_json_file = nordic_file.replace(".nii.gz", ".json")
        with open(json_file, "r") as fo:
            metadata = json.load(fo)

        # Update B0FieldIdentifier and B0FieldSource fields in BOLD JSON
        b0id = metadata["B0FieldIdentifier"][0]
        new_b0id = b0id + "nordic"
        metadata["B0FieldIdentifier"] = [new_b0id]
        b0srcs = metadata["B0FieldSource"]
        new_b0srcs = [b0src for b0src in b0srcs if b0src != b0id]
        metadata["B0FieldSource"] = new_b0srcs + [new_b0id]

        # Write out the updated JSON file
        with open(out_json_file, "w") as fo:
            json.dump(metadata, fo, sort_keys=True, indent=4)

        # Copy the SBRef file
        sbref_file = base_file.replace("_bold.nii.gz", "_sbref.nii.gz")
        out_sbref_file = nordic_file.replace("_bold.nii.gz", "_sbref.nii.gz")
        if sbref_file.endswith("_sbref.nii.gz") and os.path.isfile(sbref_file):
            shutil.copyfile(sbref_file, out_sbref_file)

        # Copy the SBRef JSON file
        sbref_json_file = sbref_file.replace(".nii.gz", ".json")
        out_sbref_json_file = out_sbref_file.replace(".nii.gz", ".json")
        if sbref_json_file.endswith(".json") and os.path.isfile(sbref_json_file):
            shutil.copyfile(sbref_json_file, out_sbref_json_file)

    # Add NORDIC files to IntendedFor field in fmap JSONs
    fmap_jsons = sorted(glob(os.path.join(in_dir, "sub-*/ses-*/fmap/*acq-func*.json")))
    for fmap_json in fmap_jsons:
        with open(fmap_json, "r") as fo:
            metadata = json.load(fo)

        if "IntendedFor" in metadata.keys():
            intended_for = metadata["IntendedFor"]
            new_intended_for = []
            for orig_uri, nordic_uri in map_dict.items():
                for i_f in intended_for:
                    if orig_uri in i_f:
                        new_intended_for.append(nordic_uri)

            # Add the new intended for files to the existing intended for files
            intended_for = sorted(intended_for + new_intended_for)
            metadata["IntendedFor"] = intended_for
            with open(fmap_json, "w") as fo:
                json.dump(metadata, fo, sort_keys=True, indent=4)
