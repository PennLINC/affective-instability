from __future__ import annotations

import os
import re
from typing import Any, Optional

from heudiconv.utils import SeqInfo

# The scanner was upgraded from 'syngo MR E11' to 'syngo MR XA60' partway through
# the study, which changed how the DICOMs are organized:
#
# 1.  XA writes enhanced (multi-frame) DICOMs, so ImageType (0008,0008) is reduced
#     to four values and loses the NORM/TE<n>/MOSAIC flags E11 used.  The classic
#     ImageType survives in a Siemens private per-frame element, which is what
#     ``custom_seqinfo`` below digs out.
# 2.  Magnitude and phase are always separate series, with '_Pha' appended to the
#     SeriesDescription of the phase series.  Under E11 the single-band references
#     held both parts in one series.
# 3.  Some multi-echo series are split into one series per echo, with '_TE<n>'
#     appended to the SeriesDescription of echoes 2 and up.  Under E11 (and for
#     some XA sequences) every echo lives in one series and dcm2niix splits them.
#
# The heuristic below detects each of these from the DICOM headers themselves, so
# no flag is needed to tell the two scanner software versions apart.

# Siemens private per-frame element holding the classic ImageType in XA DICOMs.
SIEMENS_PRIVATE_CREATOR = "SIEMENS MR SDI 02"
SIEMENS_PRIVATE_IMAGE_TYPE = 0x75

PHASE_SUFFIX = "_Pha"
ECHO_SUFFIX = re.compile(r"^(?P<base>.+)_TE(?P<echo>\d+)$")

# '<echo>' is replaced with '_echo-<n>' for series that hold a single echo of a
# multi-echo acquisition, and with nothing when dcm2niix splits the echoes itself
# (heudiconv then adds the echo entity).
T1 = "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_T1w"
T1_NORM = "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_rec-norm_T1w"
T2 = "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_T2w"
T2_NORM = "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}_rec-norm_T2w"
FMAP_DWI_PA_MAG = (
    "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}"
    "_acq-dwi_dir-PA_run-{item:02d}<echo>_part-mag_epi"
)
FMAP_DWI_PA_PHASE = (
    "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}"
    "_acq-dwi_dir-PA_run-{item:02d}<echo>_part-phase_epi"
)
DWI_AP_MAG = (
    "{bids_subject_session_dir}/dwi/{bids_subject_session_prefix}"
    "_dir-AP_run-{item:02d}<echo>_part-mag_dwi"
)
DWI_AP_PHASE = (
    "{bids_subject_session_dir}/dwi/{bids_subject_session_prefix}"
    "_dir-AP_run-{item:02d}<echo>_part-phase_dwi"
)
FMAP_FUNC_AP_MAG = (
    "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}"
    "_acq-func+meepi_dir-AP_run-{item:02d}<echo>_part-mag_epi"
)
FMAP_FUNC_AP_PHASE = (
    "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}"
    "_acq-func+meepi_dir-AP_run-{item:02d}<echo>_part-phase_epi"
)
FMAP_FUNC_PA_MAG = (
    "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}"
    "_acq-func+meepi_dir-PA_run-{item:02d}<echo>_part-mag_epi"
)
FMAP_FUNC_PA_PHASE = (
    "{bids_subject_session_dir}/fmap/{bids_subject_session_prefix}"
    "_acq-func+meepi_dir-PA_run-{item:02d}<echo>_part-phase_epi"
)
RAT_SBREF = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-rat_dir-PA_run-{item:02d}<echo>_sbref"
)
RAT_SBREF_MAG = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-rat_dir-PA_run-{item:02d}<echo>_part-mag_sbref"
)
RAT_SBREF_PHASE = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-rat_dir-PA_run-{item:02d}<echo>_part-phase_sbref"
)
RAT_MAG = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-rat_dir-PA_run-{item:02d}<echo>_part-mag_bold"
)
RAT_PHASE = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-rat_dir-PA_run-{item:02d}<echo>_part-phase_bold"
)
BAO_SBREF = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-bao_dir-AP_run-{item:02d}<echo>_sbref"
)
BAO_SBREF_MAG = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-bao_dir-AP_run-{item:02d}<echo>_part-mag_sbref"
)
BAO_SBREF_PHASE = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-bao_dir-AP_run-{item:02d}<echo>_part-phase_sbref"
)
BAO_MAG = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-bao_dir-AP_run-{item:02d}<echo>_part-mag_bold"
)
BAO_PHASE = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-bao_dir-AP_run-{item:02d}<echo>_part-phase_bold"
)
ASL = "{bids_subject_session_dir}/perf/{bids_subject_session_prefix}_run-{item:02d}_asl"
M0SCAN = (
    "{bids_subject_session_dir}/perf/{bids_subject_session_prefix}_run-{item:02d}_m0scan"
)
CBF = "{bids_subject_session_dir}/perf/{bids_subject_session_prefix}_run-{item:02d}_cbf"
MEGRE_MAG = (
    "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}"
    "_acq-1p5mm_run-{item:02d}<echo>_part-mag_MEGRE"
)
MEGRE_PHASE = (
    "{bids_subject_session_dir}/anat/{bids_subject_session_prefix}"
    "_acq-1p5mm_run-{item:02d}<echo>_part-phase_MEGRE"
)
# Not acquired in main study
RS_SBREF = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-rest_dir-AP_run-{item:02d}<echo>_sbref"
)
RS_MAG = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-rest_dir-AP_run-{item:02d}<echo>_part-mag_bold"
)
RS_PHASE = (
    "{bids_subject_session_dir}/func/{bids_subject_session_prefix}"
    "_task-rest_dir-AP_run-{item:02d}<echo>_part-phase_bold"
)


def filter_files(fn: str) -> bool:
    """Drop files heudiconv can't parse before it tries to.

    The XA localizer is an enhanced DICOM whose three frames are mutually
    orthogonal, which makes nibabel's multi-frame wrapper raise
    ``Number of slice indices and positions don't match`` and abort the whole
    run.  We never convert the localizer, so skip it outright.  The flywheel
    export names each series directory after its SeriesDescription, so matching
    on the path is enough.
    """
    return not any(
        part.lower().startswith("localizer") for part in fn.split(os.sep)
    )


def create_key(
    template: Optional[str],
    outtype: tuple[str, ...] = ("nii.gz",),
    annotation_classes: None = None,
) -> tuple[str, tuple[str, ...], None]:
    if template is None or not template:
        raise ValueError("Template must be a valid format string")
    return (template, outtype, annotation_classes)


def _private_image_type(dcm: Any) -> tuple[str, ...]:
    """Pull the classic ImageType out of an enhanced (XA) Siemens DICOM.

    Returns an empty tuple for classic (E11) DICOMs, which don't have the
    per-frame functional groups this lives in.
    """
    try:
        frame = dcm.PerFrameFunctionalGroupsSequence[0]
    except (AttributeError, IndexError, TypeError):
        return ()

    for elem in frame:
        if elem.tag.group != 0x0021:
            continue
        try:
            items = list(elem.value)
        except TypeError:
            continue
        for item in items:
            try:
                image_type = item.get_private_item(
                    0x0021, SIEMENS_PRIVATE_IMAGE_TYPE, SIEMENS_PRIVATE_CREATOR
                )
            except (AttributeError, KeyError, TypeError):
                continue
            if image_type.value:
                return tuple(str(value) for value in image_type.value)

    return ()


def custom_seqinfo(wrapper: Any, series_files: list[str]) -> tuple:  # noqa: U100
    """Record the header fields needed to tell the two DICOM flavors apart.

    heudiconv exposes the result as ``SeqInfo.custom``.  It has to be hashable,
    hence the tuples.
    """
    dcm = wrapper.dcm_data
    software_versions = str(dcm.get("SoftwareVersions", "") or "")
    image_type = tuple(str(value) for value in (dcm.get("ImageType", None) or ()))
    complex_component = str(dcm.get("ComplexImageComponent", "") or "")
    return (
        software_versions,
        _private_image_type(dcm) or image_type,
        complex_component,
    )


def _custom(s: SeqInfo) -> tuple[str, tuple[str, ...], str]:
    """Return (software versions, effective image type, complex image component)."""
    custom = getattr(s, "custom", None)
    if isinstance(custom, tuple) and len(custom) == 3:
        return custom
    # Fall back to the plain seqinfo if custom_seqinfo wasn't collected.
    return ("", tuple(s.image_type or ()), "")


def _split_description(description: str) -> tuple[str, Optional[int]]:
    """Split '<base>_TE<n>_Pha' into ('<base>', <n>)."""
    if description.endswith(PHASE_SUFFIX):
        description = description[: -len(PHASE_SUFFIX)]
    match = ECHO_SUFFIX.match(description)
    if match:
        return match.group("base"), int(match.group("echo"))
    return description, None


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

    info: dict[tuple[str, tuple[str, ...], None], list] = {}
    descriptions = {s.series_description for s in seqinfo}

    def add(template: str, s: SeqInfo, echo: Optional[int] = None) -> None:
        echo_entity = "" if echo is None else f"_echo-{echo}"
        key = create_key(template.replace("<echo>", echo_entity), outtype=outdicom)
        info.setdefault(key, []).append([s.series_id])

    def set_only(template: str, s: SeqInfo) -> None:
        """Anatomicals are repeated on rescans; only keep the last one."""
        key = create_key(template.replace("<echo>", ""), outtype=outdicom)
        info[key] = [s.series_id]

    def is_phase(s: SeqInfo) -> bool:
        _, image_type, complex_component = _custom(s)
        if complex_component:
            # Enhanced (XA) DICOMs state this outright.
            return complex_component.upper() == "PHASE"
        if "P" in image_type:
            return True
        if "M" in image_type:
            return False
        # E11 DIFFUSION series are flagged neither M nor P; only the magnitude
        # series is prescan-normalized.
        return "NORM" not in image_type

    def is_norm(s: SeqInfo) -> bool:
        return "NORM" in _custom(s)[1]

    def echo_index(s: SeqInfo) -> Optional[int]:
        """Echo number when this series holds a single echo, else None.

        XA splits some multi-echo acquisitions into one series per echo, naming
        echoes 2 and up '<base>_TE<n>'.  Echo 1 keeps the bare name, so it is only
        recognizable by the presence of its siblings.
        """
        base, echo = _split_description(s.series_description)
        if echo is not None:
            return echo
        if any(other.startswith(f"{base}_TE") for other in descriptions):
            return 1
        return None

    def parts_are_split(s: SeqInfo) -> bool:
        """Whether magnitude and phase live in separate series (XA) or one (E11)."""
        description = s.series_description
        return (
            description.endswith(PHASE_SUFFIX)
            or f"{description}{PHASE_SUFFIX}" in descriptions
        )

    for s in seqinfo:
        protocol_name = s.protocol_name
        description = s.series_description
        echo = echo_index(s)

        # Anatomical scans (we only want the last one)
        if "anat-T1w" in protocol_name:
            set_only(T1_NORM if is_norm(s) else T1, s)
        elif ("anat-T2w" in protocol_name) or ("anat_T2w_product" in protocol_name):
            set_only(T2_NORM if is_norm(s) else T2, s)
        # DWI field maps
        elif "fmap-epi_acq-dwi_dir-PA" in protocol_name:
            add(FMAP_DWI_PA_PHASE if is_phase(s) else FMAP_DWI_PA_MAG, s, echo)
        # DWI scans
        elif "dwi-dwi_acq-HASC92_dir-AP" in protocol_name:
            add(DWI_AP_PHASE if is_phase(s) else DWI_AP_MAG, s, echo)
        # fMRI field maps
        elif "fmap-epi_acq-func_dir-AP" in protocol_name:
            add(FMAP_FUNC_AP_PHASE if is_phase(s) else FMAP_FUNC_AP_MAG, s, echo)
        elif "fmap-epi_acq-func_dir-PA" in protocol_name:
            add(FMAP_FUNC_PA_PHASE if is_phase(s) else FMAP_FUNC_PA_MAG, s, echo)
        # fMRI scans
        elif "func-bold_task-rat" in protocol_name:
            if "SBRef" in description:
                if not parts_are_split(s):
                    add(RAT_SBREF, s, echo)
                else:
                    add(RAT_SBREF_PHASE if is_phase(s) else RAT_SBREF_MAG, s, echo)
            else:
                add(RAT_PHASE if is_phase(s) else RAT_MAG, s, echo)
        elif "func-bold_task-bao" in protocol_name:
            if "SBRef" in description:
                if not parts_are_split(s):
                    add(BAO_SBREF, s, echo)
                else:
                    add(BAO_SBREF_PHASE if is_phase(s) else BAO_SBREF_MAG, s, echo)
            else:
                add(BAO_PHASE if is_phase(s) else BAO_MAG, s, echo)
        elif "func-bold_task-rest" in protocol_name:
            if "SBRef" in description:
                add(RS_SBREF, s, echo)
            else:
                add(RS_PHASE if is_phase(s) else RS_MAG, s, echo)
        # ASL scans
        elif "perf-asl_ASL" in description:
            add(ASL, s)
        elif "perf-asl_M0" in description:
            add(M0SCAN, s)
        elif "perf-asl_MeanPerf" in description:
            add(CBF, s)
        # MEGRE scans
        elif "anat-MEGRE" in protocol_name:
            add(MEGRE_PHASE if is_phase(s) else MEGRE_MAG, s, echo)

    return info
