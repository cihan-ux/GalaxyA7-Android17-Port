# SLSI interfaces source discovery (2026-11-05)

**New finding:** The `interfaces` repository is **not globally missing**. GitHub repository metadata confirms [LineageOS/android_hardware_samsung_slsi-linaro_interfaces](https://github.com/LineageOS/android_hardware_samsung_slsi-linaro_interfaces), whose observed default branch is `lineage-24.0`. Likewise [LineageOS/android_hardware_samsung_slsi-linaro_config](https://github.com/LineageOS/android_hardware_samsung_slsi-linaro_config) has default branch `lineage-24.0`. This **does not** establish the existence of `lineage-18.1` branches or usable Exynos7885 revisions.

The five `8890q` repositories previously identified (`config`, `exynos`, `exynos5`, `graphics`, `openmax`) were found with observed default branch `lineage-20`; the `8890q` `interfaces` repository lookup was 404. That absence is **specific to the 8890q organization** and must not be generalized to all GitHub repositories.

The [LineageOS A21s dependency manifest](https://github.com/LineageOS/android_device_samsung_a21s-common/blob/lineage-23.2/lineage.dependencies) confirms the modern `interfaces` target path, but it is another device's manifest and **not a compatible A7 dependency manifest**. No source files or proprietary blobs have been imported.

## Verification gate

`tools/check_slsi_source_leads.py` records six candidate repositories, observed default branches, and independent flags for verified historical commit, license review and integration. **All candidates remain blocked** until these checks are substantiated. Its tests prevent accidentally equating a repository's default branch with a validated historical build dependency.

Next: check exact historical branch refs and source headers for each candidate, then resolve compatible pinned commits and the remaining vendor BSP. Do not flash or change the user's phone.
