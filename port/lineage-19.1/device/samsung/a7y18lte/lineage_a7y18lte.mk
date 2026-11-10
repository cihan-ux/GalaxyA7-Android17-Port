# SPDX-License-Identifier: Apache-2.0
#
# LineageOS 19.1 / Android 12L experimental product stage for SM-A750F.
# To apply to an isolated lineage-19.1 source checkout, replace ONLY this
# product file in device/samsung/a7y18lte/ after reviewing the diff.
# This source-only stage is NOT a functioning ROM or proven vendor interface.

# Match the tested LineageOS 18.1 product inheritance ordering.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# SM-A750F originally shipped with Android 8.0, API 26. The Android 11
# research device tree uses 28; that is not the device's launch API.
# This fixes product metadata only. Vendor/FCM compatibility is unresolved.
$(call inherit-product, $(SRC_TARGET_DIR)/product/product_launched_with_o.mk)

$(call inherit-product, device/samsung/a7y18lte/device.mk)
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

PRODUCT_NAME := lineage_a7y18lte
PRODUCT_DEVICE := a7y18lte
PRODUCT_BRAND := samsung
PRODUCT_MODEL := Galaxy A7 2018
PRODUCT_MANUFACTURER := samsung
PRODUCT_GMS_CLIENTID_BASE := android-samsung
