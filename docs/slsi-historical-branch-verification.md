# Historical SLSI branch verification — 2026-11-05

The six `LineageOS/android_hardware_samsung_slsi-linaro_{config,exynos,exynos5,graphics,interfaces,openmax}` repositories were queried for `lineage-18.1` and `lineage-19.1` branch endpoints. **No branch SHA was confirmed by these lookups.** This is **unverified**, not evidence that a branch never existed. Current default branches are not suitable substitutes for pinned historical revisions.

[LineageOS a21s dependency inventory](https://github.com/LineageOS/android_device_samsung_a21s-common/blob/lineage-23.2/lineage.dependencies) demonstrates modern repository paths, but it is not an Exynos7885 or Galaxy A7 manifest.

`tools/check_slsi_historical_branches.py` stores twelve unverified branch/component combinations. Its offline tests enforce exact SHA syntax and reject wrong branch or component identities. **Do not set a SHA merely from a branch name, or mark any historical dependency resolved without a verified exact commit and build-compatibility evidence.**

Next: identify credible historical Exynos7885 forks, verify commit/tree references and file-level licenses, and compare against the pinned `BoardConfigCommon.mk` include chain. No manifest imports, proprietary files, or phone changes.
