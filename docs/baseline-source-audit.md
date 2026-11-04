# Pinned baseline source audit — 2026-11-04 UTC

The three pins in `manifests/lineage-18.1-research.xml` match the maintained repositories’ `lineage-18.1` branch heads observed during this audit. They are not the separate `old_device_*` source trees previously linked here. See the [checksummed source evidence](source-evidence-audit.md).

| Project | Pinned commit | Source findings |
|---|---|---|
| `exynos7885-dev/device_samsung_a7y18lte` | `f17643ba01010c45b628d5acb8f48350ded61606` | Requests `lineage_a7y18lte_defconfig`; shipping API **28**; retrofit dynamic partition constants |
| `exynos7885-dev/device_samsung_exynos7885-common` | `f2ce8d2093711026f021cba7036334d381d455ef` | Kernel path `kernel/samsung/exynos7885`; **Clang enabled**; custom Samsung boot Makefile and Linaro BSP |
| `exynos7885-dev/kernel_samsung_exynos7885` | `6020dfa8315134187f07ca903c9d2ed7ee0256f5` | Requested defconfig exists; top-level Makefile declares **4.4.302** |

This corrects earlier claims about an unlocated defconfig, GCC 4.9, and shipping API 26. The previously recorded stock handset kernel, 4.4.177, is a different observation from the pinned kernel source version. Neither version proves a kernel build or boot.

The distinct historical `old_device_samsung_a7y18lte` and `old_device_samsung_exynos7885-common` `lineage-18.1` heads were observed as `ac19e6b0a55b502e2d3ecb2f0388b8c139ca922f` and `8bd541011ccfdd3f79d4cf15158fe21fa8e242ff`. Do not combine their facts with the maintained pins merely because the branch names agree.

## Partition declarations

The device BoardConfig declares physical `SYSTEM`, `VENDOR`, and `ODM` sizes of 4,093,640,704, 419,430,400, and 369,098,752 bytes. Their sum is 4,882,169,856 bytes, with a dynamic group size of 4,878,169,856 bytes. Boot, recovery, and cache sizes are 33,554,432, 39,845,888, and 262,144,000 bytes. The common BoardConfig enables a metadata partition. These are source declarations, not measurements of SM-A750F/U5. See the [partition audit](pinned-partition-source-audit.md).

## Remaining blockers

1. Complete revision-specific platform, Samsung hardware, split SLSI and vendor dependency inventory.
2. SM-A750F firmware provenance and SKU differences; NFC-specific entries name SM-A750FN and SM-A750GN.
3. Reproducible baseline source checkout, kernel/toolchain build, and ROM build.
4. Android 17 kernel, HAL/VINTF, build-system and SELinux compatibility tests against an exact target checkout.
5. Independent SM-A750F partition/recovery evidence, outside this source-only task.

No phone access, ROM/kernel build, image validation, or flashing was performed.
