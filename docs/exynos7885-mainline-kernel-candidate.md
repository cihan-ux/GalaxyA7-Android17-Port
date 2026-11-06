# Exynos7885 modern kernel source audit — pinned Linux 6.15-rc1

**2026-11-06. Experimental research lead; NO Galaxy A7 boot support verified.**

## First new path worth testing

A [Linux 6.15.0-rc1 candidate](https://github.com/Mollomm1/linux-exynos7885/tree/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c) was found at immutable commit \`c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c\` on branch \`exynos7870/6.15-rc1\`. Its top-level \`Makefile\` declares \`VERSION=6, PATCHLEVEL=15, SUBLEVEL=0, EXTRAVERSION=-rc1\`. This makes it more modern than the Android 17 NetBpfLoad version thresholds **on paper only**.

Inspected sources:
- [Exynos7885 SoC DTS](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/arch/arm64/boot/dts/exynos/exynos7885.dtsi) (SoC declarations).
- [Exynos7885 clock driver](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/drivers/clk/samsung/clk-exynos7885.c) and [SoC pinctrl DTS](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/arch/arm64/boot/dts/exynos/exynos7885-pinctrl.dtsi).
- [The ONLY Exynos7885 board DTS in the listed Exynos DTS directory](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/arch/arm64/boot/dts/exynos/exynos7885-jackpotlte.dts) identifies itself as \`Samsung Galaxy A8 (2018)\`, \`samsung,jackpotlte\` / \`samsung,exynos7885\`; not \`a7y18lte\`, not SM-A750F.
- [Exynos DT Kbuild](https://github.com/Mollomm1/linux-exynos7885/blob/c9639f4bb4a8b307dea059b404d5f0a8b0fe0e4c/arch/arm64/boot/dts/exynos/Makefile) includes \`exynos7885-jackpotlte.dtb\`, but no SM-A750F target.

Two Android ROM trees with modern branch names were also inspected: [Exynos7885-aosp lineage-24.0](https://github.com/Exynos7885-aosp/kernel_samsung_exynos7885/tree/lineage-24.0) and [crDroid 15.0](https://github.com/crdroidandroid/android_kernel_samsung_exynos7885/tree/15.0). Both have \`VERSION=4, PATCHLEVEL=4, SUBLEVEL=302\` in their root Makefiles. A LineageOS 24.0 branch label does not establish a modern kernel.

This does not rule out other uninspected sources.

## Real next CI experiment

The dedicated [Linux 6.15 Exynos7885 DTB probe](../.github/workflows/exynos7885-mainline-dtb-probe.yml) checks out the immutable kernel commit, asserts the exact version and A8 board identity, configures ARM64, **attempts a real device-tree compilation**, validates the A8 DTB \`model\` and \`compatible\` with \`fdtget\`, and stores checksums and logs. It never accesses a phone. The artifact is expressly marked NOT FOR A7 and NOT FLASHABLE. The test's status must be read from its own CI run; source presence is not a build pass.

## Engineering implications

Successful A8 DTB generation would prove only that this modern Exynos7885/A8 source description can be built. It would **not** prove an A7-compatible DTS, kernel Image, functional RAM/storage/regulators, touchscreen, panel, cameras, Mali graphics, modem, audio, Wi-Fi/Bluetooth, USB, charging, Samsung vendor ABI or Android 17 VINTF/SELinux/eBPF compatibility.

For SM-A750F, the next substantial change must be a **separately researched A7-specific device-tree and driver mapping**, not renaming or flashing \`jackpotlte.dtb\`. Establish a legitimate hardware-backed layout and test each driver. Do not substitute A8 memory, pins or power settings as A7 facts. Do not disable SELinux, spoof kernel versions or bypass NetBpfLoad.
