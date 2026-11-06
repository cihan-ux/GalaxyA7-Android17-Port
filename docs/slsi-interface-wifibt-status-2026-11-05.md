# Exynos7885 SLSI interfaces and Wi-Fi/Bluetooth source status

## Exact branch verification

- `LineageOS/android_hardware_samsung_slsi-linaro_interfaces` exists, but GitHub returned **404 for the exact `lineage-18.1` branch**. Its current default branch is not a substitute for a matching historical revision.
- `LineageOS/android_hardware_samsung_slsi_scsc_wifibt` and `LineageOS/android_hardware_samsung_slsi-linaro_scsc_wifibt` returned **repository 404** under those exact names.
- The `exynos7885-dev` exact repository names investigated earlier also returned 404.
- These results do **not** prove that Wi-Fi/Bluetooth implementation sources are absent globally; they may be in other repositories, integrated elsewhere or proprietary.

## Build impact

- `hardware/samsung_slsi-linaro/interfaces` is explicitly referenced in `config/config.mk` as a Soong namespace, but no required module from that missing directory has been proven by the current source scan.
- `hardware/samsung_slsi/scsc_wifibt` remains an unresolved source-path candidate. Its necessity must be tested against actual device/common build definitions and a real Soong configuration.
- Do not add empty directories or substitute newer Android 17 / unrelated Exynos source branches to conceal missing dependencies.

## CI integrity

The research manifest now pins 13 sources. Its original offline evidence validator required byte-level fixtures for every project; that assumption became invalid when the manifest expanded to metadata-only sources. The validator now explicitly distinguishes ten metadata-only paths from three byte-evidenced baseline projects. Metadata-only means **not yet byte verified locally**, and no proprietary vendor binaries are checked in.

Next decisive engineering step: verify the metadata-only pins through source checkout or GitHub tree gates, identify real Wi-Fi/BT module references, then attempt a complete historical Soong setup.
