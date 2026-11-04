# Build and device safety gates

**Stage 0 — research (current)**: Collect source relationships, historical kernel defconfig, HAL and vendor requirements. Run only offline tests. No Android 17 binaries.

**Stage 1 — reproducible historical baseline**: Pin all required repository commits, verify licenses and blobs, construct a complete manifest, build on an appropriate Linux host, run VINTF and image metadata checks. A successful build is not proof of safe booting.

**Stage 2 — Android 17 feasibility**: Compare platform requirements, deprecated HIDL services, SELinux policy, dynamic partition scheme, kernel interfaces and vendor binary dependencies. Record blockers before modifications.

**Stage 3 — device validation**: Only after a user-approved backup/restore plan and verified model-specific recovery process. Never assume a successful SM-A750FN procedure is safe for SM-A750F.

No CI job here flashes hardware, downloads proprietary firmware, or builds a ROM. The GitHub Actions workflow only validates XML structure and runs unit tests.
