# First modern Exynos7885 Linux 6.15 kernel Image + Android feature build

This work builds on the confirmed [A7-specific Linux 6.15 device-tree syntax/eMMC build](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42504144337) by checking real kernel source, not only DTB files.

The source is [Mollomm1/linux-exynos7885@c9639f4](https://github.com/Mollomm1/linux-exynos7885/tree/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c), Linux 6.15.0-rc1. It has Exynos7885 MMC DW, SoC clock/pinctrl source, kernel BPF, Android Binder and SELinux implementations. This establishes **source presence**, not a working SM-A750F driver set.

## Reviewed Android 17 kernel research configuration

[`android17-research.fragment`](../port/linux-6.15/config/android17-research.fragment) enables:

- BPF syscall, JIT and cgroup BPF.
- Android Binder IPC and binderfs.
- SELinux plus its network security hooks.

The fragment deliberately **does not** suppress security enforcement, VINTF checks, kernel-version checks, or fake a board memory map. The [config gate](../tools/check_exynos7885_linux615_android_config.py) requires a real evaluated `.config` with the above options and built-in MMC DW Exynos, Exynos clock and Exynos pinctrl. It obtains Android 17 kernel version minimums by parsing the pinned Connectivity loader source, not assuming Android 17 runtime compatibility.

## Build verification

[GitHub Actions compile probe](../.github/workflows/exynos7885-615-a7-kernel-image-probe.yml):

1. Checks out the immutable experimental 6.15 source.
2. Runs ARM64 `defconfig`, stages the reviewed settings with kernel `scripts/config` and applies `olddefconfig`.
3. Fetches the immutable Android 17 `NetBpfLoad.cpp` and `BpfUtils.h` to validate version requirements for API 3700 and 3710.
4. Attempts a **real ARM64 `Image` compilation** using Clang/LLVM.
5. On success, inspects kernel objects for Exynos MMC, clock, pinctrl, Android Binder/binderfs and SELinux; records checksums and logs.

This is a proper compiler experiment; it can fail, and such a failure is an engineering result to analyze. A green Python test or version check is NOT an Image build pass.

## Explicit excluded scope

The separate [A7 experimental DTBs](a7y18lte-emmc-modern-source-mapping.md) have **no verified memory map** and are NOT bootable. Building the Linux 6.15 kernel Image will **not** make an Android 17 boot.img: the SM-A750F memory/carveout mapping, firmware access, Samsung BSP drivers, HAL/vendor ABI, userspace, real runtime eBPF functionality and full SELinux/VINTF checks remain missing. No phone access, flashing, partition modification or proprietary vendor blob redistribution.

Use these source checks to find the next compiler blockers without touching the user's known-good Android 11 ROM.
