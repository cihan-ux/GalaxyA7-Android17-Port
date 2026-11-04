# Baseline source audit — 2026-11-05

Target hardware: **Samsung SM-A750F**, device `a7y18lte`, firmware `A750FXXU5CVG1` (user-reported AIDA64), Exynos 7885, arm64, Linux 4.4.177.

## Inspected upstream (LineageOS 18.1)
- Device: https://github.com/exynos7885-dev/old_device_samsung_a7y18lte/tree/lineage-18.1
- Common device: https://github.com/exynos7885-dev/old_device_samsung_exynos7885-common/tree/lineage-18.1
- `BoardConfig.mk` includes `device/samsung/exynos7885-common/BoardConfigCommon.mk`.
- `device.mk` inherits `device/samsung/exynos7885-common/exynos7885.mk`.
- `setup-makefiles.sh` delegates to common device vendor extraction setup.
- Kernel defconfig requested: `lineage_a7y18lte_defconfig`; **matching kernel source/revision not yet validated**.
- `lineage_a7y18lte.mk` sets `PRODUCT_SHIPPING_API_LEVEL := 26` and uses an **A750FNXXU5CVG2** build fingerprint. Target phone is **A750FXXU5CVG1**: do not assume compatibility or replace device identifiers without testing.

## Partition sizes in the 18.1 device tree (bytes, not independently verified against this phone)
| Image | Size |
|---|---:|
| boot | 33554432 |
| recovery | 39845888 |
| system | 4093640704 |
| vendor | 419430400 |
| odm | 369098752 |
| cache | 262144000 |

## Blocking unknowns
1. Exact kernel repository and commit containing the requested defconfig.
2. Common-device branch revision, proprietary blob provenance and vendor compatibility.
3. Android 17 / LineageOS branch build support for legacy Linux 4.4 and HALs.
4. SM-A750F-specific partition map, bootloader unlock status, recovery and stock restore path.
5. Whether the historical 18.1 tree can reproduce a working ROM.

## Next engineering task
Trace common `BoardConfigCommon.mk`, kernel path, `exynos7885.mk`, extraction lists and HAL declarations. Prepare a dependency inventory before writing an Android 17 local manifest.

**No ROM, kernel or recovery image has been built or tested. Do not flash anything from this repository.**
