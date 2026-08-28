#!/cbica/projects/pafin/miniforge3/envs/curation/bin/python
"""Record the scanner software version each participant was scanned with.

The scanner was upgraded from 'syngo MR E11' to 'syngo MR XA60' partway through
the study, which changed the reconstruction as well as the DICOM layout, so the
version belongs in participants.tsv as something analyses can covary for.
"""

import json
import os
from glob import glob

import pandas as pd


LEVELS = {
    "syngo MR E11": "Acquired before the scanner software upgrade.",
    "syngo MR XA60": "Acquired after the scanner software upgrade.",
}
DESCRIPTION = (
    "Version of the scanner software the participant's data were acquired with, "
    "from DICOM tag (0018,1020) Software Versions."
)


def get_software_version(subject_dir):
    """Collect the software versions across a participant's sidecars."""
    versions = set()
    json_files = sorted(glob(os.path.join(subject_dir, "ses-*", "*", "*.json")))
    for json_file in json_files:
        with open(json_file, "r") as fo:
            metadata = json.load(fo)

        if metadata.get("SoftwareVersions"):
            versions.add(metadata["SoftwareVersions"])

    if not versions:
        print(f"No software version found for {os.path.basename(subject_dir)}")
        return "n/a"

    if len(versions) > 1:
        # A participant scanned on both sides of the upgrade needs a sessions.tsv
        # column instead, since one value per participant can't describe them.
        print(
            f"{os.path.basename(subject_dir)} has more than one software version: "
            f"{', '.join(sorted(versions))}"
        )

    return ";".join(sorted(versions))


if __name__ == "__main__":
    dset_dir = "/cbica/projects/pafin/dset"

    participants_file = os.path.join(dset_dir, "participants.tsv")
    # Read everything as strings so the other columns are written back untouched.
    participants = pd.read_csv(
        participants_file, sep="\t", dtype=str, keep_default_na=False
    )
    participants["software_version"] = [
        get_software_version(os.path.join(dset_dir, participant_id))
        for participant_id in participants["participant_id"]
    ]
    participants.to_csv(participants_file, sep="\t", na_rep="n/a", index=False)

    participants_json = os.path.join(dset_dir, "participants.json")
    with open(participants_json, "r") as fo:
        descriptions = json.load(fo)

    versions = set()
    for value in participants["software_version"]:
        versions.update(version for version in value.split(";") if version != "n/a")

    descriptions["software_version"] = {
        "Description": DESCRIPTION,
        "Levels": {
            version: LEVELS.get(version, "Scanner software version.")
            for version in sorted(versions)
        },
    }
    with open(participants_json, "w") as fo:
        json.dump(descriptions, fo, indent=2)
        fo.write("\n")

    print(participants.to_string(index=False))
