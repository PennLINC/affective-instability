#!/cbica/projects/pafin/miniforge3/envs/curation/bin/python
"""Backfill sidecar metadata that dcm2niix can't read out of XA-era DICOMs.

The scanner upgrade from 'syngo MR E11' to 'syngo MR XA60' replaced the classic
DICOMs, and the Siemens CSA header they carried, with enhanced multi-frame
objects.  dcm2niix reads most acquisition parameters for E11 out of that CSA
header, so XA sidecars come out missing around 40 fields, including two that
matter downstream:

-   RepetitionTime, which BIDS requires for _bold and which leaves pixdim[4] at
    zero when it is absent.
-   PhaseEncodingDirection, without which fMRIPrep and QSIPrep cannot run
    PEPOLAR distortion correction.

Everything written here is read back out of the DICOMs heudiconv copied into
sourcedata/, from the standard tags the enhanced objects do carry.  Each mapping
was checked against an E11 session first: pulling the same tag out of an E11
DICOM reproduces the value dcm2niix wrote into the E11 sidecar, so both scanner
software versions end up with metadata that means the same thing.

The NIfTI headers need the same treatment: dcm2niix writes pixdim[4] from the TR
it could not find, so XA images claim a repetition time of zero.  Once the
sidecar has been fixed the two contradict each other, which the BIDS validator
reports as REPETITION_TIME_MISMATCH, so the header is patched to match.

Only files whose sidecar SoftwareVersions is 'syngo MR XA*' are touched, and only
fields that are absent get added, so E11 data is left exactly as heudiconv wrote
it.

Deliberately not backfilled:

-   PartialFourier.  E11 reports a fraction (0.75, 0.875, 1); the standard
    enhanced tag (0018,9081) only says YES or NO, which is a different quantity.
-   PhaseEncodingSteps.  E11 reports the acquired count; the enhanced tag
    (0018,9231) reports the full in-plane matrix.
-   RepetitionTime for _asl.  The DICOM says 5 s, but dcm2niix derives 34.3293 s
    for the E11 4D ASL series, so writing the DICOM value would not make the two
    versions comparable, and BIDS does not require RepetitionTime for ASL.  The
    DICOM value is written to RepetitionTimeExcitation instead, which is where
    dcm2niix puts the sequence TR for that series under E11, and which
    13_fix_asl.py reads to set RepetitionTimePreparation.  _m0scan and _cbf get a
    normal RepetitionTime, since there the DICOM and the E11 sidecar agree.
-   BaseResolution, ShimSetting, ScanningSequence, SequenceVariant, ScanOptions,
    SAR, TxRefAmp, ImagingFrequency and ConsistencyInfo, which only ever lived in
    the CSA header and have no enhanced-DICOM equivalent.
"""

import gzip
import io
import json
import os
import re
import shutil
import struct
import tarfile
import tempfile
from glob import glob

import pydicom


# Sidecar field -> DICOM tag.  In enhanced DICOMs these sit inside the shared
# functional groups rather than at the top level; find_tag handles both.
FIELD_TAGS = {
    "RepetitionTime": (0x0018, 0x0080),
    "FlipAngle": (0x0018, 0x1314),
    "EchoTrainLength": (0x0018, 0x0091),
    "PixelBandwidth": (0x0018, 0x0095),
    "PercentSampling": (0x0018, 0x0093),
    "PercentPhaseFOV": (0x0018, 0x0094),
    "ParallelReductionFactorInPlane": (0x0018, 0x9069),
    "ReceiveCoilName": (0x0018, 0x1250),
    "InPlanePhaseEncodingDirectionDICOM": (0x0018, 0x1312),
}

# Byte offsets into the 348-byte NIfTI-1 header, which is the first thing in the
# file (gzipped or not): dim[0] holds the number of dimensions and pixdim[4] the
# repetition time.
NIFTI_HEADER_SIZE = 348
DIM_OFFSET = 40
PIXDIM_4_OFFSET = 76 + 4 * 4

# Enhanced DICOMs spell this 'COLUMN'; dcm2niix writes the classic 'COL' for E11.
IN_PLANE_DIRECTIONS = {"ROW": "ROW", "COL": "COL", "COLUMN": "COL"}
PHASE_ENCODING_AXES = {"ROW": "i", "COL": "j"}
# XA DICOMs don't record the blip polarity, but the protocol names encode it, and
# these are the values dcm2niix wrote for the same protocols under E11.
PHASE_ENCODING_POLARITIES = {"AP": "-", "PA": ""}


def find_tag(dcm, tag):
    """Look a tag up at the top level or inside the functional group sequences."""
    if tag in dcm:
        return dcm[tag].value

    for group in ("SharedFunctionalGroupsSequence", "PerFrameFunctionalGroupsSequence"):
        sequence = getattr(dcm, group, None)
        if not sequence:
            continue

        for element in sequence[0]:
            if element.VR != "SQ":
                continue

            for item in element.value:
                if tag in item:
                    return item[tag].value

    return None


def find_source_tarball(json_file):
    """Locate the sourcedata tarball heudiconv wrote for this sidecar's series."""
    datatype_dir = os.path.dirname(json_file)
    session_dir, datatype = os.path.split(datatype_dir)
    subject_dir, ses_id = os.path.split(session_dir)
    dset_dir, sub_id = os.path.split(subject_dir)
    source_dir = os.path.join(dset_dir, "sourcedata", sub_id, ses_id, datatype)

    # The tarball is named after the heuristic key, so it lacks the echo and part
    # entities dcm2niix adds when it splits one series into several files.
    stems = [os.path.basename(json_file)[: -len(".json")]]
    for pattern in (r"_echo-[0-9]+", r"_part-(mag|phase)"):
        stems += [re.sub(pattern, "", stem) for stem in stems]

    for stem in dict.fromkeys(stems):
        tgz_file = os.path.join(source_dir, f"{stem}.dicom.tgz")
        if os.path.isfile(tgz_file):
            return tgz_file

    return None


def read_first_dicom(tgz_file):
    """Read the headers of the first DICOM in a heudiconv sourcedata tarball."""
    with tarfile.open(tgz_file, "r:gz") as tar:
        for member in tar:
            if not member.isfile():
                continue

            handle = tar.extractfile(member)
            if handle is None:
                continue

            try:
                return pydicom.dcmread(
                    io.BytesIO(handle.read()), stop_before_pixels=True, force=True
                )
            except Exception:
                continue

    return None


def open_nifti(nii_file, mode="rb"):
    opener = gzip.open if nii_file.endswith(".gz") else open
    return opener(nii_file, mode)


def read_nifti_header(nii_file):
    """Return the NIfTI header bytes and the byte order they are written in."""
    with open_nifti(nii_file) as fo:
        header = fo.read(NIFTI_HEADER_SIZE)

    if len(header) < NIFTI_HEADER_SIZE:
        return None, None

    for byte_order in ("<", ">"):
        if struct.unpack(f"{byte_order}i", header[:4])[0] == NIFTI_HEADER_SIZE:
            return header, byte_order

    return None, None


def needs_repetition_time(nii_file):
    """Whether this is a 4D image whose header is missing the repetition time."""
    header, byte_order = read_nifti_header(nii_file)
    if header is None:
        return False

    n_dims = struct.unpack_from(f"{byte_order}h", header, DIM_OFFSET)[0]
    pixdim_4 = struct.unpack_from(f"{byte_order}f", header, PIXDIM_4_OFFSET)[0]

    return n_dims >= 4 and pixdim_4 == 0


def set_repetition_time(nii_file, repetition_time):
    """Write the repetition time into pixdim[4], leaving the image data alone.

    dcm2niix leaves pixdim[4] at zero when it can't work the TR out, which makes
    the NIfTI header contradict the sidecar (a BIDS validation error) and hands a
    TR of zero to anything that reads it from the image rather than the JSON.
    Only the header bytes are rewritten, so the image data comes through
    untouched, but the file does have to be recompressed to write it back out.
    """
    header, byte_order = read_nifti_header(nii_file)
    if header is None:
        print(f"Not a NIfTI file: {os.path.basename(nii_file)}")
        return False

    header = bytearray(header)
    struct.pack_into(f"{byte_order}f", header, PIXDIM_4_OFFSET, repetition_time)

    suffix = ".nii.gz" if nii_file.endswith(".gz") else ".nii"
    handle, tmp_file = tempfile.mkstemp(dir=os.path.dirname(nii_file), suffix=suffix)
    os.close(handle)
    try:
        with open_nifti(nii_file) as src, open_nifti(tmp_file, "wb") as dst:
            src.read(NIFTI_HEADER_SIZE)
            dst.write(header)
            shutil.copyfileobj(src, dst, length=8 * 1024 * 1024)

        written, _ = read_nifti_header(tmp_file)
        if written != bytes(header):
            raise RuntimeError(f"Header was not written correctly to {tmp_file}")

        shutil.copymode(nii_file, tmp_file)
        os.replace(tmp_file, nii_file)
    except BaseException:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)

        raise

    return True


def as_number(value):
    """Match dcm2niix, which writes whole numbers without a decimal point."""
    value = float(value)
    return int(value) if value.is_integer() else value


def collect_fields(dcm, json_file, metadata):
    """Gather the sidecar fields that are missing and recoverable from the DICOM."""
    fields = {}
    for field, tag in FIELD_TAGS.items():
        if field in metadata:
            continue

        value = find_tag(dcm, tag)
        if value is None:
            continue

        if field == "RepetitionTime":
            value = as_number(round(float(value) / 1000, 6))
            if json_file.endswith("_asl.json"):
                # For the 4D ASL series dcm2niix splits the two apart: it puts the
                # spacing between volumes in RepetitionTime and the sequence TR in
                # RepetitionTimeExcitation.  The DICOM only gives us the latter,
                # which is also the one 13_fix_asl.py reads.
                if "RepetitionTimeExcitation" not in metadata:
                    fields["RepetitionTimeExcitation"] = value

                continue
        elif field == "EchoTrainLength":
            value = int(value)
            if value == 1:
                # dcm2niix omits this for sequences with no echo train, so adding
                # it would make the XA sidecars differ from the E11 ones.
                continue
        elif field == "InPlanePhaseEncodingDirectionDICOM":
            value = IN_PLANE_DIRECTIONS.get(str(value).upper())
            if value is None:
                continue
        elif field == "ReceiveCoilName":
            value = str(value)
        else:
            value = as_number(value)

        fields[field] = value

    if "PhaseEncodingDirection" in metadata:
        return fields

    direction = re.search(r"_dir-([A-Z]+)", os.path.basename(json_file))
    if direction is None:
        # Anatomicals and ASL have no dir entity, and no PhaseEncodingDirection
        # under E11 either.
        return fields

    in_plane = metadata.get("InPlanePhaseEncodingDirectionDICOM") or fields.get(
        "InPlanePhaseEncodingDirectionDICOM"
    )
    axis = PHASE_ENCODING_AXES.get(str(in_plane).upper())
    polarity = PHASE_ENCODING_POLARITIES.get(direction.group(1))
    if axis != "j" or polarity is None:
        # Only the AP/PA phase encoding used by this protocol is accounted for.
        print(
            f"Cannot infer PhaseEncodingDirection for {os.path.basename(json_file)} "
            f"(dir-{direction.group(1)}, in-plane direction {in_plane})"
        )
        return fields

    fields["PhaseEncodingDirection"] = f"{axis}{polarity}"

    return fields


if __name__ == "__main__":
    dset_dir = "/cbica/projects/pafin/dset"
    dicom_cache = {}

    json_files = sorted(glob(os.path.join(dset_dir, "sub-*/ses-*/*/*.json")))
    for json_file in json_files:
        with open(json_file, "r") as fo:
            metadata = json.load(fo)

        if not str(metadata.get("SoftwareVersions", "")).startswith("syngo MR XA"):
            print(f'Skipping {json_file}')
            continue

        fields = {}
        recoverable = set(FIELD_TAGS) | {"PhaseEncodingDirection"}
        if recoverable.difference(metadata):
            tgz_file = find_source_tarball(json_file)
            if tgz_file is None:
                print(f"No sourcedata DICOMs found for {os.path.basename(json_file)}")
            else:
                if tgz_file not in dicom_cache:
                    dicom_cache[tgz_file] = read_first_dicom(tgz_file)

                dcm = dicom_cache[tgz_file]
                if dcm is None:
                    print(f"Could not read DICOMs for {os.path.basename(json_file)}")
                else:
                    fields = collect_fields(dcm, json_file, metadata)

        if fields:
            metadata.update(fields)
            with open(json_file, "w") as fo:
                json.dump(metadata, fo, indent=4, sort_keys=True)

            print(f"{os.path.basename(json_file)}: added {', '.join(sorted(fields))}")

        # The sidecar now knows the TR, but the image header still doesn't.  This
        # is checked separately from the fields above so that it is still fixed on
        # a re-run, once there is nothing left to add to the sidecar.
        nii_file = json_file.replace(".json", ".nii.gz")
        repetition_time = metadata.get("RepetitionTime")
        if not repetition_time or not os.path.isfile(nii_file):
            continue

        if needs_repetition_time(nii_file):
            set_repetition_time(nii_file, repetition_time)
            print(f"{os.path.basename(nii_file)}: set repetition time in the header")
