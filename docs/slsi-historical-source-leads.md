# Historical SLSI source leads — not build-approved

Research update, 2026-11-05. The pinned Galaxy A7 baseline remains LineageOS 18.1. No Android 17 image has been built.

A historical [ivanmeler/roomservice.xml](https://github.com/ivanmeler/local_manifests/blob/hero_android12/roomservice.xml) lists five SLSI-Linaro repositories from `8890q` at `lineage-19.1`: `config`, `exynos`, `exynos5`, `graphics`, `openmax`. This is a **different Samsung chipset and Android generation**, and omits the `interfaces` sibling. It is useful for tracing the split repository history only. The modern [LineageOS a21s-common dependencies](https://github.com/LineageOS/android_device_samsung_a21s-common/blob/lineage-23.2/lineage.dependencies) include six SLSI-Linaro paths, but are likewise not an A7 build recipe.

Another [ProjectElixir Samsung p3s vendorsetup](https://github.com/ProjectElixir-Devices/android_device_samsung_p3s/blob/elixir/vendorsetup.sh) uses Exynos2100-common sources across mixed branches `14` and `lineage-21`. **Do not run this script:** it includes destructive `rm -rf` operations, fetches unrelated hardware branches, and does not validate the A7.

**Decision:** Keep `hardware/samsung_slsi-linaro/{config,exynos,exynos5,graphics,interfaces,openmax}` as unresolved for a *matching* historical baseline. No public lead above proves SM-A750F, Exynos7885 or Android17 compatibility. Do not add candidate repos to the manifest until exact commits, file licenses and dependency interfaces are verified. Never copy proprietary vendor blobs into this public repository.
