# SPDX-License-Identifier: Apache-2.0
#
# Experimental LineageOS 24.0 product delta for Galaxy A7 2018 (a7y18lte).
# This preserves the pinned historical BSP inheritance; HAL/VINTF/vendor
# compatibility is NOT solved by registering the product.
#
# Keep the 64-bit-zygote/telephony inheritance order from the pinned tree.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Samsung's SM-A750F update history confirms original Android 8.0 (API 26).
# The pinned legacy LineageOS 18.1 tree instead says 28: record that
# mismatch, but do not silently carry an inaccurate launch API into A17.
# Actual vendor/FCM viability with shipping API 26 is NOT yet verified.
$(call inherit-product, $(SRC_TARGET_DIR)/product/product_launched_with_o.mk)

$(call inherit-product, device/samsung/a7y18lte/device.mk)
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

PRODUCT_NAME := lineage_a7y18lte
PRODUCT_DEVICE := a7y18lte
PRODUCT_BRAND := samsung
PRODUCT_MODEL := Galaxy A7 2018
PRODUCT_MANUFACTURER := samsung
PRODUCT_GMS_CLIENTID_BASE := android-samsung
