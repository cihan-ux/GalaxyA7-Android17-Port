# Maintained LineageOS 18.1 SLSI source discovery

Observed 2026-11-04 UTC. Earlier discovery notes did not locate the following repositories. They exist under `exynos7885-dev`; branch names and source availability do not establish a working build set.

| Repository suffix under `exynos7885-dev/` | Observed `lineage-18.1` commit |
|---|---|
| `hardware_samsung_slsi-linaro_config` | `c7a3ba8a1d8e9a467284f8e4e36672b33494e5f8` |
| `hardware_samsung_slsi-linaro_exynos` | `f05f00d0280b5e84678a444a195ff6ccdb95d813` |
| `hardware_samsung_slsi-linaro_exynos5` | `6dff1105f24bb5a7d96806f9c61265658e836e25` |
| `hardware_samsung_slsi-linaro_graphics` | `7c28107c046cd666b01adef06617482e26311ab7` |
| `hardware_samsung_slsi-linaro_openmax` | `bf76218765ae6b3636acf0d898bdc81c1a912968` |

The branch observations used `https://api.github.com/repos/exynos7885-dev/<repository>/branches/lineage-18.1`. They are metadata snapshots, not a frozen full platform manifest or license clearance for every sibling.

## Inspected config source

The immutable [BoardConfig7885.mk](https://github.com/exynos7885-dev/hardware_samsung_slsi-linaro_config/blob/c7a3ba8a1d8e9a467284f8e4e36672b33494e5f8/BoardConfig7885.mk), [BoardConfigCommon.mk](https://github.com/exynos7885-dev/hardware_samsung_slsi-linaro_config/blob/c7a3ba8a1d8e9a467284f8e4e36672b33494e5f8/BoardConfigCommon.mk), and [config.mk](https://github.com/exynos7885-dev/hardware_samsung_slsi-linaro_config/blob/c7a3ba8a1d8e9a467284f8e4e36672b33494e5f8/config.mk) are retained in `tests/fixtures/upstream/slsi18/` with their Apache 2.0 headers. Local sizes and Git blob hashes were checked against the non-truncated upstream tree at that commit.

The board declares Linux 4.4, Exynos 7885, gralloc version 3 and **`BOARD_HWC_VERSION := libhwc2.1`**. The previously investigated LineageOS 21 config selects **`hwc3`**. This is a concrete integration difference; a matching filename or chipset declaration cannot justify substituting the newer candidate.

The common config references `hardware/samsung_slsi-linaro/exynos/kernel-$(TARGET_LINUX_KERNEL_VERSION)-headers/kernel-headers`. The product config adds namespaces for `exynos`, `exynos5`, `graphics`, **`interfaces`**, and `openmax`. Those are directories, distinct from direct Makefile includes; the current static scanner does not evaluate namespace module closure or expand header paths.

## Unresolved checks

Repository metadata endpoints for these exact names returned 404:

- `exynos7885-dev/hardware_samsung_slsi-linaro_interfaces`
- `exynos7885-dev/device_samsung_slsi_sepolicy`
- `exynos7885-dev/hardware_samsung_slsi_scsc_wifibt`

This only establishes that those public names were unavailable through the API at inspection time. It does not establish that the needed sources do not exist elsewhere, under another name, or in the platform manifest.

Next, trace their intended provider from a complete maintained 18.1 manifest, inspect each sibling's modules and licensing, verify the 4.4 header directory, and configure/build the baseline with the actual compiler. The existing three-project research manifest remains unchanged. No proprietary binaries or ROM artifacts were imported, and no Android 17 compatibility is claimed.
