# Galaxy A7 2018: reconstruct the working Android 11 source baseline

**Research and source checkout only. No finished ROM, no flashable image, and no phone access.**

The user reports that A2L5E0X1's 2026-10-17 LineageOS 18.1 ROM works on
SM-A750F (a7y18lte). The A2L5E0X1/lineage GitHub repository distributes
OTA and release metadata; it is not the full Android source code.

The 13 immutable Git pins in manifests/lineage-18.1-research.xml include:
- Exynos7885 A7 device and shared device trees
- Legacy Exynos7885 Linux kernel
- Samsung hardware, SLSI graphics, media and configuration trees
- Historical Lineage/Samsung SELinux
- Vendor repository references (never publish proprietary blob contents)

These public source pins are useful engineering starting points, not proof
that every listed SHA was used in the actual released ROM. The user's tested
October release is not interchangeable with the November 8 OTA ZIP.

## New reproducible source-checkout check

GitHub workflow: .github/workflows/a7-lineage18-pinned-baseline.yml

1. Initializes LineageOS lineage-18.1 upstream platform manifest metadata.
2. Uses tools/compose_lineage18_overlay.py to generate a safe local-manifest
   overlay, replacing any existing platform paths and refusing ambiguous
   project-name collisions, conflicting remote names, or floating revisions.
3. Runs the actual repo manifest command to validate combined declarations.
4. Syncs only the 13 pinned projects with a bounded timeout.
5. Verifies every local git HEAD against its pinned 40-character commit SHA.
6. Saves status/logs only. Proprietary vendor trees and firmware contents
   remain on the temporary CI runner and are not uploaded as artifacts.

The existing research-validation workflow exercises the generator's offline
tests. Neither workflow compiles a complete Android 11 system or demonstrates
that it can boot.

## Manual reproduction on a suitably provisioned Linux build machine

Clone this repository separately, install git, python3 and the official repo
launcher, then create an empty working directory for the LineageOS tree:

    repo init -u https://github.com/LineageOS/android.git -b lineage-18.1
    repo manifest -o /tmp/a7-base.xml
    python3 /path/to/GalaxyA7-Android17-Port/tools/compose_lineage18_overlay.py \
      --base /tmp/a7-base.xml \
      --out .repo/local_manifests/a7y18lte-pinned.xml
    repo manifest -o /tmp/a7-combined.xml

Use the workflow to verify the 13 pinned projects first. A full repo sync,
lunch and ROM build require a much larger Linux builder and additional
dependencies. Do not use your old Windows laptop as an assumed full
Android 11/17 build environment.

## Outstanding work before a baseline ROM can be built

- Establish the *full* historical platform+BSP module closure, including
  Samsung SLSI Wi-Fi/BT dependencies and the appropriate boot tooling.
- Verify that stock firmware and vendor blobs correspond to SM-A750F, not
  simply the A750FN baseline named in upstream extraction metadata.
- Resolve full LineageOS platform sync time and disk limits; past Soong CI
  attempts timed out *before* compiling a ROM.
- Run product lunch/configure, dependency checks, and a real complete
  LineageOS 18.1 build; audit resulting ZIP and checksum.
- Only then start Android 17 integration. Linux 4.4 is blocked by the
  Android 17 NetBpfLoad minimum kernel version requirements; Linux 6.15
  Exynos7885 work has not been booted on A7 hardware.

Do not commit private firmware, keys, EFS/IMEI contents or user data, and
do not flash or repartition the user's working Android 11 phone.
