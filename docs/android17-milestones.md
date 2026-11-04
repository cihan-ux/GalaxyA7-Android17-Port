# Android 17 port: evidence-based milestone tracker

This tracker separates verified source preparation from device and build validation. **No flashable ROM exists.**

| Gate | Status | Evidence / unblock requirement |
|---|---|---|
| G0: Source provenance | PASS (research only) | Three LineageOS 18.1 projects pinned to commit hashes |
| G1: Manifest structure | PASS (research only) | GitHub Actions offline tests |
| G2: Partition arithmetic | PASS (source arithmetic only) | Super sum and reserve validated, not device topology |
| G3: Exact SM-A750F partition topology | BLOCKED | Read-only device-specific partition layout evidence needed |
| G4: SM-A750F vendor provenance | BLOCKED | Upstream A750FN blob list differs from A750F stock build |
| G5: Complete historical BSP dependencies | BLOCKED | Vendor trees, Samsung SLSI and boot tooling unresolved |
| G6: Reproducible historical baseline build | NOT STARTED | G3–G5 must be addressed first |
| G7: Android 17 API/HAL/VINTF/SELinux port | NOT STARTED | No compatible target implementation verified |
| G8: Boot/recovery validation | NOT STARTED | Requires backups, safe recovery plan and explicit user approval |

## Next highest-value actions

1. Verify which public BSP dependencies match the pinned historical source and their licenses; do not assume source availability equals compatibility.
2. Add non-destructive source-level checks and tests for variant mismatch and dependency closure.
3. Request only **privacy-minimized**, read-only partition facts from the actual SM-A750F if source-level research cannot resolve topology.
4. Avoid building or distributing an Android 17 image before the above gates are met.

No public repository should contain proprietary firmware blobs, device IDs, EFS, or private partition dumps.
