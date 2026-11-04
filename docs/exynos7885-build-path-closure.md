# Exynos7885 build path closure: includes versus assigned file paths

The pinned [exynos7885-dev common BoardConfig](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/f2ce8d2093711026f021cba7036334d381d455ef/BoardConfigCommon.mk) contains `include hardware/samsung_slsi-linaro/config/BoardConfig7885.mk` and `BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk`. It also declares `TARGET_KERNEL_SOURCE := kernel/samsung/exynos7885`. The latter two are **assignments**, not literal `include` directives. A scanner limited to includes misses these important build inputs.

The new `tools/audit_exynos7885_build_paths.py` reports literal includes and selected assignment-backed paths separately. It ignores unexpanded Make expressions and does not run Make. `tests/test_exynos7885_build_paths.py` checks eight representative behaviors.

**Evidence status:** The kernel source path matches the pinned [exynos7885 kernel](https://github.com/exynos7885-dev/kernel_samsung_exynos7885), but a matching local checkout, compatible boot image tools, SLSI HAL revisions, and proprietary vendor inputs are not established. No ROM build or device modification has occurred.

**Next:** verify each source path against exact commits and check transitive includes without interpreting unresolved Make variables as available files. A static scanner cannot prove build or Android 17 compatibility.
