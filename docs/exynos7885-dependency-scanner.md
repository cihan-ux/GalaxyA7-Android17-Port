# Exynos7885 Linaro/BSP dependency closure

The pinned [Exynos7885 common tree](https://github.com/exynos7885-dev/device_samsung_exynos7885-common) uses a Linaro include `hardware/samsung_slsi-linaro/config/BoardConfig7885.mk`. A separate historical [universal7885 common tree](https://github.com/MacBookPro34-comma-7/android_device_samsung_universal7885-common) uses `TARGET_SLSI_VARIANT := bsp` and `device/samsung_slsi/sepolicy/sepolicy.mk`. These are different build graphs and must not be merged solely because they share a chipset. The Linaro config candidate [Exynos2100-common](https://github.com/Exynos2100-common/android_hardware_samsung_slsi-linaro_config) has a BoardConfig7885 file, but its newer branch does not prove LineageOS18.1 compatibility.

New offline scanner `tools/audit_makefile_dependencies.py` reads locally downloaded Makefile text and an explicit list of verified available paths. It extracts static `include` and `inherit-product` references, ignoring comments and unrelated assignments. It **does not execute Makefiles**, expand variables, resolve transitive includes, or claim build readiness. An unrecognized expression requires manual review.

Usage:

```sh
python3 tools/audit_makefile_dependencies.py /path/to/BoardConfigCommon.mk --available-list /path/to/verified-paths.txt
python3 -m unittest discover -s tests -v
```

**Current blockers:** exact compatible SLSI config and sibling revisions, `hardware/samsung/mkbootimg.mk`, `device/samsung_slsi/sepolicy` for the alternative BSP, proprietary blobs and HAL/VINTF adaptation. No source was added to the build manifest; no ROM build or phone operation was attempted.
