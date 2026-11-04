#!/usr/bin/env python3
"""Offline, read-only provenance gate for third-party ROM dependencies."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Candidate:
    repository: str
    branch: str
    license_verified: bool
    firmware_match_verified: bool
    pinned_commit: str | None
    contains_proprietary_blobs: bool

CANDIDATES = (
    Candidate("exynos7885-dev/hardware_samsung", "lineage-18.1", False, False, None, False),
    Candidate("exynos7885-dev/proprietary_vendor_samsung_a7y18lte", "lineage-18.1", False, False, None, True),
    Candidate("exynos7885-dev/proprietary_vendor_samsung_exynos7885-common", "lineage-18.1", False, False, None, True),
    Candidate("Exynos2100-common/android_hardware_samsung_slsi-linaro_config", "lineage-21", False, False, None, False),
)

def eligible_for_manifest(candidate: Candidate) -> bool:
    """Fail closed until license, pin and compatibility are independently checked."""
    return bool(
        candidate.license_verified
        and candidate.firmware_match_verified
        and candidate.pinned_commit
        and len(candidate.pinned_commit) == 40
        and all(c in "0123456789abcdef" for c in candidate.pinned_commit)
        and not candidate.contains_proprietary_blobs
    )

def main():
    for c in CANDIDATES:
        print(f"{'ELIGIBLE' if eligible_for_manifest(c) else 'BLOCKED'}: {c.repository} [{c.branch}]")
    return 1 if any(eligible_for_manifest(c) for c in CANDIDATES) else 0

if __name__ == "__main__":
    raise SystemExit(main())
