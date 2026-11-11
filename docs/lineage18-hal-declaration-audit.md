# Source-level HAL declaration audit: A7 Android 11 -> Android 17 research

This is **not** a merged VINTF manifest, proof of Android 17 service
compatibility, or a flashable ROM. It identifies model-specific declarations
and source-level overrides that could be lost if the shared Exynos7885 HAL
list were copied blindly.

## Reproducible offline audit

Inputs are already checked into this repository as public-source, SHA-256-
verified fixtures, pinned in manifests/lineage-18.1-research.xml:

- tests/fixtures/upstream/common/manifest.xml, upstream
  exynos7885-dev/device_samsung_exynos7885-common at f2ce8d2.
- tests/fixtures/upstream/device/manifest.xml, upstream
  exynos7885-dev/device_samsung_a7y18lte at f17643b.

Run:

    python3 tools/check_source_evidence.py
    python3 tools/audit_lineage18_hal_declarations.py > lineage18-hal-audit.json
    python3 -m unittest discover -s tests -p 'test_lineage18_hal_declarations.py' -v

The audit records named HALs, versions, instance declarations, fqname
entries, the source file origin and whether the **device file itself**
declares an override. It rejects malformed XML, missing names, unknown formats
and mismatched target levels. It does not read or share proprietary blobs.

## Findings from the pinned research fixtures

- Common manifest: **49 HAL entries**; device manifest: **4 HAL entries**;
  both target-level **3** (historical Android 11).
- android.hardware.nfc is declared at version 1.2 in the common manifest,
  but the A7 device manifest has an **empty override=true declaration**.
  Mark as device_empty_override and investigate model/SKU-specific NFC
  behavior. A separate vendor.nxp.nxpnfc declaration in the common source
  remains present as a *source declaration*, but none of this proves whether
  the phone exposes or runs NFC.
- vendor.lineage.touch is **overridden by the A7 device source**, declaring
  both IGloveMode/default and IStylusMode/default. The common source lists
  only glove mode. Do not silently omit the A7-specific stylus interface.
- android.hardware.biometrics.fingerprint HIDL 2.1 and
  android.hardware.keymaster HIDL 3.0 occur in the A7-specific XML.
- android.hardware.radio in the common source includes explicit
  @1.4::IRadio/slot1 and slot2 plus @1.2::ISap instances. Its multiple
  source entries include an empty override and a subsequent concrete
  declaration. The audit shows all entries; it does not incorrectly equate
  the empty entry with a proven absence of radio support.

## What is still blocking real Android 17 progress

Source XML declarations do **not** prove HAL implementations exist in the
vendor partition or will work with modern Android. Next steps must assemble
the **actual** device+vendor+framework VINTF artifacts, run official libvintf
checks against the Android 17 framework compatibility matrix, validate
SELinux policy, check binary dependencies and carry out real device tests
only with separate consent and a restoration plan. Never change a
target-level just to suppress errors.

The modern Exynos7885 Linux 6.15 Image remains experimental. This audit
does **not** close the PMIC/ACPM integration or modem/graphics/camera blockers.
