# Local manifests — research only

`lineage-18.1-research.xml` maps the three verified, matching **newer** Exynos7885 device/common/kernel repositories. It is not a complete source manifest, not pinned to commits, and **cannot by itself build Android 17**.

Never flash an image based solely on this manifest. The newer device tree includes dynamic partition configuration that requires a separate device-specific safety assessment.
