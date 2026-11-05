# SPDX-License-Identifier: Apache-2.0
#
# Experimental LineageOS 24.0 product delta for Galaxy A7 2018 (a7y18lte).
# This preserves the pinned historical BSP inheritance; HAL/VINTF/vendor
# compatibility is NOT solved by registering the product.
#
# Keep the 64-bit-zygote/telephony inheritance order from the pinned tree.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Samsung Galaxy A7 (2018) launched with Android 9 (API 28).
# The LineageOS 24.0 target provides this file setting
# PRODUCT_SHIPPING_API_LEVEL := 28; never falsify the shipping API.
$(call inherit-product, $(SRC_TARGET_DIR)/product/product_launched_with_p.mk)

$(call inherit-product, device/samsung/a7y18lte/device.mk)
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

PRODUCT_NAME := lineage_a7y18lte
PRODUCT_DEVICE := a7y18lte
PRODUCT_BRAND := samsung
PRODUCT_MODEL := Galaxy A7 2018
PRODUCT_MANUFACTURER := samsung
PRODUCT_GMS_CLIENTID_BASE := android-samsung
