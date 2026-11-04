# SLSI dependency topology: paths are separate repositories

Source: [LineageOS a21s-common lineage.dependencies](https://github.com/LineageOS/android_device_samsung_a21s-common/blob/lineage-23.2/lineage.dependencies). This is **another device's newer source inventory**, not a verified Galaxy A7 Android 17 build recipe.

The dependency inventory identifies **distinct repositories** that occupy these paths:

- `hardware/samsung_slsi-linaro/config`
- `hardware/samsung_slsi-linaro/exynos`
- `hardware/samsung_slsi-linaro/exynos5`
- `hardware/samsung_slsi-linaro/graphics`
- `hardware/samsung_slsi-linaro/interfaces`
- `hardware/samsung_slsi-linaro/openmax`
- `hardware/samsung_slsi/scsc_wifibt/wpa_supplicant_lib`
- `device/samsung_slsi/sepolicy`

This explains why finding a `BoardConfig7885.mk` file inside the config repository **does not resolve** the other SLSI dependencies. The candidate `config.mk` also adds Soong namespaces for these sibling projects. An individual repository may be public and contain an Apache-licensed file without providing licensing clearance for all sibling repositories.

## Gate

The pinned LineageOS 18.1 baseline remains incomplete. Do not add the above modern repositories to the pinned manifest until **each** has a suitable historical revision, license verification and Exynos 7885-specific compatibility evidence. The a21s source is evidence for *repository layout only*, not proof of binary compatibility or Android 17 support.

The project's offline topology check covers the six `slsi-linaro` paths. No device access is required.
