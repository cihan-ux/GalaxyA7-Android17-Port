# Kernel and vendor dependency audit — 2026-11-04 UTC

The [source evidence audit](source-evidence-audit.md) records complete source fixtures from the three manifest pins. Earlier notes here described separate `old_device_*` trees; those facts did not describe the pinned maintained baseline.

## Verified at the pins

- Device `BoardConfig.mk` requests `lineage_a7y18lte_defconfig`, which exists at `arch/arm64/configs/lineage_a7y18lte_defconfig` in kernel commit `6020dfa8315134187f07ca903c9d2ed7ee0256f5`.
- The kernel Makefile declares `VERSION = 4`, `PATCHLEVEL = 4`, `SUBLEVEL = 302`. This is a source version, not the previously recorded stock phone kernel 4.4.177 or a newly built artifact.
- Common `BoardConfigCommon.mk` points to `kernel/samsung/exynos7885` and sets `TARGET_KERNEL_CLANG_COMPILE := true`. The previous GCC-only claim is superseded. A working compiler revision is still unverified.
- For A7, the common source selects `BOARD_CUSTOM_BOOTIMG := true`, `hardware/samsung/mkbootimg.mk`, `Image`, separated DT, and the **module name** `dtbhtoolExynos`. The latter is not a literal filesystem path.
- Both device and common product files inherit vendor makefiles outside the three-project manifest. Public availability of a vendor repository establishes neither firmware provenance nor redistribution rights.
- Pinned VINTF XML declares audio HIDL 4.0, camera provider 2.5, graphics allocator 2.0, graphics composer **2.4**, fingerprint 2.1, radio 1.4 and keymaster 3.0. Both manifests use target level 3. These declarations need comparison with the complete assembled vendor manifests and target framework matrices.

## Still unverified

The matching Samsung boot tooling, split SLSI BSP, toolchain, generated DT inputs, firmware-specific extraction outputs, and source checkout must be resolved before attempting a baseline build. A defconfig’s existence is necessary evidence, but does not establish compilation or hardware support. The [Android 17 source comparison](android17-source-compatibility.md) records separate forward-port questions.

The experimental AKSharma87 kernel previously linked here is an alternative lead, not the manifest kernel. Its missing defconfig on one branch does not block locating the requested file in the actual pinned kernel.

No proprietary binaries were downloaded or distributed; no device was accessed.
