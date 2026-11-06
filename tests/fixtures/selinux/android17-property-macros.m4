dnl Reduced Android 17 macro subset (Apache-2.0), NOT complete policy.
dnl LineageOS/android_system_sepolicy public/te_macros
dnl commit d61fd80832f558d52de026097d30d695634e8b0f
dnl The treble neverallow helper is set to the strict branch.
define(`define_prop', `
  type $1, property_type, $2_property_type, $2_$3_property_type;
')
define(`treble_sysprop_neverallow', `$1')
define(`vendor_internal_prop', `
  define_prop($1, vendor, internal)
  treble_sysprop_neverallow(`
    neverallow { coredomain -init -dumpstate } $1:file no_rw_file_perms;
  ')
')
