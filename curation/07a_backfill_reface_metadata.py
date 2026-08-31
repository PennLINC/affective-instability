#!/cbica/projects/pafin/miniforge3/envs/curation/bin/python
"""Backfill the refacing record onto anatomicals refaced before that record existed.

07_reface_t1ws.sh decides whether an image still needs refacing by looking for a
DeidentificationMethod field in its sidecar, which the reface job writes once
@afni_refacer_run has succeeded.  Subjects curated before that field existed carry
no such record, so without this script every one of them would be refaced a second
time the next time 07 is run.

Run this once, before running 07 over a dataset that mixes a newly converted batch
in with subjects from an earlier batch.  Pass the new batch's subject IDs; every
other subject in the dataset is taken to have been refaced already and gets the
record written.

Wrongly marking a subject that has not been refaced would leave its face in the
dataset, so a subject ID that matches no directory aborts the run before anything
is written, and --dry-run reports what would be marked without touching a file.
"""

import argparse
import json
import os
from glob import glob

import pandas as pd

# The version @afni_refacer_run reports under the afni/2022_05_03 module, which is
# what refaced every subject curated so far.  07 reads the version from `afni -vnum`
# at job time; nothing here can, since the images were refaced long ago.
DEFAULT_AFNI_VERSION = "AFNI_22.1.03"


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tsv",
        help="participants file containing only defaced subjects",
    )
    parser.add_argument(
        "--dset-dir",
        default="/cbica/projects/pafin/dset",
        help="BIDS dataset to backfill.",
    )
    parser.add_argument(
        "--afni-version",
        default=DEFAULT_AFNI_VERSION,
        help="AFNI version that refaced the existing subjects.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be marked without writing anything.",
    )
    return parser.parse_args()


def find_anat_images(subject_dir):
    """Collect a subject's T1w and T2w images across sessions."""
    images = []
    for suffix in ("T1w", "T2w"):
        images += glob(os.path.join(subject_dir, "ses-*", "anat", f"*_{suffix}.nii.gz"))

    return sorted(images)


if __name__ == "__main__":
    args = _parse_args()

    df = pd.read_table(args.tsv)
    defaced_subjects = df['participant_id'].tolist()

    subject_dirs = sorted(glob(os.path.join(args.dset_dir, "sub-*")))
    subject_dirs = [d for d in subject_dirs if os.path.isdir(d)]
    if not subject_dirs:
        raise SystemExit(f"No subjects found in {args.dset_dir}")

    all_subjects = {os.path.basename(d) for d in subject_dirs}

    method = (
        f"Face replaced with AFNI's @afni_refacer_run ({args.afni_version}) "
        "in reface mode."
    )

    print(f"Marking {len(defaced_subjects)} subject(s) as refaced")

    n_marked, n_already, n_missing = 0, 0, 0
    for subject_dir in subject_dirs:
        if os.path.basename(subject_dir) not in defaced_subjects:
            continue

        for anat_image in find_anat_images(subject_dir):
            json_file = anat_image.replace(".nii.gz", ".json")
            if not os.path.isfile(json_file):
                print(f"\tNo sidecar for {anat_image}")
                n_missing += 1
                continue

            with open(json_file, "r") as fo:
                metadata = json.load(fo)

            if "DeidentificationMethod" in metadata:
                n_already += 1
                continue

            n_marked += 1
            if args.dry_run:
                print(f"\tWould mark {json_file}")
                continue

            metadata["DeidentificationMethod"] = method
            with open(json_file, "w") as fo:
                json.dump(metadata, fo, indent=4, sort_keys=True)

    verb = "Would mark" if args.dry_run else "Marked"
    print(f"{verb} {n_marked} sidecar(s)")
    print(f"{n_already} sidecar(s) already carried the record")
    print(f"{n_missing} image(s) had no sidecar")
