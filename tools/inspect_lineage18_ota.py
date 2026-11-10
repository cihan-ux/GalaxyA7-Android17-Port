#!/usr/bin/env python3
"""Read-only, privacy-conscious inventory of a local LineageOS OTA ZIP.

No partition images, proprietary binaries, or user files are extracted. Only
recognized OTA filenames and a small allowlist of public build metadata are
reported. This is a packaging/provenance check, NOT an Android 17 compatibility
or bootability test.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

MAX_ENTRIES = 50000
MAX_METADATA_BYTES = 65536
METADATA_PATH = "META-INF/com/android/metadata"
EXACT_MARKERS = frozenset({
    METADATA_PATH,
    "META-INF/com/google/android/updater-script",
    "META-INF/com/google/android/update-binary",
    "payload.bin",
    "payload_properties.txt",
    "dynamic_partitions_op_list",
    "care_map.txt",
})
PARTITION_PATTERN = re.compile(
    r"(?P<partition>boot|vendor_boot|init_boot|recovery|dtbo|vbmeta|"
    r"vbmeta_system|super|system|system_ext|vendor|product|odm|oem)\."
    r"(?:img|new\.dat(?:\.br)?|transfer\.list|patch\.dat|map)\Z"
)
SAFE_METADATA_KEYS = frozenset({
    "ota-type", "pre-device", "post-build", "post-build-incremental",
    "post-sdk-level", "post-security-patch-level", "post-timestamp",
    "ota-downgrade", "ota-retrofit-dynamic-partitions",
})
HEX64 = re.compile(r"[0-9a-fA-F]{64}\Z")


def _safe_entry_name(name):
    """Check paths without extracting or echoing untrusted archive names."""
    if not name or name.startswith("/") or "\\" in name or "\0" in name:
        return False
    return all(part not in {"", ".", ".."} and not any(ord(ch) < 32 for ch in part)
               for part in name.rstrip("/").split("/"))


def _sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_public_metadata(archive, info):
    if info is None:
        return {}
    if info.file_size > MAX_METADATA_BYTES:
        raise ValueError("OTA metadata exceeds the allowed size")
    with archive.open(info) as stream:
        payload = stream.read(MAX_METADATA_BYTES + 1)
    if len(payload) > MAX_METADATA_BYTES:
        raise ValueError("OTA metadata exceeds the allowed size")
    try:
        lines = payload.decode("utf-8").splitlines()
    except UnicodeError as exc:
        raise ValueError("OTA metadata must be UTF-8") from exc
    metadata = {}
    for line in lines:
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        # Do not echo arbitrary fields, even if they look like a property.
        if key not in SAFE_METADATA_KEYS or key in metadata:
            continue
        if not value or len(value) > 200 or any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
            continue
        metadata[key] = value
    return dict(sorted(metadata.items()))


def inspect_ota(path, expected_sha256=None, expected_size=None):
    """Produce a sanitized JSON-compatible report; never unpack the archive."""
    path = Path(path)
    if expected_sha256 is not None and not HEX64.fullmatch(expected_sha256):
        raise ValueError("Expected SHA-256 must be exactly 64 hex digits")
    if expected_size is not None and expected_size < 0:
        raise ValueError("Expected size cannot be negative")
    size = path.stat().st_size
    if expected_size is not None and size != expected_size:
        raise ValueError("OTA ZIP size does not match expected size")
    checksum = _sha256_file(path)
    if expected_sha256 is not None and checksum != expected_sha256.lower():
        raise ValueError("OTA ZIP SHA-256 mismatch; inventory aborted")

    with zipfile.ZipFile(path, "r") as archive:
        items = archive.infolist()
        if len(items) > MAX_ENTRIES:
            raise ValueError("OTA ZIP contains too many entries")
        seen = set()
        recognized = set()
        partitions = set()
        metadata_info = None
        file_tree = False
        for item in items:
            name = item.filename
            if not _safe_entry_name(name) or name in seen:
                raise ValueError("OTA ZIP has an unsafe or duplicate entry name")
            seen.add(name)
            if item.is_dir():
                continue
            if name in EXACT_MARKERS:
                recognized.add(name)
                if name == METADATA_PATH:
                    metadata_info = item
            match = PARTITION_PATTERN.fullmatch(name)
            if match:
                recognized.add(name)
                partitions.add(match.group("partition"))
            if name.startswith(("system/", "vendor/", "product/", "system_ext/", "odm/")):
                file_tree = True
        metadata = _read_public_metadata(archive, metadata_info)
        if "payload.bin" in recognized:
            packaging = "payload_ota"
        elif any(name.endswith(".transfer.list") or ".new.dat" in name for name in recognized):
            packaging = "block_ota"
        elif partitions:
            packaging = "image_ota"
        elif file_tree:
            packaging = "file_tree_ota"
        else:
            packaging = "unknown"

    warnings = []
    if METADATA_PATH not in recognized:
        warnings.append("standard OTA metadata not found")
    if packaging == "unknown":
        warnings.append("no known OTA payload or partition layout detected")
    return {
        "schema_version": 1,
        "research_only": True,
        "archive": {"bytes": size, "sha256": checksum, "entries": len(items)},
        "packaging": packaging,
        "recognized_entries": sorted(recognized),
        "partition_names": sorted(partitions),
        "public_metadata": metadata,
        "warnings": warnings,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path, help="existing local OTA ZIP; never extracted")
    parser.add_argument("--expected-sha256", help="published digest to verify before analysis")
    parser.add_argument("--expected-size", type=int, help="published size in bytes")
    args = parser.parse_args(argv)
    try:
        report = inspect_ota(args.zip_path, args.expected_sha256, args.expected_size)
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, NotImplementedError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
