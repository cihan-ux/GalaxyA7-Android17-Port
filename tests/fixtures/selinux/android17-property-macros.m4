dnl Minimal upstream macro excerpt, NOT a complete Android 17 policy.
dnl LineageOS/android_system_sepolicy public/te_macros
dnl d61fd80832f558d52de026097d30d695634e8b0f (Apache-2.0)
define(`define_prop', `
  type $1, property_type, $2_property_type, $2_$3_property_type;
')
define(`vendor_public_prop', `define_prop($1, vendor, public)')
