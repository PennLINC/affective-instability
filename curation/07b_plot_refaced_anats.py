#!/cbica/projects/pafin/miniforge3/envs/curation/bin/python
"""Plot sagittal slices of every refaced anatomical, so the refacing can be checked.

@afni_refacer_run replaces the face rather than zeroing it out, and it does fail
quietly on the occasional image, so every refaced anatomical gets a set of sagittal
slices written to an image directory for someone to page through before the data
leaves the project.

Only images whose sidecar records the refacing are plotted, which is the same test
07_reface_t1ws.sh uses to decide what to skip.  So this cannot be pointed at
un-refaced data by accident, and it should be run after the reface jobs have
finished.

Slices are spread across the head rather than taken at the midline alone: a
midsagittal slice shows the nose profile, but a face can survive off-midline.
"""

import argparse
import json
import os
from glob import glob

import matplotlib

# No display on the cluster, and nothing here needs an interactive figure.
matplotlib.use("Agg")

from nilearn import plotting  # noqa: E402

# Sagittal cuts per image, chosen automatically by nilearn across the head.
N_CUTS = 1
# Above nilearn's default of 100, since a residual face is easy to miss in a slice
# only a couple of hundred pixels wide.
DPI = 150


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dset-dir",
        default="/cbica/projects/pafin/dset",
        help="BIDS dataset holding the refaced anatomicals.",
    )
    parser.add_argument(
        "--out-dir",
        default="/cbica/projects/pafin/images",
        help="Directory to write the PNGs to.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Redraw images that already have a PNG.",
    )
    return parser.parse_args()


def is_refaced(anat_image):
    """Report whether the sidecar records that this image has been refaced."""
    json_file = anat_image.replace(".nii.gz", ".json")
    if not os.path.isfile(json_file):
        return False

    with open(json_file, "r") as fo:
        metadata = json.load(fo)

    return "@afni_refacer_run" in metadata.get("DeidentificationMethod", "")


if __name__ == "__main__":
    args = _parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    anat_images = []
    for suffix in ("T1w", "T2w"):
        anat_images += glob(
            os.path.join(args.dset_dir, "sub-*", "ses-*", "anat", f"*_{suffix}.nii.gz")
        )

    anat_images = sorted(anat_images)
    if not anat_images:
        raise SystemExit(
            f"No refaced anatomicals found in {args.dset_dir}. "
            "Have the reface jobs from 07_reface_t1ws.sh finished?"
        )

    print(f"Plotting {len(anat_images)} refaced anatomical(s) to {args.out_dir}")

    n_plotted, n_skipped = 0, 0
    for anat_image in anat_images:
        # Derived from the image's own name so that acq- and run- variants land in
        # separate files instead of overwriting each other.
        name = os.path.basename(anat_image).replace(".nii.gz", "")
        out_file = os.path.join(args.out_dir, f"{name}.png")

        if is_refaced(anat_image):
            name = f'{name} (refaced)'

        if os.path.isfile(out_file) and not args.overwrite:
            n_skipped += 1
            continue

        print(f"\t{name}")
        display = plotting.plot_anat(
            anat_image,
            display_mode="x",
            cut_coords=N_CUTS,
            title=name,
        )
        display.savefig(out_file, dpi=DPI)
        display.close()
        n_plotted += 1

    print(f"Wrote {n_plotted} image(s), skipped {n_skipped} that already existed")
