# SLSI BoardConfig7885 source-level inspection

Update: a [maintained 18.1 config](slsi-matching-source-discovery.md) is now recorded at an immutable revision. It selects `libhwc2.1`, unlike the newer candidate's `hwc3`. The comparison below remains candidate research, not a substitute for the matching baseline sources.

**2026-11-05 — Candidate only, not approved for build.**

Source: [Exynos2100-common/android_hardware_samsung_slsi-linaro_config, lineage-21](https://github.com/Exynos2100-common/android_hardware_samsung_slsi-linaro_config/tree/lineage-21).

Directly inspected upstream `BoardConfig7885.mk`, `BoardConfigCommon.mk` and `config.mk`. **Each of these three files contains an Apache License 2.0 header.** This is a file-specific finding, not a license clearance for the entire repository or any other Samsung BSP repository.

`BoardConfig7885.mk` declares `TARGET_LINUX_KERNEL_VERSION := 4.4`, `TARGET_SOC_BASE := exynos7885`, `BOARD_USES_EXYNOS_GRALLOC_VERSION := 3`, `BOARD_HWC_VERSION := hwc3`, `TARGET_USES_HWC2 := true`, and `BOARD_LIBACRYL_DEFAULT_COMPOSITOR := fimg2d_8895`. It includes `hardware/samsung_slsi-linaro/config/BoardConfigCommon.mk`.

`BoardConfigCommon.mk` references `hardware/samsung_slsi-linaro/exynos/kernel-$(TARGET_LINUX_KERNEL_VERSION)-headers/kernel-headers` and uses `soong_config_set` for graphics modules. `config.mk` adds five namespaces: `exynos`, `exynos5`, `graphics`, `interfaces`, `openmax`. These are **additional dependency paths**, not proof that the target build supplies them.

The pinned [device common BoardConfig](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/f2ce8d2093711026f021cba7036334d381d455ef/BoardConfigCommon.mk) includes `BoardConfig7885.mk`, so the candidate has a matching *filename and platform declaration*. But the candidate is from `lineage-21` whereas the baseline is `lineage-18.1`; Soong APIs, graphics HAL, BSP branches, VINTF, SELinux and Android 17 compatibility remain unverified.

## Decision

- **File-header licensing:** verified for these three files only.
- **Platform constants:** Exynos 7885 and Linux 4.4 confirmed.
- **Branch/revision compatibility:** **BLOCKED**.
- **Full SLSI dependency closure:** **BLOCKED**.
- **Manifest inclusion or copying:** **NOT APPROVED**.
- **Phone access / flashing:** none.

Run `python3 tools/check_slsi_candidate.py` and offline unit tests to ensure our recorded evidence remains internally consistent. These tests do not replace a build or legal review.
