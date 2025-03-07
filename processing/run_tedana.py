"""Run tedana using fMRIPrep and fMRIPost-AROMA outputs."""

import json
import os
from glob import glob

import pandas as pd
from tedana.workflows import ica_reclassify_workflow, tedana_workflow


if __name__ == "__main__":
    raw_dir = "/cbica/project/pafin/dset"
    fmriprep_dir = "/cbica/project/pafin/derivatives/fmriprep"
    aroma_dir = "/cbica/project/pafin/derivatives/fmripost_aroma"
    tedana_out_dir = "/cbica/project/pafin/derivatives/tedana"
    tedana_aroma_out_dir = "/cbica/project/pafin/derivatives/tedana+aroma"

    base_files = sorted(
        glob(
            os.path.join(
                raw_dir,
                "sub-*",
                "ses-1",
                "func",
                "sub-*_ses-1_*_echo-1_part-mag_bold.nii.gz",
            )
        )
    )
    for base_file in base_files:
        raw_files = sorted(glob(base_file.replace("echo-1", "echo-*")))

        base_filename = os.path.basename(base_file)
        subject = base_filename.split("_")[0]
        prefix = base_filename.split("_echo-1")[0]

        # Get the fMRIPrep brain mask
        mask_base = base_filename.split("_echo-1")[0]
        mask = os.path.join(
            fmriprep_dir,
            subject,
            "ses-1",
            "func",
            f"{mask_base}_part-mag_desc-brain_mask.nii.gz",
        )

        # Get the fMRIPost-AROMA mixing file
        mixing = os.path.join(
            aroma_dir,
            subject,
            "ses-1",
            "func",
            f"{mask_base}_part-mag_space-MNI152NLin6Asym_res-2_desc-melodic_mixing.tsv",
        )

        echo_times = []
        fmriprep_files = []
        for raw_file in raw_files:
            base_query = raw_file.split("_bold.nii.gz")[0]

            # Get echo time from json file
            with open(raw_file.replace(".nii.gz", ".json"), "r") as f:
                echo_times.append(json.load(f)["EchoTime"])

            # Get the fMRIPrep BOLD files
            fmriprep_file = os.path.join(
                fmriprep_dir,
                subject,
                "ses-1",
                "func",
                f"{base_query}_desc-preproc_bold.nii.gz",
            )
            fmriprep_files.append(fmriprep_file)

    tedana_run_out_dir = os.path.join(tedana_out_dir, subject, "ses-1", "func", prefix)
    os.makedirs(tedana_run_out_dir, exist_ok=True)

    tedana_workflow(
        data=fmriprep_files,
        tes=echo_times,
        mask=mask,
        out_dir=tedana_run_out_dir,
        prefix=prefix,
        fittype="curvefit",
        combmode="t2s",
        tree="minimal",
        mixm=mixing,
    )

    tedana_registry = os.path.join(
        tedana_run_out_dir,
        f"{prefix}_desc-tedana_registry.json",
    )

    # Now that tedana is done, we need to combine the classifications from tedana with the AROMA classifications
    # and save the combined classifications to the derivatives folder
    # Get the AROMA classifications
    aroma_classifications = os.path.join(
        aroma_dir,
        subject,
        "ses-1",
        "func",
        f"{mask_base}_part-mag_space-MNI152NLin6Asym_res-2_desc-aroma_metrics.tsv",
    )
    aroma_df = pd.read_table(aroma_classifications)

    # Get the tedana classifications
    tedana_classifications = os.path.join(
        tedana_out_dir,
        subject,
        "ses-1",
        "func",
        f"{prefix}_desc-tedana_metrics.tsv",
    )
    tedana_df = pd.read_table(tedana_classifications)

    assert (
        aroma_df.shape[0] == tedana_df.shape[0]
    ), "AROMA and tedana have different numbers of components"

    # Combine the classifications
    for i_row, aroma_row in aroma_df.iterrows():
        aroma_clf = aroma_row["classification"]
        aroma_rationale = aroma_row["rationale"]
        tedana_clf = tedana_df.loc[i_row, "classification"]
        tedana_rationale = tedana_df.loc[i_row, "rationale"]

        if aroma_clf == "rejected":
            tedana_clf = "rejected"
            tedana_rationale += f" AROMA {aroma_rationale}"

        tedana_df.iloc[i_row, "classification"] = tedana_clf
        tedana_df.iloc[i_row, "rationale"] = tedana_rationale

    # Save the combined classifications
    tedana_aroma_run_out_dir = os.path.join(
        tedana_aroma_out_dir,
        subject,
        "ses-1",
        "func",
        prefix,
    )
    os.makedirs(tedana_aroma_run_out_dir, exist_ok=True)

    # Replace the old classifications with the new ones
    combined_classifications = os.path.join(
        tedana_aroma_run_out_dir,
        f"{prefix}_desc-tedana+aroma_metrics.tsv",
    )
    tedana_df.to_csv(
        combined_classifications,
        sep="\t",
        index=False,
    )

    # Now, run ica_reclassify
    # XXX: Requires version that accepts ctab parameter
    ica_reclassify_workflow(
        registry=tedana_registry,
        out_dir=tedana_aroma_run_out_dir,
        tedort=True,
        prefix=prefix,
        ctab=combined_classifications,
    )

    # Use classifications and time series of components to create a confounds file
    # for XCP-D
    noise_components = tedana_df.loc[tedana_df["classification"] == "noise", "Component"].tolist()
    confounds_file = os.path.join(
        tedana_aroma_run_out_dir,
        f"{prefix}_desc-confounds_timeseries.tsv",
    )
    orth_timeseries = os.path.join(
        tedana_aroma_run_out_dir,
        f"{prefix}_desc-ICAOrth_mixing.tsv",
    )
    confounds_df = pd.read_table(orth_timeseries)
    confounds_df = confounds_df[noise_components]
    confounds_df.to_csv(confounds_file, sep="\t", index=False)
