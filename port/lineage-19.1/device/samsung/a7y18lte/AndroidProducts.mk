# SPDX-License-Identifier: Apache-2.0
# Experimental target for LINEAGEOS 19.1 (Android 12L), not Android 17.
PRODUCT_MAKEFILES := \
    $(LOCAL_DIR)/lineage_a7y18lte.mk

# LineageOS 19.1 uses the legacy PRODUCT-VARIANT lunch naming.
COMMON_LUNCH_CHOICES := \
    lineage_a7y18lte-userdebug
