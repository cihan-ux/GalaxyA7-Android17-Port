# Additional upstream repositories discovered — 2026-11-05

Research only. **No proprietary binary copied, downloaded, republished, or added to this repository.**

Update: the [maintained SLSI source discovery](slsi-matching-source-discovery.md) supersedes the unresolved-in-this-organization finding below. Five matching-branch repositories have now been located; complete dependency and license validation remains open. The [source evidence audit](source-evidence-audit.md) records immutable Samsung hardware and vendor metadata observations.

The `exynos7885-dev` organization exposes three additional public repositories on `lineage-18.1`:

| Required local path | Upstream repository | Verified file/directory | Status |
|---|---|---|---|
| `hardware/samsung` | [hardware_samsung](https://github.com/exynos7885-dev/hardware_samsung/tree/lineage-18.1) | `dtbhtool/`, `Android.mk` | Candidate; revision/toolchain compatibility not verified |
| `vendor/samsung/a7y18lte` | [proprietary_vendor_samsung_a7y18lte](https://github.com/exynos7885-dev/proprietary_vendor_samsung_a7y18lte/tree/lineage-18.1) | `a7y18lte-vendor.mk`, `proprietary/` | **Proprietary**; exact SM-A750F firmware match and redistribution rights not verified |
| `vendor/samsung/exynos7885-common` | [proprietary_vendor_samsung_exynos7885-common](https://github.com/exynos7885-dev/proprietary_vendor_samsung_exynos7885-common/tree/lineage-18.1) | `exynos7885-common-vendor.mk`, `proprietary/` | **Proprietary**; licensing, provenance and Android 17 compatibility not verified |

The `hardware/samsung_slsi-linaro` dependency remains unresolved in this organization. Its absence here does **not** prove no matching public project exists elsewhere.

## Decision

Do **not** add the proprietary repositories to the project's manifest, mirror their files, or incorporate binaries into CI. Their public visibility is not evidence of redistribution permission. Keep the pinned research manifest restricted to source trees and kernel already verified; use this document to track candidates. Resolve firmware/model provenance, applicable licenses, external BSP and exact revision pins before a complete baseline build.

The historical `A750FNXXU5CVG2` extraction list is not an exact match for the user's `A750FXXU5CVG1` firmware. A successful repository lookup does not resolve this mismatch.
