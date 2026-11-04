# Galaxy A7 2018 (SM-A750F) — Android 17 port research

**Status: research-only. Not buildable or flashable.** No Android 17 ROM has been produced or tested.

Target: Samsung Galaxy A7 (2018), **a7y18lte**, Exynos 7885. Baseline from device screenshots: Android 10, firmware A750FXXU5CVG1 (U5), Linux 4.4.177, arm64 ABI.

## Source candidates (not yet verified as a complete build set)
- [LineageOS 18.1 device tree](https://github.com/exynos7885-dev/old_device_samsung_a7y18lte/tree/lineage-18.1)
- [Experimental kernel](https://github.com/AKSharma87/android_kernel_samsung_a7y18lte)
- [Alternative device tree](https://github.com/nnhra/android_device_samsung_a7y18lte)
- [Device recovery/GSI notes](https://github.com/Hari-Pi/a7y18lte-Resources)
- [LineageOS upstream](https://github.com/LineageOS/android)

## Milestones
1. Audit device, common device, kernel, vendor trees, branches and licenses.
2. Verify a working baseline and collect hardware functionality reports.
3. Assess Android 17 kernel/HAL/SELinux/partition compatibility.
4. Prepare a reviewable experimental port; no flashing instructions until recovery is verified.
5. Build on an appropriately equipped Linux machine and validate artifacts.

Do not confuse **a7y18lte** (2018) with **a7y17lte** (2017). Do not upload proprietary firmware, credentials, or personal data.
