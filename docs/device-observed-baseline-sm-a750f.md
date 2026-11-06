# User-observed device baseline — Galaxy A7 (2018), 2026-11-05

Source: user-supplied DevCheck report captured 2026-11-05 13:33 (local). This is application-reported metadata, **not** a partition dump, boot image, bootloader verification, or proof of vendor compatibility.

| Field | Observed |
| --- | --- |
| Model | SM-A750F |
| Codename | a7y18lte |
| Hardware | universal7885 / Exynos 7885 |
| CPU | 6× Cortex-A53, 2× Cortex-A73 |
| GPU | Mali-G71; OpenGL ES 3.2 |
| RAM | 4 GB |
| Storage | 64 GB; ext4 reported |
| Android | 10 |
| Build | QP1A.190711.020.A750FXXU5CVG1 |
| Security patch | 2022-07-01 |
| Architecture | aarch64; arm64-v8a, armeabi-v7a, armeabi |
| Stock kernel | 4.4.177-22371317; 2022-07-25 build |
| Wi-Fi | 5 GHz supported |
| Bluetooth | Supported; BLE supported |

## Build implications

1. The exact target is **SM-A750F**, not SM-A750FN. Previously observed proprietary vendor provenance from **A750FNXXU5CVG2** is not evidence of compatibility with **A750FXXU5CVG1**.
2. The running stock kernel is **4.4.177**. The separately compiled **4.4.302** research kernel is not the stock boot kernel, and has not been tested on-device.
3. The report does **not** identify the Wi-Fi or Bluetooth chip/driver implementation. Do not infer `scsc_wifibt` source compatibility from radio capability alone.
4. No partition sizes/layout, bootloader lock status, recovery state, DTBO, proprietary HAL versions, camera sensor identifiers, or firmware binary provenance can be established from this report.
5. This repository remains research-only; Android 17 has not been built or flashed.

Privacy: network MAC address, device-specific identifiers, and unrelated battery/usage telemetry from the original report are intentionally **not included**. No raw user report or proprietary binary is committed.
