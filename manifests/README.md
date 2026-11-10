# Pinned local manifests — research only

lineage-18.1-research.xml currently pins **13 source projects** at immutable
40-character Git commits, including A7 device/common/kernel, Samsung SLSI,
SELinux, hardware and vendor sources. It is **not** a full platform manifest
or a complete build recipe, and is not an Android 17 ROM.

Do not copy it unmodified into a LineageOS source tree if the upstream
manifest already declares an overlapping path; use
tools/compose_lineage18_overlay.py after repo init to generate
a conflict-checked local manifest.

See docs/lineage18-baseline-source-checkout.md for the new bounded GitHub CI
checkout, limitations and Linux setup steps.

Vendor pins point to repositories that may contain proprietary binaries.
Never commit or redistribute those binaries to this public research repo.
Do not flash any image produced solely from this source research.
