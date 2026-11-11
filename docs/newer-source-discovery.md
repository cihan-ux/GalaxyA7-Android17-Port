# Newer Exynos7885 source discovery — 2026-11-05

A **newer, actively updated set of repositories** exists alongside the historical `old_` device trees:

- https://github.com/exynos7885-dev/device_samsung_a7y18lte (branch `lineage-18.1`)
- https://github.com/exynos7885-dev/device_samsung_exynos7885-common (branch `lineage-18.1`)
- https://github.com/exynos7885-dev/kernel_samsung_exynos7885 (branch `lineage-18.1`)

## Verified matching dependency

The kernel repository **does contain** `arch/arm64/configs/lineage_a7y18lte_defconfig`, matching `TARGET_KERNEL_CONFIG` in the new device tree. The configuration header says Linux 4.4.302 (not a proof of a working build). The common tree expects `kernel/samsung/exynos7885` and now sets `TARGET_KERNEL_CLANG_COMPILE := true`.

## Important caveats

- New device `BoardConfig.mk` specifies dynamic/super partitions with `BOARD_SUPER_PARTITION_SIZE := 4882169856`. This is a **major departure** from the older static partition definitions. Do not assume the SM-A750F stock partition map supports it; this must be independently validated.
- The newer device tree lists NFC ODM manifest SKUs for SM-A750FN and SM-A750GN, not SM-A750F. Investigate SM-A750F variants before using this tree.
- The newer common tree imports `hardware/samsung_slsi-linaro/config/BoardConfig7885.mk` and uses vendor and additional hardware dependencies not included in the research manifest.
- The local manifest for three source repositories is an **inventory/check-out starting point only**, not a complete build manifest. It now pins exact commits; their source files are independently recorded in the [source evidence audit](source-evidence-audit.md). A commit pin alone does not validate dependency compatibility.
- No Android 17 port or flashable image is produced.

## Next
Inspect newer `device.mk`, vendor references, kernel toolchain, manifest and required hardware trees. Resolve the dynamic-partition strategy and SM-A750F support before any build attempt.
