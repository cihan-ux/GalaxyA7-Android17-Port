# LineageOS 18.1 Soong CI sync evidence — 2026-11-05

## Observed CI results

- Run [42012292057](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42012292057): failed during `Sync platform with bounded resources`; initialization succeeded, Soong was not attempted. The job logs endpoint returned `BlobNotFound` and the artifacts listing was empty at inspection, so **the root cause cannot be established from this run**.
- Run [42017523834](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42017523834): `repo sync` exited with **status 124** after the explicit **720-second** `timeout`. This is a **time budget expiration**, not evidence of a missing Android module or a manifest collision. Soong was not attempted.
- Run [42019757954](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/42019757954): in progress at time of documentation, using a longer sync window and live verbose output. Do not infer its result in advance.

## Interpretation and next decision

1. A successful `repo init` and manifest overlay do **not** prove the entire historical platform has synced.
2. The first confirmed blocker in the readable logs is a **sync timeout** (exit 124). There is no verified Soong configuration error yet.
3. Do not fabricate missing hardware repositories or device fixes to address a time-budget failure.
4. Inspect the current verbose sync output and disk usage before adjusting concurrency or timeout again.
5. Only attempt `lunch lineage_a7y18lte-userdebug` and Soong after a complete, resolved source sync.
6. SM-A750F / A750FXXU5CVG1 observed device baseline remains separate from A750FN-derived vendor metadata. No phone access or flashing is required for this investigation.

This file contains no proprietary vendor binaries or user device identifiers.
