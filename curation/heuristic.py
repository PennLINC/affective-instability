from __future__ import annotations

from typing import Optional

from heudiconv.utils import SeqInfo


def create_key(
    template: Optional[str],
    outtype: tuple[str, ...] = ("nii.gz",),
    annotation_classes: None = None,
) -> tuple[str, tuple[str, ...], None]:
    if template is None or not template:
        raise ValueError("Template must be a valid format string")
    return (template, outtype, annotation_classes)


def infotodict(
    seqinfo: list[SeqInfo],
) -> dict[tuple[str, tuple[str, ...], None], list]:
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    session: scan index for longitudinal acq
    """
    # for this example, we want to include copies of the DICOMs just for our T1
    # and functional scans
    outdicom = ("dicom", "nii.gz")

    t1 = create_key(
        "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_T1w",
        outtype=outdicom,
    )
    t1_norm = create_key(
        "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_rec-norm_T1w",
        outtype=outdicom,
    )
    t2 = create_key(
        "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_T2w",
        outtype=outdicom,
    )
    t2_norm = create_key(
        "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_rec-norm_T2w",
        outtype=outdicom,
    )
    fmap_dwi_ap_mag = create_key(
        "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_acq-dwi_dir-AP_run-{item:02d}_part-mag_epi",
        outtype=outdicom,
    )
    fmap_dwi_ap_phase = create_key(
        "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_acq-dwi_dir-AP_run-{item:02d}_part-phase_epi",
        outtype=outdicom,
    )
    fmap_dwi_pa_mag = create_key(
        "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_acq-dwi_dir-PA_run-{item:02d}_part-mag_epi",
        outtype=outdicom,
    )
    fmap_dwi_pa_phase = create_key(
        "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_acq-dwi_dir-PA_run-{item:02d}_part-phase_epi",
        outtype=outdicom,
    )
    dwi_ap_mag = create_key(
        "{bids_subject_session_dir}/dwi/{bids_subject_session_prefix}_dir-AP_run-{item:02d}_part-mag_dwi",
        outtype=outdicom,
    )
    dwi_ap_phase = create_key(
        "{bids_subject_session_dir}/dwi/{bids_subject_session_prefix}_dir-AP_run-{item:02d}_part-phase_dwi",
        outtype=outdicom,
    )
    dwi_pa_mag = create_key(
        "{bids_subject_session_dir}/dwi/{bids_subject_session_prefix}_dir-PA_run-{item:02d}_part-mag_dwi",
        outtype=outdicom,
    )
    dwi_pa_phase = create_key(
        "{bids_subject_session_dir}/dwi/{bids_subject_session_prefix}_dir-PA_run-{item:02d}_part-phase_dwi",
        outtype=outdicom,
    )
    fmap_func_ap_mag = create_key(
        "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_acq-func+meepi_dir-AP_run-{item:02d}_part-mag_epi",
        outtype=outdicom,
    )
    fmap_func_ap_phase = create_key(
        "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_acq-func+meepi_dir-AP_run-{item:02d}_part-phase_epi",
        outtype=outdicom,
    )
    fmap_func_pa_mag = create_key(
        "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_acq-func+meepi_dir-PA_run-{item:02d}_part-mag_epi",
        outtype=outdicom,
    )
    fmap_func_pa_phase = create_key(
        "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}_acq-func+meepi_dir-PA_run-{item:02d}_part-phase_epi",
        outtype=outdicom,
    )
    rs_sbref = create_key(
        "{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-rest_dir-AP_run-{item:02d}_sbref",
        outtype=outdicom,
    )
    rs_mag = create_key(
        "{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-rest_dir-AP_run-{item:02d}_part-mag_bold",
        outtype=outdicom,
    )
    rs_phase = create_key(
        "{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-rest_dir-AP_run-{item:02d}_part-phase_bold",
        outtype=outdicom,
    )
    rat_sbref = create_key(
        "{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-rat_dir-PA_run-{item:02d}_sbref",
        outtype=outdicom,
    )
    rat_mag = create_key(
        "{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-rat_dir-PA_run-{item:02d}_part-mag_bold",
        outtype=outdicom,
    )
    rat_phase = create_key(
        "{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-rat_dir-PA_run-{item:02d}_part-phase_bold",
        outtype=outdicom,
    )
    bao_sbref = create_key(
        "{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-bao_dir-AP_run-{item:02d}_sbref",
        outtype=outdicom,
    )
    bao_mag = create_key(
        "{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-bao_dir-AP_run-{item:02d}_part-mag_bold",
        outtype=outdicom,
    )
    bao_phase = create_key(
        "{bids_subject_session_dir}/func/{bids_subject_session_prefix}_task-bao_dir-AP_run-{item:02d}_part-phase_bold",
        outtype=outdicom,
    )
    asl_asl = create_key(
        "{bids_subject_session_dir}/perf/{bids_subject_session_prefix}_run-{item:02d}_asl",
        outtype=outdicom,
    )
    asl_m0scan = create_key(
        "{bids_subject_session_dir}/perf/{bids_subject_session_prefix}_run-{item:02d}_m0scan",
        outtype=outdicom,
    )
    asl_cbf = create_key(
        "{bids_subject_session_dir}/perf/{bids_subject_session_prefix}_run-{item:02d}_cbf",
        outtype=outdicom,
    )
    megre_mag = create_key(
        "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_acq-1p5mm_run-{item:02d}_part-mag_MEGRE",
        outtype=outdicom,
    )
    megre_phase = create_key(
        "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_acq-1p5mm_run-{item:02d}_part-phase_MEGRE",
        outtype=outdicom,
    )

    info: dict[tuple[str, tuple[str, ...], None], list] = {
        t1: [],
        t1_norm: [],
        t2: [],
        t2_norm: [],
        fmap_dwi_ap_mag: [],
        fmap_dwi_ap_phase: [],
        fmap_dwi_pa_mag: [],
        fmap_dwi_pa_phase: [],
        dwi_ap_mag: [],
        dwi_ap_phase: [],
        dwi_pa_mag: [],
        dwi_pa_phase: [],
        fmap_func_ap_mag: [],
        fmap_func_ap_phase: [],
        fmap_func_pa_mag: [],
        fmap_func_pa_phase: [],
        rs_sbref: [],
        rs_mag: [],
        rs_phase: [],
        rat_sbref: [],
        rat_mag: [],
        rat_phase: [],
        bao_sbref: [],
        bao_mag: [],
        bao_phase: [],
        asl_asl: [],
        asl_m0scan: [],
        asl_cbf: [],
        megre_mag: [],
        megre_phase: [],
    }
    for s in seqinfo:
        # Anatomical scans (we only want the last one)
        if ("anat-T1w" in s.protocol_name) and ("NORM" not in s.image_type):
            info[t1] = [s.series_id]
        elif ("anat-T1w" in s.protocol_name) and ("NORM" in s.image_type):
            info[t1_norm] = [s.series_id]
        elif ("anat-T2w" in s.protocol_name) and ("NORM" not in s.image_type):
            info[t2] = [s.series_id]
        elif ("anat-T2w" in s.protocol_name) and ("NORM" in s.image_type):
            info[t2_norm] = [s.series_id]
        # DWI field maps
        elif ("fmap-epi_acq-dwi_dir-PA" in s.protocol_name) and ("NORM" in s.image_type):
            info[fmap_dwi_pa_mag].append([s.series_id])
        elif ("fmap-epi_acq-dwi_dir-PA" in s.protocol_name) and ("NORM" not in s.image_type):
            info[fmap_dwi_pa_phase].append([s.series_id])
        # DWI scans
        elif ("dwi-dwi_acq-HASC92_dir-AP" in s.protocol_name) and ("NORM" in s.image_type):
            info[dwi_ap_mag].append([s.series_id])
        elif ("dwi-dwi_acq-HASC92_dir-AP" in s.protocol_name) and ("NORM" not in s.image_type):
            info[dwi_ap_phase].append([s.series_id])
        # fMRI field maps
        elif ("fmap-epi_acq-func_dir-AP" in s.protocol_name) and ("M" in s.image_type):
            info[fmap_func_ap_mag].append([s.series_id])
        elif ("fmap-epi_acq-func_dir-AP" in s.protocol_name) and ("P" in s.image_type):
            info[fmap_func_ap_phase].append([s.series_id])
        elif ("fmap-epi_acq-func_dir-PA" in s.protocol_name) and ("M" in s.image_type):
            info[fmap_func_pa_mag].append([s.series_id])
        elif ("fmap-epi_acq-func_dir-PA" in s.protocol_name) and ("P" in s.image_type):
            info[fmap_func_pa_phase].append([s.series_id])
        # fMRI scans
        elif ("func-bold_task-rat" in s.protocol_name) and ("SBRef" in s.series_description):
            info[rat_sbref].append([s.series_id])
        elif ("func-bold_task-rat" in s.protocol_name) and ("M" in s.image_type):
            info[rat_mag].append([(s.series_id)])
        elif ("func-bold_task-rat" in s.protocol_name) and ("P" in s.image_type):
            info[rat_phase].append([(s.series_id)])
        elif ("func-bold_task-rest" in s.protocol_name) and ("SBRef" in s.series_description):
            info[rs_sbref].append([s.series_id])
        elif ("func-bold_task-rest" in s.protocol_name) and ("M" in s.image_type):
            info[rs_mag].append([(s.series_id)])
        elif ("func-bold_task-rest" in s.protocol_name) and ("P" in s.image_type):
            info[rs_phase].append([(s.series_id)])
        elif ("func-bold_task-bao" in s.protocol_name) and ("SBRef" in s.series_description):
            info[bao_sbref].append([s.series_id])
        elif ("func-bold_task-bao" in s.protocol_name) and ("M" in s.image_type):
            info[bao_mag].append([(s.series_id)])
        elif ("func-bold_task-bao" in s.protocol_name) and ("P" in s.image_type):
            info[bao_phase].append([(s.series_id)])
        # ASL scans
        elif ("perf-asl_ASL" in s.series_description):
            info[asl_asl].append([(s.series_id)])
        elif ("perf-asl_M0" in s.series_description):
            info[asl_m0scan].append([(s.series_id)])
        elif ("perf-asl_MeanPerf" in s.series_description):
            info[asl_cbf].append([(s.series_id)])
        # MEGRE scans
        elif ("anat-MEGRE" in s.protocol_name) and ("M" in s.image_type):
            info[megre_mag].append([s.series_id])
        elif ("anat-MEGRE" in s.protocol_name) and ("P" in s.image_type):
            info[megre_phase].append([s.series_id])

    return info
