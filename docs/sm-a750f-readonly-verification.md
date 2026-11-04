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
