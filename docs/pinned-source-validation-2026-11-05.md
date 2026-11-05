# Galaxy A7 pinned research source validation — 2026-11-05

**Scope:** Historical LineageOS 18.1 (Android 11) research sources for Samsung Galaxy A7 2018 (a7y18lte). **Not** an Android 17 build, Soong configuration pass, flashable image, or firmware-compatibility certification.

All 13 pinned Git repositories were synced and their checked-out HEADs compared with the exact revisions in `manifests/lineage-18.1-research.xml` across independent GitHub Actions jobs.

| Group | GitHub Actions run | Paths | Result |
| --- | --- | --- | --- |
| Device + kernel | [42028653647](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42028653647) | device/samsung/a7y18lte; device/samsung/exynos7885-common; kernel/samsung/exynos7885 | 3/3 verified |
| Samsung hardware + SELinux | [42032650132](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42032650132) | hardware/samsung; device/lineage/sepolicy; device/samsung_slsi/sepolicy; hardware/samsung_slsi-linaro/config | 4/4 verified |
| SLSI graphics + media | [42033738561](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42033738561) | hardware/samsung_slsi-linaro/exynos; hardware/samsung_slsi-linaro/exynos5; hardware/samsung_slsi-linaro/graphics; hardware/samsung_slsi-linaro/openmax | 4/4 verified |
| Vendor repository provenance | [42034221146](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42034221146) | vendor/samsung/a7y18lte; vendor/samsung/exynos7885-common | 2/2 verified |

Vendor test validates Git revision provenance only; it does not establish redistribution rights for individual blobs or compatibility with the user's stock SM-A750F A750FXXU5CVG1 firmware. The known vendor source provenance differs (A750FNXXU5CVG2). No vendor file contents are uploaded as evidence.

## Platform bottleneck

The full historical LineageOS 18.1 platform sync is substantially larger than the 13-project research manifest. [CI 42017523834](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42017523834) reached repo sync timeout (exit code 124 after 720 seconds), not Soong. Later full-platform jobs failed before Soong, with incomplete or unavailable log evidence. **No specific broken platform project is established.**

Next diagnostic: enumerate actual upstream platform manifest projects; run a bounded, staged sync of selected platform paths with explicit per-stage duration, disk, and progress evidence. Do not treat partial sync as full platform completion.
