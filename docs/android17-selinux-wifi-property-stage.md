# Android 17 Galaxy A7: Samsung SLSI Wi-Fi property SELinux port

**Source-only candidate; NOT a compiled Android 17 policy or verified handset ROM.**

## Verified inputs
- Original Samsung SLSI `common/vendor/property.te` at LineageOS 18.1 commit `9968b62f8f76c22143a8fc7491440aa11c32e6f4` defines `type vendor_wifi_prop, property_type;`.
- Official Samsung SLSI LineageOS 24.0 commit `224e135300fbb07ee12968cc57ad053a267e3ce4` defines **`vendor_internal_prop(vendor_wifi_prop)`**.
- Both versions label `vendor.wifi.` and `ro.vendor.wifi.` as `vendor_wifi_prop`; the LineageOS 24.0 Wi-Fi HAL policy uses `get_prop(hal_wifi_default, vendor_wifi_prop)`.
- LineageOS 24.0 platform SELinux at `d61fd80832f558d52de026097d30d695634e8b0f` defines the internal-property macro with conditional core-domain read restrictions.

## Security correction
The previous candidate used `vendor_public_prop`, which is broader than the official 24.0 Samsung Wi-Fi policy. The follow-up commit revises the one-line patch to `vendor_internal_prop(vendor_wifi_prop)`. This is not a claim that vendor service access is validated. The reduced `m4` fixture exercises type expansion but does not constitute full `secilc`/neverallow compilation.

## Offline checks
Run `python3 tools/check_selinux_wifi_property_port.py` and `python3 -m unittest discover -s tests -v`.

Remaining: full policy compilation and property_contexts merging, actual SM-A750F vendor HAL access, kernel 4.4.302 BPF, VINTF FCM level 3 and firmware mismatches (SM-A750F A750FXXU5CVG1 vs reference A750FNXXU5CVG2). No proprietary files, device contact or SELinux bypass.
