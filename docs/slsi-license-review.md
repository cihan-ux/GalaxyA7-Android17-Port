# License and SLSI source candidate review (2026-11-05)

The following GitHub repositories were queried for branch and GitHub license metadata. **A missing GitHub license field does not prove that every file is unlicensed**, but it does not establish redistribution rights either.

| Repository | Default branch | GitHub license metadata | Decision |
|---|---|---|---|
| [exynos7885-dev/hardware_samsung](https://github.com/exynos7885-dev/hardware_samsung) | lineage-18.1 | Not declared | Inspect individual source headers and compatible revision before reuse |
| [exynos7885-dev/proprietary_vendor_samsung_a7y18lte](https://github.com/exynos7885-dev/proprietary_vendor_samsung_a7y18lte) | lineage-18.1 | Not declared | **No copying of proprietary binaries** |
| [exynos7885-dev/proprietary_vendor_samsung_exynos7885-common](https://github.com/exynos7885-dev/proprietary_vendor_samsung_exynos7885-common) | lineage-18.1 | Not declared | **No copying of proprietary binaries** |
| [Exynos2100-common/android_hardware_samsung_slsi-linaro_config](https://github.com/Exynos2100-common/android_hardware_samsung_slsi-linaro_config) | lineage-21 | Not declared | Contains a `BoardConfig7885.mk` candidate, but wrong branch generation for pinned LineageOS 18.1 baseline; **not approved** |

The Exynos2100-common candidate demonstrates that a `BoardConfig7885.mk` exists in a public Samsung SLSI config repository. This does **not** validate the entire `hardware/samsung_slsi-linaro` dependency, matching build macros, licensing, or Android 17 support. No revision has been pinned or included in the manifest.

## Enforced research gate

`tools/check_dependency_provenance.py` contains candidate metadata and refuses manifest eligibility unless a non-proprietary candidate has independently verified licensing, firmware compatibility, and an exact 40-character commit pin. Its tests cover missing evidence and prohibited proprietary blob inclusion. The values remain **false/unverified**; do not set them to true merely because the GitHub repository is public.

Next: inspect per-file SPDX headers and exact revision of the SLSI config candidate, search for a matching LineageOS 18.1 branch, and validate against the pinned common `BoardConfigCommon.mk`. All checks are read-only.
