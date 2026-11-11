# SPDX-License-Identifier: Apache-2.0
#
# Experimental Android 17 / LineageOS 24.0 product registration.
# Staging overlay for the pinned a7y18lte device tree, not a buildable ROM.
#
PRODUCT_MAKEFILES := \
    $(LOCAL_DIR)/lineage_a7y18lte.mk

# Android 17's lunch uses PRODUCT-RELEASE-VARIANT; do not use the
# two-component Android 11 lunch shortcut for this experimental target.
COMMON_LUNCH_CHOICES := \
    lineage_a7y18lte-trunk_staging-userdebug
