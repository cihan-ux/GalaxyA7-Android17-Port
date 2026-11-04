# Verified 8890q historical SLSI branch heads (research only)

On 2026-11-05, GitHub's branch endpoint returned exact `lineage-19.1` commit SHAs:

| SLSI component | 8890q commit |
|---|---|
| config | `99f70404432d35b38eef86d29a68858ae55559b1` |
| exynos | `c04e384bc671c8aa490dfb031af5fc5551490b28` |
| exynos5 | `dd2f9115c2fcb8767a9766da898f06b657872997` |
| graphics | `400aaac267c6e5a8f8a3ad747d9b64a2d2cd281a` |
| openmax | `509019f59bf3de7633e0914718a7d001fd84888d` |

These sources are associated with historical **Exynos8890/8895** device manifests, not a verified Exynos7885 Galaxy A7 manifest. See [ivanmeler historical local manifest](https://github.com/ivanmeler/local_manifests/blob/hero_android12/roomservice.xml).

**Negative compatibility evidence:** `BoardConfig7885.mk` returned 404 at the pinned `8890q/config` commit. Its `BoardConfigCommon.mk` exists and includes an Apache 2.0 file header, but that single header is not repository-wide licensing approval. The `8890q/interfaces` counterpart is not pinned. Consequently the six-component source inventory remains incomplete and **none of these five repositories should be imported into the A7 build manifest**.

The offline `tools/check_slsi_8890q_pins.py` records the exact hashes and rejects compatibility claims while the required interface and Exynos7885 configuration evidence are absent. Unit tests check SHA syntax, missing sibling, and fail-closed behavior. This does not validate Android 17 or authorize flashing.
