# Offline LineageOS 18.1 OTA inventory for a7y18lte

This script is an **input discovery and provenance check** for the Samsung
Galaxy A7 (2018) Android 17 port. It is NOT an Android 17 ROM, driver port,
extraction utility, compatibility proof or flashable artifact.

Run against a local copy of the **2026-11-08** public A2L5E0X1 release:

    python3 tools/inspect_lineage18_ota.py \
      lineage-18.1-20261108-UNOFFICIAL-A2L5E0X1-a7y18lte.zip \
      --expected-size 742826234 \
      --expected-sha256 926cd48efb2a4b024e85bec06cdfedcbb9ca34ed4db9c458c6949b8a606d6c0d \
      > lineage18-ota-inventory.json

For the **October 17 build the user reported working**, use that exact
archive's separately published hash and size, not the November values. If
unavailable, omit both expected arguments and treat the calculated digest as
local-only evidence, **not** as third-party authentication.

The script streams SHA-256 and checks supplied digest/size *before* inventory,
reads only bounded standard OTA metadata, lists a strict allowlist of packaging
markers and partition filenames, and never extracts or mounts binary images.
It never prints unknown ZIP entries or metadata keys. Archive names are checked
for traversal/duplicate entries; the JSON omits proprietary binary contents.

Run regression tests using synthetic ZIP files only:

    python3 -m unittest discover -s tests -p 'test_lineage18_ota_inventory.py' -v

The existing research-validation GitHub Actions workflow discovers them
automatically on pushes to the development branch.

## What this does not establish

ZIP packaging does not prove Android 17 kernel support, VINTF/HAL compatibility,
modern driver availability or successful boot. The older 4.4 kernel's Android 17
NetBpfLoad incompatibility remains unresolved. Follow-up compatibility research
should use authorized *local* extraction of safe configuration details and
public-source comparisons. Never upload proprietary Samsung blobs, DRM keys,
EFS/IMEI information, credentials or personal partitions to this public repo.
Do not modify the user's working Android 11 installation.
