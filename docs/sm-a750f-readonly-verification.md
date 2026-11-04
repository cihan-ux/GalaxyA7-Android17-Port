# SM-A750F — read-only device verification

This checklist is intended for the owner's **Samsung Galaxy A7 (2018) SM-A750F** running stock Android 10. The baseline recorded from device screenshots is `A750FXXU5CVG1`. **Do not use SM-A750FN partition assumptions without verification.**

## On-device checks (no root, no flashing)

In **Settings → About phone → Software information**, record:
- Model number and baseband version (avoid sharing IMEI or serial number)
- Android version and build number
- Current security patch level

If Android developer options and USB debugging are already enabled and the owner consents, the following commands are read-only. ADB is optional; **do not enable OEM unlocking**.

```sh
adb devices
adb shell getprop ro.product.model
adb shell getprop ro.product.device
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.sdk
adb shell getprop ro.boot.bootloader
adb shell getprop ro.build.fingerprint
adb shell getprop ro.boot.dynamic_partitions
adb shell getprop ro.boot.super_partition
adb shell 'ls -l /dev/block/by-name 2>/dev/null'
```

Some stock firmware may not expose these properties or block the block-device listing. Missing output is **not** proof of absent dynamic partitions.

### Data minimization

Share only model, Android version, build ID and **partition names** if comfortable. Do not publish `getprop` full dumps, IMEI, serial numbers, EFS contents, accounts, modem/NV partitions, or device backups.

## Stop conditions

- If reported model is not SM-A750F, stop and re-evaluate.
- If partition topology differs from the newer source tree's dynamic-super assumptions, stop; do not repartition.
- If the bootloader version differs, do not assume firmware interchangeability.
- No flashing or data wipe until verified recovery, backups and build viability.

## Engineering follow-up

Use collected *non-sensitive* facts to compare `BoardConfig.mk`, partition layout and vendor extraction baseline. These commands **do not validate Android 17 compatibility**.

## Optional offline report checker

Create a local text file containing only allowlisted keys, for example:

```ini
ro.product.model=SM-A750F
ro.product.device=a7y18lte
ro.build.version.release=10
ro.build.version.sdk=29
```

Run `python3 tools/check_device_report.py report.txt`. The tool does not contact the phone, access the network or validate partition layout. **Do not paste full `adb shell getprop` output** into this file; it may include identifiers.

## Optional partition-name inventory

If you already have a **sanitized list of partition names**, place only the names in a local text file, one per line (for example, `boot`, `recovery`, `system`, `vendor`). Do not include block paths, serial numbers, partition dumps or sizes. Run:

```sh
python3 tools/check_partition_names.py partition-names.txt
```

The checker reports absent names and hints such as `super`; these are **not** evidence that dynamic partitions are correctly configured or safe to flash. Actual on-device topology remains unverified.
