# Alternative Exynos7885 historical baseline — incompatible assumptions

**Source verified:** [MacBookPro34-comma-7/android_device_samsung_universal7885-common](https://github.com/MacBookPro34-comma-7/android_device_samsung_universal7885-common/tree/lineage-18.1), `lineage-18.1` branch head `98009b1e310f04ca940bf6c1ef1cc0cc144bdb02`. The source's `BoardConfigCommon.mk` has an Apache-2.0 SPDX header; this does not automatically license unrelated BSP components.

Compared with pinned [exynos7885-dev/device_samsung_a7y18lte](https://github.com/exynos7885-dev/device_samsung_a7y18lte/blob/f17643ba01010c45b628d5acb8f48350ded61606/BoardConfig.mk) and [common tree](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/f2ce8d2093711026f021cba7036334d381d455ef/BoardConfigCommon.mk):

| Source setting | Pinned A7 | Alternative universal7885 |
|---|---|---|
| SLSI variant | `linaro` | `bsp` |
| Boot size | 33,554,432 | 33,554,432 |
| Recovery size | 39,845,888 | 39,845,888 |
| Cache size | 262,144,000 | 209,715,200 |
| System size | 4,093,640,704 (super block device) | 3,833,593,856 (legacy system image) |
| Partition architecture | source defines dynamic/super group | source defines separate system image |
| Kernel boot | Samsung custom boot and separated DT | Samsung custom boot and separated DT |

**Finding:** this is an Exynos7885 historical source tree, but it uses a different BSP approach and different partition assumptions. The alternative may be valuable for tracing older Samsung `bsp` hardware support, but **must not** be mixed into the pinned `linaro` baseline or treated as evidence that the user's SM-A750F can use these partition sizes. In particular, the alternative's userdata partition constant is not a verified size for this handset.

Run `python3 tools/check_exynos7885_alternate.py` to compare source-level constants. The offline tests check both mismatches and matches and require an explicit unverified-device status.

**Decision:** Research candidate only. No manifest import, no repartitioning, no flash, no Android 17 compatibility claim.
