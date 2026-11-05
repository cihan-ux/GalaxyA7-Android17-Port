# Pinned Samsung SLSI Soong namespace inventory

The maintained `lineage-18.1` [SLSI config.mk](https://github.com/exynos7885-dev/hardware_samsung_slsi-linaro_config/blob/c7a3ba8a1d8e9a467284f8e4e36672b33494e5f8/config.mk) adds five namespaces: `exynos`, `exynos5`, `graphics`, `interfaces`, and `openmax`, all under `hardware/samsung_slsi-linaro/`.

The earlier discovery identified public same-branch candidates for **four of these five** namespace roots (exynos, exynos5, graphics, openmax). The `interfaces` provider remains **unresolved**; a 404 under one GitHub organization is not proof that the source is unavailable elsewhere.

`tools/audit_slsi_namespaces.py` compares the actual pinned config fixture against a user-provided list of *checked-out directories*. It does not assume discovered repositories are checked out, and does not execute Make/Soong or claim module compatibility.

Example:

```sh
printf '%s\n' hardware/samsung_slsi-linaro/exynos hardware/samsung_slsi-linaro/exynos5 hardware/samsung_slsi-linaro/graphics hardware/samsung_slsi-linaro/openmax > /tmp/slsi-present.txt
python3 tools/audit_slsi_namespaces.py --available-list /tmp/slsi-present.txt --strict
```

The command should exit 1 and report `hardware/samsung_slsi-linaro/interfaces` as unresolved. This is a **synthetic inventory demonstration**, not evidence that these directories exist in a local Android checkout. Full Soong dependency closure, licenses, platform compatibility and an actual build remain blocked. No phone interaction.
