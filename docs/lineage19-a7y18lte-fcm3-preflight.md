# Galaxy A7 (2018) LineageOS 19.1 — FCM 3 device HAL declaration preflight

**Scope: source-only, incomplete. No Android 12L ROM, vendor service or full
libvintf/checkvintf verification.** This does not change the A7 phone.

## Pinned inputs

- [Legacy A7 device manifest](https://github.com/exynos7885-dev/device_samsung_a7y18lte/blob/f17643ba01010c45b628d5acb8f48350ded61606/manifest.xml): HIDL fingerprint, keymaster, NFC, touch
- [Legacy Exynos7885 common manifest](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/blob/f2ce8d2093711026f021cba7036334d381d455ef/manifest.xml): graphics, audio, radio, health, media and vendor Samsung services
- [LineageOS 19.1 framework compatibility matrix 3](https://github.com/LineageOS/android_hardware_interfaces/blob/ae469cee0dce6d71489588126a15da8e67a50102/compatibility_matrices/compatibility_matrix.3.xml)

Both inspected device manifests declare **target-level 3**. FCM 3 is
present in the pinned LineageOS 19.1 platform and its Android.bp includes
Linux 4.4 kernel configurations. That removes one of the version-specific
Android 17 blockers; it does **not** prove that the old vendor blobs satisfy
the Android 12L framework.

## Source declaration result

For the *nine mandatory HIDL HAL groups* in this specific pinned FCM 3
matrix, **eight appear as plausible declarations** in the two inspected
source manifests: audio, audio effect, gatekeeper, graphics allocator,
graphics composer, graphics mapper, health, and media OMX.

**DRM version 1.1** is required by this matrix but **is not declared in
these two files**. Another device/vendor/ODM manifest fragment may add
it, or the port may require a legitimate service/vendor change.
**Do not fabricate a DRM HAL declaration or bypass VINTF.** Declaring an
interface is not proof that a matching service or hardware implementation
exists.

The [source preflight script](../tools/audit_lineage19_fcm3_hal.py) parses
both manifests and the FCM3 XML, checks mandatory groups, version-family
and minimum minor versions, and interface/instance coverage. This is an
approximate *triage*, not an implementation of Android libvintf's complex
merge/override and HIDL instance rules.

[GitHub Actions](../.github/workflows/a7-lineage19-fcm3-preflight.yml) fetches
the exact pinned upstream sources, reruns regression tests, produces a
machine-readable report and explicitly asserts the DRM gap remains visible.
It does not fetch proprietary binaries or produce a ROM.

## Next real gate

Perform a full LineageOS 19.1 source checkout with vendor files sourced
legally; inspect all manifest fragments in the resulting vendor/ODM
partitions, use the actual Android 12L \`checkvintf\` against the built
images, and inspect first Kati/Soong failures. Only after those steps can
framework-vendor compatibility or on-device behavior be assessed.

Keep the Android 17 branch untouched. No OTA/dirty-flash or working
LineageOS 19.1 build exists yet.
